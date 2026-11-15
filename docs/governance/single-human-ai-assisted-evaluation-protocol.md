# Protocolo de evaluación con un único responsable humano y revisión asistida por IA

## 1. Propósito

Establecer un procedimiento reproducible para evaluar los casos metodológicos de SINAYXA cuando existe un único participante humano. La IA puede cuestionar y complementar el análisis, pero nunca se presenta como segundo evaluador humano ni como fuente de acuerdo interevaluador.

Este protocolo se aplica a evaluaciones de intensidad, dirección, horizonte, escenarios, evidencia y justificación. No autoriza scoring, probabilidades, predicción ni atribución causal que no estén aprobados por separado.

## 2. Roles y autoridad

- **Evaluador humano responsable:** el propietario del proyecto. Es la única persona que emite y asume la evaluación metodológica final.
- **Asistente de IA:** herramienta auxiliar que realiza una revisión crítica estructurada del paquete congelado. No tiene autoridad decisoria, no es una persona y no cuenta como evaluador humano.
- **Decisión final:** corresponde exclusivamente al evaluador humano, quien debe justificar cualquier aceptación o rechazo de los hallazgos de IA.

No se requiere incorporar una segunda persona para ejecutar este protocolo. Tampoco se afirmará que se midió acuerdo interevaluador.

## 3. Secuencia obligatoria

### Fase A — Congelación de entradas

Antes de evaluar, registrar:

1. Identificador y versión de la propuesta metodológica.
2. Identificador, versión y SHA-256 del paquete de evidencia.
3. Unidad de análisis, escenario y fecha/hora de corte.
4. Fuentes, elementos de evidencia, timestamps y limitaciones.
5. Versión de este protocolo y fecha/hora de inicio.

Si cambia cualquier entrada material, crear una nueva ejecución o versión; no sobrescribir el registro anterior.

### Fase B — Evaluación primaria humana

El evaluador humano completa primero, sin consultar una salida de IA para ese caso:

- intensidad y dirección;
- horizonte del acontecimiento, transmisión y reacción del precio, cuando proceda;
- condiciones pendientes y escenarios;
- evidencia a favor y en contra;
- unidad/segmento afectado;
- anclajes aplicados y justificación;
- incertidumbres, contradicciones y datos ausentes.

La evaluación primaria se guarda con fecha/hora y hash o mecanismo equivalente de integridad antes de iniciar la revisión de IA. No se modifica retroactivamente. Una corrección posterior genera una nueva versión enlazada.

### Fase C — Revisión adversarial asistida por IA

Después de sellar la evaluación primaria:

1. Entregar a la IA el paquete congelado y una instrucción predefinida, sin incluir la conclusión humana.
2. Preferir una conversación/contexto aislado que no tenga acceso a la evaluación primaria ni a la discusión previa del caso.
3. Pedir que identifique evidencia omitida, inferencias no justificadas, contradicciones, ambigüedad de anclajes, alternativas plausibles y límites de alcance.
4. Exigir referencias a los IDs de evidencia del paquete. La IA debe marcar explícitamente cuando una conclusión no esté respaldada.
5. No pedir a la IA que adivine datos ausentes ni que invente probabilidades, métricas o causalidad.

Si no se consigue aislar el contexto, registrarlo como limitación y no describir la revisión como ciega o independiente.

### Fase D — Comparación y resolución humana

Comparar la crítica de IA con la evaluación primaria ya sellada. Clasificar cada diferencia, al menos, como:

- evidencia relevante omitida;
- interpretación distinta de la misma evidencia;
- alcance/unidad/segmento mal delimitado;
- ambigüedad o insuficiencia del anclaje;
- error temporal o de cálculo;
- inferencia no respaldada en la salida de IA;
- diferencia no material.

El evaluador humano decide qué hallazgos acepta, rechaza o deja sin resolver. Cada decisión debe incluir evidencia y razón. No promediar intensidades, no contar la IA como voto y no llamar consenso al resultado.

Si la discrepancia revela un defecto de regla, modificar la propuesta mediante una nueva versión y repetir los casos afectados con el nuevo paquete/protocolo. Conservar la evaluación anterior.

## 4. Metadatos mínimos de la IA

Registrar, cuando estén disponibles:

- producto y modelo/versión exactos;
- fecha/hora de ejecución;
- prompt completo o identificador/versionado del prompt;
- hash del paquete entregado;
- confirmación de que la evaluación primaria no fue incluida;
- confirmación de aislamiento del contexto y sus limitaciones;
- salida íntegra o referencia inmutable;
- decisión humana sobre cada hallazgo.

Si un dato del modelo no está expuesto, usar `NOT_AVAILABLE`. No inferir ni completar el dato.

## 5. Interpretación de resultados

Este procedimiento permite documentar una evaluación humana con una revisión crítica auxiliar y medir la trazabilidad de los desacuerdos humano–IA. No permite afirmar:

- acuerdo entre dos evaluadores humanos;
- fiabilidad interevaluador;
- consenso humano;
- independencia estadística de la IA;
- validez empírica o capacidad predictiva de la metodología.

Una repetición del análisis por el mismo humano puede utilizarse como comprobación de consistencia intraevaluador, siempre que se registre como tal y no como independencia.

## 6. Ficha de registro por caso

| Campo | Registro |
| --- | --- |
| ID de ejecución/caso | PENDIENTE |
| Propuesta y versión/commit | PENDIENTE |
| Protocolo y versión | PENDIENTE |
| Paquete y versión | PENDIENTE |
| SHA-256 del paquete | PENDIENTE |
| Unidad/escenario/corte | PENDIENTE |
| Evaluador humano responsable | Propietario del proyecto |
| Fecha/hora de evaluación primaria | PENDIENTE |
| Hash/identificador del registro primario sellado | PENDIENTE |
| Resultado primario | PENDIENTE |
| Producto/modelo IA | PENDIENTE o NOT_AVAILABLE |
| Fecha/hora de revisión IA | PENDIENTE |
| Prompt/versión | PENDIENTE |
| ¿La IA recibió el resultado humano? | NO en la primera revisión |
| ¿Contexto aislado? | PENDIENTE |
| Limitaciones/contaminación | PENDIENTE |
| Hallazgos de IA con IDs de evidencia | PENDIENTE |
| Diferencias clasificadas | PENDIENTE |
| Decisión humana por hallazgo | PENDIENTE |
| Cambios metodológicos requeridos | PENDIENTE |
| Estado y justificación | NOT_EXECUTED |

## 7. Criterio de integridad

La evaluación humana primaria y la crítica de IA son artefactos distintos. No sobrescribir, fusionar ni reescribir retrospectivamente la evaluación primaria. La IA no reemplaza al responsable humano. La ausencia de una segunda persona no bloquea el proceso de SINAYXA; simplemente significa que no se realiza ni se declara validación interevaluador humana.
