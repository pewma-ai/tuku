# TUKU

> **Management as Code (MaC) para la vida personal.**

El nombre viene de *tukulpan*, en mapudungun: recordar, traer a la memoria. Esa es la promesa exacta: **lo que entró a TUKU vuelve solo cuando corresponde**, sin que nadie tenga que acordarse de acordarse.

TUKU es un sistema de gestión personal para una persona con múltiples frentes de actividad simultáneos. Registra lo que hace, recuerda lo que olvida, sostiene lo que concluye, y convierte esa acumulación en planes, alertas y reportes.

## Estructura del repositorio

- **[`docs/`](docs/README.md)** — Documentación actual y canónica de diseño (`brief.md`, `principios.md`, `libro-de-estilo.md`).
- **[`devel/`](devel/VAULT/README.md)** — Material histórico, borradores previos y notas de desarrollo para usar como referencia.
- **[`playground/`](playground/)** — Espacio para poner a prueba a TUKU y experimentar con datos del corpus.
- **[`corpus/`](corpus/)** — Datos y registros reales de prueba para verificar la regeneración y consistencia del sistema.

## Cómo funciona

TUKU son archivos Markdown, y nada más. Son del autor, se leen con cualquier editor, viajan en un pendrive y siguen siendo legibles cuando esta herramienta ya no exista.

Sobre esos archivos trabajan agentes de inteligencia artificial: el autor les cuenta lo que hizo y ellos ordenan, clasifican, recuerdan y redactan borradores. Mantener el sistema —que es justamente lo que hace abandonar todos los sistemas— deja de ser trabajo del usuario.

Lo esencial no depende de los agentes: todo lo que importa queda escrito en archivos de texto, no en la memoria de un modelo, y el sistema entero se puede operar a mano.

## El modelo

- **Bitácora** — Hechos con fecha y hora, inmutables. Todo lo demás se deriva de aquí.
- **Pendientes** — Lo que falta. Un pendiente nace de una entrada de bitácora y muere en otra.
- **Notas** — Lo que se entendió. El espacio mental del sistema, enlazadas en su propio ámbito.
- **Ámbitos** — Estructura de carpetas que refleja los frentes de actividad (personal, trabajo, proyectos, clientes).
- **Libro de estilo** — Reglas de escritura y organización que gobiernan el repositorio para humanos, agentes y janitors.

## Documentación

- [`docs/brief.md`](docs/brief.md) — Documento fundacional: qué es, para quién y el funcionamiento en tres niveles.
- [`docs/principios.md`](docs/principios.md) — Principios normativos de diseño y descarga cognitiva.
- [`docs/libro-de-estilo.md`](docs/libro-de-estilo.md) — Reglas de formato, gestión de pendientes y matriz janitor vs. agente.

## Autor

**Juan Pablo Gil Ramírez** — Ingeniero Acústico (UACH), Magíster en Modelación Matemática (UFRO). Deputy Manager del Paranal Software Group en el European Southern Observatory (ESO).

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Juan_Pablo_Gil-0A66C2?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/juan-gil-r/) [![ORCID](https://img.shields.io/badge/ORCID-0009--0003--6219--1818-A6CE39?style=flat-square&logo=orcid)](https://orcid.org/0009-0003-6219-1818) [![GitHub](https://img.shields.io/badge/GitHub-@jpgil-181717?style=flat-square&logo=github)](https://github.com/jpgil) [![Email](https://img.shields.io/badge/Email-juanpablogil@gmail.com-EA4335?style=flat-square&logo=gmail)](mailto:juanpablogil@gmail.com)

## PEWMA.AI

Desarrollado y mantenido por **PEWMA.AI**, laboratorio de innovación enfocado en herramientas agénticas y arquitectura de software para el Sur Global. TUKU implementa la metodología MaC en su variante personal; producto y metodología se versionan por separado.

🌐 [pewma.ai](https://pewma.ai)

## Licencia

Apache 2.0. Ver [LICENSE](LICENSE).
