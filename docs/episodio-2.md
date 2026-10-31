# Episodio 2: persistencia con SQLite

## Objetivo y requisito
R8: las reservas, activas y canceladas, persisten al detener y reiniciar la aplicación.

## Contexto suministrado
README.md (sección 1), .github/copilot-instructions.md y src/reglas.py.

## Instrucción al agente (extracto)
"Escribe primero tests/test_storage.py ... Ejecuta los tests y muéstrame que fallan. Implementa src/storage.py ... No modifiques src/reglas.py ni README.md, no crees consola. Pídeme aprobación antes de ejecutar comandos."

## Resultado del agente
Creó tests/test_storage.py (4 tests) y src/storage.py. Su versión quedó en el commit f233e29, que contiene solo esos dos archivos; al ejecutar yo la suite completa dio 20 passed.
Si mostró los tests fallando antes de implementar: no registrado.
Aprobaciones pedidas y cómo las di: no registradas.

## Mi revisión y hallazgos
Revisé src/storage.py. Está bien: consultas parametrizadas, commit/rollback y cierre de conexión, guarda también las reservas canceladas, y actualizar_estado falla con KeyError si el id no existe. Encontré dos problemas:
1. Agregó `buscar_solapadas`, que no pedí, que ningún test ejecuta y que duplica en SQL la regla de superposición de reglas.py (riesgo para R9).
2. El modo WAL puede crear archivos auxiliares (.db-wal, .db-shm) que mi .gitignore no excluía.

## Decisión
Aceptar con correcciones menores: eliminé `buscar_solapadas` y amplié .gitignore.

## Verificación propia
- `python -m pytest` → 20 passed (pytest 7.3.1, Python 3.11.2), antes y después de la corrección.
- Prueba manual de persistencia con procesos separados: un primer proceso guardó la reserva R-1 en data/prueba.db y imprimió "guardado"; un segundo proceso nuevo imprimió `[{'id': 'R-1', 'unidad_id': 'MIC-01', 'solicitante': 'Ana', 'inicio': '2026-11-03T10:00', 'fin': '2026-11-03T11:00', 'estado': 'activa'}]`. Luego borré el archivo de prueba.

## Evidencia
Commit del agente: f233e29. Commit de la corrección: 90cb3c8.
Archivos: src/storage.py, tests/test_storage.py, .gitignore.