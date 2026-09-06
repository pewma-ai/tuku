# Escenario · 002-001-entrada-en-su-dia

> Corpus, no diseño: esto es un caso a favor del que se prueba el sistema, referencia `spec/`
> pero no lo reemplaza. Si el resultado contradice `spec/`, se corrige `spec/`, no este archivo
> (ver `devel/epics.md`, "los epics mueven el diseño").

**Cubre:** epic 002, fase 1. Punto 1 del epic: la entrada queda en el día correcto y en orden cronológico.

## Estado inicial

**Primer paso de la cadena del epic 002.** Parte del fixture `vacio`: un vault `vanilla` recién instalado con `--desde 2026-08-11`, que es el estado con el que cerró el epic 001. Los siete días sembrados van del martes 11 al lunes 17 de agosto de 2026, y HOY es el martes 11.

Todo escenario `002-YYY` posterior parte del estado que dejó el anterior. El estado inicial no se congela en ninguna parte: se reproduce corriendo la cadena desde acá.

## Escenario: tres entradas caen en el día de hoy, ordenadas por hora

Dado un vault recién instalado, con HOY en el martes 11 de agosto
Y ninguna entrada escrita todavía
Cuando se inyectan estas tres líneas, en este orden:

```text
- 18:40 - le mandé la boleta de gastos comunes del depto centro a la administradora por WhatsApp
- 09:12 - [[personal]] **señal**: la administradora responde los mensajes con varios días de atraso
- 11:30 - hice la consulta presencial por el standing desk
```

Entonces las tres quedan bajo `## Martes 11 de agosto`
Y en orden 09:12, 11:30, 18:40, que no es el orden en que se inyectaron
Y la de las 18:40 sigue escrita tal cual quedó, sin reescribirse al insertar las otras dos
Y los otros seis días siguen con su marca de día vacío

## Escenario: la fase 1 no toca ninguna consecuencia

Dado el mismo estado
Cuando se inyectan las tres líneas
Entonces el diff contra el estado inicial toca `AHORA.md` y nada más
Y `PENDIENTES.md` queda byte a byte igual al del vault recién instalado

Es el criterio de corte de la fase 1: si en esta fase algo escribe en `PENDIENTES.md`, el corte está mal hecho.

## Escenario: la entrada sin ámbito y sin clasificación es válida

Dado el mismo estado
Cuando se inyecta la línea de las 11:30, que no lleva `[[ambito]]` ni `**clasificacion**`
Entonces queda escrita sin que el lint la marque

Ámbito y clasificación son opcionales según el contexto ([`../../spec/bitacora.md`](../../spec/bitacora.md)).

## De dónde salen las líneas

De `fixtures/002-010-dictado-del-dia-uno/entradas.md`, la salida congelada del agente para el dictado del día uno. Es el único fixture del epic y pertenece al escenario que lo produce ([`002-010-dictado-del-dia-uno.md`](002-010-dictado-del-dia-uno.md)); los nueve pasos deterministas lo consumen.

Se congela porque es lo que `README.md` sanciona congelar: una respuesta de agente no tiene original vivo en el repositorio contra el cual compararse. Todo lo demás de la cadena se reproduce.

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 002_001
```

Deja el vault en `playground/002-001-entrada-en-su-dia/`, que es el estado inicial del paso siguiente.

## Qué se mira a mano

- Abrir `AHORA.md` en Obsidian y leer el martes 11 como leería el autor: que las tres entradas se entiendan sin la conversación que las originó (principio 2 de `spec/bitacora.md`).
- Que la entrada de las 18:40, que no lleva ámbito ni clasificación, no se vea coja al lado de las otras dos.
