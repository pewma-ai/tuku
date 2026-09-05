# Escenario · 001-003-destino-no-vacio

> Corpus, no diseño: esto es un caso a favor del que se prueba el sistema, referencia `spec/`
> pero no lo reemplaza. Si el resultado contradice `spec/`, se corrige `spec/`, no este archivo
> (ver `devel/epics.md`, "los epics mueven el diseño").

**Cubre:** epic 001, fase 0, decidido #7 de [`../../devel/epics.md`](../../devel/epics.md).

## Escenario: no sobrescribir un destino que ya tiene algo, sin preguntar

Dado un directorio destino que ya existe y no está vacío
Cuando se corre `install.sh` sin `TUKU_FORCE=1`
Entonces se pregunta antes de continuar, por `stderr`
Y si no se confirma, no se descarga nada y el destino queda exactamente igual a como estaba

## Por qué importa

Es el único caso de los tres donde equivocarse borra trabajo de alguien: si `install.sh` sobrescribiera en silencio un directorio que ya tenía algo, la primera vez que alguien lo reinstale por error pierde lo que había escrito. `001-001` y `001-002` prueban que la instalación llega a buen puerto; este prueba que el instalador no hace daño cuando no debería tocar nada.

La pregunta corre antes de bajar nada de la red (`install.sh`, sección del `if` inicial), así que se prueba sin depender de `curl` ni de GitHub.

## Cómo se corre

```bash
mkdir -p /tmp/destino-no-vacio && touch /tmp/destino-no-vacio/algo
sh install.sh /tmp/destino-no-vacio
# responde "n" o cualquier cosa que no sea "s": debe cancelar sin tocar el directorio
```

## El test

`test_001_003_destino_no_vacio.py` corre `install.sh` en un subproceso sin terminal de control (`start_new_session=True`): al no poder abrir `/dev/tty`, el script trata eso igual que una respuesta vacía, que cancela. Es exactamente lo que pasa en cualquier invocación no interactiva (un script, un cron, un agente), y es el caso que hay que blindar: si algún día deja de preguntar ahí, sobrescribiría en silencio.

```bash
python3 tests/escenarios/test_001_003_destino_no_vacio.py
```

## Qué se mira a mano

- Correrlo de verdad en una terminal, responder "s", y confirmar que sí sobrescribe.
- Que `TUKU_FORCE=1` salte la pregunta. No lo cubre este test todavía.
