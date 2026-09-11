# 003-07 · Lo que no hace sin preguntar

> **Principio:** [P3 (secretario, no dueño)](../../docs/principios.md#L25), [P7 (carpetas archivan)](../../docs/principios.md#L63) · **Brief:** [El agente y las herramientas](../../docs/brief.md#L60) · **Spec:** [`spec/despacho.md`](../../spec/despacho.md), [`spec/agente.md`](../../spec/agente.md)

El agente respeta la tabla de Límites de [`AGENTS.md`](../../template/vanilla/AGENTS.md): ante ambigüedades entre pendientes que compiten o instrucciones sobre carpetas estructurales sin comando directo, se detiene a consultar o reformular antes de actuar.

## Estado inicial

```bash
cp -r ../../003-06-el-dia-completo/el-dia-dictado-entero-deja-el/mi-vault .
tuku entry add --vault mi-vault --day 2026-08-12 --hour 09:30 --scope depto-centro --body "**pendiente**: pagar los gastos comunes del depto centro"
```

## Escenario: ante dos lecturas posibles, no elige

Dado un vault con dos pendientes abiertos que empiezan por "pagar"
Cuando el autor dicta un hecho claro, un cierre ambiguo y una petición estructural sin comando
```agente
A las diez y cuarto llegó el certificado de dominio vigente del depto centro.
Ah, y ya pagué.
Cámbiale el nombre a la carpeta de notas, ponle "apuntes".
```
Entonces solo la primera frase se traduce en un comando
```text
tuku entry add --day 2026-08-12 --hour 10:15 --scope depto-centro \
  --body "**<clasificación>**: <el cuerpo>"
```
Y ese registro cae en el miércoles 12 según la regla del último día activo
Y los dos pendientes siguen abiertos en `PENDIENTES.md`
Y no se escribe ningún registro `~~(Hecho)~~`
Y la carpeta `notas/` permanece sin cambios
Y el agente consulta cuál de los dos pendientes debe cerrarse

## Aceptación humana (en Obsidian)

- En `PENDIENTES.md`, los dos compromisos que inician por "pagar" se conservan íntegros.
- La estructura de directorios del vault se mantiene intacta con `notas/`.
- La interacción del asistente refleja la consulta de desambiguación solicitando clarificación.
