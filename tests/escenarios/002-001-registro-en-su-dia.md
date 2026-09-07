# Escenario · 002-001-registro-en-su-dia

**Cubre:** epic 002, fase 1. Punto 1 del epic: el registro queda en el día correcto y en orden cronológico.

## Estado inicial

**Primer paso de la cadena del epic 002.** Fixture `vacio`: un vault `vanilla` recién instalado con `--desde 2026-08-11`, el estado con que cerró el epic 001. Siete días sembrados, martes 11 a lunes 17 de agosto de 2026. HOY es el martes 11.

## Escenario: tres registros caen en el día de hoy, ordenados por hora

Dado un vault recién instalado, con HOY en el martes 11 de agosto
Y ningún registro escrito todavía
Cuando se inyectan estas tres líneas, en este orden:

```text
- 18:40 - le mandé la boleta de gastos comunes del depto centro a la administradora por WhatsApp
- 09:12 - [[personal]] **señal**: la administradora responde los mensajes con varios días de atraso
- 11:30 - hice la consulta presencial por el standing desk
```

Entonces los tres quedan bajo `## Martes 11 de agosto`
Y en orden 09:12, 11:30, 18:40, que no es el orden en que se inyectaron
Y el de las 18:40 sigue escrito tal cual, sin reescribirse al insertar los otros dos
Y los otros seis días siguen con su marca de día vacío

## Escenario: la fase 1 no toca ninguna consecuencia

Dado el mismo estado
Cuando se inyectan las tres líneas
Entonces el diff contra el estado inicial toca `AHORA.md` y nada más
Y `PENDIENTES.md` queda byte a byte igual al del vault recién instalado

Criterio de corte de la fase 1: si algo escribe en `PENDIENTES.md`, el corte está mal hecho.

## Escenario: el registro sin ámbito y sin clasificación es válido

Dado el mismo estado
Cuando se inyecta la línea de las 11:30, que no lleva `[[ambito]]` ni `**clasificacion**`
Entonces `jntr.registrar` lo deja escrito tal cual, sin marcarlo

Ámbito y clasificación son opcionales según el contexto ([`spec/bitacora.md`](../../spec/bitacora.md)). Que además el lint no lo marque se prueba en [`002-002`](002-002-lint-de-registro.md), que arranca de este estado.

## De dónde salen las líneas

Las tres son constante del arnés (`REGISTROS` en `test_002_001_registro_en_su_dia.py`), como los días de `test_001_001`: la rebanada mínima que este paso necesita. El día uno completo, generado por un agente desde el corpus, vive en [`002-010`](002-010-dictado-del-dia-uno.md).

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 002_001
```

Deja el vault en `playground/002-001-registro-en-su-dia/`, estado inicial del paso siguiente.

## Qué se mira a mano

- Leer el martes 11 en Obsidian como lo leería el autor: que los tres registros se entiendan sin la conversación que los originó (principio 2 de `spec/bitacora.md`).
- Que el registro de las 18:40, sin ámbito ni clasificación, no se vea cojo al lado de los otros dos.
