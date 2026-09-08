# Escenario · 001-06-cli-ayuda

**Cubre:** epic 001, fase 0. La convención "la ayuda del CLI se prueba en cada epic" de [`../../devel/epics.md`](../../devel/epics.md).

## Escenario: `tuku -h` nombra lo que el epic 001 puso en el CLI

Dado el CLI de TUKU tal como lo deja el epic 001
Cuando se llama a `tuku.cli.main(["-h"])`
Entonces sale con código 0
Y el texto nombra el comando `init` y el propósito de TUKU

## Escenario: `tuku init -h` lista las opciones que añade el epic 001

Dado el mismo CLI
Cuando se llama a `main(["init", "-h"])`
Entonces sale con código 0
Y el texto nombra `dir`, `--variante`, `--author` y `--force`

## Escenario: `tuku` sin comando es error de uso

Cuando se llama a `main([])`
Entonces sale con el código de uso (2) y el error lista los comandos válidos

## Escenario: `--author` sin valor es error de uso

Cuando se llama a `main(["init", "--author"])` sin dar el nombre
Entonces sale con el código de uso (2)

## Escenario: un entorno roto no se confunde con un error de uso

Dado `TUKU_HOME` apuntando a un directorio que existe pero no tiene `template/`
Cuando se llama a `main(["init", <destino>])`
Entonces sale con el código de entorno (3), distinto del de uso
Y el error dice qué le falta al árbol

## Por qué existe

La ayuda es superficie pública: es lo primero que ve quien instala TUKU y no sabe qué es. Cada epic que toca `tuku` la amplía (comandos nuevos, opciones nuevas), y sin un test esa ampliación se olvida o se desincroniza del código.

Los códigos de salida son la otra mitad de esa superficie, y son contrato según [`../../spec/cli.md`](../../spec/cli.md). Este escenario los fija porque ya hubo un choque real: `TukuHomeInvalido` devolvía 2, el mismo que argparse emite ante una invocación mal escrita, así que desde fuera no había forma de saber si corregir el comando o la instalación. Ahora son 1 rechazo, 2 uso, 3 entorno, y el test comprueba que ninguna causa comparte código.

Corre en proceso, sobre `tuku.cli.main`, sin red ni disco: argparse imprime la ayuda y sale antes de llamar a `init()`. Por eso entra en la corrida por defecto, a diferencia de `001-01`.

No fija el texto palabra por palabra (eso se lee a mano, abajo): solo que cada pieza que el epic 001 agregó está nombrada y que `-h` sale con código 0. Que la prosa se entienda es juicio humano.

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 001_06
```

No produce vault: no deja nada en `playground/`.

## Qué se mira a mano

- Correr `uv run tuku -h` y `uv run tuku init -h` y leerlos: que se entiendan sin saber qué es TUKU, que `init` quede claro como "siembra un vault", y que el ejemplo mínimo (`tuku init mi-vault`) se deduzca de lo que hay.
