# 002-14 · Casos borde del día uno

> **Principio:** [P1 (texto operable a mano)](../../docs/principios.md#L9), [P4 (determinismo)](../../docs/principios.md#L33), [P6 (conjunto canónico)](../../docs/principios.md#L55), [P9 (reconstrucción)](../../docs/principios.md#L79) · **Brief:** [Soberanía de archivos y una sola fuente de verdad](../../docs/brief.md#L43) · **Spec:** [`spec/pendientes.md`](../../spec/pendientes.md), [`spec/bitacora.md`](../../spec/bitacora.md), [`spec/ambitos.md`](../../spec/ambitos.md)

El vault del día uno editado con cualquier editor: cada lint nombra el comando que corrige, el reparador deja el vault como lo habría dejado el comando, y lo derivado se regenera desde el canónico. Cada escenario parte del día uno completo.

## Estado inicial

```bash
cp -r ../../002-13-el-dia/repetir-el-dia-no-cambia-nada/mi-vault .
cd mi-vault
```

## Escenario: un derivado editado a mano se detecta y se regenera

Dado una copia de referencia, una línea ajena y otra borrada en `ambitos/PENDIENTES-AMBITOS.md`, y los callouts de pendientes del día borrados de `AHORA.md`
```bash
cp -r . ../referencia
sed -i.bak '/Ago\/12 09:00 - pagar la sesión con el psicólogo/d' ambitos/PENDIENTES-AMBITOS.md
echo "- una fila que nadie escribió" >> ambitos/PENDIENTES-AMBITOS.md
sed -i.bak '/^> \[!todo\] Pendientes del día$/,/^$/d' AHORA.md
rm ambitos/PENDIENTES-AMBITOS.md.bak AHORA.md.bak
```
Cuando se revisa y se regenera
```bash
tuku doctor todo
tuku regenerate
```
Entonces `tuku doctor todo` sale con código 1 (`RECHAZO`) y nombra `tuku regenerate todo`
Y `tuku regenerate` nombra cada archivo que reescribió
Y el vault vuelve a ser idéntico a la referencia, byte a byte
```bash
diff -r ../referencia .
```

## Escenario: una fila borrada a mano la nombra todo lint

Dado la fila de `pagar la sesión con el psicólogo` borrada de `PENDIENTES.md`
```bash
sed -i.bak '/pagar la sesión con el psicólogo/d' PENDIENTES.md && rm PENDIENTES.md.bak
```
Cuando se revisa
```bash
tuku doctor todo
```
Entonces sale con código 1 (`RECHAZO`) y nombra como corrección `tuku todo open`

## Escenario: abierto y cerrado a mano el mismo día lo repara fix

Dado un pendiente abierto el martes 11 y cerrado ese mismo día con un editor: el `(Hecho)` escrito en `AHORA.md` y la fila borrada de `PENDIENTES.md`
```bash
tuku todo open --at "2026-08-11 15:00" --body "renovar el carnet"
awk '{print} /^- 19:10 - /{print "- 19:20 - [personal](ambitos/personal/personal.md) (Hecho): ~~renovar el carnet~~"}' AHORA.md > ahora.tmp && mv ahora.tmp AHORA.md
sed -i.bak '/renovar el carnet/d' PENDIENTES.md && rm PENDIENTES.md.bak
```
Cuando se revisa y se repara
```bash
tuku doctor todo
tuku fix todo
tuku doctor todo
```
Entonces el primer `tuku doctor todo` sale con código 1 (`RECHAZO`) y nombra `tuku fix todo`
Y `tuku fix todo` quita el registro de las 15:00 de `AHORA.md` y de la página de `personal`, y deja el cierre de las 19:20
Y el segundo `tuku doctor todo` sale limpio

## Escenario: un registro a una categoría lo reporta scope lint

Dado una subcarpeta `gastos/` de `depto-centro` sin página propia, es decir, una categoría
```bash
mkdir ambitos/depto-centro/gastos
```
Cuando se escribe un registro a `gastos` y se revisa
```bash
tuku entry create --at "2026-08-11 20:00" --scope gastos --body "**progreso**: revisé el detalle del mes"
tuku doctor scope
```
Entonces `tuku doctor scope` sale con código 1 (`RECHAZO`) y explica que una categoría no recibe registros
Y el registro queda escrito en `AHORA.md`: un error del autor se informa, nunca se borra

## Escenario: una marca cerrada mal escrita la reporta entry lint

Cuando se escribe `**Cadencia**` en vez de `**cadencia**` y se revisa
```bash
tuku entry create --at "2026-08-11 13:30" --body "**Cadencia**: revisar la caldera"
tuku doctor entry
```
Entonces `tuku doctor entry` sale con código 1 (`RECHAZO`) y dice cómo se escribe la marca
Y la línea queda intacta en `AHORA.md` y `PENDIENTES.md` no cambia

## Escenario: un canónico roto hace que regenerate no escriba

Dado `PENDIENTES.md` sin su tabla
```bash
echo "sin tabla" > PENDIENTES.md
```
Cuando se intenta regenerar
```bash
tuku regenerate
```
Entonces sale con código 1 (`RECHAZO`) nombrando `PENDIENTES.md`
Y no escribe ningún archivo

## Escenario: corregir un pendiente con entry update arrastra su fila

Cuando se corrige el cuerpo de un pendiente abierto
```bash
tuku entry update --match "llamar a la administradora" --body "llamar a la administradora por el reajuste"
tuku doctor todo
```
Entonces el registro de las 21:32 conserva `**pendiente**:` y dice el cuerpo nuevo
Y la fila de `PENDIENTES.md` dice el cuerpo nuevo
Y `tuku doctor todo` sale limpio

## Escenario: una fila sin registro pendiente la nombra todo lint

Dado el registro de `llamar a la administradora` sin su marca `**pendiente**`, escrito con un editor
```bash
sed -i.bak 's/\*\*pendiente\*\*: llamar a la administradora/llamar a la administradora/' AHORA.md && rm AHORA.md.bak
```
Cuando se revisa
```bash
tuku doctor todo
```
Entonces sale con código 1 (`RECHAZO`) y nombra la fila huérfana `llamar a la administradora`

## Aceptación humana (en Obsidian)

- Cada mensaje de lint dice qué está mal y qué comando lo corrige, sin sonar punitivo.
- Tras `tuku regenerate` y `tuku fix todo`, las páginas de ámbito se leen completas, sin artefactos técnicos.
