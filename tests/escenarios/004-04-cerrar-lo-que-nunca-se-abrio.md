# 004-04 · Cerrar lo que nunca se abrió

> **Principio:** [P3 (secretario, no dueño)](../../docs/principios.md#L25), [P4 (determinismo)](../../docs/principios.md#L33) · **Spec:** [`spec/despacho.md`](../../spec/despacho.md), [`spec/agente.md`](../../spec/agente.md), [`spec/pendientes.md`](../../spec/pendientes.md)

Damián da por hecho dos cosas que nunca fueron pendientes. El agente las registra sin preguntar nada, sin cerrar ni abrir pendientes.

Los turnos declaran `TUKU_NOW="2026-08-12 21:00"` en el fence ```autor```: Damián y el `tuku` del agente usan esa fecha como hoy.

## Estado inicial

```bash
cp -r ../../004-00-la-conversacion/el-vault-de-partida/mi-vault .
```

## Escenario: Damián da por hecho lo que nunca abrió

Dado el vault de partida, con cuatro pendientes abiertos
Cuando Damián conversa con el agente de TUKU según este plan
```autor TUKU_NOW="2026-08-12 21:00"
1. Preguntas qué te queda abierto, antes de contar lo que hiciste.
2. Dices que ya pagaste el estacionamiento del mes.
3. Dices "listo lo del pasaporte": lo renovaste a las cuatro de la tarde.
4. Vuelves a preguntar qué te queda abierto.
```
Entonces cada turno deja el delta de esta tabla

| Turno | Damián | Delta del vault |
| --- | --- | --- |
| 1 | Consulta los pendientes | vacío; la respuesta lista los cuatro |
| 2 | Ya pagó el estacionamiento | un registro, sin pregunta del agente |
| 3 | Listo lo del pasaporte, a las 16:00 | un registro, sin pregunta del agente |
| 4 | Consulta los pendientes | vacío; la respuesta lista los mismos cuatro |

Y el vault final coincide con la tabla de verdad
Y `PENDIENTES.md` queda con las cuatro filas de partida
Y ninguna línea de `AHORA.md` lleva `(Hecho)` ni `**pendiente**` nuevo
Y cada cambio del vault tiene su comando `tuku` en la traza
Y `notas/conversation-log.md` contiene los cuatro turnos
Y `tuku doctor` confirma la coherencia total del vault
```bash
tuku doctor --vault mi-vault
```

### Tabla de verdad

Lo que el dictado directo agrega al vault de partida, bajo el miércoles 12. La clasificación la elige el agente y no se verifica.

| Hora | Ámbito | Marca cerrada |
| --- | --- | --- |
| la del turno | `personal` | ninguna |
| 16:00 | `personal` | ninguna |

## Qué se mira a mano

La conversación completa está en `playground/004-04-cerrar-lo-que-nunca-se-abrio/damian-da-por-hecho-lo-que/mi-vault/notas/conversation-log.md`.

- Las respuestas de los turnos 2 y 3 dicen qué quedó escrito, sin ofrecer abrir un pendiente.
- Las respuestas de los turnos 1 y 4 listan los mismos cuatro pendientes.
