# TUKU

Sistema de gestión personal en archivos Markdown, para quien tiene varios frentes de actividad a la vez. Registra lo que el autor hace, recuerda lo que olvida y convierte eso en pendientes, alertas y reportes. Implementa la metodología MaC (Management as Code) de PEWMA.AI en su variante personal.

Qué es y para quién, en [`docs/brief.md`](docs/brief.md).

## Instalar

Necesita [`uv`](https://docs.astral.sh/uv/) o `pipx`:

```bash
uv tool install --force "git+https://github.com/pewma-ai/tuku.git@devel"
tuku init mi-vault
```

`tuku init` copia el template a `mi-vault/` sin tocar la red y deja el primer ciclo abierto. Después, abrir un agente (Claude Code, Codex, Antigravity) sobre esa carpeta y contarle el primer hecho. Para empezar, el [tutorial](docs/tutorial/README.md) recorre una semana de trabajo en diez capítulos.

## Cómo funciona

Son archivos Markdown y nada más: se leen con cualquier editor, viajan en un pendrive, siguen siendo legibles cuando esta herramienta ya no exista.

- El autor habla con un agente. El agente escribe con comandos `tuku`: lo que pasó, los pendientes, los frentes de trabajo y las notas.
- Los comandos son deterministas y `tuku doctor` revisa que todo quede coherente.
- Todo lo que importa queda en texto plano, no en la memoria de un modelo, y el sistema entero se puede operar a mano.

## Autor

Juan Pablo Gil Ramírez — [LinkedIn](https://www.linkedin.com/in/juan-gil-r/) · [GitHub](https://github.com/jpgil) · [ORCID](https://orcid.org/0009-0003-6219-1818) · juanpablogil@gmail.com

Desarrollado por [PEWMA.AI](https://pewma.ai), laboratorio de herramientas agénticas. Producto y metodología MaC se versionan por separado.

## Licencia

Apache 2.0. Ver [LICENSE](LICENSE).
