# 003-03 · Un hecho, un comando

> **Principio:** [P1 (texto operable a mano)](../../docs/principios.md#L9), [P4 (determinismo)](../../docs/principios.md#L33) · **Brief:** [Captura rápida y ontología cerrada](../../docs/brief.md#L27) · **Spec:** [`spec/bitacora.md`](../../spec/bitacora.md), [`spec/despacho.md`](../../spec/despacho.md)

Un hecho acontecido sin consecuencias se compila en una única invocación determinista de `tuku entry add`. El agente no edita archivos a mano ni inventa pendientes no solicitados.

## Estado inicial

```bash
cp -r ../../003-02-el-agente-lee-el-vault/el-agente-dice-que-haria-y-no/mi-vault .
```

## Escenario: un hecho que no deja nada abierto es una línea y nada más

Dado un vault sembrado sin registros previos
Cuando el autor dicta un hecho suelto
```agente
A las nueve y doce me di cuenta de que la administradora responde los mensajes con varios días de atraso.
```
Entonces esa frase se traduce en un solo comando
```text
tuku entry add --day 2026-08-11 --hour 09:12 --scope personal \
  --body "**<clasificación>**: <el cuerpo>"
```
Y queda un registro a las 09:12 bajo el día de hoy con el cuerpo del hecho
Y se ejecuta mediante `tuku entry add` sin editar archivos a mano
Y no se abre ningún pendiente en `PENDIENTES.md`
Y el delta en el vault replica exactamente al gemelo determinista: `AHORA.md` y la vista del ámbito

## Aceptación humana (en Obsidian)

- Al revisar `AHORA.md` en Obsidian, el registro de las 09:12 aparece bajo el martes 11 con su texto completo y sin marcas de compromisos abiertos.
- `PENDIENTES.md` se mantiene idéntico, sin filas añadidas.
