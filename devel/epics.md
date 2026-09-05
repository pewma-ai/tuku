# Epics de TUKU

> Unidad de entrega, no unidad técnica. Un epic termina con algo que una persona puede usar. Las fases de [`que_implementar.md`](que_implementar.md) son el corte técnico interno: un epic puede abarcar varias y no cierra sin cumplir el criterio de salida de las que abarca.

Se numeran por orden de ejecución, tres dígitos. Ese número es el `XXX` de `tests/escenarios/XXX-YYY-slug.md` y de sus tests.

Solo los dos primeros están desarrollados. El resto se escribe cuando el epic 002 haya enseñado lo que hoy no sabemos.

## Los epics mueven el diseño

El diseño lo dirige la experimentación, no al revés: `spec/` y `docs/` cambian por efecto de los epics. Cada epic entrega dos cosas, su producto y lo que le enseñó al diseño (aunque sea nada). Dentro de un epic la spec manda sobre el código; entre epics, el experimento manda sobre la spec.

## Qué separa un epic del siguiente

**El estado del vault con el que empieza**, no la primitiva que construye. Las fases de `que_implementar.md` cortan por primitiva (entrada, pendientes, ámbitos, cadencias, notas); los epics cortan por el estado inicial, y por eso un epic abarca partes de varias fases.

El motivo es el criterio de entrega: "los pendientes funcionan" no es una experiencia que alguien pueda usar, "el día uno funciona" sí lo es. Y el propio `que_implementar.md` ya lo pedía sin nombrarlo, en su criterio de corte 2: si un estado inicial nuevo es lo que obliga a partir el trabajo, entonces el estado inicial es el eje.

La consecuencia práctica es que los epics 002 y 003 construyen **las mismas capacidades dos veces**, contra vaults distintos. No es repetición: en el 002 el vault está vacío y cada capacidad tiene que crear lo que necesita; en el 003 ya existe un árbol de ámbitos, notas y pendientes con historia, y la misma capacidad tiene que aprovecharlo. Casi todo lo que se descubre está en la segunda vuelta.

## De dónde sale el material

Las prácticas que se implementan salen de [`mac-jpgil`](../../mac-jpgil), el vault real del autor, donde llevan meses probadas: sus `AGENTS.md`, templates, procesos y reglas. La consecuencia "nota" del epic 002 sale de ahí, no de un diseño en abstracto.

**Se trae epic por epic, nunca por adelantado.** Ir a buscar todo lo que `mac-jpgil` hace y especificarlo antes de necesitarlo es la forma más rápida de construir sobreingeniería sobre prácticas que quizá no sobreviven al empaquetado. Cuando un epic empieza, se revisa qué resolvió ya el vault real para eso, y solo eso.

## Estado

Actualizado el 2026-09-05.

| Epic | Nombre | Estado inicial | Estado | Qué falta para cerrarlo |
| --- | --- | --- | --- | --- |
| 001 | Un TUKU mínimo instalable | `vacio` | en curso | probarlo con una persona |
| 002 | El día uno | `vacio` → `primer-dia` | sin empezar | depende del epic 001 |
| 003 | El día ciento cincuenta | `ciclo-en-curso` | sin empezar | depende del epic 002 |
| 004 | Abrir y cerrar el ciclo | `ciclo-por-cerrar` | sin empezar | depende del epic 003 |
| 005 | Que note lo que nadie pidió | `historico` | sin empezar | depende del epic 004 |

Lo hecho en el 001: `template/vanilla/` (el estado cero) y `src/install_test_scenario.py` (mecanismo). Diario en [`iteraciones/`](iteraciones/README.md); casos narrativos y arnés en `../tests/escenarios/`, pasos compartidos en `../tests/scripts/`.

Preparación previa, fuera de los epics: `spec/` y `docs/glosario.md` ordenan el vocabulario, [`que_implementar.md`](que_implementar.md) quedó reducido al plan de fases. Punto de partida, no diseño cerrado.

## Epic 001. Un TUKU mínimo instalable

Que una persona nueva instale un vault en un directorio vacío y empiece a escribir el mismo día, sin configurar nada y sin saber qué es TUKU. Va primero porque obliga al repositorio a tener estructura, instalación y template, y nada más lo va a forzar. Cubre la fase 0.

Decidido:

1. El instalador es un template que se copia, no un CLI. El empaquetado se difiere a cuando haya janitors.
2. `template/`, una carpeta por variante, hermanas y sin composición. `vanilla/` es la mínima.
3. `reglas/config.tuku.md` declara zona horaria y tipo de ciclo, en prosa.
4. El código vive en `src/` (raíz), no en `devel/VAULT/src/` (diseño anterior). Primer archivo: `src/install_test_scenario.py`.
5. Escenarios narrativos (Dado/Cuando/Entonces): caso y arnés juntos en `tests/escenarios/`, pasos compartidos en `tests/scripts/`.
6. Instalar es una línea de `curl` (`install.sh`), no `git clone`. Probado contra `pewma-ai/tuku@devel` real.
7. Sobrescribir se pregunta en `install.sh`, salvo con `TUKU_FORCE=1`. `install_test_scenario.py` sobrescribe siempre.
8. El estado cero se verifica byte a byte con fecha fija (`--desde 2026-08-11`, la del ground truth en `referencia-faena.md`), distinta de la que usa el autor real. Encontró un bug real: días etiquetados por posición, ya corregido.

**Decidido:** `docs/libro-de-estilo.md` se podó y se borró. Las ocho secciones que duplicaba a `spec/` desaparecieron con él; las tres filas de su matriz que no estaban cubiertas ([`ver además` y su motivo](../spec/notas.md), [el emparejamiento no literal al cerrar un pendiente](../spec/agente.md)) se migraron antes de borrar. El bug que destapó la migración: `spec/bitacora.md` citaba este documento de diseño como si fuera el `LIBRO-DE-ESTILO.md` que se instala en el vault del autor. Corregido.

Lo que va a mover en el diseño: esa poda, y probablemente `reglas/config.tuku.md`, ya en decisiones abiertas.

Criterio de salida: instalar en vacío produce el estado cero de `template/README.md`; alguien que no sabe qué es TUKU escribe una línea en `AHORA.md` sin romper nada. Se verifica con una persona, no con un diff. Y queda escrito qué movió en `spec/` o `docs/`.

No entra: janitors, agentes, LLM. Tampoco el tipo de ciclo real de quien lo usa: arranca semanal y el tipo verdadero emerge después.

## Epic 002. El día uno

Alguien instala TUKU y empieza a usarlo el mismo día. Todo lo que hace, lo hace sobre un vault que está vacío: cada cosa que necesita, la crea al escribirla.

Qué tiene que funcionar:

1. **La entrada se reformatea sola.** El autor dicta y lo que queda escrito cumple las reglas de `docs/` y `spec/`: hora, ámbito, marca de la ontología cerrada, clasificación, cuerpo. En el día correcto y en orden cronológico.
2. **Los pendientes se abren y se cierran solos.** Una entrada `**pendiente**` los abre, una `~~(Hecho)~~` los cierra, sin que el autor toque `PENDIENTES.md`.
3. **Escribir en un día actual o futuro fecha el pendiente.** Es la forma natural de agendar: el pendiente toma la fecha de ese día y se transcluye al inicio del día. No hace falta un comando aparte para fechar.
4. **Crear un ámbito lo deja bien guardado y enlaza hacia atrás.** El árbol queda correcto y las menciones sueltas del ciclo en curso se convierten en enlaces, de forma retroactiva.
5. **Crear una nota a petición.** El autor la pide, la nota se escribe, queda la entrada en la bitácora que deja constancia, y si lo pidió así, queda enlazada a su ámbito: *"una nota respecto al cliente X: cómo funciona la industria del papel reciclado en la Araucanía"*.

Cubre la fase 1 completa, la fase 2 completa, y **la versión mínima** de las fases 3 y 5.

**Qué quiere decir versión mínima**, y es lo que impide que este epic no cierre nunca: crear un ámbito sí, resolver reglas por cercanía en un árbol profundo no; crear una nota y enlazarla sí, notas tipadas con plantilla y destilado no. Todo eso tiene versión completa y toda versión completa pide entrar. El día uno solo ejercita lo que el día uno puede ejercitar.

Antes de empezar hay que decidir:

1. Qué entradas componen el día uno, representativas, con las tres marcas de la ontología cerrada.
2. Cómo se verifica lo que depende del agente: byte a byte para las consecuencias, otro criterio para la redacción.
3. Qué arnés de agente se usa y cómo se aísla para no gastar tokens por accidente.
4. Dónde vive el código y cómo se ejecuta. Ya no se puede diferir.

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
- **Publicar el vault en web** con Quartz.
- **Telegram como canal de captura móvil.**

## Rescatar de `devel/VAULT/`

De simple a complejo: se rescata lo puntual que un epic en curso necesite, nunca un bloque completo por adelantado.

## Cómo se actualiza

La tabla de Estado se edita al empezar y cerrar cada epic, y al resolver una decisión abierta (se reescribe como afirmación, no se borra). Decisiones de diseño que afectan al producto van a [`../spec/README.md`](../spec/README.md), no aquí.
