# 003-08 · El mismo vault, otro arnés

> **Principio:** [P1 (texto operable a mano)](../../docs/principios.md#L9), [P5 (reglas en prosa)](../../docs/principios.md#L47) · **Brief:** [El agente y las herramientas](../../docs/brief.md#L60) · **Spec:** [`spec/despacho.md`](../../spec/despacho.md)

Verifica la portabilidad agéntica ejecutando el mismo dictado simple bajo un arnés alternativo (`hermes`) con perfil vacío, garantizando que el comportamiento operativo es gobernado por el `AGENTS.md` del vault y no por peculiaridades del modelo.

## Estado inicial

```bash
tuku init mi-vault --date 2026-08-11
```

## Escenario: otro agente, el mismo comando

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

- El resultado en `AHORA.md` es estructuralmente análogo al producido con el arnés principal, confirmando la autonomía del vault.
