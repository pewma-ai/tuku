# Escenario · 001-02-init-siembra-el-estado-cero

**Cubre:** epic 001, decisiones 3 y 9.

## Escenario: `tuku init` produce el estado cero, byte a byte y sin red

Dado un directorio vacío, y el módulo `socket` parchado para que abrir un socket, conectar o resolver un nombre lance
Cuando se corre

```bash
tuku init mi-vault --variant vanilla --date 2026-08-11
```

Entonces el árbol sembrado es idéntico a `template/vanilla/` salvo `AHORA.md`, `reglas/config.tuku.md` y `reglas/comandos.tuku.md`, sin que sobre ni falte ningún archivo
Y `reglas/comandos.tuku.md` dice, por cada comando, lo mismo que su `-h`: qué hace y cómo hacerlo a mano
Y `AHORA.md` queda como el template con `desde`, `hasta` y los siete días resueltos
Y ningún archivo del vault conserva un placeholder (`AAAA-MM-DD`, `DD de mes`) fuera de un bloque de código
Y nada de esto intentó tocar la red

## Notas

- Corre `tuku init` en proceso con `TUKU_HOME` en el checkout, sin instalar nada.
- Compara contra `template/vanilla/` en vivo, nunca contra una copia congelada. El `AHORA.md` esperado es el del template con las siete fechas escritas a mano en el test.
- La red se bloquea: `socket.socket`, `socket.create_connection` y `socket.getaddrinfo` lanzan `RedBloqueada`.
- La fecha fija (2026-08-11, martes) es la de [`corpus/referencia/referencia-faena.md`](../../corpus/referencia/referencia-faena.md). No es lunes a propósito: el ciclo sembrado es la semana que la contiene, del lunes 10 al domingo 16.

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 001_02
```

Deja el vault en `playground/001-02-init-siembra-el-estado-cero/mi-vault/`, a la vista.

## Qué se mira a mano

- Abrir el resultado en Obsidian: sin cajas de error ni archivos que no sepa mostrar.
- Que `ambitos/personal/personal.md` se explique solo como el único ámbito de partida.
