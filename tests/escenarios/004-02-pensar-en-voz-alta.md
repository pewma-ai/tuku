# 004-02 · Pensar en voz alta

> **Principio:** [P3 (secretario, no dueño)](../../docs/principios.md#L25), [P4 (determinismo)](../../docs/principios.md#L33) · **Spec:** [`spec/despacho.md`](../../spec/despacho.md), [`spec/agente.md`](../../spec/agente.md)

Damián piensa en voz alta cinco turnos y no ratifica nada. El vault termina igual que empezó.

Los turnos declaran `TUKU_NOW="2026-08-12 21:00"` en el fence ```autor```: Damián y el `tuku` del agente usan esa fecha como hoy.

## Estado inicial

```bash
cp -r ../../004-00-la-conversacion/el-vault-de-partida/mi-vault .
```

## Escenario: Damián duda toda la noche y no decide nada

Dado el vault de partida, con cuatro pendientes abiertos
Cuando Damián conversa con el agente de TUKU según este plan
```autor TUKU_NOW="2026-08-12 21:00"
1. Dudas si mañana conviene dividir primero las interfaces de ODIP con Víctor Lagos o presentarle antes a Fabina el marco de Azure.
2. Piensas que el marco ya está listo y que ODIP lleva más tiempo, así que quizás ODIP primero.
3. Te echas atrás: si Víctor no puede mañana, mejor el marco. Todavía no decides.
4. Se te ocurre que quizás las reglas de MaC se minimizan si el agente aprende solo. Aclaras que es una idea y que no la anote.
5. Cierras: lo decides mañana.
```
Entonces cada turno deja el delta de esta tabla

| Turno | Damián | Delta del vault |
| --- | --- | --- |
| 1 | Duda entre ODIP y el marco de Azure | vacío |
| 2 | Se inclina por ODIP | vacío |
| 3 | Se echa atrás | vacío |
| 4 | Plantea una idea y pide no anotarla | vacío |
| 5 | Deja la decisión para mañana | vacío |

Y la traza no tiene ningún comando que escriba
Y el vault final es el de partida, más `notas/conversation-log.md`
Y `notas/conversation-log.md` contiene los cinco turnos
Y `tuku doctor` confirma la coherencia total del vault
```bash
tuku doctor --vault mi-vault
```

## Qué se mira a mano

La conversación completa está en `playground/004-02-pensar-en-voz-alta/damian-piensa-en-voz-alta/mi-vault/notas/conversation-log.md`.

- El agente delibera con Damián y no cambia de tema ni presiona por una decisión.
- Ninguna respuesta ofrece abrir un pendiente ni anotar nada, salvo para decir que no lo hará.
- En el turno 4 el agente respeta el pedido de no anotar la idea.
