# Epics de TUKU

> Unidad de entrega, no unidad técnica. Un epic termina con algo que una persona puede usar. Las fases de [`que_implementar.md`](que_implementar.md) siguen siendo el corte técnico y funcionan como checklist interno de cada epic: un epic puede abarcar varias fases, pero no puede cerrar sin cumplir el criterio de salida de las que abarca.

Los epics se numeran por orden de ejecución. Solo los dos primeros están desarrollados, y es deliberado: el resto se escribe cuando el epic 2 haya enseñado lo que hoy no sabemos.

## Los epics mueven el diseño

El diseño lo dirige la experimentación y sus resultados. No se puede saber de antemano el resultado final, así que `spec/` y `docs/` van a cambiar por efecto de los epics, y eso es el método funcionando, no una spec mal escrita.

Cada epic tiene entonces dos salidas: lo que entrega, y lo que le enseña al diseño.

Por eso **ningún epic cierra solo con su entregable**: cierra cuando además está escrito qué movió en `../spec/` o en `../docs/`, aunque la respuesta sea "nada". Dentro de un epic la spec manda sobre el código; entre epics, el resultado del experimento manda sobre la spec.

## Estado

Actualizado el 2026-09-04.

| Epic | Nombre | Estado | Qué falta para cerrarlo |
| --- | --- | --- | --- |
| 1 | Un TUKU mínimo instalable | en curso | probarlo con una persona, podar `docs/libro-de-estilo.md`, y resolver cómo se verifica un estado cero que depende de la fecha |
| 2 | El día uno simulado | sin empezar | depende del epic 1 |
| 3+ | El resto | sin desarrollar | se escriben al cerrar el epic 2 |

Lo hecho en el epic 1 hasta ahora: existe `template/vanilla/`, con los 11 archivos del estado cero y el procedimiento de instalación a mano en `template/README.md`. El mecanismo que lo automatiza para probarlo repetidas veces es `src/install_test_scenario.py`.

El detalle día a día vive en [`iteraciones/`](iteraciones/README.md). Los casos que se están probando, en forma narrativa (Dado/Cuando/Entonces) y no unitaria, viven en `../corpus/escenarios/`; el arnés que eventualmente los ejecuta, en `../tests/escenarios/` y `../tests/scripts/`.

Preparación ya hecha, fuera de los epics: `spec/` y `docs/glosario.md` ordenan el vocabulario y lo que hoy se cree del diseño, y `que_implementar.md` quedó reducido al plan de fases. Es punto de partida, no diseño cerrado.

## Epic 1. Un TUKU mínimo instalable

**Qué entrega.** Que una persona nueva pueda instalar un vault de TUKU en un directorio vacío y empezar a escribir el mismo día, sin configurar nada y sin saber qué es TUKU.

**Por qué va primero.** No es solo la fase 0. Es lo que obliga al repositorio a tener estructura, procedimiento de instalación y template, tres cosas que hoy no existen y que ninguna otra tarea va a forzar.

**Fases que cubre.** Fase 0.

**Decidido, resolviendo por construcción.**

1. **El instalador es un template que se copia**, no el CLI de Python. El estado cero es un directorio de markdown, y que sea copiable a mano es lo que exige el principio 1. El empaquetado se difiere a cuando haya janitors que empaquetar.
2. **El template vive en `template/`, una carpeta por variante.** `vanilla/` es la mínima y la más adaptable. Las variantes futuras son hermanas, nunca capas encima: si dos comparten un archivo, se duplica, porque un template que hay que componer deja de ser copiable a mano.
3. **`reglas/config.tuku.md` declara zona horaria y tipo de ciclo**, en prosa con campos en negrita, igual que las cadencias. Cierra una de las decisiones abiertas de `../spec/README.md`, a falta del visto bueno del autor.
4. **El código vive en `src/` (raíz), no en `devel/VAULT/src/`.** Es donde `pyproject.toml` ya apuntaba (`where = ["src"]`); `devel/VAULT/src/` resultó ser código del diseño anterior (`entradas/`, `tareas/`, `entidades/`) y queda como referencia histórica, no como base para seguir escribiendo. El primer archivo es `src/install_test_scenario.py`: instala una variante de `template/` y resuelve las fechas de `AHORA.md`, sin depender de nada fuera de la librería estándar.
5. **Los escenarios de prueba son narrativos (Dado/Cuando/Entonces), no unitarios**, y separan dato de arnés: el caso vive en `corpus/escenarios/` (dato, puede haber cientos), lo que lo ejecuta y compara en `tests/escenarios/`, y los pasos deterministas reutilizables entre escenarios en `tests/scripts/`.
6. **Instalar es una línea de `curl`, no `git clone`.** `install.sh` baja el tarball del branch desde GitHub, extrae `template/vanilla/` y corre `src/install_test_scenario.py`. Probado el 2026-09-04 contra `pewma-ai/tuku@devel` real: `curl -fsSL https://raw.githubusercontent.com/pewma-ai/tuku/devel/install.sh | sh -s -- <destino>`.

**Qué falta decidir.**

1. **Cómo se verifica un estado cero que depende de la fecha.** El `AHORA.md` del template lleva placeholders (`desde: AAAA-MM-DD`, `## Lunes DD de mes`) porque los días reales dependen de cuándo se instale. Eso rompe el criterio de la fase 0 tal como está escrito, que pide reproducir el fixture `vacio` byte a byte. O el fixture se parametriza por fecha, o el criterio se reescribe.
2. **Qué se hace con `docs/libro-de-estilo.md`.** El starter ya existe en el template. El de `docs/` es documentación de diseño y cinco de sus siete secciones están duplicadas en `spec/`. Falta mover a `spec/` la matriz de reglas y responsabilidades (§7), que es lo único que no está, y recién entonces podar.
3. ~~Qué pasa con `devel/VAULT/src/` y el resto de `devel/VAULT/`.~~ **Resuelto:** `devel/VAULT/` es historia, no base para código nuevo. Queda como referencia; algo puntual se puede rescatar cuando un epic lo necesite, evaluado caso a caso, no de bloque.

**Qué se espera que mueva en el diseño.** La poda de `docs/libro-de-estilo.md` y el reparto de su contenido entre el template y `spec/`. Materializar el estado cero probablemente revele que falta especificar `reglas/config.tuku.md`, que ya está anotado como decisión abierta.

**Criterio de salida.** Instalar en un directorio vacío produce el estado cero descrito en `docs/principios.md` §2. Una persona que no sabe qué es TUKU abre `AHORA.md`, escribe una línea a mano y no rompe nada. Se verifica con una persona, no con un diff. Y queda escrito qué movió en `../spec/` o en `../docs/`.

**No entra.** Ningún janitor, ningún agente, ningún LLM. Tampoco decidir el tipo de ciclo real de quien lo usa: arranca en semanal y el tipo verdadero emerge después.

## Epic 2. El día uno simulado

**Qué entrega.** Un conjunto de entradas de bitácora estándar que, inyectadas sobre el estado cero, producen sus consecuencias de forma reproducible. Y con eso, la plataforma de pruebas que todo lo demás va a usar.

**Por qué va segundo.** Fuerza tres cosas a la vez que no se pueden conseguir por separado: el sistema de testing replicable y semi determinista, la validación del stack recomendado (Obsidian, un directorio y un agente que lee las reglas), y la primera prueba real de que el formato de entrada aguanta.

**Semi determinista** porque la entrada depende de un agente. Esa es la dificultad central del epic: definir qué se compara byte a byte y qué solo se puede evaluar.

**Fases que cubre.** Fases 1 y 2 completas, y las partes de la 3 y la 5 que el día uno toque (crear un ámbito nuevo, enlazar una nota).

**Vocabulario.** Lo que el día uno produce a partir de las entradas son **consecuencias** (pendientes, ámbitos nuevos, enlaces, notas tipadas), no "entidades". "Entidad" es vocabulario del diseño anterior y no aparece en `spec/`.

**Qué hay que decidir para empezar.**

1. **Qué entradas componen el día uno.** Tienen que ser representativas y cubrir al menos las tres marcas de la ontología cerrada. Hay material en `corpus/`.
2. **Cómo se verifica lo que depende del agente.** El criterio byte a byte sirve para las consecuencias, que son deterministas. Para la redacción de la entrada hace falta otro criterio, y decidirlo es parte del epic.
3. **Qué arnés de agente se usa** y cómo se aísla para que la suite no gaste tokens por accidente.
4. **Dónde vive el código y cómo se ejecuta.** Aquí ya no se puede diferir: es la decisión que el epic 1 dejó pendiente.

**Qué se espera que mueva en el diseño.** Es el epic que más va a mover. El formato de entrada se prueba por primera vez contra dictado real, y si no aguanta, lo que cambia es `spec/bitacora.md`, no el corpus. También obliga a escribir cómo se verifica lo semi determinista, que hoy no está en ninguna parte.

**Criterio de salida.** Partiendo del estado cero, inyectar el día uno produce las consecuencias esperadas, dos veces seguidas da lo mismo, y el conjunto se puede abrir en Obsidian sin cajas de error ni enlaces rotos. Y queda escrito qué movió en `../spec/` o en `../docs/`.

**No entra.** Abrir y cerrar ciclos, cadencias, inferencia semántica. Tampoco reutilizar la suite actual de `tests/`, que es del diseño anterior y se rehace.

## Rescatar de `devel/VAULT/`

Va de simple a complejo, igual que los epics: se rescata lo puntual que un epic en curso necesite, nunca un bloque completo por adelantado. Rescatar algo es una decisión de ese epic, con su propia verificación contra `spec/`, no una migración aparte.

## Epics siguientes

Sin desarrollar a propósito. Se escriben cuando el epic 2 haya cerrado, porque es el que va a corregir los supuestos.

El material de partida está en las fases 3 a 9 de [`que_implementar.md`](que_implementar.md): el árbol de ámbitos, las cadencias, el tejido de notas y enlaces, el ciclo completo, el plan y el resumen, el endurecimiento y la inferencia semántica.

## Cómo se actualiza este documento

La tabla de Estado se edita al empezar y al cerrar cada epic, y cuando una decisión abierta se resuelve. Las decisiones que se resuelven no se borran: se reescriben como afirmación, para que se sepa qué se decidió y no solo que había una duda.

Las decisiones de diseño que afectan al producto y no al plan no van aquí, van a `../spec/README.md`.
