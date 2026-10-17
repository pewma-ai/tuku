# tests/escenarios

Un escenario es una historia en formato Dado/Cuando/Entonces con su arnés al lado: `001-01-instalacion-minima.md` es el caso, `test_001_01_instalacion_minima.py` lo ejecuta.

**Los escenarios son pruebas de extremo a extremo (E2E) de cara al usuario.** Los tests unitarios prueban módulos y funciones puras de forma aislada; los tests de escenario **deben usar siempre el comando `tuku`** (la superficie CLI mediante `main(argv)` o proceso), nunca llamadas directas a funciones internas. Solo ejecutando el comando completo se garantizan sus efectos colaterales reales (propagación de vistas, creación de archivos, reporte de errores y códigos de salida).

Son narrativos y no unitarios porque buena parte de TUKU depende de un agente y no da un resultado único. Lo que se puede verificar con un `assert` vive en el `.py`; lo que solo se puede juzgar leyendo el resultado queda escrito en el `.md` bajo "Qué se mira a mano", y no se finge que un test lo cubre.

Un escenario referencia `spec/` pero no lo reemplaza. Si un escenario contradice `spec/`, se corrige `spec/` (ver [`../../devel/epics.md`](../../devel/epics.md), "los epics mueven el diseño"), no el escenario.

**Todo test que instale un vault lo deja en la carpeta propia de ese escenario, y esa carpeta vive en dos lugares.** Se corre en `/tmp/tuku-banco/<XXX-YY-slug>/`, fuera del checkout, y al terminar el escenario el resultado se copia a `playground/<XXX-YY-slug>/`, que es donde el autor lo revisa. La separación no es comodidad: un vault dentro del repo hereda el árbol de arriba, y un agente que resuelve su proyecto por repositorio y no por `cwd` escribe en otra parte o no escribe nada. Lo que sí es regla y no preferencia es que el resultado quede a la vista y no en un tempdir que se descarta, de modo que correr `uv run pytest tests/escenarios/` deja cada corrida disponible para el `## Qué se mira a mano` del escenario. Se pisa cada vez que se vuelve a correr, y `playground/` está en `.gitignore`, así que nada de esto se versiona. El borrado lo hace el `XXX-00` del epic, una sola vez por corrida (ver abajo), y alcanza solo a `playground/XXX-*`: las corridas manuales exploratorias que uno deje con otro nombre sobreviven a `uv run pytest`. El alcance de la regla es ese y no otro: un test que **no produce un vault** simplemente no cae bajo ella. El `001-01` (que instala en un `HOME` de tempdir) y el `001-06` (que solo inspecciona la ayuda) no producen un vault revisable, así que no caen bajo la regla.

No hay problema en que esto crezca a cientos de archivos chicos: son texto, cuestan casi nada.

Esta suite se escribe desde cero: la del diseño anterior se borró entera.

Los escenarios `001-0X` prueban el modelo `pipx` + `tuku init` (epic 001 reabierto el 2026-09-07, decisión 4 del epic 002). Salvo `001-01`, que instala de verdad por sus tres vías y va marcado `red`, todos corren sin red ni instalación: el runner ejecuta sus comandos `tuku` en proceso con `TUKU_HOME` apuntando al checkout.

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

## Convención de formato BDD

Cada archivo `.md` de escenario se redacta bajo un estándar Behavior-Driven Development (BDD) conciso, sin grasa narrativa y con trazabilidad estricta:

```markdown
# XXX-YY · <Nombre del comportamiento>

> **Principio:** [P...](../../docs/principios.md) · **Brief:** [Sección](../../docs/brief.md) · **Spec:** [spec/...](../../spec/README.md) · **Origen:** [lección](../../devel/lecciones-macjpgil.md)

<Una sola frase clara que resume qué problema resuelve al autor o qué fricción elimina>.

## Estado inicial

```bash
<comandos que preparan el estado inicial o cp -r de herencia>
```

## Escenario: <lo que se está probando>

Dado <precondición del vault>
```bash
<comandos de precondición, si aplica>
```
Cuando <acción o comando ejecutado>
```bash
<el comando tuku exacto>
```
Entonces <resultado observable en el vault o salida>
Y <aserciones adicionales o idempotencia>

## Aceptación humana (en Obsidian)

- <Qué debe verificar una persona leyendo directamente el archivo en Obsidian para asegurar legibilidad a 20 años y naturalidad del flujo>.
```

**Reglas de estilo en escenarios:**
- **Sin grasa narrativa:** No incluir bloques de *"Por qué existe"*, *"De dónde salen las líneas"* ni comandos de ayuda de *"Cómo se corre"* con pytest (el runner corre automáticamente).
- **Trazabilidad obligatoria:** Todo escenario debe enlazar explícitamente a los principios, al brief y a las especificaciones.
- **Aceptación humana declarada:** Declarar qué se inspecciona con ojos humanos en Obsidian para validar que el Markdown resultante es limpio, natural y legible.

## El `.md` es la fuente ejecutable

El comando de un escenario se escribía dos veces, en prosa acá y en Python en el arnés, y las dos copias divergían en silencio. Ya no: [`../scripts/gherkin.py`](../scripts/gherkin.py) lee este `.md`, corta por `## Escenario:` y ejecuta sus bloques `bash`. El arnés queda con lo único que el texto no puede expresar, las aserciones sobre el resultado:

```python
def test_001_03_destino_no_vacio_se_niega_y_no_toca_nada() -> None:
    corrida = gherkin.correr(SLUG, "no sembrar sobre un directorio que ya tiene algo")
    assert corrida.codigo == RECHAZO
    assert "--force" in corrida.stderr
```

Un `.md` que cambia su comando cambia lo que el test corre. No hay forma de que el texto y el arnés se contradigan.

| Paso | Forma | Qué hace el runner |
| --- | --- | --- |
| `Dado` | prosa, o bloque `bash` cuando el estado inicial se construye con comandos | lo ejecuta; si falla, aborta, porque el `Cuando` ya no probaría lo que el escenario dice |
| `Cuando` | siempre un bloque `bash` | lo ejecuta y guarda código de salida, stdout y stderr para el arnés. Un código distinto de cero **no** aborta: hay escenarios cuyo tema es el rechazo |
| `Entonces` | prosa; bloque `bash` cuando el comando **es** la aserción (`tuku doctor`, `diff -r`) | si lleva comando, exige que salga cero |

`Y` y `Pero` continúan el paso anterior y heredan su tipo. Todo lo que viene después de un encabezado que no sea `## Escenario:` es documentación y no se ejecuta, así que el bloque de `## Cómo se corre` no corre dos veces.

Una línea `cd <dir>` cambia el directorio de los comandos que la siguen en el escenario, como en una terminal: tras `cd mi-vault`, `tuku todo open` no necesita `--vault`. Una línea que empieza con `tuku` se ejecuta **en proceso** (`cli.main`): es rápida, comparte intérprete con el test y por eso el `001-02` puede parchar `socket` alrededor. Cualquier otra línea va por `bash`, que es como entran `mkdir`, `grep` o `diff -r` sin caso especial.

### El escenario se lee como lo que hace una persona

El texto no lleva `TUKU_HOME=`, ni rutas de `playground/`, ni banderas que solo existen para el test. Escribe `tuku init mi-vault --at 2026-08-11` y nada más. Lo que el test necesita lo pone el runner alrededor: ejecuta con el directorio de trabajo en el banco de `/tmp`, así que `mi-vault` cae en un árbol aislado, y al terminar lo copia a `playground/<slug>/` para el `## Qué se mira a mano`, y apunta `TUKU_HOME` al checkout, así que la siembra copia de `template/` sin instalar nada.

Un `.md` con varios `## Escenario:` reparte un subdirectorio por escenario (`playground/001-03-destino-no-vacio/force-siembra-igual/`), y el nombre sale del título recortado a treinta caracteres por palabra completa, porque esa ruta se escribe a mano en los `cp -r` de la cadena. Dos escenarios de un mismo `.md` que colisionen en esos treinta caracteres empiezan igual, y lo que hay que arreglar es el título. Si los tres casos del `001-03` compartieran carpeta solo sobreviviría el último, y no habría nada que mirar a mano de los otros dos.

### La cadena se hereda con un `cp`, a la vista

El estado inicial de un paso es el estado final del anterior, y eso se escribe en el `## Estado inicial`, que hace de *Background*: sus comandos corren antes de cada escenario del archivo.

```bash
cp -r ../../002-13-el-dia/repetir-el-dia-no-cambia-nada/mi-vault .
```

Antes la herencia vivía escondida en una constante `PREVIO` del arnés. Ahora se lee en el escenario. Si el paso previo no corrió, el error lo dice con esas palabras en vez de un `cp: No such file`.

El runner toma la instantánea del directorio justo antes del primer `Cuando`, así que `corrida.delta` y `corrida.delta_de("mi-vault")` dicen qué cambió: el assert es el diff entre dos estados, que es lo que pide la sección "Escenarios encadenados" más abajo.

**Un escenario se corre una vez por sesión.** Varios tests pueden afirmar cosas distintas sobre el mismo, y `gherkin.correr` devuelve la corrida ya hecha en vez de repetirla: rehacerla sería pisar el resultado que el autor va a mirar a mano.

### El `XXX-00` prepara el ambiente del epic

El primer documento de cada epic, que ya describía su alcance, lleva además un `## Escenario: preparar el ambiente del epic` con un solo comando:

```bash
rm -rf 001-*
```

Es el único borrado del epic. Antes cada arnés borraba su propia carpeta antes de usarla, y con varios tests por escenario eso daba más de cien borrados por corrida: una pelea con el sistema de archivos que hacía fallar tests que no tenían nada que ver. Ahora se limpia una vez, al principio, y desde ahí cada escenario solo crea.

Se dispara sola la primera vez que un test del epic pide una carpeta, así que correr un escenario suelto con `-k` limpia igual que la corrida completa. El patrón es el prefijo del epic, de modo que `playground/001-*` es territorio de la suite: una carpeta propia que empiece con `001-` se borra, y cualquier otra sobrevive.

### Los pasos agénticos

Lo que le dices a un agente no es un comando y no debe parecerlo, así que lleva su propio fence:

````markdown
Cuando el autor dicta

```agente
A las dos y veinte, hay que avisarle de los gastos comunes a la administradora.
```
````

Adentro va habla del autor, sin nombrar comandos, marcas ni archivos: un turno que explique lo que el `AGENTS.md` del vault ya dice deja de probar el vault y pasa a probar el prompt.

Lo corre [`../scripts/agente.py`](../scripts/README.md) dentro de `mi-vault/`, con un `tuku` al frente del `PATH` que anota `argv` y delega en el real, así que lo que queda no es lo que el agente dijo sino lo que ejecutó: `corrida.turno.traza`. Reconocer el fence marca además el escenario como agéntico y lo deja fuera de la corrida por defecto, sin que nadie tenga que acordarse de poner la marca.

**No hay ni va a haber un comando de TUKU que abra un modelo.** El agente invoca a `tuku`, nunca al revés; esto es instrumento de pruebas y no vive en el vault de nadie.

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
| [`001-01-instalacion-con-uv-tool.md`](001-01-instalacion-con-uv-tool.md) | Epic 001, fase 0 | Los únicos que instalan de verdad, con `--force`: `uv tool install` y `pipx install` desde `git+...@devel`, y `pipx install` desde este checkout. Marcados `red`, fuera de la corrida por defecto |
| [`001-02-init-siembra-el-estado-cero.md`](001-02-init-siembra-el-estado-cero.md) | Epic 001, fase 0 | La verificación byte a byte de `tuku init` contra `template/vanilla/` en vivo, con `home` local y la red bloqueada |
| [`001-03-destino-no-vacio.md`](001-03-destino-no-vacio.md) | Epic 001, fase 0 | `tuku init` se niega a sembrar sobre contenido; `--force` reemplaza |
| [`001-04-init-author.md`](001-04-init-author.md) | Epic 001, fase 0 | La capa de identidad: `--author` deja el nombre en `LIBRO-DE-ESTILO.md`; en blanco deja el vault operable |
| [`001-06-cli-ayuda.md`](001-06-cli-ayuda.md) | Epic 001, fase 0 | `tuku init -h` nombra sus opciones, y una instalación rota sale con el código de entorno. En proceso, sin red |
| [`001-07-lint-libro-de-estilo.md`](001-07-lint-libro-de-estilo.md) | Epic 001, fase 0 | Con qué código salen `style lint` y `vocab show` ante un `LIBRO-DE-ESTILO.md` roto |
| [`002-00-el-dia-uno-a-mano.md`](002-00-el-dia-uno-a-mano.md) | Epic 002 | Descripción general, qué tiene que funcionar, qué se verifica y movimientos de diseño del Epic 002 |
| [`002-13-el-dia.md`](002-13-el-dia.md) | Epic 002 | El día uno hora por hora, un escenario por tramo encadenado al anterior: ciclo, registros, pendientes de hoy, ámbito, nota, pendientes fechados y repetir el día sin cambios |
| [`002-14-casos-borde.md`](002-14-casos-borde.md) | Epic 002 | Sobre el vault final del `002-13`: ediciones con un editor que cada lint nombra, `fix todo`, `regenerate` y un canónico roto |
| [`003-00-el-dia-uno-dictado.md`](003-00-el-dia-uno-dictado.md) | Epic 003 | Qué se verifica con un agente en el medio, y los escenarios del epic |
| [`003-01-el-vault-dice-a-donde-va.md`](003-01-el-vault-dice-a-donde-va.md) | Epic 003 | `tuku doctor` verifica que la tabla de despacho del `AGENTS.md` no nombre comandos que no existen. Sin agente |
| [`003-10-el-dia-uno-en-un-turno.md`](003-10-el-dia-uno-en-un-turno.md) | Epic 003 | El día uno dictado en un turno, con lo que no se anota: deja el vault del epic 002 |
| [`003-11-el-dia-que-no-se-dicta.md`](003-11-el-dia-que-no-se-dicta.md) | Epic 003 | Un hecho con hora y sin día cae en el último día con registros |
| [`004-00-la-conversacion.md`](004-00-la-conversacion.md) | Epic 004 | Qué se verifica con dos agentes conversando, los escenarios del epic y el vault de partida que todos copian |
| [`004-01-el-dia-conversado.md`](004-01-el-dia-conversado.md) | Epic 004 | Camino feliz: Damián consulta, aclara, delibera, se interrumpe y ratifica; el vault queda como el dictado directo de lo ratificado |

## Escenarios encadenados, desde el epic 002

El orden lo fija [`../../devel/epics.md`](../../devel/epics.md), "El orden, siempre el mismo". La cadena es la forma que toma acá.

Dentro de un epic, **el estado inicial de un escenario es el estado final del anterior**. El primero parte del fixture con el que el epic empieza (`vacio` para el 002) y el último deja el fixture con el que empieza el epic siguiente. Es la escalera de [`../../devel/epics.md`](../../devel/epics.md) bajada de grano: los estados intermedios no se escriben a mano ni se congelan, se reproducen corriendo la cadena.

Tres consecuencias prácticas:

1. **El assert es el diff entre dos estados**, no una comparación de árbol completo. Así se ven los efectos colaterales que un assert por archivo no mira, y la idempotencia sale gratis: el segundo pase de una operación tiene que dar diff vacío.
2. **Cada paso deja su propio snapshot** en `playground/<XXX-YY-slug>/`, copiando el estado heredado antes de operar. La regla del playground no cambia, y la revisión a mano pasa a ser `diff -r` entre dos carpetas consecutivas.
3. **Un paso que falla salta los siguientes en vez de reprobarlos**, y correr uno suelto con `-k` reproduce la cadena desde el estado inicial del epic. Es barato porque el tramo entero es determinista: el único escenario con LLM va al final, fuera de la cadena, y su salida se congela como fixture.

> [!question] Pendiente de decisión #REVISAR
> Con cadena, el `YY` pasa a ser **orden de ejecución** dentro del epic, y eso contradice la sección "Convención de nombre" de más arriba, que dice que el número no es orden de lectura y que no se renumera. Queda sin resolver a propósito: es una regla del repositorio, no del epic.
