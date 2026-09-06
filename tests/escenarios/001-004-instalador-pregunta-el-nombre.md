# Escenario · 001-004-instalador-pregunta-el-nombre

> Corpus, no diseño: esto es un caso a favor del que se prueba el sistema, referencia `spec/`
> pero no lo reemplaza. Si el resultado contradice `spec/`, se corrige `spec/`, no este archivo
> (ver `devel/epics.md`, "los epics mueven el diseño").

**Cubre:** epic 001, fase 0, decidido #9 de [`../../devel/epics.md`](../../devel/epics.md), la capa de identidad mínima.

## Escenario: el instalador pregunta el nombre y queda escrito en el libro de estilo

Dado un directorio destino vacío
Y el repositorio ya presente en disco (`TUKU_ORIGEN`), sin nada que bajar
Cuando se corre `install.sh` y se responde el nombre del autor en el prompt
Entonces la instalación completa sin tocar la red
Y `LIBRO-DE-ESTILO.md` del vault queda con ese nombre en la sección "El autor"
Y no sobrevive el placeholder `por declarar`

## Escenario: con el destino vacío no se pregunta por sobrescribir

Dado el mismo directorio destino, que no existe
Cuando se corre `install.sh`
Entonces el único prompt es el del nombre del autor
Y la pregunta de sobrescritura de [`001-003-destino-no-vacio.md`](001-003-destino-no-vacio.md) no se dispara

## Por qué existe, si ya está `001-001-instalacion-minima`

`001-001` cubre la instalación byte a byte, sin nombre de autor. Este es la única cobertura del flag `--autor`, y lo cubre por el camino entero: la pregunta que hace `install.sh` por `/dev/tty`, la respuesta que escribe una persona, y todo lo que ese texto atraviesa hasta llegar al archivo (`read`, `set --`, `--autor` de `src/install_test_scenario.py`).

Por eso el nombre que responde el test es `ARTURO PEREZ-REVERTE (Arturo)`, con espacios, paréntesis y guion: es un valor que se rompería si en cualquiera de esos pasos faltara una comilla.

Que no haya descarga es lo que hace barato correrlo: `TUKU_ORIGEN` apunta a la raíz del repositorio en disco y `install.sh` se salta el bloque de `curl | tar` entero. Nunca imprime "bajando".

## Cómo se corre

```bash
TUKU_ORIGEN="$PWD" sh install.sh playground/001-004-instalador-pregunta-el-nombre 2026-08-11
# responde el nombre en el prompt
```

Correr el test de pytest deja el mismo resultado en `playground/001-004-instalador-pregunta-el-nombre/`: su arnés instala ahí, no en un tempdir que se bota.

## El test

`test_001_004_instalador_pregunta_el_nombre.py`, con [`pexpect`](https://pexpect.readthedocs.io/), porque `read -r r < /dev/tty` no lee de la entrada estándar y un subproceso con pipes no le puede escribir la respuesta.

A diferencia de los tres del `001-003`, este **sí deja que la instalación complete** y espera el `EOF` con estado de salida 0: lo que se quiere revisar es justamente el artefacto que queda en `playground/`. Puede permitírselo porque ya no hay red que esperar.

Fija `--desde 2026-08-11`, la misma fecha que `001-001` y `001-002`, para que el vault que produce sea comparable con `diff -r` contra el de esos dos (salvo `LIBRO-DE-ESTILO.md`, que acá lleva el nombre).

```bash
python3 tests/escenarios/test_001_004_instalador_pregunta_el_nombre.py
```

## Qué se mira a mano

- Abrir `playground/001-004-instalador-pregunta-el-nombre/LIBRO-DE-ESTILO.md` y ver el nombre respondido **al inicio del documento**, en la sección "El autor", sin tener que buscarlo: es lo primero que el autor lee al abrir su libro de estilo recién instalado.
- Que la pregunta del instalador se entienda sin explicación previa, y que quede claro que dejarla en blanco es válido (principio 2: el vault queda operable igual).
