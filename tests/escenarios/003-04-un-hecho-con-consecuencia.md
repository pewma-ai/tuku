# 003-04 · Un hecho con consecuencia

> **Principio:** [P1 (texto operable a mano)](../../docs/principios.md#L9), [P4 (determinismo)](../../docs/principios.md#L33) · **Brief:** [Captura rápida y compromisos](../../docs/brief.md#L27) · **Spec:** [`spec/bitacora.md`](../../spec/bitacora.md), [`spec/pendientes.md`](../../spec/pendientes.md), [`spec/despacho.md`](../../spec/despacho.md)

Un compromiso pendiente dictado en lenguaje natural se compila en un `tuku entry add` con marca `**pendiente**`, estampando el registro cronológico en `AHORA.md` y abriendo el compromiso en `PENDIENTES.md` de forma atómica.

## Estado inicial

```bash
cp -r ../../003-03-un-hecho-un-comando/un-hecho-que-no-deja-nada/mi-vault .
```

## Escenario: lo que queda por hacer se escribe y además se abre

Dado un vault con un registro escrito y la tabla de pendientes vacía
Cuando el autor dicta algo que queda por hacer
```agente
A las dos y veinte, hay que avisarle de los gastos comunes a la administradora.
```
Entonces esa frase se traduce en un solo comando
```text
tuku entry add --day 2026-08-11 --hour 14:20 --scope personal \
  --body "**pendiente**: <el cuerpo>"
```
Y queda un registro a las 14:20 con la marca `**pendiente**`
Y la tabla de `PENDIENTES.md` gana una fila con el mismo cuerpo, carácter por carácter
Y la fila entra en el primer escalón de la escalera del autor (`esta semana`)
Y no queda ninguna marca sin su consecuencia en `PENDIENTES.md`
Y el delta es el mismo que deja el gemelo determinista

## Aceptación humana (en Obsidian)

- En `AHORA.md`, el registro de las 14:20 aparece con la marca `**pendiente**` en el martes 11.
- En `PENDIENTES.md`, la tabla contiene exactamente una fila en el horizonte `esta semana` con el mismo texto del registro.
- En la vista del ámbito `personal`, el compromiso se transcluye o refleja limpiamente bajo la sección correspondiente.
