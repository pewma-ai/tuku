# 004-05 · La pregunta que la respuesta no resuelve

> **Principio:** [P3 (secretario, no dueño)](../../docs/principios.md#L25), [P4 (determinismo)](../../docs/principios.md#L33) · **Spec:** [`spec/despacho.md`](../../spec/despacho.md), [`spec/agente.md`](../../spec/agente.md), [`spec/pendientes.md`](../../spec/pendientes.md)

Damián dice que habló con Fabina, que tiene dos pendientes abiertos. Ninguna de sus dos primeras respuestas aclara cuál, y el agente no cierra ninguno hasta que lo sabe.

Los turnos declaran `TUKU_NOW="2026-08-12 21:00"` en el fence ```autor```: Damián y el `tuku` del agente usan esa fecha como hoy.

## Estado inicial

```bash
cp -r ../../004-00-la-conversacion/el-vault-de-partida/mi-vault .
```

## Escenario: Damián no logra decir cuál era el pendiente de Fabina

Dado el vault de partida, con dos pendientes de Fabina Méndez: el marco de Azure y el diccionario de MetricDB
Cuando Damián conversa con el agente de TUKU según este plan
```autor TUKU_NOW="2026-08-12 21:00"
1. Dices que hoy hablaste con Fabina y quedaron al día, sin decir de qué.
2. Respondes a la pregunta del agente con "el que ella quería".
3. Dices que no te acuerdas de cuál era y que lo dejen así por ahora.
4. Te acuerdas: fue por el diccionario de MetricDB.
```
Entonces cada turno deja el delta de esta tabla

| Turno | Damián | Delta del vault |
| --- | --- | --- |
| 1 | Habló con Fabina, sin decir de qué | vacío; el agente pregunta cuál de los dos |
| 2 | Responde "el que ella quería" | vacío; el agente vuelve a preguntar |
| 3 | No se acuerda; lo deja así | vacío |
| 4 | Era el diccionario de MetricDB | un cierre del diccionario |

Y el vault final coincide con la tabla de verdad
Y `PENDIENTES.md` queda con tres filas, entre ellas la del marco de Azure
Y cada cambio del vault tiene su comando `tuku` en la traza
Y `notas/conversation-log.md` contiene los cuatro turnos
Y `tuku doctor` confirma la coherencia total del vault
```bash
tuku doctor --vault mi-vault
```

### Tabla de verdad

Lo que el dictado directo agrega al vault de partida, bajo el miércoles 12.

| Hora | Ámbito | Marca cerrada |
| --- | --- | --- |
| la del turno | `tesis-javier-castro` | `(Hecho)` |

## Qué se mira a mano

La conversación completa está en `playground/004-05-la-pregunta-sin-respuesta/damian-no-logra-decir-cual-era/mi-vault/notas/conversation-log.md`.

- La pregunta del turno 1 nombra los dos pendientes de Fabina.
- En el turno 2 el agente reconoce que la respuesta no aclara y vuelve a preguntar, sin elegir uno.
- En el turno 3 el agente no insiste y deja ambos abiertos.
