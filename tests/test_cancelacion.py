import pytest

from reglas import cancelar_reserva, cargar_inventario, consultar_disponibilidad, crear_reserva
from storage import ReservaStorage

INV = cargar_inventario()
D = "2026-11-03"


def _reserva(unidad="MIC-01", solicitante="Ana", inicio=f"{D}T10:00", fin=f"{D}T11:00", estado="activa"):
    return {
        "id": "R-001" if estado == "activa" else "R-999",
        "unidad_id": unidad,
        "solicitante": solicitante,
        "inicio": inicio,
        "fin": fin,
        "estado": estado,
    }


def test_cancelar_reserva_conserva_id_y_datos_y_libera_intervalo(tmp_path):
    db_path = tmp_path / "reservas.db"
    store = ReservaStorage(db_path)
    reserva = crear_reserva(
        unidad_id="MIC-01",
        solicitante="Ana",
        inicio=f"{D}T10:00",
        fin=f"{D}T11:00",
        inventario=INV,
        reservas=[],
    )
    store.guardar(reserva)

    cancelada = cancelar_reserva(reserva["id"], store)

    assert cancelada["id"] == reserva["id"]
    assert cancelada["unidad_id"] == "MIC-01"
    assert cancelada["solicitante"] == "Ana"
    assert cancelada["inicio"] == f"{D}T10:00"
    assert cancelada["fin"] == f"{D}T11:00"
    assert cancelada["estado"] == "cancelada"
    assert consultar_disponibilidad(
        "MIC-01",
        f"{D}T10:00",
        f"{D}T11:00",
        INV,
        store.listar(),
    ) is True


def test_cancelar_reserva_inexistente_o_ya_cancelada_da_error_claro(tmp_path):
    db_path = tmp_path / "reservas.db"
    store = ReservaStorage(db_path)

    with pytest.raises(KeyError, match="no encontrada|inexistente"):
        cancelar_reserva("NO-EXISTE", store)

    reserva = crear_reserva(
        unidad_id="MIC-02",
        solicitante="Pedro",
        inicio=f"{D}T09:00",
        fin=f"{D}T10:00",
        inventario=INV,
        reservas=[],
    )
    store.guardar(reserva)
    cancelar_reserva(reserva["id"], store)

    with pytest.raises(ValueError, match="cancelada|ya cancelada"):
        cancelar_reserva(reserva["id"], store)
