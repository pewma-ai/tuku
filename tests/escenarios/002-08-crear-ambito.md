# Escenario · 002-08-crear-ambito

**Cubre:** epic 002, punto 4, fase 3 en su **versión mínima**: crear un ámbito y enlazar hacia atrás. La resolución de reglas por cercanía en un árbol profundo no entra.

## Estado inicial

El que dejó [`002-07-transclusiones-sincronizadas`](002-07-transclusiones-sincronizadas.md). El árbol tiene un solo ámbito, `personal`, el del estado cero. En el martes 11 hay escrito, desde [`002-02`](002-02-registro-en-su-dia.md), un registro que menciona el depto centro sin enlazarlo:

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

Los dos archivos obligatorios se cobran acá para que ningún comando tenga que manejar el caso "no existe" ([`spec/ambitos.md`](../../spec/ambitos.md)).

## Escenario: las menciones sueltas del ciclo en curso pasan a enlace

Dado que en el martes 11 estaba escrito `del depto centro` sin enlazar
Cuando se crea el ámbito `depto-centro`
Entonces esa mención queda como `[[depto-centro]]` en `AHORA.md`
Y el resto de la línea no se reescribe
Y ningún otro registro del día cambia

## Escenario: el barrido retroactivo llega hasta `AHORA.md` y no más

Dado que el vault todavía no tiene `bitacoras/`, porque no ha cerrado ningún ciclo
Cuando se crea el ámbito
Entonces el barrido alcanza `AHORA.md` y nada más
Y no se crea ni se toca ningún archivo fuera de `ambitos/depto-centro/` y `AHORA.md`

Que los ciclos cerrados sean inmutables no se puede probar el día uno, porque no hay ninguno; se prueba en el epic 004. Acá se afirma lo que sí se puede.

## Escenario: un registro no puede apuntar a una categoría

Dado el ámbito `depto-centro` ya creado
Cuando se crea el directorio `ambitos/depto-centro/gastos/` con sus dos archivos obligatorios y **sin** página propia
Y se inyecta un registro que apunta a `[[gastos]]`
Entonces `tuku scope lint` lo reporta
Y el registro queda escrito igual, porque un error del autor se reporta y nunca se rechaza

Una categoría agrupa y no tiene de qué hablar. Es la única regla de los tres roles verificable sin un árbol profundo, y por eso entra en la versión mínima.

## Escenario: crear dos veces el mismo ámbito no hace nada

Dado el ámbito ya creado
Cuando se vuelve a crear
Entonces el diff es vacío
Y las menciones ya enlazadas no se enlazan dos veces

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 002_08
```

## Qué se mira a mano

- Clic en `[[depto-centro]]` desde `AHORA.md`: abre la página del ámbito, no una nota vacía ni un enlace roto.
- Leer `depto-centro.md` recién creada: si no dice nada que el autor no supiera, la plantilla está de más.
- Que el `AGENTS.md` y el `CADENCIAS.md` vacíos no parezcan rotos al abrirlos.
