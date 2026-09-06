# tests/escenarios

Un escenario es una historia en formato Dado/Cuando/Entonces con su arnés al lado: `001-001-instalacion-minima.md` es el caso, `test_001_001_instalacion_minima.py` lo ejecuta.

Son narrativos y no unitarios porque buena parte de TUKU depende de un agente y no da un resultado único. Lo que se puede verificar con un `assert` vive en el `.py`; lo que solo se puede juzgar leyendo el resultado queda escrito en el `.md` bajo "Qué se mira a mano", y no se finge que un test lo cubre.

Un escenario referencia `spec/` pero no lo reemplaza. Si un escenario contradice `spec/`, se corrige `spec/` (ver [`../../devel/epics.md`](../../devel/epics.md), "los epics mueven el diseño"), no el escenario.

**Todo test que instale un vault lo deja en `playground/<XXX-YYY-slug>/`, la carpeta propia de ese escenario.** Es regla y no preferencia: el vault resultante existe para que el autor lo revise a mano, y un test que lo bota a un tempdir le quita esa revisión. El arnés instala ahí directo, no en un tempdir que se descarta, de modo que correr `uv run pytest tests/escenarios/` deja cada corrida a la vista para el `## Qué se mira a mano` del escenario. Se pisa cada vez que se vuelve a correr, y `playground/` está en `.gitignore`, así que nada de esto se versiona. El arnés borra y recrea **solo su propia subcarpeta**, nunca `playground/` completo ni ninguna otra carpeta dentro: las corridas manuales exploratorias que uno deje en `playground/` con otro nombre sobreviven a `uv run pytest`. El alcance de la regla es ese y no otro: un test que **no produce un vault** simplemente no cae bajo ella. El `001-003` prueba que `install.sh` se niega a sobrescribir y no llega a instalar nada, así que sus tempdirs son correctos.

No hay problema en que esto crezca a cientos de archivos chicos: son texto, cuestan casi nada.

Esta suite se escribe desde cero: la del diseño anterior se borró entera.

## Convención de nombre

`XXX-YYY-slug`, donde `XXX` es el epic al que pertenece el escenario y `YYY` su orden dentro de ese epic, ambos con tres dígitos. Así `001-002-instalacion-local` es el segundo escenario del epic 001.

Tres dígitos y no dos por una razón sola: que ordenar alfabéticamente sea ordenar de verdad, hoy y con cien escenarios. El número dice de dónde salió el escenario, no en qué orden conviene leerlo, así que no se renumera cuando cambia el orden de trabajo.

El mismo par nombra las tres cosas: el caso (`XXX-YYY-slug.md`), el arnés (`test_XXX_YYY_slug.py`, con guiones bajos porque es un módulo de Python) y la corrida desechable (`playground/XXX-YYY-slug/`).

## Fixtures

`fixtures/XXX-YYY-slug/`, con guiones, porque es un directorio de datos y no un módulo. Hoy no hay ninguno, y no es un descuido.

**Nada que provenga de `template/` se congela.** Congelar una copia paralela de algo que nunca debería diferir obliga a regenerarla a mano cada vez que cambia el original, y convierte cada cambio del template en un test roto que no señala ningún defecto. El árbol instalado se compara en vivo contra `template/<variante>/`, y lo que el instalador transforma se deriva del template aplicándole el resultado que el escenario afirma a mano.

El epic 001 empezó con un fixture de `AHORA.md` y se eliminó por esto mismo: congelaba también el frontmatter fijo y el título, que el instalador no toca.

Un fixture se justifica cuando la entrada no sale del repositorio (un dictado, una respuesta de agente, un archivo que el autor trajo de afuera). Ahí no hay original vivo contra el cual comparar, y congelar es la única opción.

## Convención de formato

```markdown
# Escenario · <nombre>

**Cubre:** qué fase o epic valida.

## Escenario: <lo que se está probando>

Dado <estado inicial>
Cuando <la acción>
Entonces <lo que debería ser cierto>

## Cómo se corre

Comando para reproducirlo en `playground/`.

## Qué se mira a mano

Lo que ningún script puede verificar todavía, y hay que juzgar leyendo el resultado.
```

## Cómo correr

El nombre del test ya es el tag: `-k` de pytest filtra por él, con guion bajo (no guion, que no encuentra nada y no avisa).

```bash
uv run pytest tests/escenarios/            # todo
uv run pytest tests/escenarios/ -k 001      # un epic
uv run pytest tests/escenarios/ -k 001_002  # un escenario
```

## Índice

| Escenario | Cubre | Notas |
| --- | --- | --- |
| [`001-001-instalacion-minima.md`](001-001-instalacion-minima.md) | Epic 001, fase 0 | El camino completo: `curl` contra GitHub |
| [`001-002-instalacion-local.md`](001-002-instalacion-local.md) | Epic 001, fase 0 | El mismo mecanismo, sin red ni git, para iterar rápido |
| [`001-003-destino-no-vacio.md`](001-003-destino-no-vacio.md) | Epic 001, fase 0 | `install.sh` no sobrescribe sin preguntar, salvo `TUKU_FORCE=1`; el único de los tres que prueba `install.sh` mismo, no `instalar()`. Usa `pexpect` para simular la respuesta a un prompt que lee `/dev/tty` |
| [`001-004-instalador-pregunta-el-nombre.md`](001-004-instalador-pregunta-el-nombre.md) | Epic 001, fase 0 | La capa de identidad de punta a punta: se responde el nombre en el prompt de `install.sh` y queda en `LIBRO-DE-ESTILO.md`. Instala desde `TUKU_ORIGEN`, sin red, y es el único que deja completar la instalación |
