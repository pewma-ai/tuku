# Configuración

Lo que las automatizaciones necesitan saber y no pueden adivinar. Un campo por línea.

**Zona horaria:** America/Santiago
**Tipo de ciclo:** semanal

## Qué significa cada campo

**Zona horaria** decide qué día es HOY. De eso depende qué pendientes están atrasados, así que si está mal, vencen cosas que no habían vencido. Ninguna automatización asume UTC.

**Tipo de ciclo** es el ritmo con el que abres y cierras. `semanal` es el de partida porque es el de casi todo el mundo: la semana laboral y el fin de semana, que es donde el ritmo cambia de verdad. Si tu vida tiene otro ritmo (turnos, quincenas, temporadas), cámbialo cuando lo tengas claro, no antes: el ritmo verdadero se descubre con el uso, y cambiarlo obliga a renombrar los horizontes de `PENDIENTES.md` y del libro de estilo.
