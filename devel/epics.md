# Epics de TUKU

> Unidad de entrega, no unidad técnica. Un epic termina con algo que una persona puede usar. Las fases de [`que_implementar.md`](que_implementar.md) son el corte técnico interno: un epic puede abarcar varias y no cierra sin cumplir el criterio de salida de las que abarca.

Se numeran por orden de ejecución, tres dígitos. Ese número es el `XXX` de `tests/escenarios/XXX-YYY-slug.md` y de sus tests.

Solo los dos primeros están desarrollados. El resto se escribe cuando el epic 002 haya enseñado lo que hoy no sabemos.

## Los epics mueven el diseño

El diseño lo dirige la experimentación, no al revés: `spec/` y `docs/` cambian por efecto de los epics. Cada epic entrega dos cosas, su producto y lo que le enseñó al diseño (aunque sea nada). Dentro de un epic la spec manda sobre el código; entre epics, el experimento manda sobre la spec.

## Qué separa un epic del siguiente

**El estado del vault con el que empieza**, no la primitiva que construye. Las fases de `que_implementar.md` cortan por primitiva (registro, pendientes, ámbitos, cadencias, notas); los epics cortan por el estado inicial, y por eso un epic abarca partes de varias fases.

El motivo es el criterio de entrega: "los pendientes funcionan" no es una experiencia que alguien pueda usar, "el día uno funciona" sí lo es. Y el propio `que_implementar.md` ya lo pedía sin nombrarlo, en su criterio de corte 2: si un estado inicial nuevo es lo que obliga a partir el trabajo, entonces el estado inicial es el eje.

La consecuencia práctica es que los epics 002 y 003 construyen **las mismas capacidades dos veces**, contra vaults distintos. No es repetición: en el 002 el vault está vacío y cada capacidad tiene que crear lo que necesita; en el 003 ya existe un árbol de ámbitos, notas y pendientes con historia, y la misma capacidad tiene que aprovecharlo. Casi todo lo que se descubre está en la segunda vuelta.

## El orden, siempre el mismo

Vale entre epics y entre escenarios de un epic:

1. **De lo determinista a lo agéntico.** Un tramo determinista corre mil veces gratis; uno agéntico cuesta y no repite resultado. El escenario con LLM va al final, nunca en la base de una cadena.
2. **De lo simple a lo complejo.** Una primitiva antes que la combinación, un ámbito antes que un árbol, el mínimo de registros antes que el volumen con ruido.
3. **Del happy path al caso borde.**

Es la apuesta del proyecto: implementando en ese orden, la comprensión de TUKU emerge del uso en vez de decidirse por adelantado.

## De dónde sale el material

Dos fuentes con papeles distintos:

- **[`mac-jpgil`](../../mac-jpgil) dice qué se construye.** El vault real del autor, con meses de práctica probada. La consecuencia "nota" del epic 002 sale de ahí. Nunca es blanco de un test.
- **[`../corpus/referencia/`](../corpus/README.md) dice cómo se ve lo correcto.** `referencia-faena.md` y `referencia-pyme.md` son las únicas guías canónicas de los tests. El fixture no se copia del corpus: lo genera un agente desde él.

**Se trae epic por epic, nunca por adelantado.** Especificar antes de necesitarlo es sobreingeniería sobre prácticas que quizá no sobreviven al empaquetado. Por eso la Parte 3 de `referencia-faena.md` sigue sin traducir: la necesita el epic 003.

## Estado

Actualizado el 2026-09-07.

| Epic | Nombre | Estado inicial | Estado | Qué falta para cerrarlo |
| --- | --- | --- | --- | --- |
| 001 | Un TUKU mínimo instalable | `vacio` | reabierto | reabierto el 2026-09-07 por el cambio a `pipx` + `tuku init` (decisión 4 del epic 002); faltan los escenarios `001-00X` rehechos |
| 002 | El día uno | `vacio` → `primer-dia` | sin empezar | desbloqueado, listo para empezar |
| 003 | El día ciento cincuenta | `ciclo-en-curso` | sin empezar | depende del epic 002 |
| 004 | Abrir y cerrar el ciclo | `ciclo-por-cerrar` | sin empezar | depende del epic 003 |
| 005 | Que note lo que nadie pidió | `historico` | sin empezar | depende del epic 004 |

Lo hecho en el 001, firme tras reabrirlo: `template/vanilla/` (el estado cero), la capa de identidad del autor en `LIBRO-DE-ESTILO.md` con el libro de estilo vanilla reescrito a tercera persona, y la poda y borrado de `docs/libro-de-estilo.md`. Lo que se rehace: el mecanismo de instalación (`src/install_test_scenario.py` e `install.sh` se reemplazan por `tuku init` bajo `src/tuku/`) y los escenarios `001-001` a `001-004`, más uno nuevo. Diario en [`iteraciones/`](iteraciones/README.md); casos narrativos y arnés en `../tests/escenarios/`, pasos compartidos en `../tests/scripts/`.

Preparación previa, fuera de los epics: `spec/` y `docs/glosario.md` ordenan el vocabulario, [`que_implementar.md`](que_implementar.md) quedó reducido al plan de fases. Punto de partida, no diseño cerrado.

## Epic 001. Un TUKU mínimo instalable

Que una persona nueva instale TUKU con un comando, siembre un vault en un directorio vacío y empiece a escribir el mismo día, sin configurar nada y sin saber qué es TUKU. Va primero porque obliga al repositorio a tener estructura, instalación y template, y nada más lo va a forzar. Cubre la fase 0.

**Reabierto el 2026-09-07.** Se cerró el 2026-09-06 con un instalador de una línea (`curl | sh` sobre `install.sh`) que copiaba `template/vanilla/` a un destino. La decisión 4 del epic 002, resuelta el mismo día, cambió el modelo de distribución: TUKU pasa a instalarse como paquete Python y a sembrar vaults con `tuku init`. El entregable no cambia; el mecanismo sí, y con él los cuatro escenarios. Lo que el cierre anterior movió en el diseño (la poda de `docs/libro-de-estilo.md`) queda firme.

El entregable: una persona corre `uv tool install git+https://github.com/pewma-ai/tuku.git@devel` (o `pipx install` con la misma URL), después `tuku init mi-vault`, y ya puede abrir `mi-vault/AHORA.md` y escribir. Sin PyPI, sin editar config, sin leer `spec/`.

Decidido:

1. TUKU se distribuye como paquete Python instalable con `pipx` o `uv tool install` directo desde `git+https://github.com/pewma-ai/tuku.git@devel`. Sin PyPI. Lo fijó la decisión 4 del epic 002.
2. Esa instalación deja el repositorio completo en `~/.tuku`: código, `template/`, `spec/`, `reglas/`, el árbol entero. `tuku init` siembra desde ahí.
3. `tuku init [<dir>]` reemplaza a `install.sh` y a `src/install_test_scenario.py`. Copia `~/.tuku/template/<variante>` al destino (`vanilla` por defecto) y siembra `AHORA.md` con las fechas del primer ciclo. **Offline: no toca la red.** `install.sh` se borra, sin wrapper de reemplazo: `pipx install` ya es un comando y un wrapper solo reintroduce el `curl | sh` que este modelo elimina. La instalación "a mano" de `template/README.md` pasa a ser copiar `~/.tuku/template/vanilla/` sin más.
4. `src/install_test_scenario.py` se reemplaza por la función `init` bajo `src/tuku/`. El CLI (`src/tuku/cli.py`, aún sin escribir) es una capa fina de argparse; la lógica es importable y los tests la llaman sin subprocesos, salvo el que prueba el propio `pipx install`.
5. `tuku` resuelve la ubicación del repositorio con la variable de entorno `TUKU_HOME` (por defecto `~/.tuku`). Es el punto de override para instalaciones no estándar y para los tests, que la apuntan al checkout de trabajo y ejercen `tuku init` sin instalar nada.
6. `template/`, una carpeta por variante, hermanas y sin composición. `vanilla/` es la mínima. Sin cambio respecto al cierre anterior.
7. `reglas/config.tuku.md` declara zona horaria y tipo de ciclo, en prosa. Sin cambio.
8. Sembrar en un directorio que ya tiene contenido se rechaza, salvo `tuku init --force`. Reemplaza al prompt por `/dev/tty` de `install.sh` y a su `TUKU_FORCE=1`: ahora es un flag, no una pregunta interactiva, porque el CLI no depende de una tty.
9. El estado cero se verifica byte a byte con fecha fija (la del ground truth en `referencia-faena.md`, distinta de la que usa el autor real), contra `template/vanilla/` en vivo, nunca contra una copia congelada. El bug que este método encontró en el cierre anterior (días etiquetados por posición) sigue corregido.
10. Capa de identidad mínima: el nombre del autor vive en `LIBRO-DE-ESTILO.md` (sección "El autor", al inicio del documento). `tuku init --author "..."` lo siembra; es opcional y vacío es válido (omitir el flag deja el vault operable, principio 2). El libro de estilo vanilla ya está en tercera persona desde el cierre anterior.

**Rescatado del CLI viejo de `devel/VAULT/`:** solo la forma. `tuku <noun> <verb>` en inglés como estructura de comandos, y `tuku init [<dir>]` como el verbo que siembra. Nada de su `core/`: su `init.py` sembraba un árbol de perfil distinto (`entradas/`, `tareas/`, `ciclos/`, `.tuku/config.yaml`, `.hermes/`) que este modelo no usa. El vault de TUKU se define por `template/vanilla/`, no por ese código.

**Firme del cierre anterior:** `docs/libro-de-estilo.md` se podó y se borró; las ocho secciones que duplicaba a `spec/` desaparecieron con él y las tres filas de su matriz que no estaban cubiertas ([`ver además` y su motivo](../spec/notas.md), [el emparejamiento no literal al cerrar un pendiente](../spec/agente.md)) se migraron antes de borrar. El libro de estilo vanilla quedó reescrito a tercera persona con la sección "El autor" al inicio. El cambio de instalación no toca nada de esto.

Decisión abierta que sigue abierta: **dónde se especifica el comportamiento del agente** al dirigirse al autor (trato, registro, cómo lo nombra en conversación). Se implementó solo el nombre. La hereda el epic 002 (su decisión 5).

Criterio de salida: `uv tool install` desde `git+...@devel` deja `tuku` en el PATH y `~/.tuku` poblado con el árbol del repositorio; `tuku init` en un directorio vacío produce el estado cero de `template/README.md` sin tocar la red; alguien que no sabe qué es TUKU escribe una línea en `AHORA.md` sin romper nada. `tuku init --author` deja el nombre en `LIBRO-DE-ESTILO.md`, y omitirlo no impide escribir. Se verifica con una persona, no con un diff. Y queda escrito qué movió en `spec/` o `docs/`.

Pendiente de re-verificación: el cierre del 2026-09-06 lo probó el autor sobre la instalación por `curl`. El modelo nuevo se re-verifica igual, sobre `uv tool install` + `tuku init`. La tarea de la Wishlist (una persona ajena al diseño instala y opina) sigue pendiente y ahora prueba el camino nuevo.

No entra: janitors, agentes, LLM. Tampoco el tipo de ciclo real de quien lo usa: arranca semanal y el tipo verdadero emerge después.

### Tests que necesita

Se rehacen los cuatro escenarios `001-00X` para el modelo nuevo y se agrega uno. Numeración estable: cada uno reemplaza al escenario viejo de su número, sin renumerar el resto. **Un solo test usa `pipx`/`uv tool install`**, el primero y con `--force`; el resto llama a la función `init` de `src/tuku/` con `TUKU_HOME` apuntando al checkout, sin instalar nada, y compara el árbol sembrado en vivo contra `template/<variante>/` como hace hoy `test_001_001`.

- `001-001-instalacion-con-uv-tool` — `uv tool install --force` real desde `git+...@devel` deja `tuku` en el PATH y `~/.tuku` poblado con el árbol del repositorio. Reemplaza al viejo `001-001-instalacion-minima`, que instalaba por `curl`. — **usa pipx: sí**
- `001-002-init-siembra-el-estado-cero` — `tuku init <dir>` produce byte a byte `template/vanilla/` más `AHORA.md` con las fechas resueltas, con `TUKU_HOME` local y sin red; es la verificación byte a byte que hoy hace `test_001_001`. Reemplaza al viejo `001-002-instalacion-local`. — **usa pipx: no**
- `001-003-destino-no-vacio` — `tuku init` se niega a sembrar en un directorio que ya tiene contenido, y `tuku init --force` lo siembra igual. Reemplaza al viejo `001-003`, que probaba el prompt de `install.sh` con `pexpect`; ahora es un flag y no hace falta pty. — **usa pipx: no**
- `001-004-init-author` — `tuku init --author "..."` deja el nombre en la sección "El autor" de `LIBRO-DE-ESTILO.md`, y omitir el flag (o pasarlo vacío) deja el vault operable sin nombre. Reemplaza al viejo `001-004-instalador-pregunta-el-nombre`. — **usa pipx: no**
- `001-005-init-no-toca-la-red` — con el socket parchado para fallar, `tuku init` completa la siembra igual. Aísla la afirmación "offline" que `001-002` da por supuesta. Nuevo, no reemplaza a nadie. — **usa pipx: no**

Marcador de pytest para `001-001`: hoy `pyproject.toml` tiene `lento`, que no basta porque ese test además necesita red y descarga un repositorio. Hace falta un marcador nuevo tipo `red` y que la corrida por defecto lo excluya igual que a `agentic` (`-m "not agentic and not red"`). Solo se enuncia; `pyproject.toml` no se toca en esta tarea.

## Epic 002. El día uno

Alguien instala TUKU y empieza a usarlo el mismo día. Todo lo que hace, lo hace sobre un vault que está vacío: cada cosa que necesita, la crea al escribirla.

Los ejemplos salen de [`referencia-faena.md`](../corpus/referencia/referencia-faena.md), martes 11 de agosto de 2026: primer día del turno, y el único que un vault recién instalado recibe sin inventar ámbitos previos.

Qué tiene que funcionar:

1. **El registro se reformatea sola.** El autor dicta y lo que queda escrito cumple las reglas de `docs/` y `spec/`: hora, ámbito, marca de la ontología cerrada, clasificación, cuerpo. En el día correcto y en orden cronológico.
2. **Los pendientes se abren y se cierran solos.** Un registro `**pendiente**` los abre, una `~~(Hecho)~~` los cierra, sin que el autor toque `PENDIENTES.md`.
3. **Escribir en un día actual o futuro fecha el pendiente.** Es la forma natural de agendar: el pendiente toma la fecha de ese día y se transcluye al inicio del día. No hace falta un comando aparte para fechar.
4. **Crear un ámbito lo deja bien guardado y enlaza hacia atrás.** El árbol queda correcto y las menciones sueltas del ciclo en curso se convierten en enlaces, de forma retroactiva.
5. **Crear una nota a petición.** El autor la pide, la nota se escribe, queda el registro en la bitácora que deja constancia, y si lo pidió así, queda enlazada a su ámbito: *"una nota respecto al cliente X: cómo funciona la industria del papel reciclado en la Araucanía"*.

Cubre la fase 1 completa, la fase 2 completa, y **la versión mínima** de las fases 3 y 5.

**Qué quiere decir versión mínima**, y es lo que impide que este epic no cierre nunca: crear un ámbito sí, resolver reglas por cercanía en un árbol profundo no; crear una nota y enlazarla sí, notas tipadas con plantilla y destilado no. Todo eso tiene versión completa y toda versión completa pide entrar. El día uno solo ejercita lo que el día uno puede ejercitar.

Antes de empezar hay que decidir:

1. Qué registros componen el día uno, representativas, con las tres marcas de la ontología cerrada.
2. Cómo se verifica lo que depende del agente: byte a byte para las consecuencias, otro criterio para la redacción.
3. Qué arnés de agente se usa y cómo se aísla para no gastar tokens por accidente.
4. **Resuelto el 2026-09-07.** Dónde vive el código y cómo se ejecuta. TUKU se distribuye como paquete Python instalable con `pipx` o `uv tool install` directo desde la rama `devel` del repo (`git+https://github.com/pewma-ai/tuku.git@devel`), sin pasar por PyPI. La instalación deja el repo completo en `~/.tuku`: código, `template/`, `spec/`, `reglas/`, el árbol entero. El ejecutable es `tuku`, un CLI con subcomandos de dos niveles `tuku <noun> <verb>`, todo en inglés, porque quien lo usa sabe inglés. `tuku init [<dir>]` siembra un vault nuevo copiando desde `~/.tuku/template/<variante>`, sin red, y reemplaza a `install.sh` y a `src/install_test_scenario.py`. La lógica de cada janitor vive en funciones importables bajo `src/tuku/`; el CLI es una capa fina de argparse, y los tests llaman a las funciones sin lanzar subprocesos, salvo el que prueba el propio `pipx install`. La especificación en prosa de cada janitor sigue en `reglas/janitors.tuku.md` del vault del autor, y su nombre canónico pasa a ser el comando `tuku <noun> <verb>` en vez de `jntr.<algo>`.
5. Dónde se especifica el comportamiento del agente al dirigirse al autor: trato, registro, cómo lo nombra en conversación. Viene abierta del epic 001, que implementó solo el nombre.
6. Si las cadencias se declaran acá con material prestado de `referencia-pyme.md`, o se difieren al epic 004. `referencia-faena.md` no declara ninguna, así que hoy la tercera marca de la ontología cerrada no tiene ejemplo en el día uno.

Lo que va a mover en el diseño, ya identificado:

- **La consecuencia "nota" no existe en `spec/flujo-informacion.md`.** Su tabla tiene pendientes, enlaces, cadencias y propuesta. El punto 5 la exige, y la spec dice que la lista es abierta, así que el arreglo es agregar un archivo de regla. Sale de la práctica de `mac-jpgil`, que ya la tiene resuelta.
- Si el formato de entrada no aguanta el dictado real, cambia [`../spec/bitacora.md`](../spec/bitacora.md).
- Cómo se verifica lo semi determinista, que hoy no está escrito en ninguna parte.

Criterio de salida: una persona instala, escribe durante un día y termina con pendientes abiertos, un ámbito nuevo y una nota enlazada, sin haber abierto `PENDIENTES.md` ni `ambitos/` a mano. Reproducible por inyección. Y queda escrito qué movió en `spec/` o `docs/`.

No entra: ciclos, cadencias que emitan, inferencia, y las versiones completas de ámbitos y notas.

## Epic 003. El día ciento cincuenta

Lo mismo del epic 002, sobre un vault que ya tiene meses encima. El estado inicial deja de estar vacío y pasa a ser un activo: hay ámbitos poblados, notas escritas y pendientes con historia de arrastre.

Es la segunda vuelta de las mismas capacidades, y es donde aparece casi todo lo que el día uno no puede enseñar:

1. **Las bitácoras nuevas traen enlaces desde el primer día**, hacia ámbitos y notas que ya existen. En el epic 002 no había a qué enlazar.
2. **Los pendientes se autoasignan a su ámbito** cuando el texto lo permite, en vez de quedar sueltos.
3. **Las notas llevan su "Ver además"** con el motivo de cada enlace, y el tejido se mantiene solo.
4. **Las versiones completas** de lo que el 002 dejó mínimo: los tres roles del árbol, la regla más cercana, notas tipadas y su destilado.

Cubre las fases 3 y 5 completas, y el resto de la 4 que no vive en la apertura de ciclo.

Va acá y no al final porque es el caso con datos reales: `mac-jpgil` lleva meses de bitácoras, ámbitos y vocabulario acumulado, y el autor es el usuario. Cada fricción que aparezca es una spec escrita por el uso.

Bloqueante resuelto en la sesión que podó `docs/libro-de-estilo.md`: **"Ver además" ya está en [`../spec/notas.md`](../spec/notas.md)**.

Criterio de salida: inyectar un ciclo de `mac-jpgil` sobre un vault poblado produce enlaces, asignación a ámbitos y notas tejidas sin intervención. Y queda escrito qué movió en `spec/` o `docs/`.

No entra: abrir y cerrar el ciclo, plan y resumen.

## Epic 004. Abrir y cerrar el ciclo

Que un ciclo se abra y se cierre sin perder nada, y que lo que el sistema propone al abrirlo valga la pena leerlo.

Las cadencias entran acá, y no antes, porque **emiten en la apertura del ciclo**: una cadencia declarada el día uno no produce nada hasta que pasa el tiempo. Se declaran en el epic 002 y se cosechan en este.

Cubre las fases 6 y 7, más lo que quedó de la 4.

**El corte interno importa y no se puede perder al fundir las dos fases**: la mecánica del ciclo (abrir, promover pendientes, aplanar transclusiones, archivar) se prueba entera **antes** de que exista quien escriba el plan y el resumen, con archivos falsos inyectados. Después se reemplazan por los de verdad sin tocar la mecánica. Es lo que mantiene separado lo determinista de lo que depende de un LLM, y sin esa separación el epic no se puede verificar.

Criterio de salida: abrir dos veces no duplica días, pendientes ni emisiones; cerrar dos veces no vuelve a mover; y hay una prueba que falla a propósito si se aplana antes de generar el resumen. El plan calcula capacidad contra lo declarado y no contra el ciclo entero.

No entra: proponer nada que el autor no haya pedido.

## Epic 005. Que note lo que nadie pidió

El agente deja de responder y empieza a observar: infiere ámbitos y notas tipadas (personas, clientes, sistemas) leyendo el histórico, detecta recurrencias que nadie declaró como cadencia, y propone.

Cubre la fase 9.

Va al final porque necesita las cuatro anteriores y porque es lo único que no tiene criterio byte a byte: se mide por la proporción de propuestas que el autor acepta, y esa medición solo tiene sentido después de varios ciclos de uso real.

Criterio de salida: la prueba dura es negativa. Rechazar una propuesta no deja rastro en ninguna primitiva, y eso sí se verifica con diff. Es el principio 3 convertido en test, y es lo que permite que el resto del epic sea difuso sin ser peligroso.

No entra: ejecutar cualquier cosa sin aprobación.

## Wishlist

Lo que hay que hacer y no bloquea a nadie. No son epics: entran cuando duelan.

- **Endurecimiento.** Los casos de error, la reconstrucción completa y la idempotencia medida sobre el sistema entero junto y no janitor por janitor. Era la fase 8, y no agrega capacidades: cierra huecos. La regla que la gobierna vale desde ya, aunque la fase no exista: **un error del autor nunca se rechaza, se reporta.**
- **Probar la instalación con una persona ajena al diseño.** Que instale con el one-liner de `curl`, escriba un registro leyendo solo `AGENTS.md`, y cuánto le toma.
- **Publicar el vault en web** con Quartz.
- **Telegram como canal de captura móvil.**

## Rescatar de `devel/VAULT/`

De simple a complejo: se rescata lo puntual que un epic en curso necesite, nunca un bloque completo por adelantado.

## Cómo se actualiza

La tabla de Estado se edita al empezar y cerrar cada epic, y al resolver una decisión abierta (se reescribe como afirmación, no se borra). Decisiones de diseño que afectan al producto van a [`../spec/README.md`](../spec/README.md), no aquí.
