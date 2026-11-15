# Registro de ejecución de T01–T19

## 1. Propósito y estado

Este documento registra la ejecución verificable de la batería metodológica definida en [la propuesta de intensidad y horizontes temporales](intensity-and-time-horizons-proposal.md).

**Estado inicial:** todos los casos están **NOT_EXECUTED**. La revisión lógica de escritorio descrita en la PR no equivale a ejecutar la batería ni a validar acuerdo entre evaluadores. No se deben convertir resultados esperados en resultados observados.

Este registro no aprueba la metodología ni autoriza su implementación. Es un instrumento de trazabilidad para la evaluación y posterior decisión del propietario.

## 2. Identificación de la ejecución

Completar antes de ejecutar cada ciclo:

| Campo | Valor |
| --- | --- |
| ID de ejecución | PENDIENTE |
| Versión/commit de la propuesta | PENDIENTE |
| SHA del archivo de propuesta | PENDIENTE |
| Versión de este protocolo | PENDIENTE |
| Fecha y hora de congelación del paquete (ISO 8601) | PENDIENTE |
| Fecha y hora de corte de evaluación (ISO 8601) | PENDIENTE |
| Unidad de análisis | PENDIENTE |
| Escenario evaluado | PENDIENTE |
| Inventario de evidencias y fuentes | PENDIENTE |
| Hash del paquete congelado | PENDIENTE |
| Responsable de custodia del paquete | PENDIENTE |
| Método/herramienta de cálculo temporal, si aplica | PENDIENTE |
| Observaciones sobre limitaciones | PENDIENTE |

No iniciar una ejecución reproducible si la unidad, el escenario, el corte o el contenido del paquete no están definidos. Conservar timestamps originales, offsets, zona IANA cuando esté disponible, fuente y precisión. No completar datos ausentes mediante suposiciones.

## 3. Estados permitidos

- **NOT_EXECUTED:** no existe ejecución registrada.
- **IN_PROGRESS:** ejecución iniciada, todavía sin resultado revisado.
- **PASS:** resultado obtenido coincide con el esperado y existe evidencia suficiente del procedimiento.
- **FAIL:** resultado obtenido contradice el esperado o revela una regla ambigua/inconsistente.
- **BLOCKED:** no puede ejecutarse por una dependencia o condición no satisfecha.
- **NOT_APPLICABLE:** solo con justificación explícita; no utilizar para ocultar un caso difícil.

Un caso solo puede marcarse PASS o FAIL cuando se registren entradas, procedimiento, resultado obtenido, evidencia y responsable. Una comprobación de escritorio o una simulación no cuenta como ejecución independiente.

## 4. Matriz de seguimiento

Los resultados esperados se resumen aquí para facilitar el control. La descripción íntegra del escenario y el error que debe detectar cada caso permanecen en la propuesta vinculada.

| ID | Resultado esperado resumido | Estado inicial | Resultado obtenido | Evidencia/registro |
| --- | --- | --- | --- | --- |
| T01 | I0; dirección NEUTRAL solo si está respaldada independientemente | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T02 | I1; sustituto solo atenúa si disponibilidad, capacidad y acceso están demostrados | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T03 | I2; separar efecto observado de efecto potencial restante | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T04 | I3; demostrar exposición amplia/central y separar efecto observado/potencial | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T05 | I4; amenaza concreta a función esencial o viabilidad demostrada | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T06 | INDETERMINADA; exposición amplia no compensa mecanismo especulativo | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T07 | I4 para escenario condicional sustentado; condición pendiente separada, sin probabilidad inventada | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T08 | Separación por segmentos; MIXTA agregada solo con unidad agregada explícita y respaldada | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T09 | Contradicción preservada; INDETERMINADA para alcance controvertido | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T10 | Mitigación no verificada no reduce intensidad | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T11 | 24 h → INMEDIATO; 7 × 24 h → CORTO; 90 × 24 h → MEDIO | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T12 | Instante posterior a cada frontera → categoría siguiente | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T13 | Fecha sin hora/zona: no inventar timestamp ni categoría exacta | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T14 | Anuncio, aprobación, entrada en vigor e implementación con hitos/relojes separados | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T15 | Intervalo que cruza categorías: conservar intervalo; categoría única INDETERMINADO | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T16 | Dos evaluadores humanos independientes; discrepancia registrada y resuelta sin promediar | BLOCKED | PENDIENTE | PENDIENTE |
| T17 | INDETERMINADA, no I0, cuando no se puede confirmar ni descartar mecanismo material | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T18 | Exactamente 24 h reales durante cambio horario → INMEDIATO | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T19 | Conservar fuentes e intervalo 23 h 50 min–24 h 10 min; categoría única INDETERMINADO | NOT_EXECUTED | PENDIENTE | PENDIENTE |

## 5. Ficha obligatoria por caso

Duplicar esta ficha para cada ejecución de T01–T19. No sustituir un registro anterior: las reevaluaciones deben crear una nueva ejecución vinculada a la anterior.

### Caso TXX

| Campo | Registro |
| --- | --- |
| Estado | NOT_EXECUTED |
| Versión/commit de la propuesta | PENDIENTE |
| Hash del paquete de evidencia | PENDIENTE |
| Fecha/hora de corte | PENDIENTE |
| Unidad y escenario | PENDIENTE |
| Evaluador | PENDIENTE |
| ¿Evaluación independiente? | PENDIENTE |
| Entradas efectivamente utilizadas | PENDIENTE |
| Procedimiento aplicado | PENDIENTE |
| Resultado esperado | PENDIENTE |
| Resultado obtenido | PENDIENTE |
| Evidencia que respalda el resultado | PENDIENTE |
| Discrepancias/contradicciones | PENDIENTE |
| Regla o anclaje cuestionado | PENDIENTE |
| Justificación del estado | PENDIENTE |
| Fecha/hora de registro | PENDIENTE |

## 6. Requisitos adicionales para T16

T16 permanece **BLOCKED** hasta que existan dos evaluadores humanos realmente independientes. Ambos deben recibir el mismo paquete congelado, la misma unidad, el mismo escenario y la misma fecha de corte. Deben emitir sus evaluaciones por separado antes de conocer la respuesta del otro.

Registrar para cada evaluador:

- Identificador no ambiguo del evaluador y declaración de independencia.
- Confirmación de que recibió exactamente el mismo paquete (hash).
- Fecha/hora de inicio y cierre.
- Resultado original sin conciliación previa.
- Diferencias por dimensión, evidencia o interpretación.
- Resolución posterior, responsable y cambio de regla/anclaje, si procede.
- Repetición de la evaluación cuando se modifique la regla.

No usar al mismo evaluador en dos roles, autoevaluación, una respuesta simulada ni una evaluación generada por IA para completar el segundo puesto. No calcular acuerdo interevaluador ni afirmar consenso si no se ha realizado la comparación válida.

## 7. Cierre de una ejecución

Una ejecución de la batería solo puede considerarse completa cuando:

1. T01–T19 tienen estado terminal justificado (PASS, FAIL, BLOCKED o NOT_APPLICABLE); los BLOCKED deben explicar la dependencia pendiente.
2. Cada PASS/FAIL contiene entradas, procedimiento, resultado obtenido y evidencia rastreable.
3. Las discrepancias han sido documentadas y no ocultadas mediante promedios o cambios retrospectivos.
4. T16 se ha ejecutado con dos evaluadores humanos independientes o permanece explícitamente BLOCKED; si sigue bloqueado, no afirmar validación interevaluador completa.
5. Se conserva el paquete congelado y los hashes que permiten reproducir la evaluación.
6. Cualquier modificación de la propuesta crea una nueva versión y exige identificar qué casos deben repetirse.

**Regla de integridad:** nunca cambiar NOT_EXECUTED/BLOCKED a PASS por inferencia, revisión de escritorio o porque el resultado esperado parezca obvio.
