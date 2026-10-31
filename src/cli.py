from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from reglas import cargar_inventario, cancelar_reserva, consultar_disponibilidad, crear_reserva
from storage import DEFAULT_DB_PATH, ReservaStorage


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sistema de reservas del laboratorio")
    subparsers = parser.add_subparsers(dest="comando", required=True)

    subparsers.add_parser("unidades", help="Lista las unidades disponibles")

    disponibilidad = subparsers.add_parser("disponibilidad", help="Consulta la disponibilidad de una unidad")
    disponibilidad.add_argument("unidad")
    disponibilidad.add_argument("inicio")
    disponibilidad.add_argument("fin")

    reservar = subparsers.add_parser("reservar", help="Crea una reserva activa")
    reservar.add_argument("unidad")
    reservar.add_argument("solicitante")
    reservar.add_argument("inicio")
    reservar.add_argument("fin")

    cancelar = subparsers.add_parser("cancelar", help="Cancela una reserva por su id")
    cancelar.add_argument("reserva_id")

    subparsers.add_parser("listar", help="Muestra todas las reservas")
    return parser


def main(argv: Sequence[str] | None = None, db_path: str | Path | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    base_path = Path(db_path) if db_path is not None else DEFAULT_DB_PATH
    store = ReservaStorage(base_path)

    try:
        if args.comando == "unidades":
            for unidad in cargar_inventario():
                print(unidad)
            return 0

        if args.comando == "disponibilidad":
            disponible = consultar_disponibilidad(
                args.unidad,
                args.inicio,
                args.fin,
                cargar_inventario(),
                store.listar(),
            )
            print("Disponible" if disponible else "Ocupada")
            return 0

        if args.comando == "reservar":
            reserva = crear_reserva(
                unidad_id=args.unidad,
                solicitante=args.solicitante,
                inicio=args.inicio,
                fin=args.fin,
                inventario=cargar_inventario(),
                reservas=store.listar(),
            )
            store.guardar(reserva)
            print(f"Reserva creada: {reserva['id']}")
            return 0

        if args.comando == "cancelar":
            reserva_cancelada = cancelar_reserva(args.reserva_id, store)
            print(f"Reserva cancelada: {reserva_cancelada['id']}")
            return 0

        if args.comando == "listar":
            for reserva in store.listar():
                print(
                    f"{reserva['id']} | {reserva['unidad_id']} | {reserva['solicitante']} | "
                    f"{reserva['inicio']} | {reserva['fin']} | {reserva['estado']}"
                )
            return 0

        parser.error(f"Comando no soportado: {args.comando}")
        return 2
    except (ValueError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
