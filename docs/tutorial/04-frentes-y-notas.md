# 4. Frentes y notas

> Separar tu vida en frentes y guardar lo que sabes de una persona.

El **día** guarda lo que pasó. Un **frente** (ámbito) dice de qué trata cada cosa, y una **nota** guarda lo que sabes. Son tres ejes distintos ([principio 6](../principios.md)).

## Un frente nuevo

Abre `AHORA.md`: todo cayó en `personal`, el único frente de un vault recién instalado.

> [!tip] Dile a tu agente
> Colegio Los Robles es un cliente, ábrelo como un frente aparte.

El agente te va a preguntar qué palabras, al mencionarlas, indican que algo es de ese frente.

> [!tip] Respóndele
> Rodolfo, Cifuentes y Los Robles.

> [!check] Qué debería pasar
> - Existe `ambitos/colegio-los-robles/colegio-los-robles.md`.
> - Su línea `keywords` dice `[rodolfo, cifuentes, los-robles]`, en minúsculas y con guiones.
> - `AHORA.md` tiene el registro `**nota**: abrí el ámbito` con `[colegio-los-robles](…)`. Lo que ya habías escrito sigue en `personal`: abrir un frente no cambia nada de lo anterior.

Las **keywords** son las palabras que delatan un frente sin nombrarlo. Gracias a ellas, más adelante dices «hablé con don Rodolfo» y el registro cae en el frente correcto. Deciden el frente de lo que dictes de ahí en adelante. Lo que ya está escrito se queda donde está, salvo que pidas moverlo («ese registro era de Los Robles»).

> [!tip] Un segundo cliente
> Liceo Andes también es un cliente. Sus palabras son Patricia y Lillo.

> [!check] Qué debería pasar
> - Existe `ambitos/liceo-andes/liceo-andes.md` con `keywords: [patricia, lillo]`.

## Una ficha de persona

> [!tip] Dile a tu agente
> Guárdame una ficha de don Rodolfo Cifuentes, administrador de Los Robles. Compran para el segundo semestre y le importa más el plazo de entrega que el precio. Le dicen don Rodolfo.

> [!check] Qué debería pasar
> - Existe `notas/rodolfo-cifuentes.md` con `subtype: persona` y `aliases` que incluye «don Rodolfo».
> - La nota termina con `## Ver además`, que enlaza al frente `colegio-los-robles` con su motivo.
> - `AHORA.md` tiene el registro de que creaste la nota.

El tipo `persona` sale de `reglas/notas.user.md`. La nota guarda lo que sabes de Rodolfo, y el registro, que la creaste hoy. Consultas la ficha en marzo sin releer agosto.

## Una mención con link

> [!tip] Dile a tu agente
> Llamó don Rodolfo de nuevo: quiere la entrega antes del día 15.

> [!check] Qué debería pasar
> - El registro cayó en `colegio-los-robles` sin que lo nombraras.
> - «don Rodolfo» es un link a `notas/rodolfo-cifuentes.md`, con el texto que dijiste.

El agente encontró la ficha en lo que `tuku context` le mostró al empezar. Ningún comando enlaza por su cuenta.

Siguiente: [5. Corregir y revisar](05-corregir-y-revisar.md).
