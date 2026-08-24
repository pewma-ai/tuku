# ADR 0015 — `tuku.log` vive en el perfil sin versionar

## Contexto

El motor ejecuta operaciones que no son del usuario: corridas de cron, evaluaciones de
cadencia, builds de derivaciones, migraciones. Registrar esas operaciones es útil para
diagnóstico: saber si el cron corrió anoche, por qué apareció una tarea, qué janitor
modificó qué archivo.

Dos opciones para almacenar ese registro:

**En el repositorio Git del perfil**, como cualquier otro archivo. La ventaja es que el log
queda versionado, portable y auditable a largo plazo; si el usuario cambia de máquina, el
historial de operaciones del motor viaja con él.

**Fuera del control de versiones**, en la raíz del perfil pero en `.gitignore`. El log
existe mientras la máquina vive y se pierde al cambiarse de máquina o al limpiar el
directorio.

## Decisión

**`tuku.log` vive en la raíz del perfil, fuera del control de versiones** (incluido en
`.gitignore`).

Es un archivo de diagnóstico operacional, no de memoria del usuario. Su contenido es
distinto del de `entradas/`: las entradas son lo que la persona hizo; el log es lo que el
motor hizo. Mezclar ambas narrativas en el mismo historial de Git contamina el log de
cambios con ruido de infraestructura.

Si se pierde, no importa: no contiene información que no esté ya en los archivos que el
motor modificó o generó.

## Consecuencias

**A favor.**

- El historial de Git del perfil es exclusivamente de datos del usuario. Un `git log` cuenta
  la historia de la gestión, no de las corridas de cron.
- No hay commits de ruido cada vez que el cron corre o el janitor actualiza un hash.
- El log puede rotar libremente sin afectar el repositorio.

**En contra, y aceptado.**

- Si el usuario cambia de máquina, pierde el historial de operaciones del motor. En la
  práctica, ese historial es útil para depurar problemas en la máquina actual, no para
  auditoría a largo plazo.
- En un despliegue de servidor, el log vive en el servidor y no es accesible por el usuario
  sin acceso directo. Se mitiga porque `tuku doctor` puede responder las preguntas más
  comunes sin necesitar el log completo.

## Estado

`aceptado`
