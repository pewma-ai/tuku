# tests/escenarios

Un escenario es una historia en formato Dado/Cuando/Entonces con su arnés al lado: `001-01-instalacion-minima.md` es el caso, `test_001_01_instalacion_minima.py` lo ejecuta.

Son narrativos y no unitarios porque buena parte de TUKU depende de un agente y no da un resultado único. Lo que se puede verificar con un `assert` vive en el `.py`; lo que solo se puede juzgar leyendo el resultado queda escrito en el `.md` bajo "Qué se mira a mano", y no se finge que un test lo cubre.

Un escenario referencia `spec/` pero no lo reemplaza. Si un escenario contradice `spec/`, se corrige `spec/` (ver [`../../devel/epics.md`](../../devel/epics.md), "los epics mueven el diseño"), no el escenario.

**Todo test que instale un vault lo deja en `playground/<XXX-YY-slug>/`, la carpeta propia de ese escenario.** Es regla y no preferencia: el vault resultante existe para que el autor lo revise a mano, y un test que lo bota a un tempdir le quita esa revisión. El arnés instala ahí directo, no en un tempdir que se descarta, de modo que correr `uv run pytest tests/escenarios/` deja cada corrida a la vista para el `## Qué se mira a mano` del escenario. Se pisa cada vez que se vuelve a correr, y `playground/` está en `.gitignore`, así que nada de esto se versiona. El arnés borra y recrea **solo su propia subcarpeta**, nunca `playground/` completo ni ninguna otra carpeta dentro: las corridas manuales exploratorias que uno deje en `playground/` con otro nombre sobreviven a `uv run pytest`. El alcance de la regla es ese y no otro: un test que **no produce un vault** simplemente no cae bajo ella. El `001-03` (caso "se niega"), el `001-01` (que instala en un `HOME` de tempdir) y el `001-06` (que solo inspecciona la ayuda) no producen un vault revisable en `playground/`, así que no caen bajo la regla.

No hay problema en que esto crezca a cientos de archivos chicos: son texto, cuestan casi nada.

Esta suite se escribe desde cero: la del diseño anterior se borró entera.

Los escenarios `001-0X` prueban el modelo `pipx` + `tuku init` (epic 001 reabierto el 2026-09-07, decisión 4 del epic 002). Salvo `001-01`, que instala de verdad y va marcado `red`, todos corren sin red ni instalación: `001-02`..`001-05` llaman a `tuku.init.init()` con `home=` apuntando al checkout, y `001-06` llama a `tuku.cli.main` para fijar la ayuda del CLI.

## Convención de nombre

`XXX-YY-slug`, donde `XXX` es el epic al que pertenece el escenario y `YY` su orden dentro de ese epic. Así `001-02-instalacion-local` es el segundo escenario del epic 001.

Tres dígitos para el epic y dos para el escenario, por lo que se espera de cada uno: epics va a haber muchos, y ningún epic va a llegar a cien escenarios. Lo que importa es que el ancho sea fijo, para que ordenar alfabéticamente sea ordenar de verdad. El número dice de dónde salió el escenario, no en qué orden conviene leerlo, así que no se renumera cuando cambia el orden de trabajo.

El mismo par nombra las tres cosas: el caso (`XXX-YY-slug.md`), el arnés (`test_XXX_YY_slug.py`, con guiones bajos porque es un módulo de Python) y la corrida desechable (`playground/XXX-YY-slug/`).

## Fixtures

`fixtures/XXX-YY-slug/`, con guiones, porque es un directorio de datos y no un módulo.

**Nada que provenga de `template/` se congela.** Congelar una copia paralela de algo que nunca debería diferir obliga a regenerarla a mano cada vez que cambia el original, y convierte cada cambio del template en un test roto que no señala ningún defecto. El árbol instalado se compara en vivo contra `template/<variante>/`, y lo que el instalador transforma se deriva del template aplicándole el resultado que el escenario afirma a mano.

El epic 001 empezó con un fixture de `AHORA.md` y se eliminó por esto mismo: congelaba también el frontmatter fijo y el título, que el instalador no toca.

### El fixture se genera desde el corpus, no se copia

Lo que un escenario inyecta sale de [`../../corpus/referencia/`](../../corpus/README.md), **generado por un agente LLM avanzado**, adaptado a lo que ese escenario prueba. Adaptado en dos ejes:

1. **El tamaño es variable del test.** Probar una primitiva pide el mínimo: tres registros si bastan tres. Probar si el agente o el comando se distraen pide muchos, casi todos ruido. El mismo escenario puede tener las dos versiones.
2. **El dominio se elige.** Un escenario de cadencias genera desde pyme, porque faena no declara ninguna.

Copiar literal amarra el test a un texto que el corpus puede cambiar, y le entrega al agente el ejemplo que después se le pide reproducir.

### Qué sí se congela

Solo la **salida de un agente** que otros escenarios consumen: no hay original vivo contra el cual comparar. El dictado de entrada no, que se genera.

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
uv run pytest tests/escenarios/ -k 001_02  # un escenario
```

## Índice

| Escenario | Cubre | Notas |
| --- | --- | --- |
| [`001-00-un-tuku-minimo-instalable.md`](001-00-un-tuku-minimo-instalable.md) | Epic 001 | Descripción general, entregable, decisiones y criterios de salida del Epic 001 |
| [`001-01-instalacion-con-uv-tool.md`](001-01-instalacion-con-uv-tool.md) | Epic 001, fase 0 | El único que instala de verdad: `uv tool install` desde `git+...@devel`. Marcado `red`, fuera de la corrida por defecto |
| [`001-02-init-siembra-el-estado-cero.md`](001-02-init-siembra-el-estado-cero.md) | Epic 001, fase 0 | La verificación byte a byte de `tuku init` contra `template/vanilla/` en vivo, con `home` local y sin red |
| [`001-03-destino-no-vacio.md`](001-03-destino-no-vacio.md) | Epic 001, fase 0 | `init()` se niega a sembrar sobre contenido; `--force` reemplaza. Ahora es un flag, sin prompt ni pty |
| [`001-04-init-author.md`](001-04-init-author.md) | Epic 001, fase 0 | La capa de identidad: `init(autor=...)` deja el nombre en `LIBRO-DE-ESTILO.md`; omitirlo o vaciarlo deja el vault operable |
| [`001-05-init-no-toca-la-red.md`](001-05-init-no-toca-la-red.md) | Epic 001, fase 0 | Con el socket parchado para fallar, `tuku init` completa igual. Aísla la afirmación "offline" |
| [`001-06-cli-ayuda.md`](001-06-cli-ayuda.md) | Epic 001, fase 0 | `tuku -h` y `tuku init -h` nombran lo que el epic añadió. En proceso, sin red ni disco. Convención "la ayuda se prueba en cada epic" |
| [`001-07-lint-libro-de-estilo.md`](001-07-lint-libro-de-estilo.md) | Epic 001, fase 0 | Contratos de `LIBRO-DE-ESTILO.md` (marcador de autor y encabezados de tablas). Todo rechazo nombra defecto y corrección |
| [`002-00-el-dia-uno-a-mano.md`](002-00-el-dia-uno-a-mano.md) | Epic 002 | Descripción general, qué tiene que funcionar, qué se verifica y movimientos de diseño del Epic 002 |
| [`002-01-abrir-ciclo.md`](002-01-abrir-ciclo.md) | Epic 002, fase 1 | Primer paso de la cadena. Apertura de ciclo a partir de plantilla en `reglas/plantilla/AHORA.md` con la semana completa |
| [`002-02-registro-en-su-dia.md`](002-02-registro-en-su-dia.md) | Epic 002, fase 1 | Segundo paso de la cadena. Día correcto, orden cronológico, y el diff no toca `PENDIENTES.md` |
| [`002-03-lint-de-registro.md`](002-03-lint-de-registro.md) | Epic 002, fase 1 | Cerrada estricta, abierta permisiva. El lint informa y no escribe |
| [`002-04-abrir-pendiente.md`](002-04-abrir-pendiente.md) | Epic 002, fase 2 | Abrir es copiar el cuerpo literal. Lleva un `#REVISAR` sobre una ambigüedad de `spec/pendientes.md` |
| [`002-05-cerrar-pendiente.md`](002-05-cerrar-pendiente.md) | Epic 002, fase 2 | Cerrar es borrar, y el cierre sin pareja se reporta sin inventar nada |
| [`002-06-escribir-en-un-dia-fecha.md`](002-06-escribir-en-un-dia-fecha.md) | Epic 002, fase 2 | El punto 3 del epic: agendar es escribir donde corresponde. Fechar mueve, nunca copia |
| [`002-07-transclusiones-sincronizadas.md`](002-07-transclusiones-sincronizadas.md) | Epic 002, fase 2 | Las dos direcciones de falla, por la segunda vía. La silenciosa es la que justifica el comando |
| [`002-08-crear-ambito.md`](002-08-crear-ambito.md) | Epic 002, fase 3 mínima | El árbol correcto y el enlazado retroactivo, que acá llega solo hasta `AHORA.md` |
| [`002-09-crear-nota.md`](002-09-crear-nota.md) | Epic 002, fase 5 mínima | Obliga a agregar la consecuencia "nota" a `spec/flujo-informacion.md` |
| [`002-10-cli-superficie.md`](002-10-cli-superficie.md) | Epic 002 | Fuera de la cadena: nouns y verbs en `-h`, códigos de salida, y el barrido de que todo error nombre la corrección |
| [`003-00-el-dia-uno-dictado.md`](003-00-el-dia-uno-dictado.md) | Epic 003 | Descripción general, compilación de dictado a comandos y decisiones previas del Epic 003 |
| [`003-01-dictado-del-dia-uno.md`](003-01-dictado-del-dia-uno.md) | Epic 003 | El agente compila el dictado en llamadas `tuku`. Gasta tokens, fuera de la corrida por defecto |
| [`003-02-propuesta-no-escribe.md`](003-02-propuesta-no-escribe.md) | Epic 003 | El principio 3 con el agente en el circuito: propone y no escribe, y rechazarla no deja rastro |

## Escenarios encadenados, desde el epic 002

El orden lo fija [`../../devel/epics.md`](../../devel/epics.md), "El orden, siempre el mismo". La cadena es la forma que toma acá.

Dentro de un epic, **el estado inicial de un escenario es el estado final del anterior**. El primero parte del fixture con el que el epic empieza (`vacio` para el 002) y el último deja el fixture con el que empieza el epic siguiente. Es la escalera de [`../../devel/epics.md`](../../devel/epics.md) bajada de grano: los estados intermedios no se escriben a mano ni se congelan, se reproducen corriendo la cadena.

Tres consecuencias prácticas:

1. **El assert es el diff entre dos estados**, no una comparación de árbol completo. Así se ven los efectos colaterales que un assert por archivo no mira, y la idempotencia sale gratis: el segundo pase de una operación tiene que dar diff vacío.
2. **Cada paso deja su propio snapshot** en `playground/<XXX-YY-slug>/`, copiando el estado heredado antes de operar. La regla del playground no cambia, y la revisión a mano pasa a ser `diff -r` entre dos carpetas consecutivas.
3. **Un paso que falla salta los siguientes en vez de reprobarlos**, y correr uno suelto con `-k` reproduce la cadena desde el estado inicial del epic. Es barato porque el tramo entero es determinista: el único escenario con LLM va al final, fuera de la cadena, y su salida se congela como fixture.

> [!question] Pendiente de decisión #REVISAR
> Con cadena, el `YY` pasa a ser **orden de ejecución** dentro del epic, y eso contradice la sección "Convención de nombre" de más arriba, que dice que el número no es orden de lectura y que no se renumera. Queda sin resolver a propósito: es una regla del repositorio, no del epic.
