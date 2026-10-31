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
(pendiente)

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
(pendiente)