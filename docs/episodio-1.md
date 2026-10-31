# Episodio 1: reglas de superposición y validaciones

## Objetivo y requisito
R4, R5, R6 y R9: rechazar superposiciones, permitir límites consecutivos y unidades distintas, validar entradas, y que la consulta de disponibilidad use las mismas reglas.

## Contexto suministrado
README.md (sección 1) y .github/copilot-instructions.md (regla: intervalos semiabiertos, nunca comparar límites con <=).

## Instrucción al agente (extracto)
"Escribe primero tests/test_reglas.py ... Ejecuta los tests y muéstrame que fallan. Implementa src/reglas.py ... No toques README.md, no crees persistencia ni CLI. Pídeme aprobación antes de ejecutar comandos."

## Resultado del agente
Creó tests/test_reglas.py (10 tests) y src/reglas.py. Informó que la suite pasaba con 10 pruebas; al ejecutarla yo, pasaron.
Si mostró los tests fallando antes de implementar: no registrado.
Aprobaciones pedidas y cómo las di: no registradas.
Nota: no hice commit de la versión del agente antes de corregirla, por lo que esa versión no está en el historial de git.

## Mi revisión y hallazgos
Al leer src/reglas.py encontré problemas que los tests del agente no detectaban:
1. `hay_superposicion` devolvía False para dos intervalos idénticos sin mirar las reservas existentes.
2. La lógica de superposición estaba duplicada dentro de `crear_reserva`, por lo que no existía una consulta de disponibilidad con las mismas reglas (R9).
3. Un test (`test_unidades_distintas_simultaneas`) daba por correcta esa conducta, y el parámetro `mensaje` de `test_entradas_invalidas` no se usaba.

## Decisión
Corregir. La corrección la escribí con ayuda de un asistente de chat, no con el agente: una única función `intervalos_se_superponen` con comparaciones estrictas, `hay_conflicto`, `consultar_disponibilidad`, tests adaptados y `tests/test_disponibilidad.py`.

## Verificación propia
- `python -m pytest` → 16 passed in 0.12s (pytest 7.3.1, Python 3.11.2).
- Prueba de sensibilidad: cambié temporalmente el primer `<` por `<=` en `intervalos_se_superponen`. `python -m pytest` mostró 2 failed, 14 passed. Fallaron `test_consulta_libre_en_limite_consecutivo` (assert False) y `test_limites_consecutivos_permitidos` (ValueError: La unidad MIC-01 ya está ocupada en ese intervalo). Tras `git restore src/reglas.py`, volvieron a pasar los 16.

## Evidencia
Commit de la versión corregida: 1f7428d.
Archivos: src/reglas.py, tests/test_reglas.py, tests/test_disponibilidad.py.