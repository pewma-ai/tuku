# 003-09 · El mismo vault, tercer arnés

> **Principio:** [P1 (texto operable a mano)](../../docs/principios.md#L9), [P5 (reglas en prosa)](../../docs/principios.md#L47) · **Brief:** [El agente y las herramientas](../../docs/brief.md#L60) · **Spec:** [`spec/despacho.md`](../../spec/despacho.md)

Verifica la portabilidad agéntica ejecutando el mismo dictado simple bajo un tercer arnés (`claude`, con sonnet en esfuerzo bajo), garantizando que el comportamiento operativo es gobernado por el `AGENTS.md` del vault y no por peculiaridades del modelo.

El [`003-08`](003-08-el-mismo-vault-otro-arnes.md) ya sostiene la afirmación en dos arneses. Este agrega el caso que más se le parece a la forma en que el autor trabaja a diario, y el único de los tres que **no descubre solo** el documento del vault: `claude` busca `CLAUDE.md` y no `AGENTS.md`, así que el arnés le antepone un preámbulo que dice dónde mirar, no qué dice. Si el `AGENTS.md` no alcanzara, el turno fallaría igual.

## Estado inicial

```bash
tuku init mi-vault --date 2026-08-11
```

## Escenario: un tercer agente, el mismo comando

Dado un vault recién sembrado
Cuando el autor dicta el hecho más simple
```agente
A las nueve y doce me di cuenta de que la administradora responde los mensajes con varios días de atraso.
```
Entonces la traducción coincide con la obtenida en el arnés de referencia
```text
tuku entry add --day 2026-08-11 --hour 09:12 --scope personal \
  --body "**<clasificación>**: <el cuerpo>"
```
Y queda un registro a las 09:12 en `[[personal]]` sin marcas ontológicas cerradas
Y el delta del vault es idéntico al gemelo determinista
Y ningún archivo se edita a mano

## Aceptación humana (en Obsidian)

- El resultado en `AHORA.md` es estructuralmente análogo al producido con los arneses `agy` y `hermes`, confirmando que el vault manda sobre los tres.
