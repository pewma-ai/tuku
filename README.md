# TUKU

Sistema de gestión personal en archivos Markdown, para quien tiene varios frentes de actividad a la vez. Registra lo que el autor hace, recuerda lo que olvida y convierte eso en pendientes, alertas y reportes. Implementa la metodología MaC (Management as Code) de PEWMA.AI en su variante personal.

Qué es y para quién, en [`docs/brief.md`](docs/brief.md). Cómo se organiza este repositorio y por dónde seguir, en [`DEVEL.md`](DEVEL.md).

## Instalar

Necesita [`uv`](https://docs.astral.sh/uv/) o `pipx`:

```bash
uv tool install --force "git+https://github.com/pewma-ai/tuku.git@devel"
tuku init mi-vault
```

`tuku init` copia el template a `mi-vault/` sin tocar la red y deja el primer ciclo abierto. Después, abrir un agente (Claude Code, Codex, Antigravity) sobre esa carpeta y contarle el primer hecho. Para ver qué quedó en disco, `tuku init -h`, o seguir el [tutorial](docs/tutorial/README.md), que recorre una semana de trabajo en diez capítulos.

Para instalarlo a mano, sin `uv`, ver [`template/README.md`](template/README.md).

## Cómo funciona

Son archivos Markdown y nada más: se leen con cualquier editor, viajan en un pendrive, siguen siendo legibles cuando esta herramienta ya no exista.

- El autor habla con un agente. El agente decide qué comando `tuku` corresponde y el comando escribe: registros en `AHORA.md`, pendientes en `PENDIENTES.md`, ámbitos en `ambitos/` y notas en `notas/`.
- El agente se guía por el `AGENTS.md` del vault, la skill del asistente y el [libro de estilo](template/vanilla/LIBRO-DE-ESTILO.md), que se lee por capítulos.
- Los comandos son deterministas: lo derivado (vistas, índices, ciclos) se regenera con `tuku regenerate` y `tuku doctor` revisa la coherencia.
- Todo lo que importa queda en texto plano, no en la memoria de un modelo, y el sistema entero se puede operar a mano.

## Estado

En desarrollo en la rama `devel`. El registro, los pendientes, los ámbitos y las notas funcionan; abrir y cerrar el ciclo y las cadencias vienen después. El detalle, epic por epic, está en [`devel/epics.md`](devel/epics.md).

## Autor

Juan Pablo Gil Ramírez — [LinkedIn](https://www.linkedin.com/in/juan-gil-r/) · [GitHub](https://github.com/jpgil) · [ORCID](https://orcid.org/0009-0003-6219-1818) · juanpablogil@gmail.com

Desarrollado por [PEWMA.AI](https://pewma.ai), laboratorio de herramientas agénticas. Producto y metodología MaC se versionan por separado.

## Licencia

Apache 2.0. Ver [LICENSE](LICENSE).
