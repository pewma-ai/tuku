# 005-06 · El agente con historia

> **Principio:** [P3 (el agente es un secretario, no un dueño)](../../docs/principios.md#L25), [P4 (determinismo)](../../docs/principios.md#L33) · **Brief:** [La organización emerge](../../docs/brief.md#L49) · **Spec:** [`spec/agente.md`](../../spec/agente.md), [`spec/ambitos.md`](../../spec/ambitos.md), [`spec/flujo-informacion.md`](../../spec/flujo-informacion.md) · **Tutorial:** [capítulo 4](../../docs/tutorial/04-una-semana-despues.md)

Con dos semanas de historia, lo que Andrea dice ya no lleva el nombre completo ni el ámbito: dice «la Patricia» y «la Paula». El agente elige el ámbito leyendo las keywords de las páginas, escribe lo que ella dijo tal como lo dijo, y no adivina cuando dos personas se llaman igual.

Estos escenarios llevan un agente, así que cuestan tokens y quedan fuera de la corrida por defecto (marca `agentic`). Cada uno parte del vault de la segunda semana de [`005-01`](005-01-las-dos-semanas-de-andrea.md).

## Escenario: una keyword única decide el ámbito

Dado el vault de la segunda semana, con `Patricia` entre las keywords del liceo y de nadie más
```bash
cp -r ../../005-01-las-dos-semanas-de-andrea/la-segunda-semana-cae-sobre-lo/mi-vault .
```
Cuando Andrea cuenta una llamada con el nombre de pila
```agente TUKU_NOW="2026-08-23 22:30"
Hablé con la Patricia del precio y quedó conforme.
```
Entonces esa frase se traduce en un solo registro, del ámbito del liceo
```text
tuku entry create --scope liceo-tecnico-andes --body "<la frase tal como la dijo>"
```
Y el cuerpo conserva las palabras de Andrea: la Patricia sin apellido y el texto sin links
Y el registro cae en el domingo 23, y el delta es `AHORA.md` y la página del liceo

## Escenario: dos personas con el mismo nombre esperan al autor

Dado el mismo vault, donde `Paula` es keyword del catálogo (Paula Ibáñez, la diseñadora) y la Escuela Los Maitenes tiene a Paula Reyes, su jefa de UTP
```bash
cp -r ../../005-01-las-dos-semanas-de-andrea/la-segunda-semana-cae-sobre-lo/mi-vault .
```
Cuando Andrea nombra a una Paula sin decir cuál
```agente TUKU_NOW="2026-08-23 22:30"
Le mandé el catálogo a la Paula.
```
Entonces el agente deja sin elegir el ámbito de las dos Paulas
Y si pregunta cuál, la pregunta nombra a las dos; si en cambio escribe, lo hace en el ámbito que las contiene y con las palabras de Andrea
Y los pendientes quedan como estaban

## Qué se mira a mano

- La respuesta a «Hablé con la Patricia del precio» es breve: dice qué quedó escrito y dónde, sin repetir cómo.
- Cuando el agente pregunta por la Paula, la pregunta cabe en una línea y deja a Andrea contestar con un nombre.
- **Decisión pendiente de diseño:** el [capítulo 4](../../docs/tutorial/04-una-semana-despues.md) y el `AGENTS.md` del vault dicen que ante dos candidatos el agente pregunta («Nunca actuar sobre una petición ambigua»), y [`flujo-informacion.md`](../../spec/flujo-informacion.md) dice que la ambigüedad se deja escrita tal como la dijo el autor y se resuelve cuando una decisión lo exige, sin interrumpirlo. El test acepta las dos conductas y rechaza la que ambas prohíben: adivinar.

## Aceptación humana (en Obsidian)

- En `AHORA.md`, el registro de la Patricia se lee como lo habría escrito Andrea, y su link abre la página del liceo.
