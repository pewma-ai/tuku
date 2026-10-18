# 004-01 · El día conversado

> **Principio:** [P3 (secretario, no dueño)](../../docs/principios.md#L25), [P4 (determinismo)](../../docs/principios.md#L33) · **Spec:** [`spec/despacho.md`](../../spec/despacho.md), [`spec/agente.md`](../../spec/agente.md), [`spec/pendientes.md`](../../spec/pendientes.md)

Damián cuenta su miércoles en doce turnos: consulta, aclara, piensa en voz alta, se interrumpe, descarta una idea, ratifica y, al final, reordena sus frentes y dice qué palabras delatan a `faena`. El vault queda como lo deja el dictado directo de lo ratificado.

Los turnos declaran `TUKU_NOW="2026-08-12 21:00"` en el fence ```autor```: Damián y el `tuku` del agente usan esa fecha como hoy.

## Estado inicial

```bash
cp -r ../../004-00-la-conversacion/el-vault-de-partida/mi-vault .
```

## Escenario: Damián cuenta su miércoles, duda y ratifica al final

Dado el vault de partida, con cuatro pendientes abiertos
Cuando Damián conversa con el agente de TUKU según este plan
```autor TUKU_NOW="2026-08-12 21:00"
1. Preguntas qué te quedaba abierto hoy, antes de contar el día.
2. Dices que hoy hablaste con Fabina, sin decir de qué.
3. Aclaras que fue por el diccionario de MetricDB, a las diez y cuarto. A las diez y media supiste que por confidencialidad los manuales no se pueden entregar directos a Javier Castro, y a las diez treinta y cinco decidiste hablar con Carla Fuentes para armar presentaciones resumen que integren varios manuales.
4. Piensas en voz alta si llamar a Carla mañana a las nueve o esperar al viernes, que igual se juntan. Todavía no decides.
5. Te interrumpes: a las once te reuniste con Rodrigo Álvarez y Tomás Toledo de Casa Matriz por la versión 2 de la plataforma de servicios, y a las once cuarenta y cinco aportaste IA: LLM en máquinas NVIDIA y un harness para agentes como OpenCode.
6. Vuelves a Carla y preguntas si el viernes será una buena idea. Cuentas que a las tres de la tarde le presentaste a Fabina el marco de casos de uso con Azure LLM.
7. Preguntas si Casa Matriz amerita un ámbito propio.
8. Respondes que el tema queda en transformación digital.
9. Ratificas: el viernes hablas con Carla Fuentes por las presentaciones resumen.
10. Antes de irte te das cuenta de que faena es un frente aparte de lo personal. Pides que lo abra y que ponga adentro faena-ai y transformación digital.
11. Agregas que la tesis de Javier Castro también va dentro de faena.
12. Respondes lo que el agente te pregunta al abrir faena: cuando hablas de «la planta» o de «FNA», es de faena.
```
Entonces cada turno deja el delta de esta tabla

| Turno | Damián | Delta del vault |
| --- | --- | --- |
| 1 | Consulta los pendientes | vacío; la respuesta lista los cuatro |
| 2 | Dice que habló con Fabina | vacío; el agente pregunta si fue por el marco de Azure o por el diccionario de MetricDB |
| 3 | Aclara y cuenta tres hechos | tres comandos: el cierre del diccionario y dos registros |
| 4 | Piensa en voz alta | vacío |
| 5 | Interrumpe con dos hechos de Casa Matriz | dos registros |
| 6 | Pregunta si el viernes es buena idea y cuenta la presentación del marco | un cierre; el agente opina sobre el viernes |
| 7 | Pregunta por un ámbito | vacío |
| 8 | Deja el tema en transformación digital | vacío |
| 9 | Ratifica | un pendiente con vencimiento el viernes 14 |
| 10 | Pide abrir `faena` y poner adentro `faena-ai` y `transformacion-digital` | `scope create faena` y dos `scope move`; los links de los registros ya escritos siguen resolviendo |
| 11 | Pide poner adentro la tesis | un `scope move`; el callout de `faena` suma `tesis-javier-castro` |
| 12 | Dice qué palabras delatan a `faena` | un `scope update`; la página de `faena` suma «la planta» y «FNA» a sus `keywords` |

Y el vault final coincide con la tabla de verdad
Y `ambitos/` queda con `faena`, `personal` y `tuku`, y `faena` con `faena-ai`, `tesis-javier-castro` y `transformacion-digital`
Y la página de `faena` lista esos tres ámbitos en el callout `En **Faena**:` y declara `keywords: [faena, la planta, FNA]`
Y cada cambio del vault tiene su comando `tuku` en la traza
Y `notas/conversation-log.md` contiene los doce turnos
Y `tuku doctor` confirma la coherencia total del vault
```bash
tuku doctor --vault mi-vault
```

### Tabla de verdad

Lo que el dictado directo agrega al vault de partida, todo bajo el miércoles 12. La clasificación abierta la elige el agente y no se verifica.

| Hora | Ámbito | Marca cerrada |
| --- | --- | --- |
| 10:15 | `tesis-javier-castro` | `(Hecho)` |
| 10:30 | `tesis-javier-castro` | ninguna |
| 10:35 | `tesis-javier-castro` | ninguna |
| 11:00 | `transformacion-digital` | ninguna |
| 11:45 | `transformacion-digital` | ninguna |
| 15:00 | `faena-ai` | `(Hecho)` |
| la del turno | `tesis-javier-castro` | `**pendiente**`, vence 2026-08-14 |
| la del turno | `faena` | ninguna (la constancia de ámbito abierto) |

`PENDIENTES.md` queda con tres filas: la de `tuku`, la de ODIP en `transformacion-digital` y la de Carla Fuentes en `tesis-javier-castro`, con fecha 2026-08-14. Los registros de `tesis-javier-castro`, `transformacion-digital` y `faena-ai` enlazan su página en `ambitos/faena/<nombre>/<nombre>.md`.

## Qué se mira a mano

La conversación completa está en `playground/004-01-el-dia-conversado/damian-cuenta-su-miercoles/mi-vault/notas/conversation-log.md`.

- Las respuestas de los turnos 1, 2 y 7 son breves y contestan lo preguntado.
- La pregunta del turno 2 nombra los dos pendientes reales de Fabina.
- En los turnos 4 y 6 el agente delibera con Damián y espera su decisión.
- En el turno 10 el agente abre `faena`, mueve los dos frentes sin volver a preguntar lo que Damián ya pidió y cierra preguntando qué palabras, al mencionarlas, indican que algo es de `faena`.
- En el turno 11 el agente mueve la tesis y el callout de `faena` queda con los tres hijos.
- En el turno 12 el agente registra las palabras que Damián dio, sin inventar otras.
