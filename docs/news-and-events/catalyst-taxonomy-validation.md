# Matriz de resultados esperados: taxonomía de catalizadores

**Documento complementario del Issue:** [#1 — Definir taxonomía y cobertura de catalizadores](https://github.com/Osleyder1985/SINAYXA/issues/1)  
**Documento principal:** [Taxonomía de catalizadores](catalyst-taxonomy.md)  
**Tipo:** especificación normativa y oráculo de validación; no es un clasificador implementado.

## 1. Propósito

Esta matriz convierte los 18 casos de cobertura del Issue #1 en resultados esperados explícitos. Sirve para que una revisión humana o una futura suite de pruebas compruebe que dos evaluadores aplican la taxonomía de forma consistente.

Los resultados son reglas de clasificación, no afirmaciones de que un acontecimiento real haya ocurrido. Si faltan los datos indicados, el resultado debe quedar como indeterminado/no evaluable; nunca se completará mediante inferencias.

## 2. Oráculo de los 18 casos

| # | Entrada o escenario | Resultado esperado | Categoría principal | Distinción/condición obligatoria |
| ---: | --- | --- | --- | --- |
| 1 | Banco central anuncia una decisión de tipos | INCLUIR | MAC | ECO solo como secundaria si el contenido económico adicional está documentado; separar decisión, comunicación y efecto hipotético |
| 2 | Dato de inflación anunciado en calendario, publicado y luego revisado | INCLUIR como hitos relacionados | ECO | Mantener fecha programada, publicación inicial y revisión como hitos diferenciados; no sobrescribir el dato inicial |
| 3 | Se presenta una propuesta regulatoria todavía no aprobada | INCLUIR como propuesta | REG | Estado = propuesta; no clasificar ni describir como norma vigente |
| 4 | ETF pasa por solicitud, modificación, aprobación/rechazo, suspensión o lanzamiento | INCLUIR cada hito material | ETF | Cada fase debe tener estado propio; una solicitud no equivale a aprobación y aprobación no equivale necesariamente a lanzamiento |
| 5 | Empresa compra BTC; existen también conversaciones o rumores previos | INCLUIR la compra solo con evidencia suficiente; rumor separado como afirmación no confirmada si cumple evidencia mínima | INS | No convertir intención, negociación o rumor en compra ejecutada |
| 6 | Exchange sufre un hackeo | INCLUIR | EXC | Asociar activos, fondos y pérdidas únicamente con evidencia; distinguir incidente, alcance estimado y recuperación |
| 7 | Protocolo anuncia y activa una actualización, con resultado posterior | INCLUIR hitos materiales relacionados | TEC | Distinguir anuncio, activación, resultado observado y eventual fallo |
| 8 | Exploit afecta a un protocolo DeFi y puede propagarse | INCLUIR | TEC | Asociar protocolos, stablecoins, colateral y contagio solo cuando exista evidencia del vínculo |
| 9 | Stablecoin pierde materialmente la paridad frente a una oscilación menor | INCLUIR pérdida material; EXCLUIR fluctuación ordinaria sin relevancia acreditada | TEC si el hecho inmediato es un fallo técnico/de protocolo; INS si es solvencia, reservas o redenciones del emisor; REG si deriva de una decisión regulatoria | No inventar umbral numérico; documentar magnitud observada y clasificar por la naturaleza inmediata del hecho, no por sus consecuencias |
| 10 | Token se desbloquea, emite, transfiere o vende | INCLUIR cada hecho material que esté probado | TEC para emisión, quema, desbloqueo o cambio de tokenomics; INS para compra/venta o decisión de un titular institucional; EXC si la transferencia es un incidente de exchange/custodia | Desbloqueo no demuestra transferencia a mercado ni venta; no inferir presión vendedora realizada |
| 11 | Minería o validación cambia de forma operativa/económicamente material | INCLUIR si existe exposición y mecanismo documentados | TEC para cambios de protocolo, consenso o funcionamiento de red; INS para decisiones/cierres de operadores; ECO para shocks de energía o costes externos; REG para restricciones legales | La categoría principal corresponde al hecho inmediato; una métrica aislada no basta |
| 12 | Propuesta de gobernanza pasa a votación y luego a ejecución | INCLUIR hitos relacionados | TEC | Diferenciar propuesta, votación, resultado y ejecución efectiva |
| 13 | Acontecimiento geopolítico con canal económico/financiero plausible | INCLUIR si el canal está documentado; en caso contrario EXCLUIR como catalizador | GEO | No basta la relevancia mediática ni la coincidencia con un movimiento de precio |
| 14 | Información anterior al anuncio oficial procede de una fuente identificable y fechable | INCLUIR como anticipatoria con estado real de corroboración | Según naturaleza del acontecimiento anticipado | No confirmar por repetición; registrar por separado publicación, primera detección y anuncio oficial |
| 15 | Varios medios reproducen el mismo acontecimiento | UN SOLO acontecimiento con varias referencias | Según naturaleza del hecho | Nuevas publicaciones no crean eventos nuevos; registrar actualización solo si aportan información material |
| 16 | Acontecimiento macro sin activo cripto concreto, pero con transmisión al mercado general | INCLUIR si el mecanismo es explícito y documentable | ECO, MAC o GEO según el hecho inmediato | No inventar activos afectados; declarar alcance = mercado cripto general o activo no identificado |
| 17 | Noticia menciona Bitcoin pero no tiene mecanismo plausible de transmisión | EXCLUIR | Ninguna | La mención de un criptoactivo no satisface el criterio de relevancia |
| 18 | Un acontecimiento tiene dimensiones económicas, regulatorias y geopolíticas | UN SOLO acontecimiento con una categoría principal y secundarias justificadas | Según objeto inmediato | No duplicar por categorías; justificar la precedencia y las relaciones secundarias |

### Regla de indeterminación

Cuando el escenario no aporta evidencia suficiente para decidir inclusión, categoría o estado, el resultado esperado es **INDETERMINADO / EVIDENCIA INSUFICIENTE**, no una clasificación afirmativa. El evaluador debe indicar qué dato falta. Esta salida no equivale automáticamente a excluir el acontecimiento del sistema: significa que no se puede confirmar la decisión con la información disponible.

## 3. Identidad del acontecimiento y secuencias de hitos

Para fines taxonómicos:

- Una **fuente/publicación** es una pieza de información; no es por sí misma el acontecimiento.
- Un **acontecimiento** es un hecho, decisión o cambio verificable con identidad propia.
- Un **hito** es una fase material dentro del ciclo de vida de un proceso (por ejemplo, solicitud, aprobación, activación, ejecución, cancelación o resultado).
- Dos hitos de un mismo proceso pueden ser acontecimientos diferenciados y relacionados; no deben fusionarse si cambian el estado del proceso, producen una decisión nueva o aportan un resultado verificable.
- Una nueva noticia sobre el mismo hecho no crea otro acontecimiento salvo que introduzca un hecho/hito distinto o información material nueva.
- La relación entre hitos no implica que el resultado de uno pruebe automáticamente el siguiente.

Ejemplo normativo: una filtración sobre una posible aprobación, la aprobación oficial y la entrada efectiva en vigor son registros/hitos diferenciados y relacionados. La aprobación posterior no debe reescribir la evidencia ni la incertidumbre que existían antes de su anuncio.

Esta sección define el significado y la separación conceptual. El modelo de datos, la resolución automatizada de identidades, la deduplicación avanzada y la representación de grafos de acontecimientos requieren Issues específicos.

## 4. Afirmaciones contradictorias y preservación de evidencia

La taxonomía no debe convertir afirmaciones incompatibles en un único hecho confirmado. Como mínimo conceptual:

- conservar la atribución de cada afirmación a su fuente y fecha;
- distinguir la afirmación de la evidencia que la respalda;
- no borrar ni sobrescribir una afirmación anterior cuando aparezca una versión contradictoria;
- reflejar que el estado de confirmación puede cambiar con nueva evidencia, manteniendo la trazabilidad de los estados y decisiones anteriores;
- no resolver una contradicción por mayoría de publicaciones cuando todas reproduzcan una misma fuente original;
- marcar como no resuelto aquello que la evidencia disponible no permita dirimir.

La política de independencia de fuentes, resolución de contradicciones, versionado, confianza y auditoría se especificará en un Issue especializado. Esta definición fija únicamente el límite semántico necesario para que la taxonomía no confunda afirmaciones con hechos.

## 5. Criterios de conformidad

La matriz y sus reglas son conformes cuando:

1. Los 18 escenarios tienen una salida esperada explícita: incluir, excluir, hitos relacionados o indeterminado.
2. Cada escenario indica categoría principal cuando corresponde y las condiciones que impiden una clasificación indebida.
3. Se distinguen acontecimiento, publicación, afirmación, hito y fuente.
4. Las fases materiales de un proceso no se fusionan ni se duplican por repetición mediática.
5. Las contradicciones no autorizan sobrescribir evidencia ni confirmar por repetición.
6. Los datos ausentes permanecen desconocidos y conducen a indeterminación cuando afectan a la decisión.
7. No se introducen umbrales, probabilidades, puntuaciones ni inferencias causales no aprobadas.
8. No se implementa código: esta matriz es un contrato normativo para validación posterior.

## 6. Separación de alcance

Este documento no implementa:

- un grafo o motor de relaciones entre acontecimientos;
- deduplicación automática ni resolución de identidad;
- ranking, reputación o independencia automatizada de fuentes;
- resolución algorítmica de contradicciones;
- almacenamiento versionado ni auditoría técnica;
- clasificación automática o pruebas ejecutables en CI.

Cada capacidad de implementación debe contar con Issue propio y Pull Request trazable.
