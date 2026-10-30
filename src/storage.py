from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "reservas.db"

ESTADOS_VALIDOS = {"activa", "cancelada"}
CAMPOS_RESERVA = ("id", "unidad_id", "solicitante", "inicio", "fin", "estado")
_COLUMNAS_SQL = ", ".join(CAMPOS_RESERVA)


class ReservaStorage:
    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        """Abre una conexión, hace commit/rollback y la cierra siempre."""
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            with conn:  # commit si todo sale bien, rollback si hay excepción
                yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS reservas (
                    id TEXT PRIMARY KEY,
                    unidad_id TEXT NOT NULL,
                    solicitante TEXT NOT NULL,
                    inicio TEXT NOT NULL,
                    fin TEXT NOT NULL,
                    estado TEXT NOT NULL CHECK(estado IN ('activa', 'cancelada')),
                    CHECK(fin > inicio)
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_reservas_unidad_inicio "
                "ON reservas (unidad_id, inicio)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_reservas_inicio ON reservas (inicio)"
            )

    @staticmethod
    def _validar(reserva: dict[str, Any]) -> None:
        faltantes = [c for c in CAMPOS_RESERVA if c not in reserva]
        if faltantes:
            raise ValueError(f"Faltan campos en la reserva: {', '.join(faltantes)}")

        if reserva["estado"] not in ESTADOS_VALIDOS:
            raise ValueError(f"Estado inválido: {reserva['estado']}")

        # Formato fijo "YYYY-MM-DDTHH:MM": la comparación de texto
        # equivale a la comparación cronológica.
        if reserva["fin"] <= reserva["inicio"]:
            raise ValueError("'fin' debe ser posterior a 'inicio'")

    def guardar(self, reserva: dict[str, Any]) -> dict[str, Any]:
        self._validar(reserva)

        with self._connect() as conn:
            conn.execute(
                f"""
                INSERT INTO reservas ({_COLUMNAS_SQL})
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    unidad_id = excluded.unidad_id,
                    solicitante = excluded.solicitante,
                    inicio = excluded.inicio,
                    fin = excluded.fin,
                    estado = excluded.estado
                """,
                tuple(reserva[c] for c in CAMPOS_RESERVA),
            )
        return {c: reserva[c] for c in CAMPOS_RESERVA}

    def listar(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            filas = conn.execute(
                f"SELECT {_COLUMNAS_SQL} FROM reservas ORDER BY inicio, id"
            ).fetchall()
        return [dict(fila) for fila in filas]

    def obtener_por_id(self, reserva_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            fila = conn.execute(
                f"SELECT {_COLUMNAS_SQL} FROM reservas WHERE id = ?",
                (reserva_id,),
            ).fetchone()
        return dict(fila) if fila else None

    def actualizar_estado(self, reserva_id: str, estado: str) -> dict[str, Any]:
        if estado not in ESTADOS_VALIDOS:
            raise ValueError(f"Estado inválido: {estado}")

        with self._connect() as conn:
            cursor = conn.execute(
                "UPDATE reservas SET estado = ? WHERE id = ?",
                (estado, reserva_id),
            )
            if cursor.rowcount == 0:
                raise KeyError(f"Reserva no encontrada: {reserva_id}")

            fila = conn.execute(
                f"SELECT {_COLUMNAS_SQL} FROM reservas WHERE id = ?",
                (reserva_id,),
            ).fetchone()

        return dict(fila)

    def buscar_solapadas(
        self,
        unidad_id: str,
        inicio: str,
        fin: str,
        excluir_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Reservas activas de la unidad que se pisan con [inicio, fin)."""
        consulta = (
            f"SELECT {_COLUMNAS_SQL} FROM reservas "
            "WHERE unidad_id = ? AND estado = 'activa' "
            "AND inicio < ? AND fin > ?"
        )
        params: list[Any] = [unidad_id, fin, inicio]
        if excluir_id is not None:
            consulta += " AND id != ?"
            params.append(excluir_id)
        consulta += " ORDER BY inicio"

        with self._connect() as conn:
            filas = conn.execute(consulta, params).fetchall()
        return [dict(fila) for fila in filas]