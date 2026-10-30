from storage import ReservaStorage


def _reserva(*, reserva_id: str, unidad_id: str = "MIC-01", solicitante: str = "Ana", inicio: str = "2026-11-03T10:00", fin: str = "2026-11-03T11:00", estado: str = "activa"):
    return {
        "id": reserva_id,
        "unidad_id": unidad_id,
        "solicitante": solicitante,
        "inicio": inicio,
        "fin": fin,
        "estado": estado,
    }


def test_guardar_una_reserva_y_recuperarla(tmp_path):
    db_path = tmp_path / "reservas.db"
    store = ReservaStorage(db_path)
    reserva = _reserva(reserva_id="R-001")

    store.guardar(reserva)
    reservas = store.listar()

    assert len(reservas) == 1
    assert reservas[0]["id"] == "R-001"
    assert reservas[0]["unidad_id"] == "MIC-01"
    assert reservas[0]["solicitante"] == "Ana"
    assert reservas[0]["estado"] == "activa"


def test_guardar_reserva_activa_y_cancelada_y_recuperarlas(tmp_path):
    db_path = tmp_path / "reservas.db"
    store = ReservaStorage(db_path)

    activa = _reserva(reserva_id="R-001")
    cancelada = _reserva(reserva_id="R-002", estado="cancelada")

    store.guardar(activa)
    store.guardar(cancelada)

    reservas = store.listar()
    estados = {reserva["id"]: reserva["estado"] for reserva in reservas}

    assert estados == {"R-001": "activa", "R-002": "cancelada"}
    assert next(reserva for reserva in reservas if reserva["id"] == "R-002")["solicitante"] == "Ana"


def test_actualizar_estado_de_reserva_a_cancelada_conservando_datos(tmp_path):
    db_path = tmp_path / "reservas.db"
    store = ReservaStorage(db_path)
    reserva = _reserva(reserva_id="R-003", solicitante="Belen")

    store.guardar(reserva)
    store.actualizar_estado("R-003", "cancelada")

    guardada = store.obtener_por_id("R-003")
    assert guardada["id"] == "R-003"
    assert guardada["unidad_id"] == "MIC-01"
    assert guardada["solicitante"] == "Belen"
    assert guardada["inicio"] == "2026-11-03T10:00"
    assert guardada["fin"] == "2026-11-03T11:00"
    assert guardada["estado"] == "cancelada"


def test_reinicio_de_la_aplicacion_conserva_las_reservas(tmp_path):
    db_path = tmp_path / "reservas.db"

    primer_store = ReservaStorage(db_path)
    primer_store.guardar(_reserva(reserva_id="R-010"))
    primer_store.guardar(_reserva(reserva_id="R-011", estado="cancelada"))

    segundo_store = ReservaStorage(db_path)
    reservas = segundo_store.listar()

    assert len(reservas) == 2
    assert {reserva["id"]: reserva["estado"] for reserva in reservas} == {
        "R-010": "activa",
        "R-011": "cancelada",
    }
