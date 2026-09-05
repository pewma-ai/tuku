# TUKU

Sistema de gestión personal en archivos Markdown, para quien tiene varios frentes de actividad a la vez. Registra lo que el autor hace, recuerda lo que olvida y convierte eso en pendientes, alertas y reportes. Implementa la metodología MaC (Management as Code) de PEWMA.AI en su variante personal.

Qué es y para quién, en [`docs/brief.md`](docs/brief.md). Cómo se organiza este repositorio y por dónde seguir, en [`DEVEL.md`](DEVEL.md).

## Cómo funciona

Son archivos Markdown y nada más: se leen con cualquier editor, viajan en un pendrive, siguen siendo legibles cuando esta herramienta ya no exista.

- El autor dicta lo que hizo y un agente lo escribe en la bitácora.
- Janitors deterministas leen esa bitácora para abrir y cerrar pendientes, sembrar cadencias y mantener índices.
- Todo lo que importa queda en texto plano, no en la memoria de un modelo, y el sistema entero se puede operar a mano.

Un directorio de estado cero se instala con una línea (ver [`template/README.md`](template/README.md)):

```bash
curl -fsSL https://raw.githubusercontent.com/pewma-ai/tuku/devel/install.sh | sh -s -- mi-vault
```

## Autor

Juan Pablo Gil Ramírez — [LinkedIn](https://www.linkedin.com/in/juan-gil-r/) · [GitHub](https://github.com/jpgil) · [ORCID](https://orcid.org/0009-0003-6219-1818) · juanpablogil@gmail.com

Desarrollado por [PEWMA.AI](https://pewma.ai), laboratorio de herramientas agénticas. Producto y metodología MaC se versionan por separado.

## Licencia

Apache 2.0. Ver [LICENSE](LICENSE).
