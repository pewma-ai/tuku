# Escenario · 001-04-init-author

**Cubre:** epic 001, fase 0, decidido #10 de [`../../devel/epics.md`](../../devel/epics.md), la capa de identidad mínima.

## Escenario: el nombre del autor queda en el libro de estilo

Dado un directorio destino vacío
Cuando se llama a `init(destino, autor="ARTURO PEREZ-REVERTE (Arturo)", home=RAIZ)`
Entonces `LIBRO-DE-ESTILO.md` queda con ese nombre en la sección "El autor"
Y no sobrevive el placeholder `por declarar`
Y el resto del vault queda completo, sin placeholders vivos

## Escenario: omitir el nombre deja el vault operable

Dado el mismo destino
Cuando se llama a `init()` sin `autor`, o con `autor` en blanco
Entonces la línea `**Nombre del autor:**` queda intacta con su texto de partida
Y el vault igual queda operable (principio 2: dejar el nombre en blanco no impide escribir)

## Por qué existe

`001-02` cubre la siembra byte a byte sin nombre. Este es la única cobertura del parámetro `autor` de `init()`.

Cambió respecto al cierre anterior: antes el nombre atravesaba `install.sh` (prompt por `/dev/tty`, `read`, `set --`, `--autor`) y el test lo ejercía con `pexpect`. Ahora `init()` es una función y el texto no pasa por ninguna capa de shell. El nombre elegido, con espacios, paréntesis y guion, se mantiene: verifica que el reemplazo por prefijo de línea de `_sembrar_autor` no lo parte ni toca la prosa que sigue al marcador.

Fecha fija 2026-08-11, la misma de `001-02`, para que el vault sea comparable con `diff -r` (salvo `LIBRO-DE-ESTILO.md`).

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 001_04
```

El caso con nombre deja el vault en `playground/001-04-init-author/`.

## Qué se mira a mano

- Abrir `LIBRO-DE-ESTILO.md` y ver el nombre **al inicio del documento**, en "El autor", sin buscarlo.
- Que quede claro, leyendo, que dejarlo en blanco es válido.
