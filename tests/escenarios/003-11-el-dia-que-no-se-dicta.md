# 003-11 · El día que no se dicta

> **Principio:** [P4 (determinismo)](../../docs/principios.md#L33) · **Spec:** [`spec/bitacora.md`](../../spec/bitacora.md), [`spec/agente.md`](../../spec/agente.md)

El autor dicta una hora y no un día. El día se deriva del vault, con la regla de [`reglas/bitacora.tuku.md`](../../template/vanilla/reglas/bitacora.tuku.md): si HOY cae fuera del ciclo abierto, el registro va al último día del ciclo que ya tiene registros.

## Estado inicial

El día uno de la cadena determinista del 002, con dos pendientes escritos el miércoles 12. No hereda de un escenario con agente ([`devel/epics.md`](../../devel/epics.md)).

```bash
cp -r ../../002-13-el-dia/la-nota-del-frente-queda/mi-vault .
tuku todo open --vault mi-vault --day 2026-08-12 --hour 09:00 --scope personal --body "pagar la sesión con el psicólogo"
tuku todo open --vault mi-vault --day 2026-08-12 --hour 09:30 --scope depto-centro --body "pagar los gastos comunes del depto centro"
```

## Escenario: el registro va al último día con registros

Dado un vault cuyo último día con registros es el miércoles 12, y un HOY fuera del ciclo
Cuando el autor dicta un hecho con hora y sin día
```agente
A las diez y cuarto llegó el certificado de dominio vigente del depto centro.
```
Entonces esa frase se traduce en un solo comando
```text
tuku entry add --day 2026-08-12 --hour 10:15 --scope depto-centro \
  --body "**<clasificación>**: <el cuerpo>"
```
Y el registro de las 10:15 cae en el miércoles 12, después de los de las 09:00 y las 09:30
Y no abre ni cierra ningún pendiente
Y el delta es el de un registro sin consecuencia: `AHORA.md` y la página de `depto-centro`
