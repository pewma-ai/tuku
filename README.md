# TUKU

> **Management as Code (MaC) para la vida personal.**

**TUKU** proviene de *tukulpan*, que en mapudungun significa *recordar, traer a la memoria*. El nombre es la promesa: lo que ingresó vuelve solo cuando corresponde.

TUKU es un sistema de gestión personal basado en archivos Markdown planos versionados en Git, operado mediante janitors deterministas y asistencia conversacional.

---

## 💡 Concepto y Filosofía

TUKU implementa la metodología **Management as Code (MaC)** en su variante personal. Separa la fuente de verdad (archivos canónicos) de sus vistas (proyecciones derivadas), garantizando la propiedad total de los datos en manos del usuario.

### Primitivas del Dominio

- **Entrada**: Unidad inmutable de registro en la bitácora (`entradas/entradas.md`).
- **Tarea**: Compromiso de acción con estado, temporalidad y pertenencia a una entidad (`tareas/tareas.md`).
- **Entidad**: Objeto de gestión (proyecto, área, cliente, persona) organizado jerárquicamente.
- **Cadencia**: Regla que produce tareas, ciclos o alertas en el tiempo.
- **Ciclo**: Período de trabajo/vida (turno, semana, viaje) declarado en un plan.
- **Proceso**: Plantilla reutilizable de pasos instanciable sobre entidades.
- **RADAR**: Capa de consulta en vivo y bajo demanda sobre el estado del perfil.

---

## 📚 Documentación

- [`docs/brief.md`](docs/brief.md) — Visión, problema y criterios de éxito.
- [`docs/brief.md#3-principios`](docs/brief.md#3-principios) — Los 6 principios arquitectónicos del sistema.
- [`docs/arquitectura.md`](docs/arquitectura.md) — Modelo de datos, janitors, derivaciones y motor.
- [`docs/glosario.md`](docs/glosario.md) — Vocabulario preciso del dominio TUKU.
- [`spec/`](spec/) — Especificaciones técnicas de primitivas (`tarea`, `entradas`, `entidad`, `cadencia`, `proceso`, `artefactos-ciclo`).

---

## Autor

**Juan Pablo Gil Ramírez** — Ingeniero Acústico (UACH), Magíster en Modelación Matemática (UFRO). Deputy Manager del Paranal Software Group en el European Southern Observatory (ESO).

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Juan_Pablo_Gil-0A66C2?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/juan-gil-r/) [![ORCID](https://img.shields.io/badge/ORCID-0009--0003--6219--1818-A6CE39?style=flat-square&logo=orcid)](https://orcid.org/0009-0003-6219-1818) [![GitHub](https://img.shields.io/badge/GitHub-@jpgil-181717?style=flat-square&logo=github)](https://github.com/jpgil) [![Email](https://img.shields.io/badge/Email-juanpablogil@gmail.com-EA4335?style=flat-square&logo=gmail)](mailto:juanpablogil@gmail.com)

---

## PEWMA.AI

Este proyecto es desarrollado y mantenido por **PEWMA.AI**, laboratorio de innovación enfocado en herramientas agénticas y arquitectura de software para el Sur Global.

🌐 [pewma.ai](https://pewma.ai)

---

## Licencia

Licenciado bajo **Apache 2.0**. Consulta el archivo [LICENSE](LICENSE) para más detalles.
