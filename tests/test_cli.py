import pytest

from cli import main
from storage import ReservaStorage

D = "2026-11-03"


def test_cli_unidades(tmp_path, capsys):
    db_path = tmp_path / "reservas.db"
    codigo = main(["unidades"], db_path=db_path)
    salida = capsys.readouterr()

    assert codigo == 0
    assert "MIC-01" in salida.out
    assert "MIC-02" in salida.out


def test_cli_disponibilidad_informa_estado(tmp_path, capsys):
    db_path = tmp_path / "reservas.db"
    codigo = main(["disponibilidad", "MIC-01", f"{D}T10:00", f"{D}T11:00"], db_path=db_path)
    salida = capsys.readouterr()

    assert codigo == 0
    assert "disponible" in salida.out.lower()


def test_cli_reservar_y_listar(tmp_path, capsys):
    db_path = tmp_path / "reservas.db"

    codigo = main([
        "reservar",
        "MIC-01",
        "Ana",
        f"{D}T10:00",
        f"{D}T11:00",
    ], db_path=db_path)
    salida = capsys.readouterr()

    assert codigo == 0
    assert "Reserva creada" in salida.out

    codigo = main(["listar"], db_path=db_path)
    salida = capsys.readouterr()
    assert codigo == 0
    assert "MIC-01" in salida.out
    assert "Ana" in salida.out


def test_cli_cancelar_y_error_claro(tmp_path, capsys):
    db_path = tmp_path / "reservas.db"
    store = ReservaStorage(db_path)
    store.guardar({
        "id": "R-CLI-01",
        "unidad_id": "MIC-01",
        "solicitante": "Ana",
        "inicio": f"{D}T14:00",
        "fin": f"{D}T15:00",
        "estado": "activa",
    })

    codigo = main(["cancelar", "R-CLI-01"], db_path=db_path)
    salida = capsys.readouterr()
    assert codigo == 0
    assert "cancelada" in salida.out.lower()
    assert store.obtener_por_id("R-CLI-01")["estado"] == "cancelada"

    codigo = main(["cancelar", "R-CLI-404"], db_path=db_path)
    salida = capsys.readouterr()
    assert codigo == 1
    assert "no encontrada" in salida.err.lower() or "inexistente" in salida.err.lower()
