# 005-02 · Lo derivado se reconstruye

> **Principio:** [P6 (conjunto canónico)](../../docs/principios.md#L55), [P9 (reconstrucción)](../../docs/principios.md#L79) · **Brief:** [Cómo funciona](../../docs/brief.md#L47) · **Spec:** [`spec/pendientes.md`](../../spec/pendientes.md), [`spec/ambitos.md`](../../spec/ambitos.md), [`spec/ciclo.md`](../../spec/ciclo.md)

Con dos semanas encima, el test fundamental de arquitectura se corre sobre un vault de verdad: se borra todo lo que el vault deriva, se regenera, y el vault queda idéntico byte a byte.

Lo derivado es lo que ningún registro dice por sí solo: las vistas de pendientes de `AHORA.md`, `ambitos/PENDIENTES-AMBITOS.md`, la actividad y la lista de hijos de cada página de ámbito, y `reglas/comandos.tuku.md`. Lo canónico (registros, `PENDIENTES.md`, bitácoras, notas, la transclusión y las keywords de cada página) no se toca.

## Escenario: borrar lo derivado y regenerar devuelve lo mismo

Dado el vault de la segunda semana de Andrea
```bash
cp -r ../../005-01-las-dos-semanas-de-andrea/la-segunda-semana-cae-sobre-lo/mi-vault .
```
Cuando se borra lo derivado a mano y se regenera
```bash
cd mi-vault
rm ambitos/PENDIENTES-AMBITOS.md reglas/comandos.tuku.md
grep -v '^> ' AHORA.md > AHORA.tmp; mv AHORA.tmp AHORA.md
for f in $(grep -rl '^type: Scope' ambitos); do awk '/^## Esta semana/{exit} !/^> /{print}' "$f" > "$f.tmp"; mv "$f.tmp" "$f"; done
tuku regenerate
```
Entonces el diff del vault es vacío: cada archivo vuelve a ser el que era
Y `tuku regenerate` por segunda vez dice que todo estaba al día
```bash
tuku regenerate
```
Y `tuku doctor` dice que el vault está sano
```bash
tuku doctor
```

## Escenario: un vault armado comando a comando ya está regenerado

Dado el vault de la segunda semana, tal como lo dejaron los comandos
```bash
cp -r ../../005-01-las-dos-semanas-de-andrea/la-segunda-semana-cae-sobre-lo/mi-vault .
```
Cuando se regenera todo sin haber borrado nada
```bash
cd mi-vault
tuku regenerate
```
Entonces el diff del vault es vacío, porque cada comando que escribe deja lo derivado como lo dejaría `tuku regenerate`
Y la salida dice que todo estaba al día

## Aceptación humana (en Obsidian)

- La página de un ámbito con hijos lista a sus hijos en un orden que el autor reconoce y que no cambia entre una regeneración y la siguiente.
- Ningún archivo muestra una vista vieja de los pendientes de un día.
