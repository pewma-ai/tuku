# TUKU

> **Management as Code (MaC) para la vida personal.**

El nombre viene de *tukulpan*, en mapudungun: recordar, traer a la memoria. Esa es la promesa exacta: **lo que entró a TUKU vuelve solo cuando corresponde**, sin que nadie tenga que acordarse de acordarse.

TUKU es un sistema de gestión personal para una persona que pertenece a múltiples organizaciones a la vez. Registra lo que hace, recuerda lo que olvida, sostiene lo que concluye, y convierte esa acumulación en planes, alertas y reportes.

## Desarrollo

Estamos en desarrollo! Ver en [[DEVEL]]
## Cómo funciona

TUKU son archivos Markdown, y nada más. Son del autor, se leen con cualquier editor, viajan en un pendrive y siguen siendo legibles cuando esta herramienta ya no exista.

Sobre esos archivos trabajan agentes de inteligencia artificial: uno les cuenta lo que hizo y ellos ordenan, clasifican, recuerdan y redactan borradores. Mantener el sistema, que es justamente lo que hace abandonar todos los sistemas, deja de ser trabajo del autor.

Lo esencial no depende de los agentes: todo lo que importa queda escrito en un archivo, no en su memoria, y el sistema entero se puede operar sin ellos.

## El modelo

- **Bitácora** — Hechos con fecha y hora, inmutables. Todo lo demás se deriva de aquí.
- **Pendientes** — lo que falta. Un pendiente nace de una entrada de bitácora y muere en otra.
- **Notas** — lo que se entendió. El espacio mental del sistema, sin ritmo impuesto.
- **Entidades** — el objeto de trabajo: el cliente, el proyecto, la persona. Con sus **prácticas** asociadas.
- **Ciclo** — el período que uno está viviendo, por defecto la semana. Abre con una intención y cierra con un reporte.
- **Cadencias** — hacen aparecer tareas cuando corresponde. La más valiosa es la que se dispara **porque no pasó nada**.

## Documentación

- [`docs/brief.md`](docs/brief.md) — documento fundacional: qué es, para quién y el modelo completo.
- [`docs/principios.md`](docs/principios.md) — normativos. Cualquier decisión que los contradiga obliga a un ADR.
- [`docs/agentes.md`](docs/agentes.md) — roles, canal único, economía de contexto y motores.
- [`spec/`](spec/) — especificaciones del modelo, en orden de derivación.

## Autor

**Juan Pablo Gil Ramírez** — Ingeniero Acústico (UACH), Magíster en Modelación Matemática (UFRO). Deputy Manager del Paranal Software Group en el European Southern Observatory (ESO).

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Juan_Pablo_Gil-0A66C2?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/juan-gil-r/) [![ORCID](https://img.shields.io/badge/ORCID-0009--0003--6219--1818-A6CE39?style=flat-square&logo=orcid)](https://orcid.org/0009-0003-6219-1818) [![GitHub](https://img.shields.io/badge/GitHub-@jpgil-181717?style=flat-square&logo=github)](https://github.com/jpgil) [![Email](https://img.shields.io/badge/Email-juanpablogil@gmail.com-EA4335?style=flat-square&logo=gmail)](mailto:juanpablogil@gmail.com)

## PEWMA.AI

Desarrollado y mantenido por **PEWMA.AI**, laboratorio de innovación enfocado en herramientas agénticas y arquitectura de software para el Sur Global. TUKU implementa la metodología MaC en su variante personal; producto y metodología se versionan por separado.

🌐 [pewma.ai](https://pewma.ai)

## Licencia

Apache 2.0. Ver [LICENSE](LICENSE).
