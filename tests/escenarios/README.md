# tests/escenarios

El arnés que ejecuta los casos narrativos de `../../corpus/escenarios/`. El caso (Dado/Cuando/Entonces) vive en `corpus/`, porque es dato de prueba; lo que aquí vive es el código que lo corre y compara el resultado.

Por qué separado de `tests/` a secas: gran parte de TUKU depende de un agente y es semi determinista. Lo que se puede verificar con un `assert` clásico vive acá; lo que solo se puede juzgar leyendo el resultado se deja escrito en el propio archivo de `corpus/escenarios/`, bajo "Qué se mira a mano", y no se finge que un test lo cubre.

Vacío por ahora. El primer caso a automatizar es `001-001-instalacion-minima`, que es 100% determinista (fase 0, sin agente): instalar con `src/install_test_scenario.py` y comparar `AHORA.md` contra lo esperado para una fecha fija.

Esta suite se escribe desde cero (no reutiliza los tests del diseño anterior).

## Convención de nombre

`test_XXX_YYY_slug.py`, uno por escenario, con el mismo `XXX-YYY-slug` del archivo en `corpus/escenarios/` pero con guiones bajos, porque es un módulo de Python. El fixture asociado va en `fixtures/XXX-YYY-slug/`, con guiones, porque es un directorio de datos y no un módulo. La función de test lleva el mismo prefijo: `test_XXX_YYY_slug_<qué verifica>`.
