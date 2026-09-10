# 002-12 · Reconstrucción determinista

> **Principio:** [P6 (conjunto canónico que no se regenera)](../../docs/principios.md#L55), [P9 (reconstruir lo derivado devuelve lo mismo)](../../docs/principios.md#L79) · **Brief:** [Soberanía de archivos y una sola fuente de verdad](../../docs/brief.md#L43) · **Spec:** [`spec/README.md`](../../spec/README.md)

El test fundamental de arquitectura: borrar todas las vistas y archivos derivados y regenerarlos mediante `tuku rebuild` devuelve exactamente el mismo resultado, idéntico byte a byte. El conjunto canónico (`AHORA.md`, `PENDIENTES.md`, notas) es la única fuente de verdad y jamás se regenera.

## Estado inicial

```bash
cp -r ../../002-11-renombrar/corregir-un-registro-corrige/mi-vault .
```

## Escenario: borrar lo derivado y regenerarlo devuelve lo mismo

Dado un vault sano con copia de respaldo de lo derivado para contrastar
```bash
cp -r mi-vault referencia
```
Cuando se borra todo lo derivado y se reconstruye desde el canónico
```bash
cd mi-vault && tuku rebuild
```
Entonces cada archivo derivado vuelve idéntico, byte a byte
```bash
diff -r referencia mi-vault
```
Y ningún archivo del conjunto canónico resulta alterado
Y el vault queda plenamente sano
```bash
cd mi-vault && tuku scope lint
```

## Escenario: reconstruir dos veces seguidas no mueve nada

Cuando se ejecuta `tuku rebuild` por segunda vez consecutiva
```bash
cd mi-vault && tuku rebuild
```
Entonces el vault no sufre ninguna modificación (idempotencia estricta)

## Escenario: un derivado editado a mano se corrige al reconstruir

Dado que alguien editó a mano un archivo derivado agregando una línea ajena
```bash
cd mi-vault && echo "- una fila que nadie escribió" >> ambitos/PENDIENTES-AMBITOS.md
```
Cuando se reconstruye el vault
```bash
cd mi-vault && tuku rebuild
```
Entonces la línea agregada desaparece y el archivo vuelve a reflejar exactamente el conjunto canónico

## Escenario: reconstruir sobre un canónico roto informa y no escribe

Dado un vault cuyo archivo canónico `PENDIENTES.md` tiene un defecto de formato
```bash
echo "sin tabla" > mi-vault/PENDIENTES.md
```
Cuando se intenta reconstruir
```bash
cd mi-vault && tuku rebuild
```
Entonces sale con código 1 (`RECHAZO`), nombra el defecto y no deja archivos derivados a medio escribir

## Aceptación humana (en Obsidian)

- Al borrar los derivados con `rm` y correr `tuku rebuild`, las páginas de ámbito en Obsidian deben leerse completas y legibles, preservando el contexto del autor sin artefactos técnicos.
- El informe en terminal de `tuku rebuild` debe dejar total claridad de qué vistas fueron actualizadas.
