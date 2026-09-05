# Epics de TUKU

> Unidad de entrega, no unidad técnica. Un epic termina con algo que una persona puede usar. Las fases de [`que_implementar.md`](que_implementar.md) son el corte técnico interno: un epic puede abarcar varias y no cierra sin cumplir el criterio de salida de las que abarca.

Se numeran por orden de ejecución, tres dígitos. Ese número es el `XXX` de `corpus/escenarios/XXX-YYY-slug.md` y de sus tests.

Solo los dos primeros están desarrollados. El resto se escribe cuando el epic 002 haya enseñado lo que hoy no sabemos.

## Los epics mueven el diseño

El diseño lo dirige la experimentación, no al revés: `spec/` y `docs/` cambian por efecto de los epics. Cada epic entrega dos cosas, su producto y lo que le enseñó al diseño (aunque sea nada). Dentro de un epic la spec manda sobre el código; entre epics, el experimento manda sobre la spec.

## Estado

Actualizado el 2026-09-04.

| Epic | Nombre | Estado | Qué falta para cerrarlo |
| --- | --- | --- | --- |
| 001 | Un TUKU mínimo instalable | en curso | probarlo con una persona, podar `docs/libro-de-estilo.md` |
| 002 | El día uno simulado | sin empezar | depende del epic 001 |
| 003+ | El resto | sin desarrollar | se escriben al cerrar el epic 002 |

Lo hecho en el 001: `template/vanilla/` (estado cero, 11 archivos) y `src/install_test_scenario.py` (mecanismo). Diario en [`iteraciones/`](iteraciones/README.md); casos narrativos en `../corpus/escenarios/`; arnés en `../tests/escenarios/` y `../tests/scripts/`.

Preparación previa, fuera de los epics: `spec/` y `docs/glosario.md` ordenan el vocabulario, `que_implementar.md` quedó reducido al plan de fases. Punto de partida, no diseño cerrado.

## Epic 001. Un TUKU mínimo instalable

Que una persona nueva instale un vault en un directorio vacío y empiece a escribir el mismo día, sin configurar nada y sin saber qué es TUKU. Va primero porque obliga al repositorio a tener estructura, instalación y template, y nada más lo va a forzar. Cubre la fase 0.

Decidido:

1. El instalador es un template que se copia, no un CLI. El empaquetado se difiere a cuando haya janitors.
2. `template/`, una carpeta por variante, hermanas y sin composición. `vanilla/` es la mínima.
3. `reglas/config.tuku.md` declara zona horaria y tipo de ciclo, en prosa.
4. El código vive en `src/` (raíz), no en `devel/VAULT/src/` (diseño anterior). Primer archivo: `src/install_test_scenario.py`.
5. Escenarios narrativos (Dado/Cuando/Entonces): dato en `corpus/escenarios/`, arnés en `tests/escenarios/` y `tests/scripts/`.
6. Instalar es una línea de `curl` (`install.sh`), no `git clone`. Probado contra `pewma-ai/tuku@devel` real.
7. Sobrescribir se pregunta en `install.sh`, salvo con `TUKU_FORCE=1`. `install_test_scenario.py` sobrescribe siempre.
8. El estado cero se verifica byte a byte con fecha fija (`--desde 2026-08-11`, la del ground truth en `referencia-faena.md`), distinta de la que usa el autor real. Encontró un bug real: días etiquetados por posición, ya corregido.

Falta decidir: podar `docs/libro-de-estilo.md`. Mover a `spec/` la matriz de reglas y responsabilidades (§7, lo único no duplicado), y recién entonces podar.

Lo que va a mover en el diseño: esa poda, y probablemente `reglas/config.tuku.md`, ya en decisiones abiertas.

Criterio de salida: instalar en vacío produce el estado cero de `docs/principios.md` §2; alguien que no sabe qué es TUKU escribe una línea en `AHORA.md` sin romper nada. Se verifica con una persona, no con un diff. Y queda escrito qué movió en `spec/` o `docs/`.

No entra: janitors, agentes, LLM. Tampoco el tipo de ciclo real de quien lo usa: arranca semanal y el tipo verdadero emerge después.

## Epic 002. El día uno simulado

Un conjunto de entradas de bitácora estándar que, inyectadas sobre el estado cero, producen sus consecuencias de forma reproducible. Es también la plataforma de pruebas que todo lo demás va a usar.

Va segundo porque fuerza a la vez el testing semi determinista, la validación del stack recomendado (Obsidian + directorio + agente que lee reglas) y la primera prueba real del formato de entrada. Semi determinista porque la entrada depende de un agente: qué se compara byte a byte y qué solo se evalúa es el problema central del epic.

Cubre las fases 1 y 2 completas, y partes de la 3 y la 5 (ámbito nuevo, enlazar una nota).

Vocabulario: el día uno produce consecuencias (pendientes, ámbitos, enlaces, notas tipadas), no "entidades" (diseño anterior, no aparece en `spec/`).

Para empezar hay que decidir:

1. Qué entradas componen el día uno, representativas, con las tres marcas de la ontología cerrada.
2. Cómo se verifica lo que depende del agente: byte a byte para consecuencias, otro criterio para la redacción.
3. Qué arnés de agente se usa y cómo se aísla para no gastar tokens por accidente.
4. Dónde vive el código y cómo se ejecuta. Ya no se puede diferir.

Es el epic que más va a mover el diseño: si el formato de entrada no aguanta el dictado real, cambia `spec/bitacora.md`. También obliga a escribir cómo se verifica lo semi determinista, que hoy no está en ninguna parte.

Criterio de salida: inyectar el día uno sobre el estado cero produce las consecuencias esperadas, es reproducible, y abre en Obsidian sin errores. Y queda escrito qué movió en `spec/` o `docs/`.

No entra: abrir/cerrar ciclos, cadencias, inferencia semántica. Tampoco la suite actual de `tests/` (diseño anterior, se rehace).

## Rescatar de `devel/VAULT/`

De simple a complejo: se rescata lo puntual que un epic en curso necesite, nunca un bloque completo por adelantado.

## Material para epics siguientes

Rescatado de `technical_stack.md` antes de borrarlo. Ninguna decisión tomada: Obsidian como visor (el epic 002 lo prueba), Quartz para publicar el vault en web, Telegram como canal de captura móvil.

## Epics siguientes

Sin desarrollar hasta que cierre el epic 002. Material de partida: fases 3 a 9 de [`que_implementar.md`](que_implementar.md) — ámbitos, cadencias, notas y enlaces, ciclo, plan y resumen, endurecimiento, inferencia semántica.

## Cómo se actualiza

La tabla de Estado se edita al empezar y cerrar cada epic, y al resolver una decisión abierta (se reescribe como afirmación, no se borra). Decisiones de diseño que afectan al producto van a `../spec/README.md`, no aquí.
