# Epic 003 · El día uno, dictado

> El mismo día uno del epic 002, dictado en lenguaje natural en vez de invocado a mano. El vault de salida tiene que ser el mismo.

Es la réplica agéntica del 002 y esa es su forma de verificarse: el estado final ya existe, producido a mano y revisado, así que el epic no tiene que decidir qué es correcto, solo si el agente llega ahí.

Un turno por escenario. El autor dicta y el agente ejecuta. La conversación de ida y vuelta, donde el agente delibera y el autor rectifica, es el epic 004: acá un fallo tiene que poder atribuirse a una sola cosa.

## Qué entrega el epic

El [`AGENTS.md`](../../template/vanilla/AGENTS.md) que `tuku init` siembra en cada vault. Es el documento que hace que un agente cualquiera opere el vault de la misma forma, y lo que este epic prueba es si funciona ([`spec/despacho.md`](../../spec/despacho.md)).

El resto (el dictado, el arnés, la comparación) es instrumento para medirlo.

## La escalera: de menos a más

El LLM está en el medio y no repite resultado, así que el orden de construcción no puede ser el de la narración. Se sube por dos ejes a la vez.

**Cuánto agente hay**, de nada a todo:

| Peldaño | Qué hay | Cuesta |
| --- | --- | --- |
| 1 | Ningún agente: el vault y su `AGENTS.md` | nada |
| 2 | Agente que responde qué haría, sin ejecutar | un turno |
| 3 | Agente que ejecuta un hecho sin consecuencias | un turno |
| 4 | Agente que ejecuta un hecho con consecuencia | un turno |
| 5 | Agente contra los casos negativos | un turno |
| 6 | Agente contra el día completo | un turno largo |

**Qué se compara**, de lo barato a lo caro:

| Nivel | Aserción | Determinista |
| --- | --- | --- |
| 1 | El archivo existe y sus comandos existen en el CLI | sí |
| 2 | El agente nombra el comando correcto | no, pero no toca el vault |
| 3 | La traza de comandos ejecutados es la esperada | no |
| 4 | El diff del vault es el esperado | no |
| 5 | El vault final equivale al del epic 002 | no |

El primer peldaño de cada eje no gasta un token y es el que más valor deja instalado: si la tabla de despacho nombra un comando que no existe, ningún agente del mundo lo arregla.

## Cada escenario agéntico tiene un gemelo determinista

Los seis peldaños prueban capacidades que el epic 002 ya dejó en verde con los comandos escritos a mano. Eso no es redundancia, es el instrumento de diagnóstico: cuando un escenario del 003 falla, su gemelo del 002 dice de quién es el defecto. Si el gemelo está verde, el agente eligió mal; si está rojo, el comando está roto y el agente no tiene nada que ver.

Por eso ningún escenario de este epic prueba una capacidad que el 002 no haya probado antes. Si aparece una, es que el epic se está saliendo de su alcance.

## Cómo se observa al agente

El agente corre **dentro del vault**, que es como se opera en la vida real: lee su `AGENTS.md` porque está ahí, no porque el test se lo pegue en el prompt. Un prompt de test que explique lo que el `AGENTS.md` ya dice invalida el escenario, porque entonces se está probando el prompt.

Lo que ejecuta se captura con un `tuku` puesto al frente del `PATH` que anota los argumentos y delega en el real. El agente no tiene que cooperar ni saber que está siendo observado, y la traza queda como una lista de comandos que se relee, se compara y se vuelve a correr.

De ahí salen las tres evidencias, y ninguna es el texto de la conversación:

1. **La traza:** qué comandos, con qué campos, en qué orden.
2. **El diff del vault:** lo mismo que afirma todo el epic 002.
3. **Lo que no ocurrió:** que no editó ningún archivo a mano, que no abrió pendientes que nadie pidió, que no inventó un cierre.

La tercera es la que se rompe en silencio y por eso se afirma explícitamente.

## Qué hace fallar y qué solo se reporta

Un test que exige a un LLM devolver el mismo texto dos veces está mal escrito. La línea es esta:

- **Falla:** un comando distinto, un campo de la ontología cerrada distinto (la marca, el ámbito, el día), una consecuencia que no se aplicó, un archivo tocado a mano, un efecto que nadie pidió.
- **Se reporta y no falla:** la redacción del cuerpo, la clasificación abierta, el orden entre comandos que no dependen entre sí.

Lo que se reporta no es ruido: una diferencia de redacción repetida es información sobre el libro de estilo, y una de clasificación es vocabulario del autor que todavía no está declarado.

Una sola corrida por escenario. Si el resultado no es estable entre corridas, eso es el hallazgo del epic y no un test que haya que repetir hasta que pase.

## Estado inicial y cadena

Empieza donde el 002, en el fixture `vacio`, y termina en el mismo `primer-dia`. La diferencia no está en el estado inicial sino en quién arma las llamadas, y por eso este epic va aparte y no dentro del anterior.

Los escenarios se encadenan en [`playground/`](../../playground/README.md) igual que los del 002: el estado final de uno es el inicial del siguiente, declarado con un `cp -r` en su `## Estado inicial`.

## El fixture del dictado

```text
fixtures/003-dictado/
  martes-11.md    # lo que el autor dijo, en lenguaje natural
  README.md       # de dónde sale cada frase, y contra qué se regenera
```

**Sale del vault del 002, no del corpus.** Cada invocación de `tuku` de la cadena del 002 se lee al revés y se reescribe como la frase que la habría provocado. El destino manda sobre el origen, porque lo que este epic afirma es que el agente llega al mismo vault, y ese vault ya existe y está revisado.

No sale de [`referencia-faena.md`](../../corpus/referencia/referencia-faena.md), y conviene decirlo porque la versión anterior de este archivo afirmaba que sí. El corpus tiene un día de trabajo entero con una docena de ámbitos; el epic 002 se quedó con un día más chico y doméstico, que es lo único que un vault del día uno puede recibir. El corpus vuelve en el epic 005, cuando el vault tenga con qué recibirlo.

Las horas van dichas como las diría una persona ("a las dos y veinte"), porque el vault del 002 las tiene exactas y sin ellas la comparación no podría serlo. Lo que se prueba es la traducción, no la adivinación.

## Dónde queda cada corrida

Cada escenario escribe en `playground/003-<escenario>/` y limpia esa carpeta antes de usarla. Solo esa.

Hasta el 2026-09-09 esto era un `rm -rf 003-*` al empezar el epic, y eso borraba también el resultado de los escenarios que la corrida no iba a regenerar. En un epic determinista da igual, porque todo se rehace en dos segundos; en uno agéntico se lleva por delante turnos que costaron tokens y que no se repiten. Una carpeta tuya que empiece con `003-` sobrevive salvo que le pongas el nombre exacto de un escenario.

## Cómo se corre

El primer escenario es determinista y entra en la corrida por defecto. Los otros cinco gastan tokens y se piden explícitos:

```bash
uv run pytest tests/escenarios/ -k 003_01
```

```bash
uv run pytest -m agentic tests/escenarios/
```

## Decisiones previas

Las tres están tomadas y las tres están implementadas en [`../scripts/agente.py`](../scripts/agente.py).

1. **Qué arnés.** `agy`, y cambiable sin tocar un test: `TUKU_AGENTE` elige cuál, `TUKU_AGENTE_BIN` el ejecutable y `TUKU_AGENTE_MODELO` el modelo. Agregar otro arnés es decirle a `ARNESES` cómo se le pasa un turno.
2. **Qué modelo.** El barato que alcance. Si un escenario solo pasa con el caro, eso es un hallazgo sobre el `AGENTS.md` y no una razón para subir de modelo.
3. **Cómo se genera el dictado sin contaminarlo.** Derivado del vault del 002 y auditable frase por frase, con la regla escrita en el `README.md` del fixture: ninguna frase nombra un comando, una marca, un ámbito ni un archivo.

Lo demás ya estaba decidido: el comportamiento del agente se especifica en el `AGENTS.md` del vault ([`spec/despacho.md`](../../spec/despacho.md)) y su conducta al dirigirse al autor en [`spec/agente.md`](../../spec/agente.md).

## Cómo se escribe un turno en el escenario

El `.md` es la fuente ejecutable, igual que en el epic 002. Un bloque `bash` es un comando; un bloque `agente` es lo que el autor le dice:

````text
Cuando el autor dicta

```agente
A las dos y veinte, hay que avisarle de los gastos comunes a la administradora.
```
````

El arnés lo corre dentro de `mi-vault/`, con un `tuku` al frente del `PATH` que anota `argv` y delega en el real. La corrida deja el turno en `corrida.turno`, con `traza`, `comandos` e `invocaciones_de("entry", "add")`.

## Criterio de salida

Dictar el día uno del corpus produce un vault equivalente al que el epic 002 produjo a mano: los campos de la ontología cerrada idénticos, las mismas consecuencias aplicadas, y ningún efecto que el dictado no haya pedido.

## No entra

- **La conversación de varios turnos**, donde el agente delibera, pregunta y el autor rectifica. Epic 004, que además refina el `AGENTS.md` con lo que este epic descubra.
- **Las propuestas.** El epic 002 no las produce, así que replicarlo tampoco. La consecuencia sin comando entra cuando exista, en el epic 004.
- **El histórico poblado y el destilado** (Epic 005). **Inferir lo que nadie pidió** (Epic 007).

## Escenarios del epic

Los cinco últimos gastan tokens y van marcados `agentic`.

1. `003-01` El vault dice a dónde va cada cosa. Sin agente: el `AGENTS.md` está sembrado y `tuku doctor` confirma que cada comando que nombra existe.
2. `003-02` El agente lee el vault. Un turno que responde qué comando usaría, sin ejecutar nada. El diff es vacío por construcción.
3. `003-03` Un hecho, un comando. El dictado más simple posible deja una línea en `AHORA.md` y nada más.
4. `003-04` Un hecho con consecuencia. El pendiente se abre en `PENDIENTES.md`, que es donde el agente tiene que acordarse de la segunda llamada.
5. `003-05` Lo que no se registra y lo que no se inventa. "Recuérdame" desaparece del registro, un cierre sin pareja se reporta sin inventar el pendiente, y ningún archivo se edita a mano.
6. `003-06` El día completo. El dictado entero del martes 11 contra el vault que dejó el epic 002.
