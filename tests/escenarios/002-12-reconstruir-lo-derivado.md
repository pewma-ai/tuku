# 002-12 · Reconstrucción determinista

> **Principio:** [P6 (conjunto canónico que no se regenera)](../../docs/principios.md#L55), [P9 (reconstruir lo derivado devuelve lo mismo)](../../docs/principios.md#L79) · **Brief:** [Soberanía de archivos y una sola fuente de verdad](../../docs/brief.md#L43) · **Spec:** [`spec/README.md`](../../spec/README.md)

El test fundamental de arquitectura: regenerar lo derivado con `tuku regenerate` devuelve exactamente el mismo resultado, byte a byte, aunque se haya editado a mano. El conjunto canónico (los registros de `AHORA.md`, `PENDIENTES.md`, notas) no se regenera.

## Estado inicial

```bash
cp -r ../../002-11-renombrar/corregir-un-registro-corrige/mi-vault .
```

## Escenario: borrar lo derivado y regenerarlo devuelve lo mismo

Dado un vault sano con una copia de referencia, un derivado editado a mano con una línea ajena y el callout de pendientes del día borrado de `AHORA.md`
```bash
cp -r mi-vault referencia
echo "- una fila que nadie escribió" >> mi-vault/ambitos/PENDIENTES-AMBITOS.md
sed -i.bak '/^> \[!todo\] Pendientes del día$/,/^$/d' mi-vault/AHORA.md && rm mi-vault/AHORA.md.bak
```
Cuando se reconstruye desde el canónico
```bash
cd mi-vault && tuku regenerate
```
Entonces el vault vuelve a ser idéntico a la referencia, byte a byte: sin la línea ajena y con el callout del día
```bash
diff -r referencia mi-vault
```
Y el vault queda plenamente sano
```bash
cd mi-vault && tuku scope lint
```

## Escenario: reconstruir dos veces seguidas no mueve nada

Cuando se ejecuta `tuku regenerate` por segunda vez consecutiva
```bash
cd mi-vault && tuku regenerate
```
Entonces el vault no sufre ninguna modificación (idempotencia estricta)

## Escenario: reconstruir sobre un canónico roto informa y no escribe

Dado un vault cuyo archivo canónico `PENDIENTES.md` tiene un defecto de formato
```bash
echo "sin tabla" > mi-vault/PENDIENTES.md
```
Cuando se intenta regenerar
```bash
cd mi-vault && tuku regenerate
```
Entonces sale con código 1 (`RECHAZO`), nombra el defecto y no deja archivos derivados a medio escribir

## Aceptación humana (en Obsidian)

- Al borrar los derivados con `rm` y correr `tuku regenerate`, las páginas de ámbito en Obsidian deben leerse completas y legibles, preservando el contexto del autor sin artefactos técnicos.
- El informe en terminal de `tuku regenerate` debe dejar total claridad de qué vistas fueron actualizadas.
