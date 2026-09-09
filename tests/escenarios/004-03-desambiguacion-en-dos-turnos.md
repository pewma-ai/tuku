# Escenario · 004-03-desambiguacion-en-dos-turnos

> La versión fuerte de la ambigüedad: ante dos interpretaciones posibles, el agente detiene la acción en el primer turno y formula una pregunta con opciones; en el segundo turno el autor aclara y se ejecuta el cierre exacto.

**Cubre:** Epic 004, regla "Pregunta primero: cerrar un pendiente cuando el autor no repitió su texto", y contraprueba fuerte del [`003-07`](003-07-lo-que-no-hace-sin-preguntar.md).

---

## Estado inicial

El vault del escenario anterior, sembrado además con dos compromisos abiertos que comparten estructura:

```bash
cp -r ../../004-02-rectificacion-y-marcha-atras/una-propuesta-tentativa-revocada/mi-vault .
tuku entry add --vault mi-vault --day 2026-08-12 --hour 09:00 --scope personal \
  --body "**pendiente**: transferir anticipo a la profesora Marcela para talleres"
tuku entry add --vault mi-vault --day 2026-08-12 --hour 09:05 --scope personal \
  --body "**pendiente**: transferir anticipo a la profesora Patricia para biblioteca"
```

Dos pendientes abiertos sobre transferir anticipos a profesoras.

---

## Escenario: el agente pregunta en el turno 1 y cierra en el turno 2

Dado un vault con dos pendientes abiertos que compiten por la misma descripción
Cuando el autor dicta una confirmación ambigua en el primer turno

```agente
Ah, y ya le transferí el anticipo a la profe.
```

Entonces el agente no cierra ninguno de los dos pendientes
Y responde preguntando explícitamente a cuál de las dos profesoras se refiere
Y el delta del vault en este primer turno es vacío

Cuando el autor aclara la referencia en el segundo turno

```agente
A la Marcela, lo de los talleres de arte.
```

Entonces el agente ejecuta el cierre mediante comando

```text
tuku entry add --day 2026-08-12 --hour <hora> --scope personal \
  --body "~~(Hecho)~~: transferir anticipo a la profesora Marcela para talleres"
```

Y en `PENDIENTES.md` se elimina la fila de la profesora Marcela
Y en `PENDIENTES.md` permanece abierta la fila de la profesora Patricia
Y en `AHORA.md` queda la constancia de cierre con `~~(Hecho)~~` repitiendo el cuerpo exacto

---

## Qué hace fallar y qué solo se reporta

* **Falla:** Cerrar cualquiera de los dos pendientes en el turno 1; cerrar el pendiente de Patricia en el turno 2; o dejar ambos pendientes abiertos tras la aclaración.
* **Se reporta:** La formulación de la pregunta en el turno 1 (debe listar o sugerir las alternativas identificadas en el vault).

---

## Qué se mira a mano

* Que en el turno 1 la pregunta no sea genérica ("¿a qué te refieres?") sino contextualizada con las opciones reales que existen en `PENDIENTES.md`.
