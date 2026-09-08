# Escenario · 001-02-init-siembra-el-estado-cero

**Cubre:** epic 001, fase 0, decididos #3 y #9 de [`../../devel/epics.md`](../../devel/epics.md).

## Escenario: `tuku init` produce el estado cero, byte a byte y sin red

Dado un directorio vacío
Cuando se corre

```bash
tuku init mi-vault --variant vanilla --date 2026-08-11
```

Entonces el árbol sembrado es idéntico a `template/vanilla/` salvo `AHORA.md`, sin que sobre ni falte ningún archivo
Y `AHORA.md` queda como el template con `desde`, `hasta` y los siete días resueltos
Y ningún archivo del vault conserva un placeholder (`AAAA-MM-DD`, `DD de mes`) fuera de un bloque de código
Y nada de esto necesitó la red

## Qué prueba, y qué no

Es la verificación byte a byte que antes hacía `test_001_01`, ahora sobre `tuku init` en vez de `install.sh`. Corre el comando con `TUKU_HOME` en el checkout, sin instalar nada: la decisión 4 del epic 002 reserva ese camino para todos los `001-00X` menos el `001-01`.

**No compara contra ninguna copia congelada del template.** El contraste es siempre contra `template/vanilla/` en vivo, y el `AHORA.md` esperado se deriva del template real aplicándole las siete fechas que el escenario escribe a mano, que es donde estuvo el bug (días etiquetados por posición, sin mirar el día real de `desde`). La consecuencia: el template puede cambiar todo lo que haga falta sin tocar el test; solo lo rompe un cambio en la forma de `AHORA.md` o en la lógica de sembrado.

La tercera afirmación cubre el crecimiento del template: si un archivo nuevo trae `DD de mes` y la siembra no lo sustituye, las otras dos pasan en silencio y esta no.

La fecha fija (2026-08-11, martes) es la del ground truth de `corpus/referencia/referencia-faena.md`. El usuario real siembra con la fecha de hoy; el test la fija para comparar byte a byte. No es lunes a propósito: nada en `spec/` obliga a que un ciclo semanal empiece en lunes.

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 001_02
```

Deja el vault en `playground/001-02-init-siembra-el-estado-cero/mi-vault/`, a la vista.

## Qué se mira a mano

- Abrir el resultado en Obsidian: sin cajas de error ni archivos que no sepa mostrar.
- Que `ambitos/personal/personal.md` se explique solo como el único ámbito de partida.
