# Epic 004 · La conversación

> **Marco:** [Brief de TUKU](../../docs/brief.md) · [Principios normativos](../../docs/principios.md) · [Especificaciones](../../spec/README.md)

El autor conversa en vez de dictar: consulta, duda, cambia de rumbo, atiende un imprevisto y ratifica al final. El vault contiene lo que ratificó. El agente delibera con él y escribe solo mediante comandos `tuku` ([P3, secretario, no dueño](../../docs/principios.md#L25)).

## Qué entrega el epic

1. **El conductor de sesión:** sostiene un diálogo de varios turnos entre el agente del autor y el de TUKU, con un adaptador por arnés, y anota el delta del vault tras cada turno.
2. **Los `AGENTS.md` del vault** corregidos por lo que la conversación rompa.
3. **Los Límites verificados como delta:** vacío mientras se delibera, y el comando de cada hecho una vez aclarado.

## Qué se verifica

- **Dos agentes.** El autor es un agente que interpreta a Damián Ulloa, de [`referencia-faena.md`](../../corpus/referencia/referencia-faena.md), y sigue el plan de cada escenario. El otro es el agente de TUKU, con el arnés por defecto.
- **Cada turno** deja un delta del vault que el escenario declara.
- **Al cierre** el vault coincide con el que deja el dictado directo de lo ratificado: hora, ámbito, marca cerrada y filas de `PENDIENTES.md`.
- **Los Límites** de la tabla de [`AGENTS.md`](../../template/vanilla/AGENTS.md) se comprueban en todos los escenarios: cada cambio del vault tiene su comando `tuku` en la traza y `tuku doctor` confirma la coherencia.

## Escenarios del epic

Cada escenario copia el vault de partida y corre por su cuenta. Ninguno hereda del anterior.

- [`004-01-el-dia-conversado.md`](004-01-el-dia-conversado.md): camino feliz. Consulta, pregunta del agente, hechos aclarados, deliberación, imprevisto, propuesta descartada y ratificación.
- `004-02` Pensar en voz alta sin ratificar nunca: el delta es vacío durante toda la sesión.
- `004-03` Ratificar tras tres giros: el vault queda como el dictado del último acuerdo.
- `004-04` Cerrar lo que nunca se abrió: el hecho se registra sin pregunta y sin pendiente inventado.
- `004-05` La pregunta que la respuesta no resuelve: ningún pendiente se cierra mientras la ambigüedad persiste.

## Estado inicial común

Todos los escenarios parten del martes 11 de agosto de [`referencia-faena.md`](../../corpus/referencia/referencia-faena.md): cuatro frentes con un pendiente abierto cada uno. Dos son de Fabina Méndez (el marco de Azure y el diccionario de MetricDB), lo que permite el cierre ambiguo. El reloj de todos los turnos es `TUKU_NOW="2026-08-12 21:00"`, el miércoles por la noche.

## Escenario: el vault de partida

Dado un directorio vacío
Cuando se siembra el vault y se abren cuatro frentes, cada uno con su pendiente del martes 11
```bash
tuku init mi-vault --at 2026-08-11
cd mi-vault
tuku scope create tuku --at "2026-08-11 09:15"
tuku scope create transformacion-digital --at "2026-08-11 10:00"
tuku scope create faena-ai --at "2026-08-11 11:00"
tuku scope create tesis-javier-castro --at "2026-08-11 12:50"
tuku todo open --at "2026-08-11 09:20" --scope tuku --body "investigar cómo minimizar las reglas de MaC aprovechando el aprendizaje nativo de los agentes"
tuku todo open --at "2026-08-11 10:05" --scope transformacion-digital --body "reunirse con Víctor Lagos para dividir las interfaces de ODIP en tareas manejables"
tuku todo open --at "2026-08-11 11:05" --scope faena-ai --body "presentar a Fabina Méndez la propuesta de marco de casos de uso con Azure LLM"
tuku todo open --at "2026-08-11 12:55" --due 2026-08-12 --scope tesis-javier-castro --body "conversar el diccionario de MetricDB con Fabina Méndez"
```
Entonces `PENDIENTES.md` tiene cuatro filas: tres en `esta semana` y una con fecha, que vence el 2026-08-12
Y `AHORA.md` tiene bajo el martes 11 las cuatro constancias de ámbito abierto y los cuatro pendientes
Y `tuku doctor` confirma la coherencia total del vault
```bash
tuku doctor
```

## El registro de la conversación

Cada escenario deja la conversación completa en `notas/conversation-log.md` del vault que queda en `playground/`, donde se lee desde Obsidian. Lleva el frontmatter `type: Note` y, por turno, lo que dijo Damián, lo que respondió el agente, los comandos `tuku` que ejecutó y el delta del vault.

El conductor lo escribe al terminar la sesión, también cuando el escenario falla, de modo que el agente conversa sin verlo. El delta y la verificación de la traza lo excluyen.

## Criterio de salida

Una conversación en que el autor duda, se contradice, atiende un imprevisto y rectifica deja el vault en el estado que ratificó al final, y todas las filas de la tabla de Límites se cumplen en el camino.
