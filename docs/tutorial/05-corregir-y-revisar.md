# 5. Corregir y revisar

> Arreglar lo mal dicho, y qué revisa `tuku doctor`.

Te equivocas, o el agente te entiende mal. Corregir también se dicta.

## Corregir un registro y su pendiente

> [!tip] Dile a tu agente
> La reunión de apoderados de la Emilia no era a las siete, es a las seis y media.

> [!check] Qué debería pasar
> - El registro y la fila de `PENDIENTES.md` dicen «seis y media», los dos.
> - `Vence` trae el jueves a las 18:30.

Si uno cambiara y el otro no, el pendiente ya no se podría cerrar, porque cerrar es repetir su texto. Por eso corregir es un solo comando.

## Renombrar un frente

> [!tip] Dile a tu agente
> Cámbiale el nombre al frente Colegio Los Robles: que se llame Los Robles.

> [!check] Qué debería pasar
> - La carpeta y la página pasaron a `ambitos/los-robles/los-robles.md`.
> - Ningún link del vault conserva el nombre viejo: ni `AHORA.md`, ni la ficha de don Rodolfo.
> - Las keywords siguen igual.

## Pedir lo que ningún comando hace

> [!tip] Dile a tu agente
> Fusiona Los Robles y Liceo Andes en un solo frente que se llame colegios.

> [!check] Qué debería pasar
> - El agente te dice en una frase qué entendió, en tus palabras y sin jerga, y espera.
> - Nada se escribió todavía.

Fusionar no tiene comando, y las fusiones destruyen historia. Un agente que empieza a trabajar sin avisar, o que contesta con tecnicismos, tiene algo que arreglar.

> [!tip] Respóndele
> No, déjalos separados.

> [!check] Qué debería pasar
> - Ningún archivo cambió.

## Revisar con el doctor

Es el segundo y último comando que corres tú:

```bash
tuku doctor
```

> [!check] Qué debería pasar
> - Muestra los hallazgos y los avisos, o dice que todo está sano.
> - Con `tuku doctor --verbose` ves también cada revisión que salió bien.

### Edita a mano y doctor lo acepta

Abre `AHORA.md` y corrige una palabra de un registro.

> [!check] Qué debería pasar
> - `tuku doctor` sigue sano.

El vault es tuyo y lo puedes editar con cualquier programa. Lo que el agente no hace es editar a mano un archivo que tiene comando, porque lo cubre `tuku`.

### Hazlo enojar

Abre `PENDIENTES.md` y borra una fila a mano. Corre `tuku doctor`.

> [!check] Qué debería pasar
> - Reporta que el registro `**pendiente**` de `AHORA.md` no tiene su fila.

`doctor` cruza `AHORA.md` con `PENDIENTES.md` y avisa cuando dejan de coincidir. Deshaz el cambio antes de seguir.

Siguiente: [6. El día completo](06-el-dia-completo.md).
