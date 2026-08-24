# ADR 0007 — El conjunto de archivos `plan_*` es el calendario del usuario

## Contexto

Las tareas pueden tener fechas relativas al tipo de ciclo del usuario: `(next:turno)`,
`(next:descanso)`. Para resolver esas referencias a fechas concretas, el motor necesita saber
cuándo ocurre el próximo ciclo de cada tipo.

La alternativa directa es que el motor proyecte el calendario futuro a partir de las reglas
de cadencia: si `cad-ciclo-turno` dispara cada 14 días desde una fecha inicial conocida, el
motor puede calcular la fecha del próximo turno sin necesidad de archivos adicionales.

Esa alternativa es determinista, compacta y no requiere que el usuario cree nada explícito.
Su costo es que los ciclos excepcionales —un viaje, una misión, un período de vacaciones—
no tienen representación: son desviaciones respecto a la regla, no objetos en el sistema.

## Decisión

**El archivo `plan_*` es la declaración canónica de un ciclo**. Contiene el tipo, el lugar,
la fecha de inicio y la fecha de fin. El conjunto de todos los archivos `plan_*` —pasados,
presentes y futuros sembrados por cadencia— **es el calendario del usuario**.

La resolución de `(next:turno)` ocurre buscando el `plan_*` más próximo con
`cycle_type: turno` y `cycle_start > hoy`, no calculando desde las reglas de cadencia.

Esto tiene una consecuencia que es su ventaja principal: **declarar un ciclo excepcional es
el mecanismo normal, no un caso especial**. Si la próxima semana el usuario trabaja desde
otra ciudad, crea `plan_2026-08-10_viaje.md`; todas las tareas con `(next:turno)` se
re-resuelven solas. Romper la cadencia no exige modificar ninguna regla.

## Consecuencias

**A favor.**

- Los ciclos excepcionales tienen el mismo estatus que los regulares. Un plan creado a mano
  y uno sembrado por cadencia son indistinguibles para el motor.
- El historial de planes es un historial auditable de cómo la persona organizó su tiempo,
  legible en Git sin herramientas adicionales.
- La resolución de fechas relativas es un grep sobre el directorio `ciclos/`, sin cálculo.

**En contra, y aceptado.**

- Si el usuario no siembra planes futuros, las fechas relativas no pueden resolverse. Las
  cadencias siembran el plan inmediato siguiente, pero no el calendario de los próximos meses.
  El motor puede advertir cuando una tarea con `(next:X)` no tiene plan futuro disponible.
- Un plan borrado que tenía tareas resueltas contra él deja esas tareas con fecha incorrecta.
  El janitor puede detectarlo como inconsistencia.

## Estado

`aceptado`
