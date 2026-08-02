# Plan de implementación

> `devel/plan-implementacion.md` · Propuesta, 2026-08-01. **No es un compromiso ni una spec**:
> es una ruta de construcción para discutir. Lo que aquí se decida y cierre una alternativa
> viable pasa a [`docs/decisiones/`](../docs/decisiones/); lo que fije un formato, a
> [`spec/`](../spec/).

---

## 1. Punto de partida

El diseño está cerrado a un nivel poco común para un proyecto sin código: ocho specs
completas con invariantes numeradas y garante declarado, **dieciséis ADR**, y **dos
simulaciones que son de facto los tests de aceptación**
([`corpus/simulaciones/`](../corpus/simulaciones/)).

Los ADR importan para este plan más de lo habitual: no solo registran por qué el sistema es
como es, sino que **cada uno fija un comportamiento verificable**. La §2.1 los mapea a las
fases que los implementan.

Lo que existe en `src/` es un esqueleto: `cli.py` lanza `SystemExit('no implementado aún')`,
y `core/`, `janitors/`, `migrations/` son `__init__.py` vacíos.

La restricción que ordena todo el plan está en el brief §8: **un desarrollador, tiempo
escaso**. Ante dos opciones, gana la que reduce superficie.

### 1.1 La decisión que ordena el orden

El brief §8 ya nombra el núcleo que hace verdadera la promesa del nombre: **cadencias,
backlog canónico de tareas y captura conversacional**. Pero hay una dependencia dura entre
esas tres que fija el orden de construcción:

```
parser/serializer  →  janitors de invariantes  →  cadencias  →  ciclo  →  agente
```

Ningún janitor puede validar T1–T8 sin un parser que lea la línea posicional. Ninguna
cadencia puede emitir una tarea sin un serializador que la escriba. Y el agente no puede
normalizar a forma canónica lo que el motor no sabe leer todavía.

**Corolario incómodo pero liberador: el agente va al final.** Es lo contrapuesto a la
intuición ("es un producto conversacional, empecemos por el chat"), pero es exactamente lo
que exige P3 — y significa que las cinco primeras fases se construyen y se testean **sin
gastar un solo token**.

---

## 2. Fases

### 2.1 Qué ADR implementa cada fase

Los dieciséis ADR no son historia: son la especificación del comportamiento. Este mapeo dice
dónde se implementa cada uno y, sobre todo, **dónde se verifica**.

| ADR | Qué fija | Fase | Cómo se verifica |
|---|---|---|---|
| [0001](../docs/decisiones/0001-id-estable.md) `id` estable | identidad independiente del path | F1 | mover una entidad no rompe referencias |
| [0002](../docs/decisiones/0002-motor-fuera-del-perfil.md) motor fuera | punteros, no vendorizado | F0 | `tuku init` + `tuku sync` |
| [0003](../docs/decisiones/0003-version-de-esquema.md) esquema | `schema_version`, migraciones acumulativas | F0 | `tuku doctor` ante esquema mayor |
| [0004](../docs/decisiones/0004-canonico-no-es-vista.md) canónico ≠ vista | qué es fuente y qué proyección | F3 | borrar derivadas y regenerar → diff cero |
| [0005](../docs/decisiones/0005-derivadas-no-readonly.md) no read-only | detección por hash, preguntar antes de pisar | F3 | editar zona derivada → el motor pregunta |
| [0006](../docs/decisiones/0006-regla-muere-emitido-sobrevive.md) regla muere | `origin` colgante no es violación | F2 | K7: borrar cadencia, la tarea sobrevive |
| [0007](../docs/decisiones/0007-plan-es-calendario.md) plan = calendario | `next:X` resuelve por grep, no por cálculo | F4 | crear plan excepcional → tareas se re-resuelven |
| [0008](../docs/decisiones/0008-parent-derivado-del-path.md) `parent` derivado | jerarquía desde el path | F1 | N3/N4 |
| [0009](../docs/decisiones/0009-type-string-libre.md) `type` libre | sin catálogo cerrado | F2 | simulación 2 sin tocar `src/` |
| [0010](../docs/decisiones/0010-friccion-no-se-declara.md) fricción | no hay clasificación; se descubre | F5 | §5.1 |
| [0011](../docs/decisiones/0011-proceso-sin-almacenamiento.md) proceso sin almacén | instancia = grupo de tareas | F4 | estado por consulta, no por campo |
| [0012](../docs/decisiones/0012-blockuntil-causa-unica.md) `blocked_until` | un campo, dos causas | F4 | `blocked_until >= hoy` → no dispara |
| [0013](../docs/decisiones/0013-cadencias-en-comentario.md) cadencias en comentario | comentario es fuente, lo visible es derivado | F1 + F3 | round-trip + builder `cadencias-legibles` |
| [0014](../docs/decisiones/0014-formato-posicional-tareas.md) formato posicional | campos fijos + comentario del motor | F1 | round-trip exacto |
| [0015](../docs/decisiones/0015-tuku-log-no-versionado.md) `tuku.log` | fuera de Git | F0 | `.gitignore` sembrado por `init` |
| [0016](../docs/decisiones/0016-atomos-diferidos.md) átomos diferidos | **no se implementa transclusión** | — | alcance negativo explícito |
| [0017](../docs/decisiones/0017-pydantic-v2-para-modelos.md) Pydantic v2 | modelos e I/O declarativos y acelerados | F1+F2 | validación de modelos Pydantic en `src/` |

**0016 es el único que se implementa no haciendo nada**, y conviene tenerlo presente: el
motor de la primera versión no implementa transclusión, lo que simplifica los janitors de
build. El gancho —`id` por sección— ya existe sin costo.

**Dos ADR concentran el riesgo de F1**: 0013 y 0014, porque ambos ponen contenido semántico
dentro de comentarios HTML. Son la razón de que el criterio de salida de F1 sea round-trip
exacto y no algo más laxo.

Cada fase termina con algo verificable y usable a mano (P2). Ninguna fase depende de trabajo
de una posterior.

### F0 — Cimientos ✅ *completado*

Antes de escribir el motor hay dos cosas que retrofitear cuesta caro.

| Entregable | Por qué ahora |
|---|---|
| `pyproject.toml` con `[dev]`: pytest, ruff, mypy (fijado en **Python 3.14**) | Definir el listón antes que el código |
| `tuku --profile` y `tuku doctor` que reporte versión, commit y rama | `deployment.md` §2.3 lo exige: sin esto ningún bug es accionable |
| `core/config.py`: cargar `.tuku/config.yaml` y validar `schema_version` | ADR 0003; el resto lo asume disponible |
| `tuku init` que siembre el layout de `arquitectura.md` §2, **con `.gitignore` que excluya `tuku.log` y `.tuku/cache/`** | ADR 0015: si el log entra a Git una vez, sacarlo después no borra el historial de ruido |
| `tuku sync`: punteros a procesos + `AGENTS.md` por nivel | ADR 0002; sin esto los assets de agente no son descubribles |

**Nota sobre `schema_version`.** El ADR 0003 declara que el compromiso de migración empieza
en la versión 1, y hoy la plantilla está en 0. Propongo mantener 0 hasta el final de F4 y
declarar 1 cuando el formato haya sobrevivido a las dos simulaciones completas. Migrar
formatos durante la construcción sería trabajo puro de fricción.

### F1 — Parser y serializador ✅ *completado*

El corazón. Todo lo demás lo consume.

- Front matter (`spec/frontmatter.md` creado y compatible con `spec/*`).
- Línea de tarea posicional de 7 campos + comentario `<!-- tuku: … -->` **en una sola línea**
  (ADR 0014) + cita `>`.
- Entrada de bitácora: hora opcional, entidad opcional, clasificación, marcadores `#tag`,
  continuación indentada.
- Gramática temporal completa: precisa, rango, difusa, `next:<tipo>`.
- Zonas `<!-- tuku:editable -->` / `<!-- tuku:derived hash=… -->` / `<!-- tuku:cadencias -->`.
- Adopción de Pydantic v2 (**ADR 0017**) para modelos e I/O declarativos.

**Criterio de salida — round-trip exacto.** Parsear y volver a serializar cualquier archivo
del perfil produce *byte por byte* el mismo contenido (`test_roundtrip.py` parametrizado por `specref.casos()`).

### F2 — Janitors de invariantes ✅ *completado*

Inspección determinista de reglas sobre todo el perfil.

- Implementación del motor `Janitor` (`src/tuku/core/janitor.py`).
- Verificaciones de invariantes de perfil, entidades, entradas, tareas, notas.
- Subcomando CLI `tuku janitor [--fix]`.
- Suite de pruebas de invariantes (`tests/test_janitor_invariantes.py`).

Las 40+ invariantes ya están escritas y con garante asignado. Esta fase es sobre todo
transcripción, y es donde el diseño paga.

| Grupo | Invariantes |
|---|---|
| Entidad | N1–N9 |
| Entradas | E1–E7 |
| Tarea | T1–T8 |
| Cadencia | K1–K9 |
| Ciclo | C1–C7 |
| Proceso | P1–P6 |
| Nota | O1–O8 |
| Perfil | P1–P2 (`spec/perfil.md`) |

**Colisión de prefijos resuelta**: `spec/proceso.md` usa `R` (R1–R6, de *proceso recurrente*) y `spec/perfil.md` conserva `F` / `P` para perfil, evitando colisiones en el reporte del janitor.

Salida: `tuku janitor [--fix]`, idempotente por construcción. Correrlo dos veces produce el
mismo resultado.

### F3 — Grafo de derivaciones y build sobre diff (~1 semana)

- Grafo declarado en `config.yaml`, validación de aciclicidad al arrancar.
- Builders: `bitacora_entidad` (agrupada por mes y clasificación), `tareas_del_ciclo`,
  `dashboard`, `cadencias-legibles`, `indice_notas`, `notas_entidad`.
- **Hash de fuentes y detección de divergencia** (ADR 0005): si el usuario escribió dentro de
  una zona derivada, se pregunta antes de sobrescribir. No se bloquea nada a nivel de
  sistema de archivos.
- Build sobre diff: recibe archivos cambiados, recomputa solo lo alcanzable.

**Criterio de salida:** borrar todas las zonas derivadas del perfil y reconstruirlas produce
diff cero (ADR 0004: "borrar una proyección es limpieza, no pérdida").

> **Trampa señalada por el propio ADR 0005**, y que conviene resolver en esta fase y no
> después: si el hash se calcula sobre bytes crudos, cualquier cambio de formato entre
> versiones del motor dispara la pregunta de divergencia en **todos** los perfiles
> existentes, aunque el contenido sea semánticamente idéntico. El ADR indica la mitigación
> —normalizar antes de hashear: espacios finales, saltos de línea— y advierte que "requiere
> atención en las migraciones". Traducción para F3: **la función de normalización es parte
> del contrato de esquema**, y cambiarla es una migración (ADR 0003), no un refactor.

### F4 — Cadencias, ciclo y RADAR (~1½ semanas)

Aquí el sistema empieza a cumplir su promesa.

1. **Colector** (`spec/cadencia.md` §3.1): combina sistema → ámbito → niveles → tipo →
   entidad por sobrescritura sobre `id`, cachea en `.tuku/cache/cadencias-resueltas.yaml`.
2. **Cuatro disparos**: `calendar`, `event` (con marcadores), `absence` (con silenciador por
   `status`), `completion`.
3. **Registro de ocurrencias** para idempotencia (K4) — es lo que permite que el cron corra
   tan seguido como haga falta.
4. **Resolución de `next:<tipo>`** (ADR 0007): es **un grep sobre `ciclos/`**, no un cálculo
   desde las reglas de cadencia. El ADR lo dice explícitamente y simplifica la
   implementación: buscar el `plan_*` más próximo con ese `cycle_type` y `cycle_start > hoy`.
5. **`tuku abrir` / `tuku cerrar`**: los órdenes de operaciones de `artefactos-ciclo.md` §5 y
   §6, **con el paso del agente omitible**. Sin modelo, el plan se crea con los insumos y sin
   redacción.
6. **RADAR** (`arquitectura.md` §11): consulta en vivo, determinista, sin archivo propio.
   ADR 0011 le agrega una responsabilidad: **el estado de una instancia de proceso es una
   consulta de RADAR**, no un campo — se deduce de qué tareas del grupo siguen abiertas.
7. **Procesos** (`spec/proceso.md`, ADR 0011): instanciación, `deps` entre pasos,
   `repeatable`, `closes_instance`. Sin primitiva de almacenamiento nueva: todo vive en
   `tareas/tareas.md` con `process=` y `step=` en el comentario.

**Criterio de salida — el test de recuerdo** (criterio 3 del brief): una cadencia declarada
meses atrás produce su tarea en el ciclo correcto, sin ningún LLM en el lazo.

> **Advertencia heredada del ADR 0007**, que vale como requisito de `tuku doctor`: si el
> usuario no tiene planes futuros sembrados, `next:<tipo>` **no puede resolverse** —las
> cadencias siembran el plan inmediato siguiente, no el calendario de los próximos meses—.
> El ADR ya nombra la mitigación: el motor advierte cuando una tarea con `(next:X)` no tiene
> plan futuro contra el cual resolver. Es una advertencia, no un error.

### F5 — Agente y Hermes (~1½ semanas)

Recién aquí entra el modelo. Detalle en §4.

- Los tres procesos de `src/tuku/procesos/` escritos como Markdown ejecutable (hoy son
  títulos vacíos).
- `tuku registrar` — captura conversacional: lenguaje natural → forma canónica.
- Siembra de `plan_*` y `resultados_*`.
- Tesauro vivo inyectado en contexto.

### F6 — Scheduler (~½ semana)

Cron que evalúa cadencias vencidas, `followup` vencidos, difusas por reevaluar, y
encadenamientos con `max_chain_depth`. `arquitectura.md` §8 es explícito: **no es opcional**,
porque sin lazo periódico el sistema pierde su carácter proactivo.

---

## 3. Estrategia de tests

Cuatro niveles, tres de ellos sin gastar un token.

### Nivel 1 — Unitarios sobre los ejemplos de las specs

[`spec/README.md`](../spec/README.md) declara que **los ejemplos son normativos**: los
bloques de código de las specs son casos que el parser debe aceptar. Se extraen a fixtures y
se testean uno a uno.

```
tests/
├── fixtures/spec/          # extraídos de los bloques de las specs
├── test_parser_tarea.py    # la línea posicional, campo por campo
├── test_parser_entrada.py
├── test_temporal.py        # las cuatro modalidades + next:<tipo>
└── test_roundtrip.py       # parse → serialize → idéntico byte a byte
```

### Nivel 2 — Un test por invariante

Cada invariante numerada tiene un test que la viola deliberadamente y verifica que el janitor
la detecta. La numeración de las specs se convierte en la numeración de los tests:

```python
def test_T6_tarea_en_dos_archivos_canonicos(perfil_tmp): ...
def test_K5_cadencia_de_entidad_archivada_no_emite(perfil_tmp): ...
def test_C2_solapamiento_mismo_cycle_type(perfil_tmp): ...
```

Este mapeo 1:1 es el mayor dividendo de haber escrito las specs primero: la cobertura no se
inventa, se transcribe. Y una invariante sin test es visible de inmediato.

### Nivel 3 — Las simulaciones como tests de aceptación

Esto es lo más valioso que tiene el repo y conviene no desaprovecharlo.
[`flujo-turno.md`](../corpus/simulaciones/flujo-turno.md) y
[`flujo-pyme-semana.md`](../corpus/simulaciones/flujo-pyme-semana.md) narran, paso a paso y
con marcas `▸ INPUT` / `⚙ TUKU`, dos ciclos completos con sus artefactos esperados.

Propongo convertirlas en fixtures ejecutables: perfil inicial + secuencia de inputs + estado
final esperado. Cada `⚙ TUKU` determinista es una aserción.

La simulación 2 es además el **test de P6**: modela un dominio comercial ajeno al del autor.
Su criterio de aceptación literal es *"funciona sin tocar `src/`"* — si para hacerla pasar hay
que modificar el motor, P6 está violado y el hallazgo es de diseño, no de código.

### Nivel 4 — Replay

El criterio de éxito 1 del brief y, según P3, **un detector de agencia mal ubicada**:

| Qué se reconstruye | Criterio | Si falla |
|---|---|---|
| Producido por janitors | diff **exactamente cero** | defecto de código |
| Producido por agentes | equivalencia semántica | evaluación aparte (§4.3) |

> Y la regla que hace de esto un instrumento de diseño y no solo una prueba de regresión: **si
> algo que debería ser determinista solo pasa el test semántico, hay juicio del agente donde
> debería haber una regla.**

### Fixtures

**Ya construidas** en [`../tests/conftest.py`](../tests/conftest.py): `perfil_tmp` (perfil
sembrado por `tuku init` en un `tmp_path` con Git inicializado), `hermes_efimero` y
`assert_diff_cero`. Todos los tests corren contra perfiles desechables; ninguno toca datos
reales. `corpus/referencia/` (hoy solo un `.gitkeep`) se llena con los perfiles de las dos
simulaciones.

Mientras `tuku init` no exista, `perfil_tmp` **salta** el test en vez de fallar. Eso permite
escribir hoy los tests de F1–F4 y que se activen solos cuando el comando aterrice, en vez de
vivir en rojo durante semanas. Un `skip` masivo es el indicador de que F0 sigue abierta.

### Lo que ya corre sin motor

La suite pasa en verde desde hoy, y lo que verifica no es código sino el corpus documental
del que come el desarrollo asistido: que los enlaces relativos resuelvan, que no queden
referencias a specs eliminadas, que no se filtren identificadores del contexto real, y que
toda invariante de `spec/` tenga test o esté declarada pendiente.

Esto último es el mecanismo que hace que la cobertura no se degrade en silencio: si alguien
agrega `T9` a una spec, la suite falla hasta que exista su test o se registre la deuda. El
mapeo 1:1 deja de depender de que alguien se acuerde.

Ver [`../tests/README.md`](../tests/README.md).

---

## 4. Configuración de Hermes

`arquitectura.md` §8 fija Hermes + modelo económico como motor agéntico de pruebas, y §8
agrega el requisito de aislamiento. Verifiqué contra la instalación real y las docs oficiales.

### 4.1 El mecanismo de aislamiento es `HERMES_HOME`

Es la pieza clave y ya existe, no hay que construirla. La documentación oficial de perfiles
lo dice explícitamente: `HERMES_HOME` es **la frontera del perfil** — config, `.env`,
sesiones, memoria, skills, base de estado, PID del gateway, logs y cron se resuelven contra
esa variable. Los propios tests de Hermes la redirigen a directorios temporales para no tocar
`~/.hermes`.

Eso da exactamente lo que pide `arquitectura.md` §8: **cada test integrado instancia un perfil
de Hermes desde cero**, sin arrastrar contexto previo.

```python
@pytest.fixture
def hermes_efimero(tmp_path):
    home = tmp_path / "hermes-home"
    home.mkdir()
    (home / "config.yaml").write_text(CONFIG_TEST)   # modelo económico, sin gateway
    env = {**os.environ, "HERMES_HOME": str(home), "TZ": "UTC"}
    yield env       # el tmp_path se destruye al terminar el test
```

`TZ=UTC` no es cosmético: medio sistema resuelve fechas relativas, y un test que pase en
Chile y falle en CI por zona horaria es una tarde perdida.

### 4.2 Invocación

La forma correcta para scripting es `-z/--oneshot`, que imprime **solo** la respuesta final:

```bash
HERMES_HOME=$TMP hermes -z "$(cat prompt.txt)" \
    --safe-mode \
    -m deepseek-v4-flash \
    --ignore-rules
```

| Flag | Por qué |
|---|---|
| `-z` | salida limpia, sin banner ni spinner: parseable |
| `--safe-mode` | desactiva **todas** las personalizaciones del usuario |
| `--ignore-rules` | no inyecta `AGENTS.md`/`SOUL.md`/memoria/skills del entorno |
| `-m deepseek-v4-flash` | el modelo económico que ya usa tu instalación |

`--safe-mode` e `--ignore-rules` son los que convierten "corre en la máquina de jpgil" en
"corre igual en CI". Sin ellos, tu `SOUL.md` y tus skills entran al prompt y el test deja de
ser reproducible.

**Regla dura que conviene respetar desde el primer día**: nunca dos gateways contra el mismo
directorio de datos. Los tests no deben levantar gateway — solo `-z`.

### 4.3 Cómo se testea lo no determinista

Un LLM no da salida idéntica dos veces, así que asertar texto exacto es garantizar tests
inestables. Propongo tres capas, de menor a mayor costo:

| Capa | Qué verifica | Cuándo corre |
|---|---|---|
| **Estructural** | el artefacto tiene los encabezados de C7, front matter válido, secciones obligatorias no vacías (C5) | siempre, en CI |
| **Factual** | los hechos citados existen en el canónico — cero invención | siempre, en CI |
| **Semántica** | los mismos hechos, las mismas desviaciones señaladas | manual o *nightly* |

La capa factual es la que más protege: verifica que cada tarea o entrada mencionada en un
informe **existe con ese `id`**. Un informe bien redactado sobre hechos inventados es el peor
fallo posible en un sistema cuya promesa es recordar, y esa verificación es determinista y
barata.

### 4.4 La prueba de P2, que es una prueba del proceso

P2 dice que si un proceso necesita un modelo de frontera para no descarrilar, **el proceso
está mal escrito — no falta modelo**. Eso convierte cada test agéntico fallido en una
pregunta de diseño antes que de código, y significa que la suite debe correr con el modelo
económico y no con el mejor disponible.

Todo test agéntico debe tener su gemelo sin agente: `tuku abrir --sin-agente` produce el plan
con los insumos y sin redacción, y ese camino se testea siempre.

---

## 5. Bloqueantes antes de empezar

Tres cosas que conviene cerrar antes de F1, ordenadas por costo de arreglarlas después.

| # | Qué | Por qué bloquea | Costo |
|---|---|---|---|
| 1 | **[`spec/frontmatter.md`](../spec/frontmatter.md) está vacío** (solo el título) | Es transversal: F1 lo necesita para el parser y F2 para N1/E1/T1. Hoy los campos están dispersos en siete specs | medio |
| 2 | **`.tuku/config.yaml` sin spec completa** | Existe como fragmentos ilustrativos en cuatro documentos. F0 lo carga y F3 lee de él el grafo de derivaciones. `spec/perfil.md` hoy solo cubre `capacidad.md` | medio |
| 3 | **Colisión de prefijos `P`** entre `proceso.md` y `perfil.md` | Trivial ahora, permanente después | mínimo |

Ninguno exige diseño nuevo: los tres son consolidación de decisiones ya tomadas y dispersas.

El tercero ya no depende de la memoria de nadie: `test_prefijos_de_invariante_no_colisionan`
está marcado `xfail(strict=True)`. Mientras la colisión exista, falla y la suite sigue verde;
el día que alguien renombre el prefijo, el test pasa a XPASS y **rompe la suite**, obligando
a retirar el marcador. Un bloqueante conocido no se convierte así en un bloqueante olvidado.

### 5.1 Consecuencia para E5 (ADR 0010)

La clasificación `friccion` quedó descartada por [ADR 0010](../docs/decisiones/0010-friccion-no-se-declara.md),
de modo que el conjunto por defecto queda cerrado en **`hito`, `decision`, `senal`, `msg`**,
más lo que el usuario extienda en `config.yaml`. Es el conjunto contra el que valida E5 y el
que debe sembrar `tuku init`.

La consecuencia de diseño importa más que la lista: **las Desviaciones no salen de un filtro
por clasificación**, sino del contraste por entidad del cierre
(`artefactos-ciclo.md` §3.2). Para F4 y F5 eso significa que la sección Desviaciones no tiene
un builder determinista que la produzca — tiene un builder que produce sus *insumos*
(intención sin correspondencia, arrastre sobre umbral) y un paso de agente que la redacta
contrastando. Confundir ambas cosas sería exactamente la agencia mal ubicada que el test de
replay detecta (§3, nivel 4).

---

## 6. Resumen

| Fase | Entregable | Semanas | Agente |
|---|---|---|---|
| F0 | Cimientos, `init`, `doctor` | ⅓ | no |
| F1 | Parser/serializador con round-trip exacto | 1 | no |
| F2 | Janitors de invariantes | 1 | no |
| F3 | Grafo de derivaciones, build sobre diff | 1 | no |
| F4 | Cadencias, ciclo, RADAR, procesos | 1½ | no |
| F5 | Agente, Hermes, procesos en Markdown | 1½ | **sí** |
| F6 | Scheduler | ½ | no |

**≈ 7 semanas de trabajo efectivo**, con la advertencia de que "tiempo escaso" del brief §8
significa que el calendario real será bastante más largo que la suma de esfuerzos.

**Al terminar F4 el sistema ya cumple su promesa**: registra, recuerda, abre y cierra ciclos,
y lo hace sin conexión y sin créditos. F5 lo vuelve cómodo; F6 lo vuelve proactivo. Si el
tiempo se acaba antes de F5, lo construido sigue siendo un sistema usable a mano — que es
justamente lo que P2 exige y lo que hace que este orden sea el correcto.

---

## 7. Lo que este plan no decide

- **Interfaz de usuario.** Ni GUI, ni Telegram, ni voz. El brief §8 los tiene registrados y
  ordenados detrás del núcleo.
- **Modelo de identidad multiusuario** y quién paga la inferencia (`deployment.md` §7).
- **Las decisiones abiertas de `spec/`**, que se cierran con experiencia de uso y no antes:
  `effortTime`, reevaluación de la descripción inferida, formato interno del informe anual.
- **Federación entre perfiles vía MCP.** Aparcada; el ADR 0001 ya dejó el gancho.

Dos cosas que este plan **ya no decide porque un ADR las cerró**, y que conviene no reabrir
durante la construcción: la promoción de secciones a átomos
([0016](../docs/decisiones/0016-atomos-diferidos.md) — diferida, sin transclusión en la
primera versión) y la separación de `blocked_until` en causa y efecto
([0012](../docs/decisiones/0012-blockuntil-causa-unica.md) — un campo, dos causas, y la
distinción la infiere el agente si hace falta). Ambas son tentaciones naturales al escribir
el código; ambas tienen su costo ya declarado y aceptado.

---

## 8. Anexo — El eje deliberativo (notas)

Incorporado el 2026-08-01, después de constatar que el sistema predecesor `mac-jpgil` tenía
**181 notas y 1.7 MB** con ontología propia, janitor de índice y reglas de enlace, mientras
TUKU solo declaraba `notas/` como directorio vacío en el layout. La spec resultante
—[`spec/nota.md`](../spec/nota.md)— **transcribe una práctica probada**; no diseña un formato
nuevo.

### 8.1 Por qué no altera el orden de las fases

Las notas no bloquean nada y nada las bloquea. El parser de F1 ya necesita front matter y
zonas marcadas, que cubren el caso completo; el índice es un builder más en F3. Concretamente:

| Fase | Qué agrega | Costo |
|---|---|---|
| **F0** | `tuku init` siembra `notas/notas.md` (índice vacío) y `notas/AGENTS.md` | horas |
| **F1** | Nada nuevo: el front matter y las zonas ya están en el parser | — |
| **F2** | Invariantes **O1–O8**. O5 (sin wikilinks) y O4 (enlaces resuelven) son las que aportan | ½ día |
| **F3** | Builders `indice_notas` y `notas_entidad` | 1 día |
| **F4** | Nada: las notas no tienen cadencias, no arrastran, no entran al cierre | — |
| **F5** | `tuku nota`, alta conversacional e inferencia de `summary` | 1 día |

**≈ 2½ días sobre las 7 semanas.** Es barato precisamente porque el eje deliberativo es
inerte: no tiene estado, ni ritmo, ni interacción con cadencias.

### 8.2 Lo que aporta al resto del sistema

Tres cosas que el diseño no tenía y que salieron del corpus real:

1. **`summary` obligatorio con regla de calidad.** Es el mismo argumento del brief §3.5 —"el
   informe es la memoria"— aplicado al eje deliberativo: un corpus solo es consultable si se
   puede decidir qué leer sin leerlo. El antipatrón (reformular el título) ya estaba
   documentado con ejemplos en el sistema viejo.
2. **`## Ver Además` con justificación de enlace.** La regla de que la frase responda *"¿por
   qué haría clic el lector de esta nota?"* convierte el enlace en información. Un grafo se
   calcula solo; la razón solo la tiene quien escribió la nota.
3. **La confirmación empírica de P3.** El proceso del sistema viejo decía literalmente
   *"Janitor: mechanical work. Agent: summary inference."* — el reparto determinista/agente
   que TUKU elevó a principio fue descubierto usándolo, no deducido. Es la mejor evidencia
   disponible de que P3 describe una práctica y no una aspiración.

### 8.3 Las tres adaptaciones al modelo nuevo

No es copia literal: el modelo viejo choca con decisiones ya tomadas en TUKU.

| Sistema viejo | TUKU | Por qué cambia |
|---|---|---|
| `area:` apunta a `org/{ORG}/VIGENTES/` | `entidad:` con `id` estable | ADR 0001 y 0008: el path lleva jerarquía, nunca estado |
| `topic` whitelist estricta ("NEVER invent") | string libre indexado | ADR 0009: sin catálogo cerrado; el sistema indexa, no valida |
| `[[wikilinks]]` prohibidos por convención | prohibidos por invariante **O5** | la regla existía y había 135 en el corpus: sin garante, no es regla |

La segunda merece atención en la implementación. La whitelist resolvía un problema real
—evitar que el agente multiplicara categorías sinónimas— y quitarla sin más lo reabre. La
sustitución es **hacer visible lo existente en vez de prohibir lo nuevo**: el índice agrupa por
`topic`, el agente lo lee antes de escribir, y reutiliza. Si aun así proliferan sinónimos, el
diagnóstico es de sembrado (P4), no de validación — y conviene medirlo en uso real antes de
volver a cerrar el catálogo.

### 8.4 Lo que queda abierto

Cuatro decisiones al final de la spec, y una anterior a todas ellas: **si el corpus existente
se migra**. Son 181 notas con `org`/`area` apuntando a rutas `VIGENTES/` que ya no existen en
TUKU. Migrarlas es un script de una sola vez —mapear `org`+`area` a `entidad`, normalizar
`topic`, convertir 135 wikilinks— y es un buen primer caso de uso de `tuku migrate`, pero **no
está decidido** si el corpus entra al perfil TUKU o se queda donde está. Conviene resolverlo
antes de F3, porque cambia si `indice_notas` debe tolerar front matter heredado.
