# 003-11 · El día que no se dicta

> **Principio:** [P4 (determinismo)](../../docs/principios.md#L33) · **Spec:** [`spec/tuku.md`](../../spec/tuku.md), capítulo Registro del [libro de estilo](../../template/vanilla/LIBRO-DE-ESTILO.md)

El autor dicta un día por su nombre y una hora, sin fecha. El agente deriva la fecha del calendario y pasa `--at` completo: el registro cae en ese día de `AHORA.md`, en su lugar por hora.

El turno del agente declara `TUKU_NOW="2026-08-25 10:00"` en el fence ```agente```: el `tuku` que el agente ejecuta usa esa fecha como hoy (martes) y la anuncia por `stderr`.

## Estado inicial

El viernes 21 ya tiene un registro. No hereda de un escenario con agente ([`devel/epics.md`](../../devel/epics.md)).

```bash
export TUKU_NOW="2026-08-21 09:00"
tuku init mi-vault
tuku scope create depto-centro --vault mi-vault --at "2026-08-21 09:10"
tuku entry create --vault mi-vault --at "2026-08-21 09:30" --scope depto-centro --body "pagué los gastos comunes del depto centro"
```

## Escenario: el registro va al viernes pasado

Dado un vault cuya ventana abarca el viernes 21, y un HOY martes 25
Cuando el autor dicta un hecho con hora y con el día por su nombre
```agente TUKU_NOW="2026-08-25 10:00"
El viernes pasado a las cinco de la tarde llegó el certificado de dominio vigente del depto centro.
```
Entonces esa frase se traduce en un solo comando
```text
tuku entry create --at "2026-08-21 17:00" --scope depto-centro \
  --body "**<clasificación>**: <el cuerpo>"
```
Y el registro de las 17:00 abre el viernes 21, sobre el de las 09:30
Y `AHORA.md` no gana el martes 25
Y el delta es el de un registro sin consecuencia: `AHORA.md` y la página de `depto-centro`
