# ADR 0002 — El motor nunca se vendoriza en el perfil

## Contexto

TUKU se compone de dos cosas con ciclos de vida distintos: el **motor** —código, janitors,
procesos, plantillas, versionado por PEWMA.AI, vida útil de años— y el **perfil** —los datos
del usuario, versionados por él, con vida útil de décadas
([`docs/arquitectura.md`](../arquitectura.md) §1).

La pregunta es dónde vive el motor respecto del perfil. Hay dos opciones viables y la
tentación de vendorizar es genuina, no un error de principiante:

- **Reproducibilidad.** Con el código dentro del repo de datos, un commit captura a la vez el
  estado y la versión exacta que lo produjo. Volver a un commit de 2027 devuelve el motor de
  2027.
- **Descubribilidad por agentes.** Un agente de codificación lee lo que está en la carpeta.
  Si los procesos viven solo en site-packages, no los ve — y se pierde toda la ventaja del
  anidamiento POSIX de instrucciones, que es una razón de diseño de la jerarquía
  ([`spec/entidad.md`](../../spec/entidad.md) §2.4).
- **Autocontención.** Clonar el perfil sería suficiente para operarlo.

Los costos, en cambio, son estructurales:

- El historial de las bitácoras queda contaminado con churn de versiones del motor. Un
  `git log` sobre los datos deja de responder "qué pasó en mi gestión".
- Cada actualización se convierte en un merge sobre un repositorio de datos ajeno al motor.
- En despliegue servidor, N perfiles significan N copias del mismo código.
- Contradice P1: si el motor vive dentro del perfil, el perfil deja de ser un artefacto de
  texto plano interpretable sin TUKU.

## Decisión

**El motor nunca se copia dentro del perfil. El perfil contiene datos y punteros; nada más.**

- El motor se instala vía `pipx` y vive en site-packages, fuera de los datos.
- Un motor sirve N perfiles. El flag `--profile` existe **desde el primer commit**, aunque
  al principio solo haya un perfil: el diseño local es el diseño del servidor.
- El registro de perfiles vive en `~/.tuku/config.toml`, que es configuración de máquina, no
  de datos. `~/.tuku/cache/` es enteramente reconstruible y `~/.tuku/credentials` nunca entra
  al perfil ni a Git.
- **La descubribilidad se resuelve sin vendorizar**: `tuku init` genera `.tuku/procesos/` como
  punteros o symlinks a los procesos del motor instalado, más un `AGENTS.md` por nivel. Se
  regeneran con `tuku sync` y no ensucian el historial de datos.
- La reproducibilidad se resuelve por versionado explícito, no por copia: el paquete estampa
  su procedencia en tiempo de build (`setuptools_scm`) y todo artefacto sembrado registra qué
  lo produjo en `seeded_by: tuku 0.4.2+g27b3aed / <modelo>`
  ([`spec/artefactos-ciclo.md`](../../spec/artefactos-ciclo.md) §2.1).

Descartadas también dos formas de distribución: **npm**, porque los janitors son Python y un
wrapper Node añadiría una dependencia de runtime sin aportar nada, especialmente costosa en
los contextos de usuario que TUKU busca servir; y **`curl | bash`**, porque el gesto correcto
es descargar, inspeccionar, ejecutar — nunca canalizar directo a shell.

## Consecuencias

**A favor.**

- El historial del perfil es historial de la gestión. Es lo que hace creíble la vida útil de
  décadas.
- El salto a servidor multiusuario no exige rediseño: cambia dónde viven los perfiles, no el
  modelo.
- Actualizar el motor no toca los datos del usuario, y por tanto no puede corromperlos.

**En contra, y aceptado.**

- **Un perfil no es autocontenido.** Clonarlo no basta para operarlo: hace falta instalar el
  motor. Se acepta porque el perfil sigue siendo *legible* sin motor, que es lo que P1 exige
  —no *ejecutable*.
- **Un commit del perfil no captura la versión del motor que lo produjo.** Se mitiga con
  `seeded_by` en los artefactos sembrados y con `tuku doctor`, que reporta versión, commit y
  rama. Sin eso, ningún reporte de bug de esta etapa sería accionable.
- **Los punteros de `.tuku/procesos/` pueden quedar colgando** tras actualizar o mover el
  motor. Se regeneran con `tuku sync`, y `tuku doctor` detecta el desfase. Es un derivado:
  borrarlo no pierde información.

Esta decisión es la que **obliga** al ADR 0003: si el motor evoluciona por separado de los
datos, el contrato entre ambos tiene que estar versionado explícitamente.

## Estado

`aceptado`
