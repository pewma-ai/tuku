# 8. Una semana después

> El agente entiende de qué hablas con el historial, y pregunta cuando dos cosas calzan.

Con semanas de uso hay historial: frentes, notas, pendientes. Al empezar, el agente lee un resumen de todo eso (`tuku context`) y lo usa para ubicar lo que dices. Puedes seguir en el mismo vault: con menos historia funciona igual.

Para el segundo caso, guarda antes dos fichas con el mismo apodo:

> [!tip] Dile a tu agente
> Guárdame una ficha de la señora Patricia Lillo, compradora del Liceo Andes. Le dicen la Patricia.
>
> Guárdame otra de Patricia Soto, de la imprenta que hace mis etiquetas. A ella también le dicen la Patricia.

> [!check] Qué debería pasar
> - Existen `notas/patricia-lillo.md` y `notas/patricia-soto.md`, ambas con `subtype: persona` y el alias `la Patricia`.

## Elegir el frente sin que lo nombres

> [!tip] Dile a tu agente, sin más contexto
> Hablé con don Rodolfo del precio y quedó conforme.

> [!check] Qué debería pasar
> - El registro cayó en `los-robles`, porque «Rodolfo» es una de sus keywords.
> - «don Rodolfo» es un link a su ficha, con tu texto.
> - No se agregó el apellido, el colegio ni el precio: el registro dice lo que dijiste.

## Un nombre que calza con dos

> [!tip] Ahora un caso ambiguo
> Hablé con la Patricia del precio.

> [!check] Qué debería pasar
> - El agente pregunta a cuál te refieres, la del Liceo Andes o la de la imprenta, y no escribe nada hasta que contestes.

> [!tip] Respóndele
> La del Liceo Andes.

> [!check] Qué debería pasar
> - El registro cayó en `liceo-andes`, y «la Patricia» es un link a `notas/patricia-lillo.md`.

Asumir en silencio la opción más reciente deja registros erróneos en un historial que casi nadie audita.

## Lo atrasado

Cuando ya haya vencido algún pendiente, pregunta:

> [!tip] Dile a tu agente
> ¿Qué tengo atrasado?

> [!check] Qué debería pasar
> - El agente lista los pendientes cuyo `Vence` ya pasó, del más antiguo al más reciente.
> - Ningún archivo cambió.

Un atraso es información, no una orden: TUKU no corre un compromiso por su cuenta. Tú decides si lo cumples, lo pospones o lo cierras.

Siguiente: [9. Cerrar la semana](09-cerrar-la-semana.md).
