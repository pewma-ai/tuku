# ADR 0009 — `type` es string libre; el sistema indexa, no valida

## Contexto

Las entidades del sistema son de naturalezas distintas: proyectos, áreas permanentes,
clientes, instrumentos, empleados, profesionales de salud. La forma estándar de manejar
esta diversidad es definir un catálogo cerrado de tipos y validar contra él. Eso permite
plantillas específicas, cadencias por tipo, y restricciones semánticas.

Un catálogo cerrado tiene una ventaja real: el sistema sabe de antemano qué puede esperar de
cada tipo y puede optimizar su comportamiento. Los errores de tipo se detectan al alta, no
después.

## Decisión

El campo `type` es **string libre**. El sistema lo indexa para el tesauro vivo y para la
resolución de cadencias heredadas, pero no lo valida contra ningún catálogo predefinido.

Un tipo de entidad es, como mucho, una plantilla de front matter más una lista de cadencias
declaradas en `tipos/<ámbito>/<tipo>.md`. No hay editor de esquemas, ni validación fuerte,
ni UI de configuración. El usuario define tipos conversando con el agente; el agente los
escribe.

La alternativa cerrada implicaría que el sistema conoce de antemano que una PyME de insumos
escolares necesita `cliente`, `proveedor`, `producto`, y que un observatorio necesita
`instrumento`, `turno`, `colaboracion`. Eso es exactamente lo que no se puede anticipar sin
conocer al usuario.

## Consecuencias

**A favor.**

- Un nuevo tipo surge de una conversación, no de una pantalla de configuración. El onboarding
  es registrar, no configurar.
- El mismo motor sirve a un observatorio y a una PyME sin modificación. La diversidad de
  dominios es configuración del usuario, no código del sistema.
- El catálogo puede crecer sin migración: agregar `type: cotizacion` a una entidad no rompe
  nada.

**En contra, y aceptado.**

- El sistema no puede advertir sobre un tipo mal escrito (`clietne` en vez de `cliente`). El
  RADAR puede detectar tipos sin cadencias ni plantilla asociada y sugerir revisión.
- Las plantillas de tipo son opcionales: el usuario puede crear entidades sin plantilla y el
  sistema las acepta. Requiere más disciplina del usuario o más proactividad del agente.
- Sin catálogo, la documentación de qué tipos existen en un perfil vive solo en el índice
  que construyen los janitors, no en ninguna fuente de verdad explícita.

## Estado

`aceptado`
