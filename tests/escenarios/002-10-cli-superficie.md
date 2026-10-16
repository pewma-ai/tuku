# 002-10 · Superficie pública del CLI

> **Principio:** [P1 (soberanía y equivalente manual)](../../docs/principios.md#L9), [P4 (determinismo)](../../docs/principios.md#L33) · **Brief:** [Herramientas transparentes y gobernanza](../../docs/brief.md#L43) · **Spec:** [`spec/cli.md`](../../spec/cli.md)

La ayuda de `tuku` nombra cada sustantivo y sus verbos, y una invocación incompleta es error de uso (2), no rechazo. El contrato del CLI está en [`spec/cli.md`](../../spec/cli.md); lo que no necesita un vault lo prueban los unitarios.

## Escenario: tuku -h nombra los nouns del epic

Cuando se consulta la ayuda principal del CLI
```bash
tuku -h
```
Entonces sale con código 0 (`EXITO`)
Y el texto nombra todos los sustantivos del sistema: `init`, `cycle`, `doctor`, `fix`, `rebuild`, `vocab`, `style`, `entry`, `todo`, `scope` y `note`

## Escenario: cada noun lista sus verbs

Cuando se consulta la ayuda de cada sustantivo
```bash
tuku entry -h
tuku vocab -h
tuku cycle -h
tuku style -h
tuku todo -h
tuku scope -h
tuku note -h
tuku doctor -h
tuku fix -h
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

## Aceptación humana (en Obsidian)

- Al consultar `tuku <comando> -h`, el párrafo antes de las opciones alcanza para hacer lo mismo con un editor de texto: qué archivos toca y cómo.
- Los mensajes de rechazo deben ser claros y directos, indicando siempre la acción correctiva en vez de arrojar trazas de error crudas.
