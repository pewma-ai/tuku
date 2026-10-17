# 004-03 · Ratificar tras tres giros

> **Principio:** [P3 (secretario, no dueño)](../../docs/principios.md#L25), [P4 (determinismo)](../../docs/principios.md#L33) · **Spec:** [`spec/despacho.md`](../../spec/despacho.md), [`spec/agente.md`](../../spec/agente.md), [`spec/pendientes.md`](../../spec/pendientes.md)

Damián cambia tres veces el día de una reunión y ratifica el último. El vault queda como si hubiera dictado solo ese acuerdo.

Los turnos declaran `TUKU_NOW="2026-08-12 21:00"` en el fence ```autor```: Damián y el `tuku` del agente usan esa fecha como hoy.

## Estado inicial

```bash
cp -r ../../004-00-la-conversacion/el-vault-de-partida/mi-vault .
```

## Escenario: Damián propone jueves, viernes y lunes, y ratifica el lunes

Dado el vault de partida, con cuatro pendientes abiertos
Cuando Damián conversa con el agente de TUKU según este plan
```autor TUKU_NOW="2026-08-12 21:00"
1. Dices que quieres juntarte con Javier Castro para revisar el avance de la tesis, quizás el jueves.
2. Cambias: el jueves tienes directorio, mejor el viernes.
3. Cambias otra vez: el viernes Javier no está, quizás el lunes 17. Todavía no decides.
4. Ratificas: quedan en reunirse con Javier Castro el lunes 17 para revisar el avance de la tesis.
```
Entonces cada turno deja el delta de esta tabla

| Turno | Damián | Delta del vault |
| --- | --- | --- |
| 1 | Propone el jueves | vacío |
| 2 | Cambia al viernes | vacío |
| 3 | Cambia al lunes 17 | vacío |
| 4 | Ratifica el lunes 17 | un pendiente con vencimiento el lunes 17 |

Y el vault final coincide con la tabla de verdad
Y `PENDIENTES.md` queda con cinco filas: las cuatro de partida y la nueva
Y ninguna fila ni registro nombra el jueves 13 ni el viernes 14
Y cada cambio del vault tiene su comando `tuku` en la traza
Y `notas/conversation-log.md` contiene los cuatro turnos
Y `tuku doctor` confirma la coherencia total del vault
```bash
tuku doctor --vault mi-vault
```

### Tabla de verdad

Lo que el dictado directo del último acuerdo agrega al vault de partida, en el miércoles 12.

| Hora | Ámbito | Marca cerrada |
| --- | --- | --- |
| la del turno | `tesis-javier-castro` | `**pendiente**`, vence 2026-08-17 |

## Qué se mira a mano

La conversación completa está en `playground/004-03-ratificar-tras-tres-giros/damian-propone-jueves-viernes/mi-vault/notas/conversation-log.md`.

- En los turnos 1 a 3 el agente acompaña el cambio de día sin anotar ninguno.
- En el turno 4 el agente abre un solo pendiente, con el cuerpo del último acuerdo.
