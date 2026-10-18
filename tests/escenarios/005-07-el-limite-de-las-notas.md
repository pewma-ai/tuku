# 005-07 · El límite de las notas

> **Principio:** [P3 (el agente es un secretario, no un dueño)](../../docs/principios.md#L25), [P4 (determinismo)](../../docs/principios.md#L33) · **Spec:** [`spec/notas.md`](../../spec/notas.md), "Enlazar notas"

Con treinta personas en `notas/`, `tuku context note` trae las veinticinco de `updated` más reciente (`context_note_limit`). El agente enlaza a las que `context` ofrece y no inventa la ruta de las que no.

Cada escenario parte del vault de la segunda semana de [`005-01`](005-01-las-dos-semanas-de-andrea.md). Las personas las escribe [`personas.py`](fixtures/005-07-el-limite-de-las-notas/personas.py), de Rodrigo Salinas (la más antigua) a Daniela Paredes (la más reciente).

## Escenario: context note trae las veinticinco más recientes

Dado el vault de la segunda semana con treinta personas en `notas/`
```bash
cp -r ../../005-01-las-dos-semanas-de-andrea/la-segunda-semana-cae-sobre-lo/mi-vault .
python3 ../../tests/escenarios/fixtures/005-07-el-limite-de-las-notas/personas.py mi-vault
```
Cuando se piden las notas enlazables
```bash
cd mi-vault
tuku context note
```
Entonces la lista tiene veinticinco personas, de Daniela Paredes a Teresa Montt, ordenadas por `updated`
Y Rodrigo Salinas, Elena Vidal, Hugo Ortega, Inés Cabrera y Samuel Toro no salen

## Escenario: el agente enlaza a quien context ofrece y a nadie más

Dado el mismo vault con treinta personas
```bash
cp -r ../../005-01-las-dos-semanas-de-andrea/la-segunda-semana-cae-sobre-lo/mi-vault .
python3 ../../tests/escenarios/fixtures/005-07-el-limite-de-las-notas/personas.py mi-vault
```
Cuando Andrea nombra a Daniela Paredes, la más reciente, y a las dos más antiguas
```agente TUKU_NOW="2026-08-23 22:30"
Hablé con Daniela Paredes del pedido. Almorcé con Rodrigo Salinas. Y le escribí a Elena Vidal.
```
Entonces el registro de Daniela Paredes enlaza a `notas/daniela-paredes.md`
Y Rodrigo Salinas y Elena Vidal quedan con el nombre de Andrea y sin link, porque `context` no los trae
Y el agente no crea notas por su cuenta
