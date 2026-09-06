# Escenario · 002-007-crear-ambito

> Corpus, no diseño: esto es un caso a favor del que se prueba el sistema, referencia `spec/`
> pero no lo reemplaza. Si el resultado contradice `spec/`, se corrige `spec/`, no este archivo
> (ver `devel/epics.md`, "los epics mueven el diseño").

**Cubre:** epic 002, punto 4, fase 3 en su **versión mínima**: crear un ámbito y enlazar hacia atrás. La resolución de reglas por cercanía en un árbol profundo no entra, y es lo que impide que este epic no cierre nunca.

## Estado inicial

El que dejó [`002-006-transclusiones-sincronizadas`](002-006-transclusiones-sincronizadas.md). El árbol tiene un solo ámbito, `personal`, que es el que trae el estado cero.

En el martes 11 hay escrita, desde [`002-001`](002-001-entrada-en-su-dia.md), una entrada que menciona el depto centro sin enlazarlo:

```text
- 18:40 - le mandé la boleta de gastos comunes del depto centro a la administradora por WhatsApp
```

## Escenario: crear un ámbito deja el árbol correcto

Dado un vault cuyo único ámbito es `personal`
Cuando se crea el ámbito `depto-centro`
Entonces existe el directorio `ambitos/depto-centro/`
Y contiene `AGENTS.md` y `CADENCIAS.md`, aunque estén vacíos
Y contiene su página propia `depto-centro.md`, en minúscula, que es lo que lo hace ámbito y no categoría
Y `ambitos/personal/` no cambió en nada
Y no se creó ningún `CAPACIDAD.md`, que es opcional en todas partes

Los dos archivos obligatorios se cobran acá: ningún janitor tiene que manejar el caso "no existe" ([`../../spec/ambitos.md`](../../spec/ambitos.md)).

## Escenario: las menciones sueltas del ciclo en curso pasan a enlace

Dado que en el martes 11 estaba escrito `del depto centro` sin enlazar
Cuando se crea el ámbito `depto-centro`
Entonces esa mención queda como `[[depto-centro]]` en `AHORA.md`
Y el resto de la línea no se reescribe
Y ninguna otra entrada del día cambia

## Escenario: el barrido retroactivo llega hasta `AHORA.md` y no más

Dado que el vault todavía no tiene `bitacoras/`, porque no ha cerrado ningún ciclo
Cuando se crea el ámbito
Entonces el barrido alcanza `AHORA.md` y nada más
Y no se crea ni se toca ningún archivo fuera de `ambitos/depto-centro/` y `AHORA.md`

El alcance real de la regla (que los ciclos cerrados son inmutables) no se puede probar el día uno, porque no hay ciclo cerrado que dejar sin tocar. Se prueba en el epic 003. Acá se afirma lo que sí se puede: que el barrido no se sale de `AHORA.md`.

## Escenario: una entrada no puede apuntar a una categoría

Dado el ámbito `depto-centro` ya creado
Cuando se crea el directorio `ambitos/depto-centro/gastos/` con sus dos archivos obligatorios y **sin** página propia
Y se inyecta una entrada que apunta a `[[gastos]]`
Entonces `jntr.ambitos-lint` lo reporta
Y la entrada queda escrita igual, porque un error del autor se reporta y nunca se rechaza

Una categoría agrupa y no tiene de qué hablar. Es la única regla de los tres roles que se puede verificar sin un árbol profundo, y por eso es la que entra en la versión mínima.

## Escenario: crear dos veces el mismo ámbito no hace nada

Dado el ámbito ya creado
Cuando se vuelve a crear
Entonces el diff es vacío
Y las menciones ya enlazadas no se enlazan dos veces

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 002_007
```

## Qué se mira a mano

- Abrir `AHORA.md` en Obsidian y hacer clic en `[[depto-centro]]`: tiene que abrir la página del ámbito, no una nota vacía ni un enlace roto.
- Leer `ambitos/depto-centro/depto-centro.md` recién creada: si no dice nada que el autor no supiera, la plantilla del ámbito está de más.
- Que el `AGENTS.md` y el `CADENCIAS.md` vacíos no den la impresión de estar rotos al abrirlos.
