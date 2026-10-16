# Epic 002 · El día uno, a mano

> **Marco:** [Brief de TUKU](../../docs/brief.md) · [Principios normativos](../../docs/principios.md) · [Especificaciones](../../spec/README.md) · [Lecciones de mac-jpgil](../../devel/lecciones-macjpgil.md)

El autor instala TUKU y opera su primer día entero mediante comandos directos (`tuku`) sobre un vault inicialmente vacío: cada compromiso, ámbito o nota que necesita se crea al registrarse, estampando constancia cronológica en la bitácora del ciclo y aplicando sus consecuencias atómicas e idempotentes.

## Principios rectores del epic

1. **El archivo de texto es lo primero ([P1](../../docs/principios.md#L9)):** La ayuda de cada comando dice qué archivos toca y cómo, y alcanza para hacerlo con un editor.
2. **La organización emerge del uso ([P2](../../docs/principios.md#L17)):** No se preconfiguran taxonomías ni frentes artificiales; nacen de los registros diarios.
3. **Todo baja hasta donde alcance el determinismo ([P4](../../docs/principios.md#L33)):** La captura y la sincronización de tablas y vistas son 100% mecánicas y libres de LLM.
4. **Conjunto canónico inmutable y tres ejes ([P6](../../docs/principios.md#L55)):** `AHORA.md` y `PENDIENTES.md` son fuentes primarias; ninguna vista guarda registros paralelos.
5. **Reconstrucción determinista ([P9](../../docs/principios.md#L79)):** Reconstruir lo derivado desde el canónico (`tuku regenerate`) devuelve un resultado idéntico byte a byte.

## Qué se verifica

- **Superficie del vault:** Diff exacto entre estados de `playground/`, sin efectos colaterales y con estricta idempotencia (el segundo pase produce diff vacío).
- **Superficie del comando:** Códigos de salida y mensajes que nombran la corrección, según [`spec/cli.md`](../../spec/cli.md). Lo que no necesita un vault va en [`../unitarios/`](../unitarios/README.md).
- **Aceptación humana:** Criterios de legibilidad directa en Obsidian para asegurar experiencia natural y perdurabilidad a 20 años.

## Escenarios BDD del epic

- [`002-13-el-dia.md`](002-13-el-dia.md) — Los caminos felices: el martes 11 hora por hora, cada tramo sobre el vault del anterior, hasta repetir el día y regenerar lo derivado sin cambios ([P9](../../docs/principios.md#L79)).
- [`002-14-casos-borde.md`](002-14-casos-borde.md) — Los casos borde que necesitan el día: ediciones con un editor que cada lint nombra, `tuku fix todo`, `tuku regenerate` y un canónico roto.

Los rechazos que no necesitan el día (ámbito inexistente, día fuera del ciclo, nota sin cuerpo, renombrar sobre un nombre ocupado) están en [`../unitarios/`](../unitarios/README.md).
