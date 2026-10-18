# 003-09 · El mismo vault, tercer arnés

> **Principio:** [P1 (texto operable a mano)](../../docs/principios.md#L9), [P5 (reglas en prosa)](../../docs/principios.md#L47) · **Brief:** [El agente y las herramientas](../../docs/brief.md#L60) · **Spec:** [`spec/despacho.md`](../../spec/despacho.md)

Verifica la portabilidad agéntica ejecutando el mismo dictado simple bajo un tercer arnés (`claude`, con sonnet en esfuerzo bajo), garantizando que el comportamiento operativo es gobernado por el `AGENTS.md` del vault y no por peculiaridades del modelo.

`claude` no descubre solo el documento del vault (busca `CLAUDE.md`, no `AGENTS.md`), así que el arnés le antepone un preámbulo que dice dónde mirar, no qué dice. Si el `AGENTS.md` no alcanzara, el turno fallaría igual.

El turno del agente declara `TUKU_NOW="2026-08-11 22:00"` en el fence ```agente```: el `tuku` que el agente ejecuta usa esa fecha como hoy y la anuncia por `stderr`. Así el agente y el escenario viven en el mismo día.

## Estado inicial

```bash
tuku init mi-vault --at 2026-08-11
```

## Escenario: un tercer agente, el mismo comando

Dado un vault recién sembrado
Cuando el autor dicta el hecho más simple
```agente TUKU_NOW="2026-08-11 22:00"
A las nueve y doce me di cuenta de que la administradora responde los mensajes con varios días de atraso.
```
Entonces la traducción coincide con la obtenida en el arnés de referencia
```text
tuku entry create --at "2026-08-11 09:12" --scope personal \
  --body "**<clasificación>**: <el cuerpo>"
```
Y queda un registro a las 09:12 en `[personal](ambitos/personal/personal.md)` sin marcas ontológicas cerradas
Y el delta del vault es idéntico al gemelo determinista
Y ningún archivo se edita a mano

## Aceptación humana (en Obsidian)

- El resultado en `AHORA.md` es estructuralmente análogo al producido con los arneses `agy` y `hermes`, confirmando que el vault manda sobre los tres.
