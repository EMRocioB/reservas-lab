import pytest

from reglas import cargar_inventario, crear_reserva, hay_conflicto


@pytest.fixture
def inventario():
    return cargar_inventario()


def test_creacion_valida(inventario):
    reserva = crear_reserva(
        unidad_id="MIC-01",
        solicitante="Ana Lopez",
        inicio="2026-11-03T10:00",
        fin="2026-11-03T11:00",
        inventario=inventario,
        reservas=[],
    )

    assert reserva["unidad_id"] == "MIC-01"
    assert reserva["solicitante"] == "Ana Lopez"
    assert reserva["inicio"] == "2026-11-03T10:00"
    assert reserva["fin"] == "2026-11-03T11:00"
    assert reserva["estado"] == "activa"


def test_rechazo_de_superposicion(inventario):
    reservas = [
        crear_reserva(
            unidad_id="MIC-01",
            solicitante="Pedro",
            inicio="2026-11-03T10:00",
            fin="2026-11-03T11:00",
            inventario=inventario,
            reservas=[],
        )
    ]

    with pytest.raises(ValueError, match="ocupada"):
        crear_reserva(
            unidad_id="MIC-01",
            solicitante="Maria",
            inicio="2026-11-03T10:30",
            fin="2026-11-03T11:30",
            inventario=inventario,
            reservas=reservas,
        )


def test_limites_consecutivos_permitidos(inventario):
    reservas = [
        crear_reserva(
            unidad_id="MIC-01",
            solicitante="Pedro",
            inicio="2026-11-03T10:00",
            fin="2026-11-03T11:00",
            inventario=inventario,
            reservas=[],
        )
    ]

    reserva = crear_reserva(
        unidad_id="MIC-01",
        solicitante="Maria",
        inicio="2026-11-03T11:00",
        fin="2026-11-03T12:00",
        inventario=inventario,
        reservas=reservas,
    )

    assert reserva["inicio"] == "2026-11-03T11:00"
    assert reserva["fin"] == "2026-11-03T12:00"


def test_unidades_distintas_simultaneas(inventario):
    reservas = [
        crear_reserva(
            unidad_id="MIC-01",
            solicitante="Pedro",
            inicio="2026-11-03T10:00",
            fin="2026-11-03T11:00",
            inventario=inventario,
            reservas=[],
        )
    ]

    # MIC-01 sí está ocupada en ese horario
    assert hay_conflicto(
        "MIC-01", "2026-11-03T10:00", "2026-11-03T11:00", reservas
    )
    # MIC-02 no tiene conflicto con la reserva de MIC-01
    assert not hay_conflicto(
        "MIC-02", "2026-11-03T10:00", "2026-11-03T11:00", reservas
    )

    reserva = crear_reserva(
        unidad_id="MIC-02",
        solicitante="Maria",
        inicio="2026-11-03T10:00",
        fin="2026-11-03T11:00",
        inventario=inventario,
        reservas=reservas,
    )
    assert reserva["unidad_id"] == "MIC-02"


@pytest.mark.parametrize(
    "unidad_id, solicitante, inicio, fin, mensaje",
    [
        ("XXX-99", "Ana", "2026-11-03T10:00", "2026-11-03T11:00", "(?i)unidad desconocida"),
        ("MIC-01", "   ", "2026-11-03T10:00", "2026-11-03T11:00", "(?i)solicitante"),
        ("MIC-01", "Ana", "2026-13-40T10:00", "2026-11-03T11:00", "(?i)fecha"),
        ("MIC-01", "Ana", "2026-11-03T11:00", "2026-11-03T11:00", "(?i)anterior"),
        ("MIC-01", "Ana", "2026-11-03T10:00", "2026-11-03T10:05", "(?i)duraci"),
        ("MIC-01", "Ana", "2026-11-03T10:00", "2026-11-03T18:16", "(?i)duraci"),
    ],
)
def test_entradas_invalidas(inventario, unidad_id, solicitante, inicio, fin, mensaje):
    with pytest.raises(ValueError, match=mensaje):
        crear_reserva(
            unidad_id=unidad_id,
            solicitante=solicitante,
            inicio=inicio,
            fin=fin,
            inventario=inventario,
            reservas=[],
        )