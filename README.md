# TUKU

> **Management as Code (MaC) para la vida personal.**

El nombre viene de *tukulpan*, en mapudungun: recordar, traer a la memoria. Esa es la promesa exacta: **lo que entró a TUKU vuelve solo cuando corresponde**, sin que nadie tenga que acordarse de acordarse.

TUKU es un sistema de gestión personal para personas con múltiples frentes de actividad simultáneos. Registra lo que hace, recuerda lo que olvida, sostiene lo que concluye, y convierte esa acumulación en planes, alertas y reportes.

---

## Estructura del repositorio

- **[`docs/`](docs/README.md)** — Documentación canónica de diseño ([`brief.md`](docs/brief.md), [`principios.md`](docs/principios.md), [`libro-de-estilo.md`](docs/libro-de-estilo.md)).
- **[`devel/`](devel/que_implementar.md)** — Especificación técnica maestra de implementación, entorno de desarrollo y arquitectura.
- **[`tests/`](tests/)** — Suite de pruebas deterministas y escalera de fixtures (`vacio`, `primer-dia`, `ciclo-en-curso`, `ciclo-por-cerrar`, `historico`).
- **[`corpus/`](corpus/)** — Datos y registros reales de prueba para verificar formateo, ground truth y consistencia.
- **[`playground/`](playground/)** — Espacio para experimentar con el CLI y prototipar nuevos janitors y flujos.

---

## Cómo funciona

TUKU son archivos Markdown, y nada más. Son propiedad del autor, se leen con cualquier editor básico, viajan en un pendrive y siguen siendo legibles cuando esta herramienta ya no exista (horizonte: 20 años).

Sobre esos archivos trabajan agentes de inteligencia artificial y scripts deterministas (*janitors*):
- El autor dicta lo que hizo y el agente interpreta, formatea y escribe en la bitácora (`AHORA.md`).
- Los janitors deterministas leen lo escrito para abrir y cerrar pendientes, sembrar cadencias, verificar transclusiones y mantener índices.
- Todo lo que importa queda escrito en archivos de texto plano, no en la memoria de un modelo, y el sistema entero se puede operar a mano.

---

## El Modelo de Datos

### Conjunto canónico (fuente primaria, nunca se regenera)
- **`AHORA.md`** — Ciclo en curso con entradas vivas y vistas transcluidas de plan y pendientes.
- **`bitacoras/`** — Ciclos cerrados, inmutables y autocontenidos con transclusiones aplanadas.
- **`PENDIENTES.md`** — Fuente única de verdad de compromisos abiertos, estructurada en callouts permanentes de horizonte y efímeros fechados.
- **`ambitos/`** — Árbol de frentes de actividad (ámbitos, categorías y actividades) con `AGENTS.md` y `CADENCIAS.md` en cada carpeta.
- **`notas/`** — Zettelkasten global de ideas libres y notas tipadas (`persona`, `sistema`, etc.) destiladas en contexto aislado.

### Derivados y reglas
- **`planes/`** — Planes de ciclo calculados sobre capacidad neta y aprobados por el autor.
- **`reportes/`** — Resúmenes de ciclo con veredicto por intención y reportes agregados.
- **`reglas/`** — Especificación formal de janitors (`janitors.tuku.md`) y configuraciones de zona horaria y tipos.
- **`archivado/`** — Ramas y actividades concluidas con preservación de enlaces históricos.

---

## Documentación

- [`docs/brief.md`](docs/brief.md) — Documento fundacional: qué es, para quién y el funcionamiento en tres niveles.
- [`docs/principios.md`](docs/principios.md) — Principios normativos de diseño, conjunto canónico y jerarquía determinista.
- [`docs/libro-de-estilo.md`](docs/libro-de-estilo.md) — Manual operativo, flujo de información, anatomía de archivos y matriz janitor vs. agente.
- [`devel/que_implementar.md`](devel/que_implementar.md) — Hoja de ruta de implementación técnica en 10 fases (F0 a F9).

---

## Autor

**Juan Pablo Gil Ramírez** — Ingeniero Acústico (UACH), Magíster en Modelación Matemática (UFRO). Deputy Manager del Paranal Software Group en el European Southern Observatory (ESO).

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Juan_Pablo_Gil-0A66C2?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/juan-gil-r/) [![ORCID](https://img.shields.io/badge/ORCID-0009--0003--6219--1818-A6CE39?style=flat-square&logo=orcid)](https://orcid.org/0009-0003-6219-1818) [![GitHub](https://img.shields.io/badge/GitHub-@jpgil-181717?style=flat-square&logo=github)](https://github.com/jpgil) [![Email](https://img.shields.io/badge/Email-juanpablogil@gmail.com-EA4335?style=flat-square&logo=gmail)](mailto:juanpablogil@gmail.com)

---

## PEWMA.AI

Desarrollado y mantenido por **PEWMA.AI**, laboratorio de innovación enfocado en herramientas agénticas y arquitectura de software para el Sur Global. TUKU implementa la metodología MaC en su variante personal; producto y metodología se versionan por separado.

🌐 [pewma.ai](https://pewma.ai)

---

## Licencia

Apache 2.0. Ver [LICENSE](LICENSE).
