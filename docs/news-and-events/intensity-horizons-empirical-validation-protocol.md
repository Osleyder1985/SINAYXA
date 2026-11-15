# Protocolo de validación empírica de intensidad y horizontes

**Relacionado:** Issue #14; propuesta `intensity-and-time-horizons-proposal.md`  
**Estado:** protocolo preparado; ejecución empírica pendiente.  
**Naturaleza:** protocolo de investigación y control de calidad; no es evidencia de que la escala ya haya sido validada.

## 1. Propósito

La batería sintética T01–T19 comprueba que los criterios documentados pueden aplicarse a ejemplos controlados y que el validador detecta defectos estructurales. No demuestra que I0–I4 discrimine adecuadamente acontecimientos reales, que las ventanas temporales sean útiles en mercados reales ni que una clasificación anticipe movimientos de precio.

Este protocolo separa tres preguntas que deben evaluarse por separado:

1. **Validez de constructo:** ¿los anclajes I0–I4 representan de forma coherente la magnitud del mecanismo y la exposición definida?
2. **Validez temporal-operativa:** ¿los tres relojes y las ventanas propuestas describen correctamente los hitos, la transmisión y las ventanas de observación?
3. **Relación con el mercado:** ¿qué reacción de precio se observó después del corte, sin convertirla en prueba de la noticia ni de causalidad?

## 2. Diseño contra sesgo retrospectivo

Antes de examinar resultados posteriores al acontecimiento:

- congelar la versión de la metodología, el universo de activos, el periodo, las reglas de inclusión/exclusión y el plan de análisis;
- registrar la fecha/hora de corte y el paquete de evidencia disponible en ese instante;
- ocultar al evaluador primario los retornos y noticias posteriores al corte;
- registrar y sellar la evaluación primaria humana antes de mostrar la crítica auxiliar de IA;
- preservar separadamente evaluación primaria, crítica de IA, discrepancias y resolución final;
- no modificar reglas después de conocer resultados sin abrir una nueva versión y un nuevo conjunto de confirmación;
- separar un conjunto de desarrollo de un conjunto de confirmación cronológico; no mezclar eventos futuros en decisiones pasadas.

La IA es una herramienta de crítica adversarial, no un segundo evaluador humano, no un voto y no una medida de acuerdo interevaluador.

## 3. Muestreo de acontecimientos

El muestreo debe incluir casos positivos, negativos, mixtos, neutrales, condicionados e indeterminados; eventos de distinta intensidad aparente; acontecimientos con fases múltiples; eventos con mitigación; información contradictoria; y casos sin mecanismo material demostrado.

La selección debe documentar:

- universo y criterio de elegibilidad;
- periodo y cobertura de activos;
- fuentes disponibles en el momento histórico;
- eventos incluidos y excluidos, con motivo;
- duplicados y eventos relacionados;
- sesgo de supervivencia, disponibilidad de fuentes y cobertura desigual;
- tamaño de muestra y justificación estadística, si se pretende estimar una propiedad poblacional.

No se fija un tamaño mínimo arbitrario. El tamaño debe justificarse antes del análisis según el objetivo, la heterogeneidad, la prevalencia esperada de clases y la precisión que se pretenda estimar. Si no existe base para calcular potencia o precisión, el estudio se declara exploratorio y no se presenta como confirmatorio.

## 4. Evaluación del constructo I0–I4

Para cada caso, registrar unidad, segmento/población, escenario, mecanismo, condición, evidencia favorable, evidencia contraria, ausencias, fecha de corte y nivel propuesto.

Comprobar expresamente:

- I0 solo cuando una revisión delimitada y auditable no identifique mecanismo material dentro de ese alcance; no significa ausencia universal de impacto.
- I1–I4 deben justificarse mediante los anclajes observables y las fronteras de la propuesta, no por el tamaño posterior del movimiento de precio.
- una exposición amplia no compensa un mecanismo débil;
- la severidad condicional no se convierte en probabilidad de que la condición ocurra;
- impactos heterogéneos se evalúan por segmento; no se promedian ni se cancelan;
- contradicciones no resueltas y evidencia esencial ausente conducen a INDETERMINADA cuando impidan sostener una categoría;
- la intensidad no se interpreta como porcentaje, retorno esperado ni ranking universal entre activos.

Registrar todos los desacuerdos de clasificación y su causa. No ocultar discrepancias mediante promedios o una categoría forzada.

## 5. Validación de los tres relojes

Para cada acontecimiento, registrar por separado:

1. **Reloj del acontecimiento:** anuncio, decisión, entrada en vigor, ejecución u otro hito, cada uno con su timestamp y precisión.
2. **Reloj de transmisión:** mecanismo, pasos intermedios, latencia observada y evidencia que permita fecharlos. No inferir latencia a partir de la reacción del precio.
3. **Reloj de reacción del precio:** ventana de observación predefinida, activo/mercado de referencia, fuente de datos, frecuencia, zona horaria, liquidez y controles de calidad.

Las ventanas INMEDIATO (hasta 24 h), CORTO (>24 h hasta 7 días), MEDIO (>7 hasta 90 días) y LARGO (>90 días) son convenciones operativas provisionales. Su utilidad se evalúa por cobertura, ambigüedad, estabilidad y capacidad descriptiva; no se presuponen como fronteras naturales del mercado.

Las fechas sin hora, intervalos que crucen fronteras, timestamps contradictorios y cambios DST deben permanecer explícitos. No completar precisión ausente por conjetura.

## 6. Análisis de reacción del mercado: separado de la verdad y la causalidad

La reacción del precio se analiza solo después de congelar la evaluación probatoria y la evaluación primaria de impacto. El protocolo debe definir de antemano:

- benchmark y universo de comparación;
- ventanas pre/post y frecuencia;
- retornos simples o logarítmicos y tratamiento de datos faltantes;
- costes, liquidez, spreads y horarios del mercado;
- eventos concurrentes y factores de confusión;
- análisis de sensibilidad y ventanas placebo;
- reglas de exclusión y tratamiento de outliers.

Un movimiento posterior no demuestra que la noticia sea verdadera, que el evento lo causara ni que la intensidad asignada fuera correcta. Correlación temporal y causalidad deben permanecer separadas. No reportar causalidad sin un diseño causal defendible y supuestos explícitos.

## 7. Criterios de evaluación y decisión

El informe final debe presentar, como mínimo:

- cobertura por clase I0–I4 e INDETERMINADA;
- proporción de casos sin evidencia suficiente y razones;
- frecuencia y naturaleza de contradicciones;
- estabilidad de clasificación ante evidencia retirada, añadida o corregida;
- sensibilidad a cambios de unidad, segmento, escenario y fecha de corte;
- cobertura y ambigüedad de cada ventana temporal;
- discrepancias entre evaluación humana primaria y crítica IA, sin denominarlas acuerdo interevaluador;
- resultados de mercado por separado, con limitaciones y sin atribución causal automática;
- resultados por periodo y activo, evitando agregados que oculten fallos;
- desviaciones del protocolo y análisis no preregistrados claramente identificados.

No se fija un umbral de aprobación numérico antes de conocer el diseño muestral y el objetivo de validación. Los criterios y umbrales deben quedar preregistrados y justificados; no se pueden escoger después de observar resultados para obtener un PASS.

Un fallo sistemático en fronteras, confusión de relojes, sobreasignación de I0, uso del precio como evidencia, o clasificación forzada ante incertidumbre exige revisar la metodología y repetir la confirmación con una nueva versión.

## 8. Artefactos obligatorios

Cada ejecución debe conservar:

- protocolo y versión congelados;
- inventario de eventos y reglas de selección;
- paquete de evidencia por caso con hashes y procedencia legítima;
- fecha/hora de corte y timestamps originales;
- evaluación primaria humana sellada;
- crítica IA separada, prompt/modelo/fecha cuando estén disponibles y limitaciones;
- resolución del propietario;
- datos de mercado y benchmark separados;
- scripts, parámetros, logs, resultados y hashes;
- desviaciones, exclusiones, limitaciones y decisión final.

## 9. Estado de validación

Hasta que exista una ejecución real con datos históricos, corte temporal, muestra justificada, artefactos y resultados reproducibles:

- la validación empírica permanece **NOT_EXECUTED**;
- las ventanas permanecen **PROVISIONAL_OPERATIONAL_CONVENTIONS**;
- no se declara validez predictiva, causalidad, calibración ni rendimiento de inversión;
- T01–T19 sintéticos se consideran pruebas de consistencia del diseño, no evidencia de validez externa.

La aprobación de este protocolo autoriza únicamente el diseño de la evaluación. No convierte por sí sola la escala en empíricamente validada.
