# 005-03 · Reorganizar con historia

> **Principio:** [P7 (las carpetas archivan, los enlaces conectan)](../../docs/principios.md#L65), [P1 (texto operable a mano)](../../docs/principios.md#L9), [P9 (reconstrucción)](../../docs/principios.md#L79) · **Brief:** [Los tres ejes](../../docs/brief.md#L25) · **Spec:** [`spec/ambitos.md`](../../spec/ambitos.md)

En un vault nuevo, mover un ámbito es mover una carpeta. En uno con dos semanas, cada ámbito tiene registros, pendientes y una bitácora cerrada que lo enlaza, y reorganizar no puede dejar un solo link sin resolver: el archivo histórico tiene que seguir leyéndose.

## Escenario: mover y renombrar ámbitos anidados mantiene cada link

Dado el vault de la segunda semana de Andrea, con la primera archivada en `bitacoras/`
```bash
cp -r ../../005-01-las-dos-semanas-de-andrea/la-segunda-semana-cae-sobre-lo/mi-vault .
```
Cuando Andrea pone el canal de la feria dentro de la temporada de marzo y acorta el nombre del liceo
```bash
cd mi-vault
tuku scope move canal-feria --parent temporada-marzo
tuku scope rename liceo-tecnico-andes liceo-andes
```
Entonces cada ámbito está en su lugar nuevo, con su página
Y toda mención a los ámbitos, en la bitácora cerrada y en el resto del vault, usa la ruta y el nombre nuevos
Y `tuku doctor` dice que el vault está sano
```bash
tuku doctor
```

## Escenario: lo que el ámbito tenía sigue siendo suyo

Dado el vault con el canal de la feria movido y el liceo renombrado
```bash
cp -r ../mover-y-renombrar-ambitos/mi-vault .
cd mi-vault
```
Cuando se regenera lo derivado
```bash
tuku regenerate
```
Entonces el diff del vault es vacío: mover y renombrar ya dejaron todo como lo dejaría `tuku regenerate`
Y las keywords del liceo llevan el nombre nuevo en lugar del viejo y conservan las demás palabras con que Andrea lo nombra
Y la bitácora cerrada enlaza las páginas nuevas con la ruta desde `bitacoras/`

## Escenario: repetir la reorganización deja el vault igual

Dado el vault reorganizado
```bash
cp -r ../mover-y-renombrar-ambitos/mi-vault .
```
Cuando se repite el movimiento y se vuelve a pedir el nombre viejo del liceo
```bash
cd mi-vault
tuku scope move canal-feria --parent temporada-marzo
tuku scope rename liceo-tecnico-andes liceo-andes
```
Entonces mover otra vez deja el vault igual
Y renombrar con el nombre viejo se rechaza, el vault queda igual y el mensaje dice que `liceo-tecnico-andes` ya no existe

## Aceptación humana (en Obsidian)

- Desde la bitácora cerrada de la primera semana, cada link de ámbito abre la página nueva.
- La lista de hijos de `temporada-marzo` muestra `canal-feria`, y la de `negocio` ya no.
