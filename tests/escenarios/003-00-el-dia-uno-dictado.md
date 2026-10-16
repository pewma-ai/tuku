# Epic 003 · El día uno, dictado

> **Marco:** [Brief de TUKU](../../docs/brief.md) · [Principios normativos](../../docs/principios.md) · [Especificaciones](../../spec/README.md) · [Lecciones de mac-jpgil](../../devel/lecciones-macjpgil.md)

El autor dicta su primer día en lenguaje natural y el agente ejecuta las operaciones mediante el CLI de TUKU: cada hecho, compromiso o nota se traduce en comandos deterministas gobernados por [`AGENTS.md`](../../template/vanilla/AGENTS.md), alcanzando un vault de salida equivalente al producido a mano en el [Epic 002](002-00-el-dia-uno-a-mano.md).

## Principios rectores del epic

1. **El agente es un secretario, no un dueño ([P3](../../docs/principios.md#L25)):** Traduce la intención del autor a operaciones del CLI y consulta ante ambigüedades; nunca inventa datos ni toma decisiones ejecutivas.
2. **Todo baja hasta donde alcance el determinismo ([P4](../../docs/principios.md#L33)):** El agente compila el dictado a comandos CLI (`tuku`) y no toca archivos a mano; la ejecución en disco es 100% determinista.
3. **Las reglas se escriben en prosa, en un solo lugar ([P5](../../docs/principios.md#L47)):** La conducta del agente se rige por el `AGENTS.md` sembrado en el vault ([`spec/despacho.md`](../../spec/despacho.md)) y sus contratos en [`spec/agente.md`](../../spec/agente.md).
4. **Las carpetas archivan; los enlaces conectan ([P7](../../docs/principios.md#L63)):** La regla más cercana prevalece y el agente respeta las carpetas estructurales y la tabla de Límites.
5. **Reconstrucción determinista ([P9](../../docs/principios.md#L79)):** El estado final generado por el dictado equivale en ontología cerrada y consecuencias al obtenido a mano en el [Epic 002](002-00-el-dia-uno-a-mano.md).

## Qué se verifica

- **Traza del agente:** Comandos invocados, flags y orden capturados mediante el shim de intercepción, garantizando que el agente opera exclusivamente a través del CLI.
- **Superficie del vault:** Diff exacto de la ontología cerrada (marcas, fechas, ámbitos y consecuencias) contra el vault esperado en `playground/`.
- **Límites negativos:** Que no edite archivos a mano, no invente cierres huérfanos, descarte muletillas de voz y consulte antes de actuar ante casos ambiguos o carpetas protegidas.

## Escenarios BDD del epic

### Verificación determinista (sin consumo de tokens)

- [`003-01-el-vault-dice-a-donde-va.md`](003-01-el-vault-dice-a-donde-va.md) — Comprueba que todos los comandos declarados en la tabla de despacho existen en el CLI (`tuku doctor`).

### Escenarios agénticos (`-m agentic`)

- [`003-10-el-dia-uno-en-un-turno.md`](003-10-el-dia-uno-en-un-turno.md) — El criterio de salida: el día uno dictado entero en un turno deja un vault equivalente al del Epic 002, con lo que no se anota en el mismo turno (una consulta, una instrucción, una pregunta, un cierre ambiguo y un pedido sin comando).
- [`003-11-el-dia-que-no-se-dicta.md`](003-11-el-dia-que-no-se-dicta.md) — Un hecho con hora y sin día cae en el último día del ciclo que ya tiene registros.
- [`003-08-el-mismo-vault-otro-arnes.md`](003-08-el-mismo-vault-otro-arnes.md) — Portabilidad: evalúa que las reglas operativas dependen del vault y no del arnés de ejecución (`hermes`).
- [`003-09-el-mismo-vault-tercer-arnes.md`](003-09-el-mismo-vault-tercer-arnes.md) — Portabilidad, tercer caso: el mismo dictado bajo `claude` con sonnet en esfuerzo bajo, el único arnés que no descubre solo el `AGENTS.md`.

Del `003-02` al `003-07` medían lo mismo de a una frase y se fundieron en el `003-10` el 2026-10-16; el día derivado del `003-07` quedó en el `003-11`.
