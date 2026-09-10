# 002-10 · Superficie pública del CLI

> **Principio:** [P1 (soberanía y equivalente manual)](../../docs/principios.md#L9), [P4 (determinismo)](../../docs/principios.md#L33) · **Brief:** [Herramientas transparentes y gobernanza](../../docs/brief.md#L43) · **Spec:** [`spec/cli.md`](../../spec/cli.md)

El CLI `tuku` es el contrato público determinista entre el usuario y el vault: códigos de salida estrictos (0 éxito, 1 rechazo, 2 error de sintaxis), mensajes de error que siempre nombran defecto y corrección, y el campo obligatorio «A mano» en cada comando.

## Escenario: tuku -h nombra los nouns del epic

Cuando se consulta la ayuda principal del CLI
```bash
tuku -h
```
Entonces sale con código 0 (`EXITO`)
Y el texto nombra todos los sustantivos del sistema: `init`, `cycle`, `doctor`, `rebuild`, `vocab`, `style`, `entry`, `todo`, `scope`, `link` y `note`

## Escenario: cada noun lista sus verbs

Cuando se consulta la ayuda de cada sustantivo
```bash
tuku entry -h
tuku vocab -h
tuku cycle -h
tuku style -h
tuku todo -h
tuku scope -h
tuku link -h
tuku note -h
tuku entry add -h
tuku entry rename -h
```
Entonces todas las ayudas salen con código 0
Y cada sustantivo lista sus verbos correspondientes
Y `tuku entry add -h` nombra `--body`, `--scope`, `--day` y `--hour`
Y `tuku entry rename -h` nombra `--day`, `--hour` y `--body`

## Escenario: un noun sin verb es error de uso

Cuando se invoca un sustantivo sin especificar verbo
```bash
tuku entry
```
Entonces sale con código 2 (`USO`), distinguiéndose claramente de un rechazo de negocio

## Escenario: el lint sale con rechazo cuando encuentra un error

Dado un vault con una clasificación abierta desconocida
```bash
tuku init mi-vault --date 2026-08-11
tuku entry add --vault mi-vault --day 2026-08-11 --hour 12:05 --scope personal --body "**cachureo**: ordené los cables"
tuku entry lint --vault mi-vault
```
Cuando se introduce además una marca cerrada mal escrita y se valida
```bash
tuku entry add --vault mi-vault --day 2026-08-11 --hour 13:00 --scope personal --body "**Cadencia**: comprar una maleta"
tuku entry lint --vault mi-vault
```
Entonces la validación abierta sale con código 0 y la cerrada sale con código 1 (`RECHAZO`)

## Escenario: un directorio que no es un vault se rechaza diciendo qué hacer

Dado un directorio cualquiera sin `AHORA.md`
```bash
mkdir no-es-vault
```
Cuando se corre
```bash
tuku entry add --vault no-es-vault --body "un registro huérfano"
```
Entonces el comando falla con código 1 (`RECHAZO`), no con el de uso
Y el error nombra AHORA.md y dice que se puede corregir con tuku init

## Aceptación humana (en Obsidian)

- Al consultar `tuku <comando> -h`, la ayuda debe incluir el campo `A mano:` explicando cómo lograr exactamente el mismo resultado con un editor de texto estándar sin software propietario.
- Los mensajes de rechazo deben ser claros y directos, indicando siempre la acción correctiva en vez de arrojar trazas de error crudas.
