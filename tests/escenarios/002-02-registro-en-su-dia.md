# Escenario · 002-02-registro-en-su-dia

**Cubre:** epic 002, fase 1. Punto 1 del epic: el registro queda en el día correcto y en orden cronológico.

## Estado inicial

El que dejó [`002-01-abrir-ciclo`](002-01-abrir-ciclo.md): `AHORA.md` abierto con día inicial y día final del 11 al 17 de agosto de 2026. HOY es el martes 11.

```bash
cp -r ../../002-01-abrir-ciclo/crear-ahora-md-a-partir-de-la/mi-vault .
```

La cadena queda a la vista: el estado inicial de un paso es el estado final del anterior, y acá se copia con un comando en vez de reconstruirse. Si el paso previo no corrió, la copia falla diciéndolo.

## Escenario: tres registros caen en el día de hoy, ordenados por hora

Dado un vault con el ciclo abierto, con HOY en el martes 11 de agosto
Y ningún registro escrito todavía
Cuando se corren estas tres líneas, en este orden

```bash
tuku entry add --vault mi-vault --day 2026-08-11 --hour 18:40 --body "le mandé la boleta de gastos comunes del depto centro a la administradora por WhatsApp"
tuku entry add --vault mi-vault --day 2026-08-11 --hour 09:12 --scope personal --body "**señal**: la administradora responde los mensajes con varios días de atraso"
tuku entry add --vault mi-vault --day 2026-08-11 --hour 11:30 --body "hice la consulta presencial por el standing desk"
```

Entonces los tres quedan bajo `## Martes 11 de agosto`
Y en orden 09:12, 11:30, 18:40, que no es el orden en que se inyectaron
Y el de las 18:40 sigue escrito tal cual, sin reescribirse al insertar los otros dos
Y el día final sigue con su marca de día vacío

## Escenario: la fase 1 propaga hacia ámbitos y no toca PENDIENTES.md

Dado el mismo estado
Cuando se corren las tres líneas

```bash
tuku entry add --vault mi-vault --day 2026-08-11 --hour 18:40 --body "le mandé la boleta de gastos comunes del depto centro a la administradora por WhatsApp"
tuku entry add --vault mi-vault --day 2026-08-11 --hour 09:12 --scope personal --body "**señal**: la administradora responde los mensajes con varios días de atraso"
tuku entry add --vault mi-vault --day 2026-08-11 --hour 11:30 --body "hice la consulta presencial por el standing desk"
```

Entonces el diff contra el estado inicial toca `AHORA.md` y `ambitos/personal/personal.md`
Y `PENDIENTES.md` queda byte a byte igual al del vault recién instalado

Criterio de corte de la fase 1: si algo escribe en `PENDIENTES.md`, el corte está mal hecho.

## Escenario: el registro sin ámbito y sin clasificación es válido

Dado el mismo estado
Cuando se corre solo la línea de las 11:30, que no lleva `[[ambito]]` ni `**clasificacion**`

```bash
tuku entry add --vault mi-vault --day 2026-08-11 --hour 11:30 --body "hice la consulta presencial por el standing desk"
```

Entonces `tuku entry add` lo deja escrito tal cual, sin marcarlo

Ámbito y clasificación son opcionales según el contexto ([`spec/bitacora.md`](../../spec/bitacora.md)). Que además el lint no lo marque se prueba en [`002-03`](002-03-lint-de-registro.md), que arranca de este estado.

## De dónde salen las líneas

Las tres están escritas acá, en los comandos: son la rebanada mínima que este paso necesita, y el arnés ya no las repite. El día uno completo, dictado a un agente, vive en `003-06` ([`003-00`](003-00-el-dia-uno-dictado.md)).

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 002_02
```

Cada escenario deja su vault en `playground/002-02-registro-en-su-dia/<escenario>/mi-vault/`. El del primero es el estado inicial del paso siguiente.


## Qué se mira a mano

- Leer el martes 11 en Obsidian como lo leería el autor: que los tres registros se entiendan sin la conversación que los originó (principio 2 de `spec/bitacora.md`).
- Que el registro de las 18:40, sin ámbito ni clasificación, no se vea cojo al lado de los otros dos.
