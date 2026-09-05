# tests/ — cómo se prueba TUKU

> Esta suite es del diseño anterior a la reescritura de agosto de 2026 y se rehace (ver [`../devel/entorno-devel.md`](../devel/entorno-devel.md)). Documenta lo que hay en disco hoy, no lo que se está construyendo: eso vive en [`escenarios/`](escenarios/README.md).

## Estado

Esta suite (los archivos sueltos de este directorio) no corre todavía: importan un paquete `tuku` que ya no existe en `src/`. `tests/escenarios/` sí corre, aislada, con `tests/correr.sh`.

## Los cuatro niveles

| Nivel | Marcador | Qué prueba | Tokens |
|---|---|---|---|
| 1 | `spec` | ejemplos normativos de `spec/`, uno a uno | no |
| 2 | `invariante` | cada invariante, violándola a propósito | no |
| 3 | `aceptacion` | las simulaciones de `corpus/simulaciones/` | no |
| 4 | `replay` | reconstrucción con diff exactamente cero | no |
| — | `agentic` | lo que invoca un modelo | sí |

`agentic` está excluido por defecto (`uv run pytest -m agentic` para pedirlo).

## Archivos

| Archivo | Qué hace |
|---|---|
| `conftest.py` | fixtures: `perfil_tmp`, `hermes_efimero`, `assert_diff_cero` |
| `specref.py` | lee los bloques normativos y las invariantes directo de `spec/` |
| `test_coherencia_docs.py` | enlaces, anonimización, prefijos de invariante |
| `test_cobertura_specs.py` | qué invariantes tienen test y cuáles faltan |

## Los ejemplos salen de las specs, no de copias

`specref.py` lee los ejemplos del Markdown de `spec/` en vez de copiarlos a `fixtures/`: una copia se desincroniza. Un bloque se marca como caso ejecutable con un comentario antes:

```markdown
<!-- tuku:caso id=tarea-minima tipo=tarea -->
```

## Un test por invariante

El nombre codifica la invariante: `test_T6_tarea_en_dos_archivos_canonicos`. Ese prefijo es lo que permite a `test_cobertura_specs.py` saber qué está cubierto sin lista escrita a mano.

Al implementar una invariante, borrar su entrada de `PENDIENTES`: si se olvida, `test_la_lista_de_pendientes_no_miente` lo dice. Las invariantes negativas (K7, C3, P5) no llevan test — declaran que algo *no* es violación.

## Diff cero

`assert_diff_cero(perfil)` es el criterio del nivel 4: no "parecido", idéntico, medido con Git.

> Si algo que debería ser determinista solo pasa el test semántico, hay juicio del agente donde debería haber una regla.

## Escribir un test nuevo

1. Busca la regla en `spec/`. Si no está, escríbela ahí primero, no en el test.
2. Marca el nivel (`@pytest.mark.invariante`, etc.).
3. Usa `perfil_tmp` si necesita perfil. Nunca datos reales ni `~/.tuku`.
4. Inyecta la fecha si la necesita. Nada de `date.today()`.
