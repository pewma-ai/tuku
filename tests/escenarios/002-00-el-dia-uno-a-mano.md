# Epic 002 · El día uno, a mano

> **Marco:** [Brief de TUKU](../../docs/brief.md) · [Principios normativos](../../docs/principios.md) · [Especificaciones](../../spec/README.md) · [Lecciones de mac-jpgil](../../devel/lecciones-macjpgil.md)

El autor instala TUKU y opera su primer día entero mediante comandos directos (`tuku`) sobre un vault inicialmente vacío: cada compromiso, ámbito o nota que necesita se crea al registrarse, estampando constancia cronológica en la bitácora del ciclo y aplicando sus consecuencias atómicas e idempotentes.

## Principios rectores del epic

1. **El archivo de texto es lo primero ([P1](../../docs/principios.md#L9)):** Toda operación determinista tiene su equivalente «A mano» documentado.
2. **La organización emerge del uso ([P2](../../docs/principios.md#L17)):** No se preconfiguran taxonomías ni frentes artificiales; nacen de los registros diarios.
3. **Todo baja hasta donde alcance el determinismo ([P4](../../docs/principios.md#L33)):** La captura y la sincronización de tablas y vistas son 100% mecánicas y libres de LLM.
4. **Conjunto canónico inmutable y tres ejes ([P6](../../docs/principios.md#L55)):** `AHORA.md` y `PENDIENTES.md` son fuentes primarias; ninguna vista guarda registros paralelos.
5. **Reconstrucción determinista ([P9](../../docs/principios.md#L79)):** Reconstruir lo derivado desde el canónico (`tuku rebuild`) devuelve un resultado idéntico byte a byte.

## Qué se verifica

- **Superficie del vault:** Diff exacto entre estados de `playground/`, sin efectos colaterales y con estricta idempotencia (el segundo pase produce diff vacío).
- **Superficie del comando:** Contrato estricto del CLI ([`spec/cli.md`](../../spec/cli.md)): códigos de salida `0` (éxito), `1` (rechazo informativo) y `2` (error de sintaxis de argumentos), mensajes con diagnóstico y acción correctiva, y presencia del campo «A mano».
- **Aceptación humana:** Criterios de legibilidad directa en Obsidian para asegurar experiencia natural y perdurabilidad a 20 años.

## Escenarios BDD del epic

### Cadena determinista (herencia de estado en `playground/`)

- [`002-01-abrir-ciclo.md`](002-01-abrir-ciclo.md) — Abre el ciclo semanal desde plantilla editable de lunes a domingo.
- [`002-02-registro-en-su-dia.md`](002-02-registro-en-su-dia.md) — Inserta registros en el día de hoy en estricto orden cronológico.
- [`002-03-lint-de-registro.md`](002-03-lint-de-registro.md) — Valida ontología cerrada estricta y ontología abierta libre y permisiva.
- [`002-04-abrir-pendiente.md`](002-04-abrir-pendiente.md) — Apertura atómica e idempotente de compromiso en `PENDIENTES.md`.
- [`002-05-cerrar-pendiente.md`](002-05-cerrar-pendiente.md) — Cierre literal con `~~(Hecho)~~` y reporte orientador de cierres huérfanos.
- [`002-06-fechar-pendiente.md`](002-06-fechar-pendiente.md) — Fechado de compromisos directo con `tuku todo open --when` y vía bitácora.
- [`002-08-crear-ambito.md`](002-08-crear-ambito.md) — Alta de ámbito con transclusiones y enlazado retroactivo en el ciclo.
- [`002-09-crear-nota.md`](002-09-crear-nota.md) — Creación de nota enlazada con frontmatter OKF y motivos en `## Ver además`.
- [`002-11-renombrar.md`](002-11-renombrar.md) — Renombrado atómico de entidades sin dejar enlaces rotos en el grafo.
- [`002-12-reconstruir-lo-derivado.md`](002-12-reconstruir-lo-derivado.md) — Reconstrucción de vistas derivadas idéntica byte a byte ([P9](../../docs/principios.md#L79)).

### Fuera de la cadena

- [`002-10-cli-superficie.md`](002-10-cli-superficie.md) — Superficie pública del CLI (`-h`, códigos fijos, correcciones y campo «A mano»).
