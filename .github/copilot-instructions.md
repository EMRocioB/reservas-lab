# Instrucciones para el agente

## Proyecto
Sistema de reservas de laboratorio, en consola. Lee README.md (sección 1) antes de actuar.

## Stack
- Python 3.11, SQLite (módulo sqlite3), pytest. Sin otras dependencias.
- Código en src/, pruebas en tests/, inventario en data/inventario.json.

## Reglas obligatorias
- Los intervalos son semiabiertos [inicio, fin). Dos reservas se superponen
  solo si inicio_A < fin_B y inicio_B < fin_A. Nunca compares límites con <=.
- Una reserva cancelada no bloquea; se conserva con su identificador y datos.
- Toda lectura y escritura de reservas pasa por src/storage.py.
- Escribe primero los tests y no modifiques los existentes sin avisar.
- Solicitantes ficticios. Nunca escribas claves ni datos reales.

## Antes de terminar
Ejecuta `python -m pytest` y muestra el resultado real.