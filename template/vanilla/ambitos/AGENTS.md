# Reglas de todos los ámbitos

Vale para todo lo que cuelga de `ambitos/`. Una regla de una sola rama va en el `AGENTS.md` de esa carpeta, y gana la más cercana.

## Crear un ámbito

- **Cuando el autor lo pide** («ábrelo aparte»), en el punto del dictado donde lo pide: lo que contó antes se registra en el ámbito que correspondía en ese momento. Si algo aparece seguido sin página, propónselo y espera el sí.
- **`tuku scope create NOMBRE`**, con el nombre como lo dijo el autor y `--at` como en un registro. El comando deja la constancia en la bitácora.
- **Las keywords** son las palabras que delatan el ámbito sin nombrarlo: personas, siglas, lugares. La salida del comando las pide: pregúntaselas al autor y súmalas con `tuku scope update colegio-los-robles --keyword "don Rodolfo",LR`. Si ya las dijo, van en el mismo `scope create`.
- **Si un comando rechaza un ámbito que no existe**, ofrécele al autor crearlo y espera el sí.

## Un ámbito dentro de otro

`--parent` al crearlo (`tuku scope create bodega --parent negocio`), o `tuku scope move bodega --parent negocio` si ya existe; sin `--parent`, `move` lo lleva a la raíz de `ambitos/`. El padre tiene que existir: si falta, ofrécele al autor crearlo. Los registros nombran el ámbito sin ruta: `--scope bodega`.

## Reglas y cadencias de un ámbito

Un ámbito trae solo su página. Su `AGENTS.md` o su `CADENCIAS.md` se crean con la primera regla o cadencia, después de preguntarle al autor.
