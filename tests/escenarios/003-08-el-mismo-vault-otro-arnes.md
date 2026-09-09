# Escenario · 003-08-el-mismo-vault-otro-arnés

**Cubre:** epic 003, la afirmación que le da sentido a todo lo demás. Gemelo: el [`003-03`](003-03-un-hecho-un-comando.md), el mismo dictado con el otro arnés.

El entregable del epic no es que `agy` opere un vault. Es que **el `AGENTS.md` del vault haga que cualquier agente lo opere igual** ([`spec/despacho.md`](../../spec/despacho.md)). Con un solo arnés esa frase no se puede sostener: todo lo verde hasta acá es compatible con que el documento no diga nada y `agy` acierte por su cuenta.

Este escenario cambia el arnés y deja todo lo demás igual. Si el resultado es el mismo, la causa es el vault.

## Estado inicial

El mismo del [`003-03`](003-03-un-hecho-un-comando.md): un vault sembrado y vacío de registros.

```bash
tuku init mi-vault --date 2026-08-11
```

## El arnés

`hermes`, sobre un perfil creado para esto y **deliberadamente vacío**: sin skills, sin nada en su `SOUL.md` que hable de TUKU, con su propia base de sesiones. Un perfil que supiera de TUKU invalidaría el escenario por la misma puerta que un prompt de test que explique lo que el vault ya dice.

Lo elige el `.py` con `TUKU_AGENTE`, que es el mismo interruptor de siempre. El escenario no sabe de arneses; solo se corre con otro.

## Escenario: otro agente, el mismo comando

Dado un vault sembrado, cuya tabla de despacho ningún agente ha visto todavía
Cuando el autor dicta el hecho más simple posible

```agente
A las nueve y doce me di cuenta de que la administradora responde los mensajes con varios días de atraso.
```

Entonces la traducción es la misma que produjo el otro arnés

```text
tuku entry add --day 2026-08-11 --hour 09:12 --scope personal \
  --body "**<clasificación>**: <el cuerpo>"
```

Y queda un registro a las 09:12 en `[[personal]]`, sin ninguna marca de la ontología cerrada
Y el delta del vault es el mismo del gemelo determinista
Y ningún archivo se editó a mano

## Qué hace fallar y qué solo se reporta

**Falla:** exactamente lo mismo que en el `003-03`. Los criterios no se relajan porque cambie el arnés; si hubiera que relajarlos, el hallazgo sería que el `AGENTS.md` depende de quién lo lee.

**Se reporta:** la redacción del cuerpo y la clasificación abierta. Que dos arneses elijan clasificaciones distintas para el mismo hecho es información sobre el vocabulario del autor, no un defecto de ninguno de los dos.

## Qué se mira a mano

El archivo del turno, comparado **lado a lado** con el del `003-03`. Quedan los dos en `playground/`, con el arnés en el nombre, así que se leen juntos.

Lo interesante no es si acertaron, que lo afirma el `.py`. Es **en qué se diferencian**: qué exploró cada uno antes de escribir, si uno leyó el `AGENTS.md` y el otro no lo necesitó, si uno pidió ayuda del comando y el otro adivinó bien. Ahí está lo que el documento no dice y cada arnés está supliendo por su cuenta, que es lo que hay que escribirle.

Este arnés además entrega la sesión entera y no solo su respuesta final, así que en su archivo se ve el camino, no la conclusión.

## Por qué un solo hecho y no el día completo

El `003-06` cuesta once frases y varios minutos. Acá no se está midiendo la capacidad del agente, que ya se midió: se está midiendo si el vault manda igual sobre dos lectores distintos. El hecho más simple posible basta para eso, y si falla, falla por la razón correcta.

Si algún día un arnés pasa este y falla el `003-06`, ese es un hallazgo sobre el arnés y no sobre el documento.

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 003_08 -m "not red and not pendiente"
```
