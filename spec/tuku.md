# spec · tuku

Qué archivos del vault lee (línea punteada) y escribe (línea continua) cada comando de `tuku` y cada opción, según su ayuda. Lo derivado es lo que rehace [`tuku regenerate`](#sembrar-y-regenerar), y `--vault` elige el vault en todos los comandos salvo `init`.

## entry

```mermaid
%%{init: {'flowchart': {'useMaxWidth': true}, 'theme': 'neutral', 'themeVariables': {'fontSize': '11px'}}}%%
flowchart LR
    subgraph CMD["tuku entry"]
        direction TB
        EC["entry create<br/>--body --scope --at"]
        ER["entry rename<br/>--body --at"]
        EL["entry lint"]
    end
    subgraph VAULT["Vault"]
        direction TB
        AH["AHORA.md"]
        PE["PENDIENTES.md"]
        AM["ambitos/"]
        CF["reglas/config.tuku.md"]
        LE["LIBRO-DE-ESTILO.md"]
        DER["Lo derivado<br/>(como tuku regenerate)"]
    end

    EC -->|"el registro bajo el día de --at,<br/>en orden de hora"| AH
    EC -.->|"sin --scope, scope_default"| CF
    EC -.->|"que exista el ámbito de --scope,<br/>y su ruta para el link"| AM
    EC -->|"rehace"| DER
    ER -->|"reemplaza el cuerpo del registro de --at"| AH
    ER -->|"si es pendiente, también su fila"| PE
    ER -->|"si es pendiente, rehace"| DER
    EL -.->|"forma de cada registro"| AH
    EL -.->|"que cada marca exista"| LE

    style EC fill:#dcfce7,color:#166534,stroke:#86efac
    style ER fill:#dcfce7,color:#166534,stroke:#86efac
    style EL fill:#fce7f3,color:#831843,stroke:#f9a8d4
    style AH fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style PE fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style AM fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style CF fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style LE fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style DER fill:#fef3c7,color:#92400e,stroke:#fcd34d
```

## todo

```mermaid
%%{init: {'flowchart': {'useMaxWidth': true}, 'theme': 'neutral', 'themeVariables': {'fontSize': '11px'}}}%%
flowchart LR
    subgraph CMD["tuku todo"]
        direction TB
        TO["todo open<br/>--body --scope --at<br/>--due o --horizon<br/>--no-propagate"]
        TC["todo close<br/>--body --scope --at<br/>--no-propagate"]
        TL["todo lint"]
    end
    subgraph VAULT["Vault"]
        direction TB
        AH["AHORA.md"]
        PE["PENDIENTES.md"]
        CF["reglas/config.tuku.md"]
        LE["LIBRO-DE-ESTILO.md"]
        DER["Lo derivado<br/>vistas de pendientes,<br/>salvo --no-propagate;<br/>actividad de los ámbitos, siempre"]
    end

    TO -->|"registro pendiente bajo el día de --at,<br/>una sola vez"| AH
    TO -->|"fila bajo su horizonte:<br/>con fecha si --due,<br/>el de --horizon o el primero"| PE
    TO -.->|"los horizontes"| LE
    TC -->|"registro (Hecho) tachado;<br/>borra el pendiente si se abrió<br/>ese mismo día"| AH
    TC -->|"borra la fila que coincide<br/>palabra por palabra"| PE
    TO & TC -.->|"sin --scope, scope_default"| CF
    TO & TC -->|"rehace"| DER
    TL -.->|"cada pendiente con su fila"| AH
    TL -.->|"ninguno en dos filas, vistas al día"| PE

    style TO fill:#dcfce7,color:#166534,stroke:#86efac
    style TC fill:#dcfce7,color:#166534,stroke:#86efac
    style TL fill:#fce7f3,color:#831843,stroke:#f9a8d4
    style AH fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style PE fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style CF fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style LE fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style DER fill:#fef3c7,color:#92400e,stroke:#fcd34d
```

## scope

```mermaid
%%{init: {'flowchart': {'useMaxWidth': true}, 'theme': 'neutral', 'themeVariables': {'fontSize': '11px'}}}%%
flowchart LR
    subgraph CMD["tuku scope"]
        direction TB
        SC["scope create NOMBRE<br/>--keyword --parent --at"]
        SU["scope update NOMBRE<br/>--keyword"]
        SM["scope move NOMBRE<br/>--parent"]
        SR["scope rename NOMBRE NUEVO"]
        SL["scope lint"]
    end
    subgraph VAULT["Vault"]
        direction TB
        PG["ambitos/…/NOMBRE/NOMBRE.md"]
        AH["AHORA.md"]
        PA["ambitos/PENDIENTES-AMBITOS.md"]
        VA["Todo el vault<br/>(incluye bitacoras/)"]
        DER["Lo derivado<br/>(como tuku regenerate)"]
    end

    SC -->|"carpeta dentro de --parent<br/>o en la raíz, página con<br/>keywords de --keyword"| PG
    SC -->|"nota: abrí el ámbito, bajo --parent,<br/>a la hora de --at"| AH
    SU -->|"suma cada --keyword a keywords"| PG
    SM -->|"mueve la carpeta dentro de --parent<br/>o a la raíz"| PG
    SR -->|"renombra carpeta, página,<br/>keywords y ancla"| PG
    SM & SR -->|"ruta y texto de cada link al ámbito"| VA
    SC & SM & SR -->|"rehace"| DER
    SL -.->|"ningún registro apunta a una categoría"| AH
    SL -.->|"cada página transcluye sus pendientes"| PG
    SL -.->|"un callout por ámbito"| PA

    style SC fill:#dcfce7,color:#166534,stroke:#86efac
    style SU fill:#dcfce7,color:#166534,stroke:#86efac
    style SM fill:#dcfce7,color:#166534,stroke:#86efac
    style SR fill:#dcfce7,color:#166534,stroke:#86efac
    style SL fill:#fce7f3,color:#831843,stroke:#f9a8d4
    style PG fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style AH fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style PA fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style VA fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style DER fill:#fef3c7,color:#92400e,stroke:#fcd34d
```

## note

```mermaid
%%{init: {'flowchart': {'useMaxWidth': true}, 'theme': 'neutral', 'themeVariables': {'fontSize': '11px'}}}%%
flowchart LR
    subgraph CMD["tuku note"]
        direction TB
        NC["note create TÍTULO<br/>--body o --body-file<br/>--scope --at --no-record"]
        NR["note rename TÍTULO NUEVO"]
        NL["note lint ARCHIVO"]
    end
    subgraph VAULT["Vault"]
        direction TB
        NO["notas/TITULO-EN-SLUG.md"]
        AH["AHORA.md"]
        PG["ambitos/…/NOMBRE/NOMBRE.md"]
        VA["Todo el vault<br/>(incluye bitacoras/)"]
    end

    NC -->|"frontmatter con created de --at,<br/>cuerpo, link a --scope<br/>y Ver además"| NO
    NC -->|"nota: escribí la nota,<br/>salvo --no-record"| AH
    NC -->|"con --scope, la actividad de su página"| PG
    NR -->|"renombra archivo y título"| NO
    NR -->|"ruta y texto de cada link a la nota"| VA
    NL -.->|"Ver además y para qué<br/>conecta cada link;<br/>sin ARCHIVO, todas"| NO

    style NC fill:#dcfce7,color:#166534,stroke:#86efac
    style NR fill:#dcfce7,color:#166534,stroke:#86efac
    style NL fill:#fce7f3,color:#831843,stroke:#f9a8d4
    style NO fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style AH fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style PG fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style VA fill:#f1f5f9,color:#334155,stroke:#cbd5e1
```

## cycle

```mermaid
%%{init: {'flowchart': {'useMaxWidth': true}, 'theme': 'neutral', 'themeVariables': {'fontSize': '11px'}}}%%
flowchart LR
    subgraph CMD["tuku cycle"]
        direction TB
        CO["cycle open<br/>--at"]
        CL["cycle lint"]
    end
    subgraph VAULT["Vault"]
        direction TB
        TP["reglas/plantilla/AHORA.md"]
        BI["bitacoras/"]
        AH["AHORA.md"]
        PE["PENDIENTES.md"]
    end

    CO -.->|"la plantilla"| TP
    CO -->|"la semana de lunes a domingo<br/>que contiene --at;<br/>si ya la cubre, solo verifica"| AH
    CO -.->|"si hay una bitácora anterior"| BI
    CO -->|"con bitácora anterior, abre<br/>revisar la bitácora anterior<br/>como tuku todo open"| PE
    CL -.->|"frontmatter y días consecutivos"| AH

    style CO fill:#dcfce7,color:#166534,stroke:#86efac
    style CL fill:#fce7f3,color:#831843,stroke:#f9a8d4
    style TP fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style BI fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style AH fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style PE fill:#f1f5f9,color:#334155,stroke:#cbd5e1
```

## Sembrar y regenerar

```mermaid
%%{init: {'flowchart': {'useMaxWidth': true}, 'theme': 'neutral', 'themeVariables': {'fontSize': '11px'}}}%%
flowchart LR
    subgraph CMD["init y regenerate"]
        direction TB
        IN["init DIR<br/>--variant --author --at --force"]
        RG["regenerate TEMA<br/>todo, scope o comandos"]
    end
    subgraph VAULT["Vault"]
        direction TB
        VA["Todo el vault"]
        AH["AHORA.md"]
        CF["reglas/config.tuku.md"]
        LE["LIBRO-DE-ESTILO.md"]
        PE["PENDIENTES.md"]
        PA["ambitos/PENDIENTES-AMBITOS.md"]
        PG["ambitos/…/NOMBRE/NOMBRE.md"]
        CM["reglas/comandos.tuku.md"]
    end

    IN -->|"copia template/ de --variant;<br/>--force reemplaza un destino<br/>con contenido"| VA
    IN -->|"desde la plantilla, con el ciclo de --at"| AH
    IN -->|"la zona horaria de la máquina"| CF
    IN -->|"la línea del autor de --author"| LE
    RG -.->|"la tabla"| PE
    RG -->|"todo: el callout de pendientes<br/>bajo cada día"| AH
    RG -->|"todo: un callout por ámbito"| PA
    RG -->|"scope: la actividad desde AHORA.md<br/>y el callout de hijos"| PG
    RG -->|"comandos: desde la ayuda"| CM

    style IN fill:#dcfce7,color:#166534,stroke:#86efac
    style RG fill:#dcfce7,color:#166534,stroke:#86efac
    style VA fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style AH fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style CF fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style LE fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style PE fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style PA fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style PG fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style CM fill:#f1f5f9,color:#334155,stroke:#cbd5e1
```

Sin TEMA, `regenerate` hace los tres.

## Revisar y reparar

```mermaid
%%{init: {'flowchart': {'useMaxWidth': true}, 'theme': 'neutral', 'themeVariables': {'fontSize': '11px'}}}%%
flowchart LR
    subgraph CMD["doctor, fix, vocab y style"]
        direction TB
        DO["doctor TEMA<br/>-v"]
        FX["fix TEMA<br/>link o todo"]
        VS["vocab show"]
        SL["style lint"]
    end
    subgraph VAULT["Vault"]
        direction TB
        VA["Todo el vault<br/>(incluye bitacoras/)"]
        AH["AHORA.md"]
        LE["LIBRO-DE-ESTILO.md"]
        DER["Lo derivado<br/>(como tuku regenerate)"]
    end

    DO -.->|"todos los lint, config, types.md,<br/>AGENTS.md, links y versión;<br/>con TEMA, solo esa parte"| VA
    FX -->|"link: cada wikilink a link<br/>con ruta relativa"| VA
    FX -->|"todo: borra el registro pendiente<br/>cerrado el mismo día"| AH
    FX -->|"todo: rehace"| DER
    VS -.->|"Clasificaciones, Horizontes<br/>y Tipos de nota"| LE
    SL -.->|"la línea del autor y las tres tablas"| LE

    style DO fill:#fce7f3,color:#831843,stroke:#f9a8d4
    style FX fill:#dcfce7,color:#166534,stroke:#86efac
    style VS fill:#fce7f3,color:#831843,stroke:#f9a8d4
    style SL fill:#fce7f3,color:#831843,stroke:#f9a8d4
    style VA fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style AH fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style LE fill:#f1f5f9,color:#334155,stroke:#cbd5e1
    style DER fill:#fef3c7,color:#92400e,stroke:#fcd34d
```
