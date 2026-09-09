# Escenario · 002-05-cerrar-pendiente

**Cubre:** epic 002, fase 2. Punto 2 del epic, segunda mitad: un registro `~~(Hecho)~~` cierra el pendiente. Más el cierre sin pareja, el error que el vault real cometía ([`lecciones-macjpgil.md`](../../devel/lecciones-macjpgil.md), lección 4).

## Estado inicial

El que dejó [`002-04-abrir-pendiente`](002-04-abrir-pendiente.md): un ítem en la tabla con horizonte `esta semana`.

```bash
cp -r ../../002-04-abrir-pendiente/el-registro-abre-el-pendiente/mi-vault .
```

## Escenario: el cierre repite el texto y borra el ítem

Dado un pendiente abierto en `esta semana` con cuerpo `avisar de los GGCC a la administradora`
Cuando se escribe el cierre y se aplica

```bash
tuku entry add --vault mi-vault --dia "## Martes 11 de agosto" "- 19:05 - [[personal]] ~~(Hecho)~~: avisar de los GGCC a la administradora"
tuku todo close --vault mi-vault "- 19:05 - [[personal]] ~~(Hecho)~~: avisar de los GGCC a la administradora"
```

Entonces la fila desaparece de la tabla de `PENDIENTES.md`
Y la tabla queda vacía, con su cabecera intacta
Y el registro de apertura de las 14:20 sigue escrito en el martes 11, sin tocar
Y el diff toca `AHORA.md`, `PENDIENTES.md` y `ambitos/PENDIENTES-AMBITOS.md`
Y el cierre queda aplicado: `tuku doctor` no reporta ninguna consecuencia pendiente

El cierre repite el texto del pendiente en vez de reescribirlo en pasado, y por eso el emparejamiento es literal y no semántico ([`spec/bitacora.md`](../../spec/bitacora.md)). El historial queda en la bitácora, no en `PENDIENTES.md`.

## Escenario: un cierre sin pendiente abierto se reporta, no se inventa nada

Dado que nunca se abrió ningún pendiente con el cuerpo `comprar una maleta`, y el de los GGCC ya se cerró

```bash
tuku entry add --vault mi-vault --dia "## Martes 11 de agosto" "- 19:05 - [[personal]] ~~(Hecho)~~: avisar de los GGCC a la administradora"
tuku todo close --vault mi-vault "- 19:05 - [[personal]] ~~(Hecho)~~: avisar de los GGCC a la administradora"
```

Cuando se escribe el cierre huérfano y se aplica

```bash
tuku entry add --vault mi-vault --dia "## Martes 11 de agosto" "- 19:10 - [[personal]] ~~(Hecho)~~: comprar una maleta"
tuku todo close --vault mi-vault "- 19:10 - [[personal]] ~~(Hecho)~~: comprar una maleta"
```

Entonces el comando lo reporta como cierre sin pareja
Y `PENDIENTES.md` queda byte a byte igual que antes de la inyección
Y no se crea el pendiente que falta, ni se borra ningún otro ítem
Y la línea queda escrita en la bitácora, porque un error del autor se reporta y nunca se rechaza

El caso negativo más importante del epic: con `PENDIENTES.md` como fuente de verdad, un cierre inventado deja el archivo mintiendo.

## Escenario: cerrar dos veces no vuelve a mover

Dado el pendiente ya cerrado

```bash
tuku entry add --vault mi-vault --dia "## Martes 11 de agosto" "- 19:05 - [[personal]] ~~(Hecho)~~: avisar de los GGCC a la administradora"
tuku todo close --vault mi-vault "- 19:05 - [[personal]] ~~(Hecho)~~: avisar de los GGCC a la administradora"
```

Cuando se corre el comando otra vez sobre el mismo registro

```bash
tuku todo close --vault mi-vault "- 19:05 - [[personal]] ~~(Hecho)~~: avisar de los GGCC a la administradora"
```

Entonces el diff es vacío
Y el segundo pase se reporta igual que el primer cierre sin pareja, porque ya no hay nada abierto que emparejar

El segundo pase de un cierre correcto es, por construcción, un cierre sin pareja. Que los dos den el mismo reporte hace al comando idempotente sin llevar estado.

## Lo que este escenario deja fuera

El cierre **no literal**, cuando el dictado no repite el texto palabra por palabra: deja de ser paso 5 y pasa a juicio del agente ([`spec/agente.md`](../../spec/agente.md)), que ante la duda confirma. Entra en `003-05`, entre los casos negativos del dictado ([`003-00`](003-00-el-dia-uno-dictado.md)).

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 002_05
```

Cada escenario deja su vault en `playground/002-05-cerrar-pendiente/<escenario>/mi-vault/`.

## Qué se mira a mano

- Leer el martes 11 completo: la apertura de las 14:20 y el cierre de las 19:05 tienen que leerse como la misma tarea, tachada.
- El reporte del cierre sin pareja: que le diga al autor qué escribió y qué esperaba el sistema, sin sonar a rechazo.
