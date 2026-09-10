# Escenario · 002-04-abrir-pendiente

**Cubre:** epic 002, fase 2. Punto 2 del epic, primera mitad: un registro `**pendiente**` abre el pendiente vía bitácora sin que el autor toque `PENDIENTES.md` ni requiera un comando secundario.

## Estado inicial

El que dejó [`002-03-lint-de-registro`](002-03-lint-de-registro.md).

```bash
cp -r ../../002-03-lint-de-registro/un-tipo-abierto-desconocido-se/mi-vault .
```


## Escenario: el registro abre el pendiente y copia el cuerpo literal

Dado el estado anterior, con la tabla de pendientes vacía
Cuando se escribe el registro y se abre su pendiente

```bash
tuku entry add --vault mi-vault --day 2026-08-11 --hour 14:20 --scope personal --body "**pendiente**: avisar de los GGCC a la administradora"
```

Entonces la tabla contiene `| esta semana |  | [[personal]] | avisar de los GGCC a la administradora |`
Y el cuerpo es el mismo texto en los dos lugares, carácter por carácter
Y la columna `Cuándo` queda vacía, porque el pendiente todavía no tiene fecha
Y la tabla tiene exactamente una fila y su cabecera sigue intacta
Y no aparece ningún horizonte que el registro no haya pedido
Y el diff contra el estado anterior toca `AHORA.md`, `PENDIENTES.md` y `ambitos/PENDIENTES-AMBITOS.md`
Y la marca del registro queda reflejada en la tabla: `tuku doctor` no reporta ninguna consecuencia sin aplicar

Abrir es copiar: el comando no interpreta, y por eso este paso no necesita LLM ([`spec/agente.md`](../../spec/agente.md)).

La última afirmación garantiza la integridad entre la bitácora y la tabla. `tuku entry add` escribe el registro y aplica de forma atómica su consecuencia en `PENDIENTES.md`: no deja el vault a medias ni requiere invocar `tuku todo open`. Si una edición manual dejara un registro huérfano, `tuku doctor` detecta la discrepancia.

El archivo es una sola tabla y el horizonte es una columna, así que la escalera no ocupa lugar cuando está vacía. Bajar de escalón o agendar edita una celda: no crea ni destruye estructura, que era lo que pedía [`spec/pendientes.md`](../../spec/pendientes.md). El caso fechado entra en [`002-06`](002-06-escribir-en-un-dia-fecha.md).

## Escenario: abrir dos veces no duplica

Dado el pendiente ya abierto

```bash
tuku entry add --vault mi-vault --day 2026-08-11 --hour 14:20 --scope personal --body "**pendiente**: avisar de los GGCC a la administradora"
```

Cuando se corre el comando otra vez sobre el mismo registro

```bash
tuku entry add --vault mi-vault --day 2026-08-11 --hour 14:20 --scope personal --body "**pendiente**: avisar de los GGCC a la administradora"
```

Entonces el diff es vacío
Y la tabla sigue con una sola fila

## Dónde queda un pendiente escrito en el día de hoy

Con horizonte `esta semana` (el horizonte del ciclo en curso), y ya no es ambiguo: [`spec/pendientes.md`](../../spec/pendientes.md) dice ahora que **el día de hoy no fecha** y que fechar es escribir bajo un día futuro. Escribir bajo hoy es el acto por defecto de registrar, no una decisión de agendar: entra al horizonte del ciclo en curso. El caso que sí fecha, un día futuro, vive en [`002-06`](002-06-escribir-en-un-dia-fecha.md).

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 002_04
```

Cada escenario deja su vault en `playground/002-04-abrir-pendiente/<escenario>/mi-vault/`.

## Qué se mira a mano

- Si la tabla se lee de un vistazo con una sola fila, y si la columna `Horizonte` se entiende sin explicación.
- Que el autor no haya tenido que abrir `PENDIENTES.md`, que es la mitad del criterio de salida del epic.
