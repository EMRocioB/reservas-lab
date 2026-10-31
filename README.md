# Sistema de reservas de laboratorio

## 1. Especificación breve

### Problema
La coordinación de un laboratorio registra pedidos en mensajes y una planilla. A veces se confirma la misma unidad para horarios superpuestos, y a veces una cancelación sigue bloqueando el horario. Se necesita consultar disponibilidad, reservar y cancelar sin perder el historial.

### Alcance
- Incluye: leer el inventario, consultar disponibilidad, reservar, cancelar y persistir los datos. Interfaz de consola.
- No incluye: administrar el inventario, autenticación y roles, notificaciones, pagos, integraciones externas, interfaz gráfica ni concurrencia distribuida.

### Inventario inicial
Cada ID identifica una unidad física distinta.

| ID de unidad | Equipo |
|---|---|
| MIC-01 | Microscopio digital |
| MIC-02 | Microscopio digital |
| OSC-01 | Osciloscopio |
| MUL-01 | Multímetro |
| FUE-01 | Fuente de alimentación |

### Requisitos verificables
- **R1.** El sistema carga el inventario de 5 unidades desde `data/inventario.json`.
- **R2.** Se puede consultar si una unidad está disponible en un intervalo.
- **R3.** Se puede crear una reserva con identificador único, unidad, solicitante, inicio y fin.
- **R4.** Se rechaza una reserva que se superponga con otra reserva activa de la misma unidad.
- **R5.** Se permiten reservas con límites consecutivos y reservas simultáneas de unidades distintas.
- **R6.** Se rechazan entradas inválidas: unidad desconocida, solicitante vacío o solo espacios, fechas u horas inválidas, e inicio no estrictamente anterior al fin.
- **R7.** Se puede cancelar una reserva: conserva identificador y datos, cambia su estado a cancelada y libera el intervalo.
- **R8.** Las reservas (activas y canceladas) persisten al detener y reiniciar la aplicación.
- **R9.** La consulta de disponibilidad (R2) aplica las mismas reglas que la creación de reservas.

### Reglas
- Una reserva **activa** ocupa el intervalo; una **cancelada** no bloquea.
- Los intervalos son semiabiertos `[inicio, fin)`: dos reservas se superponen si `inicio_A < fin_B` y `inicio_B < fin_A`.
- Una reserva incluye una sola unidad.

### Supuestos (decisiones propias, modificables)
- Formato de fecha y hora: ISO 8601 sin zona, por ejemplo `2026-11-03T10:00`.
- Zona horaria: única y sin conversión (hora local de Buenos Aires, `America/Argentina/Buenos_Aires`).
- Fechas pasadas: se permiten (así las pruebas no dependen del reloj).
- Duración mínima 15 minutos y máxima 8 horas.
- Sin límite de anticipación.
- Cancelar una reserva ya cancelada o inexistente produce un error claro.
- Los solicitantes son nombres ficticios.

### Criterios de aceptación
1. Con MIC-01 reservado de 10:00 a 11:00, se rechaza 10:30 a 11:30.
2. Con MIC-01 reservado de 10:00 a 11:00, se permite 11:00 a 12:00.
3. Con MIC-01 ocupado de 10:00 a 11:00, MIC-02 puede reservarse de 10:00 a 11:00.
4. Tras cancelar la reserva de MIC-01 de 10:00 a 11:00, ese intervalo vuelve a estar disponible y la reserva cancelada sigue registrada con su identificador.
5. Tras detener y reiniciar la aplicación, las reservas activas y canceladas siguen presentes.
6. Se rechazan: unidad `XXX-99`, solicitante `"   "`, fecha `2026-13-40T10:00` e inicio igual o posterior al fin.

## 2. Solución
### Estructura
```
data/inventario.json      Inventario inicial (5 unidades)
src/reglas.py             Validaciones, superposición, disponibilidad, creación y cancelación
src/storage.py            Persistencia en SQLite
src/cli.py                Consola (argparse)
tests/                    Pruebas automáticas (pytest)
docs/                     Progreso y registro de cada episodio
.github/copilot-instructions.md   Instrucciones del agente
```

### Decisiones técnicas
- Python 3.11 con la biblioteca estándar; la única dependencia es `pytest` (`requirements.txt`).
- Almacenamiento en SQLite (módulo estándar `sqlite3`); alternativa descartada: un archivo JSON.
- Interfaz de consola con `argparse`.
- Una sola regla de superposición (`intervalos_se_superponen`, intervalos semiabiertos), usada por la consulta de disponibilidad y por la creación de reservas (R9).

### Requisitos previos y versiones
Python 3.11 o superior y git. Probado con Python 3.11.2, pytest 7.3.1 y git 2.45.2 en Windows 10.

### Instalación
```
git clone https://github.com/EMRocioB/reservas-lab.git
cd reservas-lab
python -m pip install -r requirements.txt
```

### Carga inicial y reinicio de datos
- El inventario se lee de `data/inventario.json` en cada ejecución; no hay que cargarlo.
- Las reservas se guardan en `data/reservas.db`, que se crea sola la primera vez. El archivo no se sube a git.
- Para reiniciar los datos, borra la base: `Remove-Item data/reservas.db*` (PowerShell). **Esto elimina todas las reservas, activas y canceladas.**

### Comandos
```
python src/cli.py unidades
python src/cli.py disponibilidad <unidad> <inicio> <fin>
python src/cli.py reservar <unidad> <solicitante> <inicio> <fin>
python src/cli.py cancelar <id>
python src/cli.py listar
```
Las fechas van en formato `AAAA-MM-DDTHH:MM`. Si el solicitante lleva espacios, ponlo entre comillas.

Pruebas automáticas: `python -m pytest` (26 pruebas).

### Ejemplo de entrada y salida
```
> python src/cli.py reservar MIC-01 Ana 2026-11-03T10:00 2026-11-03T11:00
Reserva creada: dc79b1ade73c4f90b0f2a8a58cc1b726
> python src/cli.py reservar MIC-01 Maria 2026-11-03T10:30 2026-11-03T11:30
La unidad MIC-01 ya está ocupada en ese intervalo
> python src/cli.py reservar MIC-01 Maria 2026-11-03T11:00 2026-11-03T12:00
Reserva creada: b26e4125d37c450a95b20a63b52e18ce
> python src/cli.py cancelar dc79b1ade73c4f90b0f2a8a58cc1b726
Reserva cancelada: dc79b1ade73c4f90b0f2a8a58cc1b726
> python src/cli.py disponibilidad MIC-01 2026-11-03T10:00 2026-11-03T11:00
Disponible
> python src/cli.py listar
dc79b1ade73c4f90b0f2a8a58cc1b726 | MIC-01 | Ana | 2026-11-03T10:00 | 2026-11-03T11:00 | cancelada
b26e4125d37c450a95b20a63b52e18ce | MIC-01 | Maria | 2026-11-03T11:00 | 2026-11-03T12:00 | activa
```

### Pendientes y limitaciones
- Los ids son uuid de 32 caracteres, incómodos de copiar.
- El error por id inexistente sale con comillas (`'Reserva no encontrada: ...'`).
- No hay zona horaria ni conversión; se permiten fechas pasadas.
- Los tests de consola no cubren superposición ni fechas inválidas (se comprobaron a mano; ver `docs/episodio-3.md`).
- Sin autenticación, notificaciones ni administración del inventario, según el alcance.
- Sin control de concurrencia entre varios procesos escribiendo a la vez.

## 3. Preparación del agente
### Entorno y modelo
- Agente: GitHub Copilot (plan Free, según github.com/settings/copilot el 30/10/2026), chat de VS Code en modo **Agent** (opciones disponibles: Agent, Ask y Plan).
- VS Code 1.127.0, Windows 10 x64.
- Modelo: no visible. El selector estaba en "Auto"; Claude Sonnet 5.5, GPT-6 Luna y GPT-6.1 Sol aparecían con el botón "Upgrade".
- Motivo de la elección: gratuito y ya integrado en el editor.

### Instrucciones y contexto
- Instrucciones del repositorio: [`.github/copilot-instructions.md`](.github/copilot-instructions.md) (commit `1e69365`). Se comprobó que Copilot las cargó: el panel "Agent Customizations" las lista como Agent Instructions (1).
- Contexto que se le dio en cada episodio: la sección 1 de este README, el archivo de instrucciones y el código ya existente (`src/reglas.py`, `src/storage.py`).
- Qué no se le dio: (COMPLETAR: por ejemplo, el enunciado completo del desafío, si no lo adjuntaste).

### Permisos y controles
- Permisos: "Default permissions".
- Las aprobaciones pedidas y las decisiones tomadas en cada episodio están en [`docs/episodio-1.md`](docs/episodio-1.md), [`docs/episodio-2.md`](docs/episodio-2.md) y `docs/episodio-3.md`.
- Revisé el diff y ejecuté `python -m pytest` yo misma antes de aceptar cada resultado. Lo que informó el agente y lo que verifiqué se distinguen en cada registro.

### Adaptación específica
Las instrucciones fijan dos reglas: intervalos semiabiertos `[inicio, fin)` sin comparar límites con `<=`, y que toda lectura y escritura de reservas pase por `src/storage.py`.
- Comprobación: cambié temporalmente el primer `<` por `<=` en `intervalos_se_superponen` y fallaron 2 tests de límites consecutivos (detalle en [`docs/episodio-1.md`](docs/episodio-1.md)).
- Al revisar el Episodio 2, el agente agregó `buscar_solapadas` en `storage.py`, que duplicaba la regla de superposición fuera de `reglas.py`; la eliminé (commit `90cb3c8`).

### Retención del progreso
El progreso y las decisiones se conservan en archivos versionados: [`docs/PROGRESS.md`](docs/PROGRESS.md) y los registros `docs/episodio-N.md`.

### Uso de un asistente de chat
Además del agente, usé un asistente de chat (fuera del repositorio) para planificar los pasos y para escribir la corrección del Episodio 1. Esa corrección no la hizo el agente, y así consta en [`docs/episodio-1.md`](docs/episodio-1.md).

## 4. Registro de decisiones y delegación
### Los tres episodios de delegación

| Episodio | Requisito | Qué hizo el agente | Decisión humana | Evidencia |
|---|---|---|---|---|
| 1. Reglas | R4, R5, R6, R9 | Escribió 10 tests y `src/reglas.py` | **Corregir**: encontré un atajo que daba "sin superposición" para intervalos idénticos, lógica duplicada que dejaba R9 sin cumplir y un test que daba por buena esa conducta | [registro](docs/episodio-1.md), commit `1f7428d` (versión corregida) |
| 2. Persistencia | R8 | Escribió 4 tests y `src/storage.py` | **Aceptar con correcciones**: quité `buscar_solapadas` (no pedida, sin tests, duplicaba la regla) y amplié `.gitignore` | [registro](docs/episodio-2.md), commits `f233e29` (agente) y `90cb3c8` (corrección) |
| 3. Cancelación y consola | R2, R3, R7 | Escribió 6 tests, `src/cli.py` y `cancelar_reserva` | **Aceptar sin cambios**: usa las mismas reglas y no hay errores que corregir | [registro](docs/episodio-3.md), commit HASH_EPISODIO3 |

Cada registro detalla contexto, extracto de instrucción, resultado del agente, decisión y las pruebas que ejecuté yo. Suite completa verificada: 26 passed (pytest 7.3.1, Python 3.11.2).

### Decisiones significativas
- **Intervalos semiabiertos `[inicio, fin)`**. Permiten reservas consecutivas sin ambigüedad. Alternativa: intervalos cerrados, que obligarían a un margen entre reservas.
- **SQLite en vez de JSON**. Escritura con commit/rollback y recuperación al reiniciar sin reescribir todo el archivo. Consecuencia: aparece un archivo `.db` (y auxiliares) que se excluyó de git.
- **Una sola regla de superposición** en `reglas.py`. Evita que la consulta y la creación se contradigan (R9). Consecuencia: eliminé `buscar_solapadas`, que repetía la regla en SQL.
- **Fechas pasadas permitidas y sin zona horaria**. Así las pruebas no dependen del reloj. Consecuencia: el sistema no impide reservar en el pasado.
- **Un agente (Copilot Free)** más un asistente de chat externo para planificar y para escribir la corrección del episodio 1; esa corrección no la hizo el agente.
- **No guardé capturas**: la evidencia es textual y reproducible (comandos y resultados en los registros).
- **Limitación en el historial**: en el episodio 1 no hice commit de la versión del agente antes de corregirla, por lo que esa versión no se puede recuperar de git.
