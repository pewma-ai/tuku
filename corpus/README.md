# Corpus

`referencia/` es ficticio y público. El corpus real vive en un repositorio privado aparte.

**Estos dos archivos son las únicas guías canónicas de los tests.** Ningún escenario inventa material por su cuenta.

| Archivo | Perfil | Para qué |
| --- | --- | --- |
| [`referencia/referencia-faena.md`](referencia/referencia-faena.md) | Damián Ulloa, jefe de software de un observatorio; por turnos, dominio propio del autor | Ground truth principal y columna de la escalera de estados. Su fecha de arranque (2026-08-11) es la que fijan los tests |
| [`referencia/referencia-pyme.md`](referencia/referencia-pyme.md) | Andrea Bustos, dueña de una PYME de insumos educacionales | Dominio ajeno al del autor, y cadencias de fecha impuesta desde afuera |

Los dos se leen igual: **Parte 1** es el dictado crudo, **Parte 2** la tabla de verdad en formato [`spec/bitacora.md`](../spec/bitacora.md), **Parte 3** el estado del repositorio reconstruible desde ahí.

## Qué cubre cada uno

Ninguno basta solo.

| | faena | pyme |
| --- | --- | --- |
| Ciclo | El turno: nueve días arriba, cuatro de descanso | La semana, lunes a domingo |
| Dominio | El del autor del diseño | Ajeno, comercial, calendario impuesto |
| `**cadencia**` | **Ninguna** | Doce: dos de evento, una de ausencia |
| Traspaso de rol | Con hora, parte el día en dos | No aplica |
| `~~(Hecho)~~` sin pendiente previo | Abundante, medido con un `#REVISAR` en el archivo | Raro |

La tercera marca de la ontología cerrada solo tiene ejemplo en pyme: todo escenario de cadencias genera desde ahí.

## Formato

La Parte 2 de ambos está en formato TUKU. La de faena se tradujo desde el formato de `mac-jpgil`, de donde salió; su Parte 3 sigue pendiente y lo dice con un `#REVISAR` propio.

Si `spec/bitacora.md` cambia, **la Parte 2 se regenera**: es derivada. La fuente es la Parte 1, que es habla y no cambia.

## Guía, no fixture

Un test **nunca copia literal** una porción del corpus. Un agente LLM avanzado **genera** el fixture desde acá, adaptado a lo que el escenario prueba. Detalle en [`../tests/escenarios/README.md`](../tests/escenarios/README.md), sección "Fixtures".

Los casos narrativos viven en [`../tests/escenarios/`](../tests/escenarios/README.md): un Dado/Cuando/Entonces es una aserción, no un dato. `ANTIGUO/` es material del diseño anterior.
