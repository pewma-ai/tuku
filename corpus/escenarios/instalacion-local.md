# Escenario · instalacion-local

> Corpus, no diseño: esto es un caso a favor del que se prueba el sistema, referencia `spec/`
> pero no lo reemplaza. Si el resultado contradice `spec/`, se corrige `spec/`, no este archivo
> (ver `devel/epics.md`, "los epics mueven el diseño").

**Cubre:** epic 1, fase 0. Complementa a [`instalacion-minima.md`](instalacion-minima.md), que instala vía `curl` contra GitHub.

## Escenario: instalar sin red ni git, por simplicidad

Dado el repositorio ya presente en disco (el checkout de trabajo, no un tarball bajado)
Cuando se corre `src/install_test_scenario.py` directo, sin pasar por `install.sh` ni por `curl`
Entonces se obtiene el mismo vault que produciría el escenario de `curl`, para la misma fecha
Y no hace falta red, ni GitHub, ni que el branch esté empujado

## Por qué existe, si ya está `instalacion-minima`

`instalacion-minima` prueba lo que **verá el usuario final**: una línea de `curl` contra un repo real. Es el camino completo, pero depende de red y de que el commit esté empujado.

Este escenario prueba lo mismo **más rápido y sin esas dos dependencias**: sirve para iterar sobre `template/` y sobre el propio `install_test_scenario.py` sin esperar una descarga, y es el candidato natural para correr en CI el día que exista.

Los dos deben coincidir. Si un vault instalado por `curl` difiere de uno instalado local, el defecto está en `install.sh` (la parte que arma el tarball y localiza `ORIGEN`), no en el mecanismo de instalación.

## Cómo se corre

```bash
python3 src/install_test_scenario.py --variante vanilla --destino playground/epic-1_test-2 --desde AAAA-MM-DD
```

## Qué se mira a mano

- Que el árbol de archivos y el contenido de `AHORA.md` sean idénticos a una corrida de `instalacion-minima` con el mismo `--desde` (`diff -r`, cero diferencias).
