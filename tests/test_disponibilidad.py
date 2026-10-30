import pytest

from reglas import cargar_inventario, consultar_disponibilidad, crear_reserva

INV = cargar_inventario()
D = "2026-11-03"


def _reserva(unidad="MIC-01", inicio=f"{D}T10:00", fin=f"{D}T11:00", reservas=None):
    return crear_reserva(
        unidad_id=unidad,
        solicitante="Ana Test",
        inicio=inicio,
        fin=fin,
        inventario=INV,
        reservas=reservas or [],
    )


def test_rechaza_intervalo_identico_en_misma_unidad():
    existente = _reserva()
    with pytest.raises(ValueError):
        _reserva(reservas=[existente])


def test_consulta_ocupado_en_superposicion():
    existente = _reserva()
    assert not consultar_disponibilidad(
        "MIC-01", f"{D}T10:30", f"{D}T11:30", INV, [existente]
    )


def test_consulta_libre_en_limite_consecutivo():
    existente = _reserva()
    assert consultar_disponibilidad(
        "MIC-01", f"{D}T11:00", f"{D}T12:00", INV, [existente]
    )


def test_consulta_libre_en_otra_unidad():
    existente = _reserva()
    assert consultar_disponibilidad(
        "MIC-02", f"{D}T10:00", f"{D}T11:00", INV, [existente]
    )


def test_consulta_libre_si_la_reserva_esta_cancelada():
    existente = _reserva()
    existente["estado"] = "cancelada"
    assert consultar_disponibilidad(
        "MIC-01", f"{D}T10:00", f"{D}T11:00", INV, [existente]
    )


def test_consulta_rechaza_unidad_desconocida():
    with pytest.raises(ValueError):
        consultar_disponibilidad("XXX-99", f"{D}T10:00", f"{D}T11:00", INV, [])