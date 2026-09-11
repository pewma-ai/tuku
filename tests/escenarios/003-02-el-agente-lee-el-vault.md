# 003-02 · El agente lee el vault

> **Principio:** [P1 (texto operable a mano)](../../docs/principios.md#L9), [P3 (secretario, no dueño)](../../docs/principios.md#L25), [P4 (determinismo)](../../docs/principios.md#L33) · **Brief:** [El agente y las herramientas](../../docs/brief.md#L60) · **Spec:** [`spec/despacho.md`](../../spec/despacho.md), [`spec/agente.md`](../../spec/agente.md)

El autor consulta qué registraría ante un hecho hipotético sin autorizar su ejecución. El agente consulta el vault y su `AGENTS.md` sin mutar archivos ni invocar comandos de escritura, identificando los dos destinos: el registro en `AHORA.md` y el compromiso en `PENDIENTES.md`.

## Estado inicial

```bash
cp -r ../../003-01-el-vault-dice-a-donde-va/el-vault-nace-con-su-tabla-de/mi-vault .
```

## Escenario: el agente dice qué haría y no toca nada

Dado un vault sembrado sin registros previos
Cuando el autor pregunta antes de dictar
```agente
Si te digo que hay que avisarle de los gastos comunes a la administradora, ¿qué anotarías y en qué archivo? No lo hagas todavía, quiero ver primero.
```
Entonces esa frase no se traduce en ningún comando
```text
(ninguno)
```
Y el vault queda exactamente igual que antes del turno
Y el agente no ejecutó ningún comando que escriba
Y su respuesta nombra los dos destinos: el registro va a `AHORA.md` y su consecuencia a `PENDIENTES.md`

## Aceptación humana (en Obsidian)

- Tras la consulta, el vault permanece completamente inalterado con diff vacío.
- La respuesta del agente informa con exactitud que el hecho va a `AHORA.md` y el pendiente a `PENDIENTES.md`, absteniéndose de ejecutar escrituras sin autorización.
