# Epic 002 · El día uno, a mano

> **Marco:** [Brief de TUKU](../../docs/brief.md) · [Principios normativos](../../docs/principios.md) · [Especificaciones](../../spec/README.md) · [Lecciones de mac-jpgil](../../devel/lecciones-macjpgil.md)

El autor instala TUKU y vive sus primeras dos semanas con comandos `tuku` a mano sobre un vault recién sembrado: registra, promete pendientes, abre un ámbito y escribe una nota. `AHORA.md` ordena sus días del más nuevo al más viejo, lo que sale de la ventana pasa solo a una bitácora semanal, y todo se repite sin cambiar nada.

## Principios rectores del epic

1. **El archivo de texto es lo primero ([P1](../../docs/principios.md#L9)):** La ayuda de cada comando dice qué archivos toca y cómo, y alcanza para hacerlo con un editor.
2. **La organización emerge del uso ([P2](../../docs/principios.md#L17)):** No se preconfiguran taxonomías ni frentes artificiales; nacen de los registros diarios.
3. **Todo baja hasta donde alcance el determinismo ([P4](../../docs/principios.md#L33)):** La captura y la sincronización de tablas y vistas son 100% mecánicas y libres de LLM.
4. **Conjunto canónico inmutable y tres ejes ([P6](../../docs/principios.md#L55)):** `AHORA.md`, `PENDIENTES.md` y las bitácoras son fuentes primarias; ninguna vista guarda registros paralelos.
5. **Reconstrucción determinista ([P9](../../docs/principios.md#L79)):** Reconstruir lo derivado desde el canónico (`tuku regenerate`) devuelve un resultado idéntico byte a byte.

## Qué se verifica

- **Superficie del vault:** Diff exacto entre estados de `playground/`, sin efectos colaterales y con estricta idempotencia (el segundo pase produce diff vacío).
- **Superficie del comando:** Códigos de salida y mensajes que nombran la corrección, según [`spec/tuku.md`](../../spec/tuku.md). Lo que no necesita un vault va en [`../unitarios/`](../unitarios/README.md).
- **Aceptación humana:** Criterios de legibilidad directa en Obsidian para asegurar experiencia natural y perdurabilidad a 20 años.

## Escenarios BDD del epic

- [`002-13-el-dia.md`](002-13-el-dia.md) — La historia entera con el reloj inyectado: el martes 11 de agosto (registros, pendientes con `Creado` y su ventana, un ámbito con su jerarquía, una nota, el foco del autor) y los lunes 17 y 24 (el orden descendente de los días, el autoarchivado en `bitacoras/bitacora-AAAAMMDD-AAAAMMDD.md`, un registro de fecha antigua que va a su bitácora, la idempotencia y `tuku doctor` sano).
- [`002-14-casos-borde.md`](002-14-casos-borde.md) — Sobre el vault final: un derivado editado a mano se regenera idéntico y un pendiente abierto y cerrado a mano lo repara `tuku fix todo` ([P9](../../docs/principios.md#L79)).

Las reglas deterministas (el plazo de un horizonte desde `Creado`, la ventana, el orden, el nombre de una bitácora, los rechazos) están en [`../unitarios/`](../unitarios/README.md) y no se repiten acá.
