# spec · tuku

> La superficie del CLI: qué comandos hay, con qué firma, y qué archivos del vault lee y escribe cada uno. La gramática que comparten está en [cli.md](cli.md), y qué significa lo que escriben, en la spec de cada primitiva. [`test_superficie.py`](../tests/unitarios/test_superficie.py) compara cada firma con el árbol de argparse.

## Cómo se lee

**La firma.** Un bloque por sección, y es lo normativo. `[x]` es opcional, `(a | b)` es uno de los dos y `…` es repetible. `--vault` vale en todos los comandos salvo `init` y no se repite. `# pendiente` marca un comando especificado y sin implementar; `# pendiente: --opción` marca las piezas que le faltan a uno que existe.

**El diagrama.** La línea continua escribe y la punteada lee. Un rótulo que empieza con "pendiente:" es comportamiento especificado y sin implementar.

| Color | Qué es |
| --- | --- |
| Verde | Comando que escribe |
| Rosa | Comando que revisa o lee, sin escribir |
| Gris punteado | Comando sin implementar |
| Gris | Archivo del vault |
| Ámbar | Lo derivado, lo que rehace [`tuku regenerate`](#mantención) |

## Sembrar

```text
tuku init DIR [--variant] [--author] [--at] [--force]
```

```mermaid
%%{init: {'flowchart': {'useMaxWidth': true}, 'theme': 'neutral', 'themeVariables': {'fontSize': '11px'}}}%%
flowchart LR
    subgraph CMD["tuku init"]
        direction TB
        IN["init DIR<br/>--variant --author --at --force"]
    end
    subgraph VAULT["Vault"]
        direction TB
        VA["Todo el vault"]
        AH["AHORA.md"]
        CF["reglas/config.tuku.md"]
        LE["LIBRO-DE-ESTILO.md"]
        CM["reglas/comandos.tuku.md"]
    end

    IN -->|"copia template/ de --variant;<br/>--force reemplaza un destino<br/>con contenido"| VA
    IN -->|"desde la plantilla, con el ciclo de --at"| AH
    IN -->|"la zona horaria de la máquina"| CF
    IN -->|"la línea del autor de --author"| LE
    IN -->|"la ayuda de cada comando"| CM

    classDef escribe fill:#dcfce7,color:#166534,stroke:#86efac
    classDef archivo fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    class IN escribe
    class VA,AH,CF,LE,CM archivo
```

## process

Un proceso es una rutina con nombre ([despacho.md](despacho.md)). Los de `tuku` son deterministas; los de `procesos/` los escribe el autor y los ejecuta el agente.

```text
tuku process
tuku process cycle [--from] [--to] [--name] [--force]   # pendiente: --from --to --name --force
```

```mermaid
%%{init: {'flowchart': {'useMaxWidth': true}, 'theme': 'neutral', 'themeVariables': {'fontSize': '11px'}}}%%
flowchart LR
    subgraph CMD["tuku process"]
        direction TB
        PL["process"]
        PC["process cycle<br/>--from --to --name --force"]
    end
    subgraph VAULT["Vault"]
        direction TB
        PR["procesos/"]
        TP["reglas/plantilla/AHORA.md"]
        BI["bitacoras/"]
        AH["AHORA.md"]
        PE["PENDIENTES.md"]
        CF["reglas/config.tuku.md"]
    end

    PL -.->|"lista los de tuku<br/>y los de procesos/"| PR
    PC -.->|"la plantilla"| TP
    PC -->|"la semana de lunes a domingo<br/>que contiene la fecha;<br/>si ya la cubre, solo verifica"| AH
    PC -.->|"pendiente: el rango de --from a --to;<br/>con semana, el que contiene --from"| AH
    PC -.->|"rechaza una fecha<br/>anterior a su from"| AH
    PC -.->|"pendiente: rechaza un --from que no sea<br/>el día siguiente al to del anterior,<br/>salvo repetir el ciclo abierto"| AH
    PC -.->|"pendiente: el nombre avanza en cycle_name<br/>solo si --from empieza después del to;<br/>--name fuera de la lista, solo con --force"| CF
    PC -.->|"si hay una bitácora anterior"| BI
    PC -->|"con bitácora anterior, abre<br/>revisar la bitácora anterior<br/>como tuku todo open"| PE

    classDef escribe fill:#dcfce7,color:#166534,stroke:#86efac
    classDef revisa fill:#fce7f3,color:#831843,stroke:#f9a8d4
    classDef archivo fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    class PC escribe
    class PL revisa
    class PR,TP,BI,AH,PE,CF archivo
```

## entry

```text
tuku entry create --body [--scope] [--at]
tuku entry update [CUÁNDO] --match TEXTO --body
tuku entry move [CUÁNDO] --match TEXTO --scope
```

`--match` ubica el último registro de `AHORA.md` que calza, y `CUÁNDO` busca en un ciclo cerrado ([bitacora.md](bitacora.md), "Corregir un registro ya escrito").

```mermaid
%%{init: {'flowchart': {'useMaxWidth': true}, 'theme': 'neutral', 'themeVariables': {'fontSize': '11px'}}}%%
flowchart LR
    subgraph CMD["tuku entry"]
        direction TB
        EC["entry create<br/>--body --scope --at"]
        EU["entry update<br/>CUÁNDO --match --body"]
        EM["entry move<br/>CUÁNDO --match --scope"]
    end
    subgraph VAULT["Vault"]
        direction TB
        AH["AHORA.md"]
        BI["bitacoras/"]
        PE["PENDIENTES.md"]
        AM["ambitos/"]
        CF["reglas/config.tuku.md"]
        DER["Lo derivado"]
    end

    EC -->|"el registro bajo el día de --at,<br/>en orden de hora"| AH
    EC -->|"en un día pasado sin hora,<br/>al final del día"| AH
    EC -.->|"sin --scope, scope_default"| CF
    EC -.->|"que exista el ámbito de --scope,<br/>y su ruta para el link"| AM
    EU -->|"el cuerpo del último registro<br/>que calza con --match"| AH
    EU & EM -->|"si es pendiente, su fila"| PE
    EM -->|"el ámbito del registro"| AH
    EM -->|"con CUÁNDO, en un ciclo cerrado"| BI
    EC & EU & EM -->|"rehace"| DER

    classDef escribe fill:#dcfce7,color:#166534,stroke:#86efac
    classDef archivo fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    classDef derivado fill:#fef3c7,color:#92400e,stroke:#fcd34d
    class EC,EU,EM escribe
    class AH,BI,PE,AM,CF archivo
    class DER derivado
```

## todo

```text
tuku todo open --body [--scope] [--at] [--due | --horizon] [--no-regenerate]
tuku todo close TEXTO [--scope] [--at] [--no-regenerate]
```

```mermaid
%%{init: {'flowchart': {'useMaxWidth': true}, 'theme': 'neutral', 'themeVariables': {'fontSize': '11px'}}}%%
flowchart LR
    subgraph CMD["tuku todo"]
        direction TB
        TO["todo open<br/>--body --scope --at<br/>--due o --horizon<br/>--no-regenerate"]
        TC["todo close TEXTO<br/>--scope --at<br/>--no-regenerate"]
    end
    subgraph VAULT["Vault"]
        direction TB
        AH["AHORA.md"]
        PE["PENDIENTES.md"]
        CF["reglas/config.tuku.md"]
        LE["LIBRO-DE-ESTILO.md"]
        DER["Lo derivado<br/>vistas de pendientes,<br/>salvo --no-regenerate;<br/>actividad de los ámbitos, siempre"]
    end

    TO -->|"registro pendiente bajo el día de --at,<br/>una sola vez"| AH
    TO -->|"fila bajo su horizonte:<br/>con fecha si --due,<br/>el de --horizon o el primero"| PE
    TO -.->|"los horizontes"| LE
    TC -->|"registro (Hecho) tachado;<br/>borra el pendiente si se abrió<br/>ese mismo día"| AH
    TC -->|"borra la fila cuyo texto es TEXTO"| PE
    TO -.->|"sin --scope, scope_default"| CF
    TC -.->|"sin --scope, el ámbito de la fila;<br/>si no tiene, scope_default"| CF
    TO & TC -->|"rehace"| DER

    classDef escribe fill:#dcfce7,color:#166534,stroke:#86efac
    classDef archivo fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    classDef derivado fill:#fef3c7,color:#92400e,stroke:#fcd34d
    class TO,TC escribe
    class AH,PE,CF,LE archivo
    class DER derivado
```

## scope

```text
tuku scope create NOMBRE [--parent] [--keyword…] [--at] [--since]
tuku scope update NOMBRE [--keyword…]
tuku scope move NOMBRE [--parent]
tuku scope rename NOMBRE NUEVO
tuku scope archive NOMBRE                                           # pendiente
```

`--parent` acepta el nombre o la ruta (`negocio/clientes`). En `scope create`, `--since` vale 7 días por defecto ([ambitos.md](ambitos.md), "Lo escrito antes de abrir un ámbito").

```mermaid
%%{init: {'flowchart': {'useMaxWidth': true}, 'theme': 'neutral', 'themeVariables': {'fontSize': '11px'}}}%%
flowchart LR
    subgraph CMD["tuku scope"]
        direction TB
        SC["scope create NOMBRE<br/>--parent --keyword --at --since"]
        SU["scope update NOMBRE<br/>--keyword"]
        SM["scope move NOMBRE<br/>--parent"]
        SR["scope rename NOMBRE NUEVO"]
        SA["scope archive NOMBRE"]
    end
    subgraph VAULT["Vault"]
        direction TB
        PG["ambitos/…/NOMBRE/NOMBRE.md"]
        AH["AHORA.md"]
        BI["bitacoras/"]
        VA["Todo el vault"]
        DER["Lo derivado: callout de hijos<br/>y parent: de cada página"]
    end

    SC -->|"carpeta dentro de --parent<br/>(crea la categoría que falta)<br/>o en la raíz, página con<br/>sus keywords y su parent:"| PG
    SC -->|"constancia en la bitácora,<br/>con link al ámbito padre"| AH
    SC -.->|"lista los registros que lo nombran,<br/>desde --since"| BI
    SU -->|"suma cada --keyword a keywords"| PG
    SM -->|"mueve la carpeta dentro de<br/>--parent o a la raíz"| PG
    SR -->|"renombra carpeta, página,<br/>keywords y ancla"| PG
    SM & SR -->|"ruta y texto de cada link<br/>al ámbito, también en bitacoras/"| VA
    SC & SM & SR -->|"rehace"| DER

    classDef escribe fill:#dcfce7,color:#166534,stroke:#86efac
    classDef pendiente fill:#f8fafc,color:#64748b,stroke:#94a3b8,stroke-dasharray: 4 3
    classDef archivo fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    classDef derivado fill:#fef3c7,color:#92400e,stroke:#fcd34d
    class SC,SU,SM,SR escribe
    class SA pendiente
    class PG,AH,BI,VA archivo
    class DER derivado
```

## note

```text
tuku note create TÍTULO (--body | --body-file) [--scope] [--subtype] [--at] [--no-record]
tuku note rename TÍTULO NUEVO
tuku note archive TÍTULO                                            # pendiente
```

```mermaid
%%{init: {'flowchart': {'useMaxWidth': true}, 'theme': 'neutral', 'themeVariables': {'fontSize': '11px'}}}%%
flowchart LR
    subgraph CMD["tuku note"]
        direction TB
        NC["note create TÍTULO<br/>--body o --body-file<br/>--scope --subtype --at --no-record"]
        NR["note rename TÍTULO NUEVO"]
        NA["note archive TÍTULO"]
    end
    subgraph VAULT["Vault"]
        direction TB
        NO["notas/TITULO-EN-SLUG.md"]
        LE["LIBRO-DE-ESTILO.md"]
        AH["AHORA.md"]
        VA["Todo el vault"]
        DER["Lo derivado: actividad<br/>de la página del ámbito"]
    end

    NC -->|"frontmatter con subtype, created y updated de --at,<br/>cuerpo y Ver además con --scope<br/>y los links del cuerpo"| NO
    NC -.->|"--subtype debe ser una fila<br/>de Tipos de nota"| LE
    NC -->|"constancia en la bitácora,<br/>salvo --no-record"| AH
    NC -->|"con --scope, rehace"| DER
    NR -->|"renombra archivo y título"| NO
    NR -->|"ruta y texto de cada link<br/>a la nota, también en bitacoras/"| VA

    classDef escribe fill:#dcfce7,color:#166534,stroke:#86efac
    classDef pendiente fill:#f8fafc,color:#64748b,stroke:#94a3b8,stroke-dasharray: 4 3
    classDef archivo fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    classDef derivado fill:#fef3c7,color:#92400e,stroke:#fcd34d
    class NC,NR escribe
    class NA pendiente
    class NO,LE,AH,VA archivo
    class DER derivado
```

## context

Lo que el agente necesita para decidir, sin abrir archivos. Sin `TEMA`, todos.

```text
tuku context [TEMA] [--since] [--late]
```

`--since` (2 días por defecto) acota los registros de `entry`. `context note` trae las últimas notas de cada tipo enlazable, tantas como diga `context_note_limit` en `reglas/config.tuku.md` (25 por defecto). `--late` solo vale con `todo` y deja únicamente los pendientes atrasados.

```mermaid
%%{init: {'flowchart': {'useMaxWidth': true}, 'theme': 'neutral', 'themeVariables': {'fontSize': '11px'}}}%%
flowchart LR
    subgraph CMD["tuku context"]
        direction TB
        CX["context TEMA<br/>--since --late"]
    end
    subgraph VAULT["Vault"]
        direction TB
        AH["AHORA.md"]
        BI["bitacoras/"]
        AM["ambitos/"]
        PE["PENDIENTES.md"]
        LE["LIBRO-DE-ESTILO.md"]
        NO["notas/"]
    end

    CX -.->|"entry: los registros<br/>desde --since"| AH
    CX -.->|"entry: si --since cruza<br/>un ciclo cerrado"| BI
    CX -.->|"scope: el árbol con sus keywords"| AM
    CX -.->|"todo: abiertos y atrasados;<br/>con --late, solo los atrasados"| PE
    CX -.->|"style: clasificaciones,<br/>horizontes y tipos de nota"| LE
    CX -.->|"note: por tipo enlazable, las últimas<br/>con título y aliases"| NO

    classDef revisa fill:#fce7f3,color:#831843,stroke:#f9a8d4
    classDef archivo fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    class CX revisa
    class AH,BI,AM,PE,LE,NO archivo
```

## Mantención

Se distinguen por lo que escriben, y por eso se sabe cuál puede correr desatendido ([cli.md](cli.md)).

```text
tuku doctor [TEMA] [ARCHIVO] [--verbose]
tuku regenerate [TEMA]
tuku fix TEMA
```

| Comando | Escribe | Temas |
| --- | --- | --- |
| `doctor` | Nada | `config`, `version`, `types`, `files`, `frontmatter`, `dispatch`, `link`, `cycle`, `entry`, `todo`, `style`, `scope` y `note`, el único que acepta `ARCHIVO` |
| `regenerate` | Solo lo derivado | `todo`, `scope` y `comandos` |
| `fix` | Lo canónico, solo lo determinista, y devuelve las decisiones del autor | `link` y `todo` |

```mermaid
%%{init: {'flowchart': {'useMaxWidth': true}, 'theme': 'neutral', 'themeVariables': {'fontSize': '11px'}}}%%
flowchart LR
    subgraph CMD["doctor, regenerate y fix"]
        direction TB
        DO["doctor TEMA ARCHIVO<br/>--verbose"]
        RG["regenerate TEMA"]
        FX["fix TEMA"]
    end
    subgraph VAULT["Vault"]
        direction TB
        VA["Todo el vault"]
        PE["PENDIENTES.md"]
        AH["AHORA.md"]
        BI["bitacoras/"]
        PA["ambitos/PENDIENTES-AMBITOS.md"]
        PG["ambitos/…/NOMBRE/NOMBRE.md"]
        CM["reglas/comandos.tuku.md"]
    end

    DO -.->|"cada tema; con TEMA, solo ese"| VA
    RG -.->|"la tabla"| PE
    RG -.->|"los registros de los<br/>últimos doce meses"| BI
    RG -->|"todo: el callout de pendientes<br/>bajo cada día"| AH
    RG -->|"todo: un callout por ámbito"| PA
    RG -->|"scope: Esta semana, Actividad<br/>reciente y el callout de hijos"| PG
    RG -->|"comandos: desde la ayuda"| CM
    FX -->|"link: cada wikilink a link<br/>con ruta relativa"| VA
    FX -->|"todo: borra el registro pendiente<br/>cerrado el mismo día, y rehace"| AH

    classDef escribe fill:#dcfce7,color:#166534,stroke:#86efac
    classDef revisa fill:#fce7f3,color:#831843,stroke:#f9a8d4
    classDef archivo fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    classDef derivado fill:#fef3c7,color:#92400e,stroke:#fcd34d
    class RG,FX escribe
    class DO revisa
    class VA,PE,AH,BI archivo
    class PA,PG,CM derivado
```

## Lo que se retira

Comandos y opciones que existen hoy y que la firma de arriba reemplaza. Una línea sale de aquí cuando sale del CLI ([`../TODO.md`](../TODO.md), "Superficie del CLI").

```text
tuku process cycle --at         → tuku process cycle --from
```
