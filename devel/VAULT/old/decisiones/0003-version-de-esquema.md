# ADR 0003 — Versionado de esquema y migraciones

## Contexto

Del ADR 0002 se sigue que motor y perfil evolucionan por separado: el motor cambia en semanas,
el perfil vive décadas. Entre ambos hay un contrato implícito —qué campos lleva el front
matter, cómo se marcan las zonas, cómo se nombran los archivos, qué gramática tiene una
cadencia— y ese contrato **va a cambiar**. Las specs actuales tienen decisiones abiertas
declaradas en casi todos sus capítulos; algunas se cerrarán de forma incompatible con lo ya
escrito en disco.

El escenario que hay que soportar no es hipotético y es el que define el proyecto: **un
usuario instala TUKU, lo usa un año, lo deja dos, y vuelve.** Su repositorio debe seguir
siendo legible y el motor nuevo debe saber qué está leyendo. Si en ese momento el motor
interpreta mal un formato viejo —o peor, lo reescribe silenciosamente según reglas nuevas—
el usuario pierde años de gestión y la promesa de P1 queda desmentida.

Las alternativas viables:

- **No versionar y mantener retrocompatibilidad indefinida en el parser.** Funciona un tiempo
  y luego el motor se convierte en una acumulación de ramas condicionales sobre formatos que
  nadie recuerda por qué existen. El costo crece sin techo y no hay momento en que se pueda
  limpiar.
- **Versionar por la versión del motor.** Ata el formato de los datos al número de release del
  código, cuando la mayoría de los releases no tocan el formato en absoluto. Obliga a migrar
  por cambios que no son de esquema.
- **Migración implícita al vuelo**, sin commit propio: el motor detecta formato viejo y lo
  actualiza al pasar. Es cómodo, y es exactamente lo que no se puede hacer: mezcla la
  transformación con el trabajo del usuario en el mismo diff, y vuelve imposible revisar o
  revertir.

## Decisión

**El perfil declara su versión de esquema. El motor declara qué rango soporta. La migración
es explícita, aislada y acumulativa.**

- `.tuku/config.yaml` declara `schema_version`, independiente de la versión del motor. Solo
  cambia cuando cambia el contrato de los datos.
- El motor declara el rango de esquemas que sabe leer. `tuku doctor` compara ambos y avisa;
  ante un perfil de esquema **mayor** al soportado, el motor se niega a operar en lugar de
  adivinar.
- `tuku migrate` transforma el perfil **siempre en un commit propio y aislado**, sin mezclar
  cambios de datos del usuario, para que el diff sea revisable y revertible con `git revert`.
- Las migraciones viven en `src/tuku/migrations/`, son parte del motor, **se acumulan y
  ninguna se borra**. Un perfil de esquema 3 llega al 7 aplicando 3→4→5→6→7.
- Una migración es determinista y pertenece a la familia *derivación* (P3): sin LLM, sin red,
  reproducible. Si una transformación necesitara juicio semántico, no es una migración — es
  una propuesta al usuario.

## Consecuencias

**A favor.**

- Un perfil abandonado dos años sigue siendo recuperable, y el usuario ve exactamente qué se
  le cambió antes de aceptarlo.
- El motor puede limpiar código de formatos viejos con criterio: la migración se aplica una
  vez y el parser solo mantiene el rango declarado.
- Definirlo hoy cuesta poco. Retrofitearlo cuesta muchísimo, porque exigiría inferir la
  versión de perfiles que nunca la declararon.

**En contra, y aceptado.**

- **Cada cambio de formato tiene un costo fijo**: escribir la migración, probarla y no
  borrarla nunca. Esto es deliberado — encarece cambiar el esquema por capricho, que es
  justo el incentivo que se busca en esta etapa de decisiones abiertas.
- `src/tuku/migrations/` crece de forma monótona y nunca se poda.
- El usuario debe ejecutar un comando explícito tras actualizar el motor. Se mitiga con
  `tuku doctor`, que lo detecta y lo indica; nunca migrando en silencio.

**Sobre `schema_version: 0`.** El valor sembrado hoy en
[`src/tuku/templates/profile.yaml`](profile.yaml) declara que el
esquema **aún no es estable**. Mientras sea 0, no hay garantía de migración automática entre
cambios de formato y los perfiles son experimentales. El compromiso de este ADR empieza a
regir en `schema_version: 1`, que se declarará cuando cierren las decisiones abiertas de
`spec/`.

## Estado

`aceptado`
