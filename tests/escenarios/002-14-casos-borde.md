# 002-14 · El vault editado con un editor

> **Principio:** [P1 (texto operable a mano)](../../docs/principios.md#L9), [P4 (determinismo)](../../docs/principios.md#L33), [P6 (conjunto canónico)](../../docs/principios.md#L55), [P9 (reconstrucción)](../../docs/principios.md#L79) · **Brief:** [Soberanía de archivos y una sola fuente de verdad](../../docs/brief.md#L43) · **Spec:** [`spec/tuku.md`](../../spec/tuku.md)

El vault de las dos semanas editado con cualquier editor: el lint nombra el comando que corrige, el reparador deja el vault como lo habría dejado el comando y lo derivado se regenera desde el canónico. Las reglas de cada lint están en [`../unitarios/`](../unitarios/README.md); acá solo las historias.

## Estado inicial

```bash
cp -r ../../002-13-el-dia/repetir-el-dia-no-cambia-nada/mi-vault .
cd mi-vault
```

## Escenario: un derivado editado a mano se detecta y se regenera

Dado una copia de referencia, una línea ajena y otra borrada en `ambitos/PENDIENTES-AMBITOS.md`, y el bloque de pendientes de la ventana borrado de `AHORA.md`
```bash
cp -r . ../referencia
sed -i.bak '/Ago\/13 - llamar al contador/d' ambitos/PENDIENTES-AMBITOS.md
echo "- una fila que nadie escribió" >> ambitos/PENDIENTES-AMBITOS.md
sed -i.bak '/^> \[!todo\] Pendientes de los próximos 7 días$/,/^$/d' AHORA.md
rm ambitos/PENDIENTES-AMBITOS.md.bak AHORA.md.bak
```
Cuando se revisa y se regenera
```bash
TUKU_NOW="2026-08-24 09:20" tuku doctor todo
TUKU_NOW="2026-08-24 09:21" tuku regenerate
```
Entonces `tuku doctor todo` sale con código 1 (`RECHAZO`) y nombra `tuku regenerate todo`
Y `tuku regenerate` nombra cada archivo que reescribió
Y el vault vuelve a ser idéntico a la referencia, byte a byte
```bash
diff -r ../referencia .
```

## Escenario: abierto y cerrado a mano el mismo día lo repara fix

Dado un pendiente abierto el lunes 24 y cerrado ese mismo día con un editor: el `(Hecho)` escrito en `AHORA.md` y la fila borrada de `PENDIENTES.md`
```bash
TUKU_NOW="2026-08-24 15:00" tuku todo open --body "renovar el carnet"
awk '/\*\*pendiente\*\*: renovar el carnet/{print "- 15:20 - [personal](ambitos/personal/personal.md) (Hecho): ~~renovar el carnet~~"} {print}' AHORA.md > ahora.tmp && mv ahora.tmp AHORA.md
sed -i.bak '/renovar el carnet/d' PENDIENTES.md && rm PENDIENTES.md.bak
```
Cuando se revisa y se repara
```bash
TUKU_NOW="2026-08-24 15:30" tuku doctor todo
TUKU_NOW="2026-08-24 15:31" tuku fix todo
TUKU_NOW="2026-08-24 15:32" tuku doctor todo
```
Entonces el primer `tuku doctor todo` sale con código 1 (`RECHAZO`) y nombra `tuku fix todo`
Y `tuku fix todo` quita el registro de las 15:00 de `AHORA.md` y de la página de `personal`, y deja el cierre de las 15:20
Y el segundo `tuku doctor todo` sale limpio

## Aceptación humana (en Obsidian)

- Cada mensaje de lint dice qué está mal y qué comando lo corrige, sin sonar punitivo.
- Tras `tuku regenerate` y `tuku fix todo`, las páginas de ámbito se leen completas, sin artefactos técnicos.
