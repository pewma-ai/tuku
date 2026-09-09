# Escenario · 003-02-el-agente-lee-el-vault

**Cubre:** epic 003, segundo peldaño del eje "cuánto agente hay" y segundo del eje "qué se compara" ([`003-00`](003-00-el-dia-uno-dictado.md)).

El primer turno del epic, y el más barato de los que gastan tokens: el autor pregunta qué pasaría, el agente responde, y el vault no cambia. El diff vacío es por construcción, así que si algo cambió, cambió por una razón que ningún escenario posterior podría diagnosticar.

Lo que se afirma es que el agente **leyó su `AGENTS.md`**. No se lo pega nadie en el prompt: está en el vault y el agente corre dentro.

## Estado inicial

El que dejó [`003-01-el-vault-dice-a-donde-va`](003-01-el-vault-dice-a-donde-va.md): un vault sembrado cuya tabla de despacho no nombra ningún comando inexistente.

```bash
cp -r ../../003-01-el-vault-dice-a-donde-va/el-vault-nace-con-su-tabla-de/mi-vault .
```

## Escenario: el agente dice qué haría y no toca nada

Dado un vault sembrado, sin ningún registro escrito
Cuando el autor pregunta antes de dictar

```agente
Si te digo que hay que avisarle de los gastos comunes a la administradora, ¿qué anotarías y en qué archivo? No lo hagas todavía, quiero ver primero.
```

Entonces esa frase no se traduce en ningún comando

```text
(ninguno)
```

Y el vault queda exactamente igual que antes del turno
Y el agente no ejecutó ningún comando que escriba
Y su respuesta nombra los dos destinos: el registro va a `AHORA.md` y su consecuencia a `PENDIENTES.md`

La tercera es el punto entero del escenario. Un agente que responde "lo anoto en la bitácora" y para ahí va a dejar el vault a medias en cuanto se le pida de verdad, porque `tuku entry add` escribe el registro y nada más. Que sean dos pasos es lo primero que el `AGENTS.md` tiene que lograr transmitir, y es lo único que este turno mide.

## Qué no hace fallar

**Que corra comandos de lectura.** `tuku doctor`, un `entry lint` o un `ls` para mirar el vault antes de responder son legítimos y no cambian nada; lo que se afirma es el diff, no la abstinencia.

**Cómo lo dice.** La redacción es suya. Solo se busca que los dos destinos estén nombrados.

## Qué se mira a mano

La respuesta completa queda en `playground/<arnés>.<fecha>.003-02-el-agente-lee-el-vault.txt`, con lo que el autor dijo y lo que el agente ejecutó. Un turno no repite resultado, así que eso es la única evidencia que va a existir de esa corrida.

Léela una vez. Si explica el mecanismo en vez de decir qué quedaría escrito, eso es un hallazgo sobre el `AGENTS.md` y no sobre este escenario: la sección de estilo pide justamente lo contrario.

## Cómo se corre

Gasta tokens, así que se pide explícito. Y hereda del `003-01`, que es determinista: `-m agentic` lo dejaría fuera y la copia del estado inicial fallaría, así que se corren los dos.

```bash
uv run pytest tests/escenarios/ -k "003_01 or 003_02" -m "not red and not pendiente"
```

Necesita un arnés en el `PATH` (`agy` por defecto, o el que diga `TUKU_AGENTE`). Sin él, el test se salta en vez de fallar: no tener el ejecutable instalado no es un defecto del vault.

## El agente tiene que estar aislado de la máquina

El arnés lanza el turno con lo que aísle la sesión de la configuración del autor (en `agy`, `--new-project`). No es un detalle de implementación: la primera corrida de este escenario, sin eso, contestó sobre el vault real del autor, con sus rutas y el nombre de su administradora, pese a correr con el `cwd` dentro del vault de prueba.

Lo grave es cómo falla. Dos de los tres tests **pasaron**: un agente que está mirando otro vault tampoco toca este, así que el diff vacío y la ausencia de escrituras se cumplen solos. El único que lo destapó fue el que mira la respuesta. Sin él, el epic habría quedado verde midiendo la configuración de la máquina.
