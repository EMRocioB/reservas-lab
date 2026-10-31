from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

FORMATO_FECHA = "%Y-%m-%dT%H:%M"
LARGO_FECHA = 16  # "YYYY-MM-DDTHH:MM"
DURACION_MINIMA_MIN = 15
DURACION_MAXIMA_MIN = 8 * 60


def cargar_inventario() -> list[str]:
    """Carga los IDs de unidad desde data/inventario.json."""
    ruta = Path(__file__).resolve().parents[1] / "data" / "inventario.json"
    with ruta.open("r", encoding="utf-8") as archivo:
        datos = json.load(archivo)
    return [unidad["id"] for unidad in datos]


def _parse_iso_datetime(valor: str) -> datetime:
    """Convierte 'YYYY-MM-DDTHH:MM' (con ceros) en datetime."""
    if not isinstance(valor, str) or len(valor) != LARGO_FECHA:
        raise ValueError(f"Fecha u hora inválida: {valor!r}")
    try:
        return datetime.strptime(valor, FORMATO_FECHA)
    except ValueError as exc:
        raise ValueError(f"Fecha u hora inválida: {valor!r}") from exc


def _validar_unidad(unidad_id: str, inventario: list[str]) -> None:
    if unidad_id not in inventario:
        raise ValueError(f"Unidad desconocida: {unidad_id}")


def _validar_solicitante(solicitante: str) -> None:
    if not isinstance(solicitante, str) or not solicitante.strip():
        raise ValueError("Solicitante vacío o inválido")


def _validar_intervalo(inicio: str, fin: str) -> None:
    inicio_dt = _parse_iso_datetime(inicio)
    fin_dt = _parse_iso_datetime(fin)

    if inicio_dt >= fin_dt:
        raise ValueError("El inicio debe ser estrictamente anterior al fin")

    minutos = int((fin_dt - inicio_dt).total_seconds() // 60)
    if minutos < DURACION_MINIMA_MIN or minutos > DURACION_MAXIMA_MIN:
        raise ValueError("La duración debe estar entre 15 minutos y 8 horas")


def intervalos_se_superponen(
    inicio_a: str, fin_a: str, inicio_b: str, fin_b: str
) -> bool:
    """Intervalos semiabiertos [inicio, fin): solo comparaciones estrictas."""
    return _parse_iso_datetime(inicio_a) < _parse_iso_datetime(fin_b) and (
        _parse_iso_datetime(inicio_b) < _parse_iso_datetime(fin_a)
    )


def hay_conflicto(
    unidad_id: str, inicio: str, fin: str, reservas: list[dict[str, Any]]
) -> bool:
    """True si hay una reserva ACTIVA de la misma unidad que se superpone."""
    for reserva in reservas:
        if reserva.get("estado", "activa") != "activa":
            continue
        if (reserva.get("unidad_id") or reserva.get("unidad")) != unidad_id:
            continue
        if intervalos_se_superponen(
            inicio, fin, str(reserva["inicio"]), str(reserva["fin"])
        ):
            return True
    return False


def _validar_disponibilidad(
    unidad_id: str,
    inicio: str,
    fin: str,
    inventario: list[str],
    reservas: list[dict[str, Any]],
) -> None:
    """Reglas compartidas por la consulta y la creación (R9)."""
    _validar_unidad(unidad_id, inventario)
    _validar_intervalo(inicio, fin)
    if hay_conflicto(unidad_id, inicio, fin, reservas):
        raise ValueError(f"La unidad {unidad_id} ya está ocupada en ese intervalo")


def consultar_disponibilidad(
    unidad_id: str,
    inicio: str,
    fin: str,
    inventario: list[str],
    reservas: list[dict[str, Any]],
) -> bool:
    """True si la unidad está libre. Entradas inválidas lanzan ValueError."""
    _validar_unidad(unidad_id, inventario)
    _validar_intervalo(inicio, fin)
    return not hay_conflicto(unidad_id, inicio, fin, reservas)


def crear_reserva(
    *,
    unidad_id: str,
    solicitante: str,
    inicio: str,
    fin: str,
    inventario: list[str],
    reservas: list[dict[str, Any]],
) -> dict[str, Any]:
    """Devuelve una reserva nueva o lanza ValueError."""
    _validar_solicitante(solicitante)
    _validar_disponibilidad(unidad_id, inicio, fin, inventario, reservas)
    return {
        "id": uuid4().hex,
        "unidad_id": unidad_id,
        "solicitante": solicitante.strip(),
        "inicio": inicio,
        "fin": fin,
        "estado": "activa",
    }


def cancelar_reserva(reserva_id: str, storage: Any) -> dict[str, Any]:
    """Cancela una reserva activa conservando su identificador y datos."""
    reserva = storage.obtener_por_id(reserva_id)
    if reserva is None:
        raise KeyError(f"Reserva no encontrada: {reserva_id}")

    if reserva.get("estado") == "cancelada":
        raise ValueError(f"La reserva {reserva_id} ya está cancelada")

    reserva["estado"] = "cancelada"
    storage.guardar(reserva)
    return reserva
