# Propuesta de escalas de intensidad y horizontes temporales

**Issue:** [#14 — Definir escalas de intensidad y horizontes temporales](https://github.com/Osleyder1985/SINAYXA/issues/14)  
**Estado:** propuesta pendiente de revisión y aprobación expresa del propietario.  
**Dependencias semánticas:** glosario operativo aprobado en el Issue #13.  
**Ámbito:** evaluación del impacto potencial de acontecimientos y catalizadores. Este documento no implementa scoring, predicción, señales de trading ni atribución causal.

## 1. Objetivo y principios

Esta propuesta establece un vocabulario común para describir la intensidad potencial y el horizonte temporal de una hipótesis de impacto. Su finalidad es hacer comparables las evaluaciones sin presentar juicios cualitativos como mediciones exactas.

Principios obligatorios:

1. La intensidad describe la **relevancia y magnitud potencial del mecanismo de impacto**, no el porcentaje de variación esperado del precio.
2. La dirección, la intensidad y el horizonte son dimensiones independientes. Una intensidad alta no implica dirección positiva ni mayor probabilidad de materialización.
3. La evaluación debe identificar activo o segmento expuesto, mecanismo, condiciones, evidencia favorable, evidencia contraria y datos ausentes.
4. No se asignan probabilidades, porcentajes de retorno, puntuaciones ponderadas ni confianza numérica.
5. Si la evidencia no permite clasificar una dimensión, se declara **INDETERMINADO / EVIDENCIA INSUFICIENTE**. No se fuerza una categoría.
6. El horizonte del acontecimiento, el tiempo de transmisión del mecanismo y el horizonte de reacción del precio no son intercambiables.
7. Las categorías temporales propuestas son convenciones operativas para revisión, no leyes del mercado ni afirmaciones empíricas sobre cuánto tarda el precio en reaccionar.

## 2. Dimensiones que deben registrarse por separado

Cada hipótesis de impacto debe conservar, como mínimo conceptual, los siguientes campos:

| Dimensión | Valores propuestos | Qué representa |
| --- | --- | --- |
| Dirección potencial | POSITIVA, NEGATIVA, MIXTA, NEUTRAL, INDETERMINADA | Signo o combinación de efectos del mecanismo sobre la exposición identificada |
| Intensidad potencial | I0–I4 o INDETERMINADA | Importancia potencial del efecto, según los anclajes de la sección 3 |
| Horizonte del acontecimiento | INMEDIATO, CORTO, MEDIO, LARGO, FECHA/VENTANA CONCRETA, INDETERMINADO | Cuándo se espera que ocurra o se materialice el hito |
| Horizonte de transmisión | INMEDIATO, CORTO, MEDIO, LARGO, VARIABLE/CONDICIONAL, INDETERMINADO | Cuánto podría tardar el mecanismo en afectar la exposición |
| Horizonte de reacción del precio | INMEDIATO, CORTO, MEDIO, LARGO, MÚLTIPLE, NO EVALUADO | Ventana de reacción que se estudiará; no constituye pronóstico |

**Regla:** no copiar automáticamente el horizonte del acontecimiento al horizonte de transmisión ni al horizonte de reacción del precio. Si no hay fundamento para estimar una de estas dimensiones, se mantiene sin evaluar.

## 3. Escala ordinal propuesta de intensidad potencial

La intensidad se asigna mediante juicio estructurado contra los anclajes observables siguientes. No se suman puntos ni se promedian factores. La categoría debe justificarse en texto y citar la evidencia concreta.

| Nivel | Denominación | Anclaje operativo |
| --- | --- | --- |
| I0 | SIN IMPACTO MATERIAL IDENTIFICADO | La evidencia examinada permite concluir, dentro de la unidad, el escenario y la fecha de corte declarados, que no existe un mecanismo material hacia la exposición evaluada. La mera ausencia de evidencia de un mecanismo no basta para I0. Si faltan datos esenciales o la revisión no permite descartar el mecanismo, usar INDETERMINADA. |
| I1 | BAJA | Existe un mecanismo plausible identificable y el efecto potencial permanece local o acotado, sin comprometer una función central. Si la justificación invoca sustitución o recuperación, debe demostrarse su disponibilidad, capacidad y acceso para la población expuesta. |
| I2 | MODERADA | La evidencia respalda una exposición concreta y un mecanismo directo o indirecto, así como una alteración potencial apreciable de una condición relevante para el activo, protocolo, entidad o segmento; su alcance permanece limitado por condiciones, duración o alternativas demostradas. |
| I3 | ALTA | La exposición es amplia o central para el activo/segmento y el mecanismo podría modificar materialmente una condición económica, operativa, regulatoria, de seguridad, liquidez, oferta, demanda o acceso. La evidencia debe respaldar tanto la importancia de la exposición como el canal de transmisión. |
| I4 | CRÍTICA | El mecanismo podría comprometer la continuidad, solvencia, seguridad, integridad, acceso esencial o viabilidad de la exposición evaluada, o producir una alteración sistémica documentable. Requiere evidencia sólida de la exposición y de la severidad potencial; no se asigna por titulares alarmistas. |
| — | INDETERMINADA | No hay evidencia suficiente para distinguir niveles, existen contradicciones relevantes o faltan datos esenciales. Debe especificarse qué información falta. |

### 3.1 Matriz de comprobación de evidencia

Antes de asignar I1–I4, documentar cada dimensión por separado. Esta matriz es una lista de comprobación cualitativa: no es una escala, no suma puntos y no establece pesos.

| Dimensión | Pregunta de comprobación | Evidencia que debe conservarse | Tratamiento si no está acreditada |
| --- | --- | --- | --- |
| Exposición | ¿Qué activo, entidad, protocolo, usuarios, volumen, jurisdicción o infraestructura queda realmente expuesto? ¿Qué parte del total representa, si existe un denominador verificable? | Unidad y población expuesta, alcance conocido, fuente, fecha de referencia y límites de los datos | No describir la exposición como amplia o central; limitar el alcance o declarar indeterminación |
| Mecanismo | ¿Qué cadena concreta conecta el acontecimiento con un cambio en la exposición? | Secuencia causal hipotética, dependencias, condiciones necesarias y evidencia de cada eslabón | No elevar intensidad por la mera coexistencia temporal del acontecimiento y un movimiento de mercado |
| Magnitud potencial | ¿Qué condición económica, operativa, regulatoria, de seguridad, liquidez, oferta, demanda o acceso podría cambiar y con qué evidencia? | Medidas observadas, documentos, alcance del cambio y comparación pertinente, cuando existan | No inventar cantidades ni convertir adjetivos de una fuente en magnitud demostrada |
| Persistencia | ¿Durante cuánto tiempo podría mantenerse el efecto y qué condición lo terminaría? | Duración observada o calendario/condición documentada; incertidumbres explícitas | No asumir permanencia; registrar duración desconocida o condicionada |
| Reversibilidad | ¿Puede revertirse el efecto? ¿Quién puede hacerlo y mediante qué procedimiento o coste conocido? | Mecanismo de reversión, autoridad/actor, pasos, restricciones y evidencia | No llamar reversible o irreversible sin fundamento; dejarlo indeterminado |
| Alternativas y mitigaciones | ¿Existen sustitutos, rutas alternativas, recuperación, cobertura o mitigaciones que reduzcan la exposición? | Alternativas realmente disponibles, capacidad, límites y evidencia de acceso/uso | No presumir que una alternativa existe o es efectiva; señalar la laguna |

La ficha debe conservar también evidencia contraria, contradicciones, supuestos y datos ausentes. Una dimensión no documentada no se considera satisfecha por defecto.

### 3.2 Registro explicativo de la asignación

Toda clasificación I1–I4 debe acompañarse de un registro que permita a otra persona reconstruir el razonamiento sin adivinar los criterios aplicados. Como mínimo:

- unidad de análisis y escenario al que se aplica la clasificación;
- evidencia y referencia concreta para cada dimensión de la matriz, incluida la fecha de corte;
- nivel propuesto y anclaje observable que se considera satisfecho;
- explicación de por qué el nivel inmediatamente inferior no representa adecuadamente la evidencia;
- explicación de por qué el nivel inmediatamente superior no está justificado por la evidencia disponible;
- contradicciones, condiciones pendientes, alternativas, limitaciones y datos ausentes;
- responsable y fecha/hora de evaluación.

No se exige una explicación artificial cuando los niveles adyacentes no puedan distinguirse con la evidencia disponible. En ese caso, registrar la ambigüedad y usar INDETERMINADA, o conservar explícitamente la incertidumbre si una clasificación provisional está permitida por el flujo que finalmente se apruebe. No resolver desacuerdos entre dimensiones mediante suma, promedio, ponderación ni selección automática del valor máximo.

### 3.3 Reglas de asignación

- La unidad evaluada debe quedar explícita: activo concreto, protocolo, entidad, infraestructura, sector o mercado agregado. Una clasificación para un protocolo no se extrapola automáticamente a todo el mercado.
- Se consideran conjuntamente, sin ponderación matemática: alcance de la exposición, centralidad del mecanismo, magnitud del cambio respaldado, duración/persistencia plausible, reversibilidad y disponibilidad de alternativas.
- Ningún factor aislado determina el nivel. Una exposición amplia sin mecanismo documentado no justifica I3/I4; un incidente grave en una entidad pequeña no se extrapola al mercado completo.
- La categoría debe incluir una justificación breve que explique por qué satisface sus anclajes y por qué no corresponde el nivel inmediatamente inferior o superior.
- Si los factores apuntan a niveles diferentes, se adopta el nivel más alto solo cuando la evidencia respalda que ese factor puede materializarse en la exposición evaluada; de lo contrario se registra el conflicto y se usa INDETERMINADA.
- La intensidad puede diferir por activo, segmento, jurisdicción y escenario. No se fuerza una única intensidad global para impactos heterogéneos.
- Una evaluación I0 debe explicar por qué no se identifica impacto material. La falta de información nunca se convierte en I0.
- La intensidad potencial no mide probabilidad. La posibilidad de que se cumplan condiciones debe describirse separadamente como condición pendiente, no cuantificarse sin metodología aprobada.

### 3.4 Reglas de frontera entre niveles

Los niveles forman una escala ordinal de severidad potencial para una unidad de análisis y un escenario concretos. No representan probabilidad, frecuencia ni confianza. Para evitar que los adjetivos se interpreten libremente, se aplican las siguientes pruebas de frontera:

| Frontera | Pregunta que debe resolverse | Regla de decisión |
| --- | --- | --- |
| I0 / I1 | ¿Existe un mecanismo material plausible y respaldado hacia la exposición evaluada? | I0 solo cuando la evidencia examinada permite descartar, dentro de la unidad, el escenario y la fecha de corte declarados, la existencia de un mecanismo material. La mera falta de evidencia de un mecanismo no basta. Si faltan datos esenciales o la revisión no permite descartarlo, usar INDETERMINADA. I1 requiere un mecanismo plausible identificable y un efecto acotado. |
| I1 / I2 | ¿El mecanismo y la exposición están verificados con evidencia concreta y el cambio puede alterar apreciablemente una condición relevante? | I1 cuando el canal sigue siendo indirecto, limitado o sustituible y el efecto permanece acotado. I2 cuando la exposición concreta y el canal están verificados y existe una alteración apreciable respaldada, aunque limitada. |
| I2 / I3 | ¿La exposición es amplia o central para la unidad definida y el mecanismo puede modificar materialmente una condición relevante de esa unidad? | I2 cuando el alcance permanece acotado o existen límites demostrados. I3 exige evidencia tanto de la centralidad/amplitud de la exposición como de la materialidad del cambio. No basta con que el acontecimiento sea importante para una entidad aislada si la unidad evaluada es el mercado. |
| I3 / I4 | ¿Está comprometida una función esencial, continuidad, solvencia, seguridad, integridad o viabilidad, o existe una alteración sistémica documentable? | I3 cuando el cambio es material y amplio/central, pero no se acredita amenaza a una función esencial o viabilidad. I4 exige identificar la función esencial o el carácter sistémico, la vía concreta de compromiso y la evidencia que conecta ambos. |

La asignación se hace mediante estas reglas de suficiencia, no mediante una suma de dimensiones. Persistencia, reversibilidad y mitigaciones sirven para delimitar el escenario y su severidad; no elevan por sí solas la categoría.

Para hacer observables los términos cualitativos, se aplican además estos marcadores:

- **I0:** solo puede asignarse cuando una revisión de alcance delimitado —unidad, población/segmento, escenario, fecha de corte, fuentes y áreas examinadas, y limitaciones conocidas— respalda que no se identifica un mecanismo material que altere una condición relevante dentro de ese alcance. La revisión debe indicar qué canales plausibles se examinaron y por qué la evidencia disponible permite descartarlos para esa unidad/escenario. I0 no prueba ausencia absoluta de efectos ni se extiende a canales, poblaciones o periodos no examinados. Si la revisión es incompleta, faltan fuentes esenciales o persisten lagunas que impiden descartar un mecanismo material, usar INDETERMINADA; «no encontramos evidencia» no equivale por sí solo a I0.
- **I1:** el efecto potencial queda limitado a una fricción, variación o restricción local/acotada y no compromete una función central de la unidad. La existencia de una sustitución o recuperación ordinaria solo puede invocarse como atenuante cuando su disponibilidad, capacidad y acceso estén demostrados para la población expuesta; no es un requisito universal de I1. Si el acontecimiento ya ocurrió, se distingue el efecto observado del efecto potencial restante.
- **I2:** la evidencia respalda una alteración potencial concreta en una condición relevante para una población delimitada —como acceso, disponibilidad, coste operativo, liquidez, cumplimiento, seguridad o funcionamiento— y permite justificar por qué sería material para esa población. No demuestra que la exposición sea amplia/central para la unidad superior ni que comprometa una función esencial. Si el acontecimiento ya ocurrió, se registra por separado el cambio observado y cualquier efecto potencial aún no materializado.
- **I3:** además de una alteración potencial material concreta, la evidencia respalda que la población o función expuesta es amplia o central respecto de la unidad evaluada. Debe demostrarse esa relación con el conjunto (por ejemplo, dependencia operativa central, cobertura de una parte sustancial del segmento documentada o afectación de una función principal). Si el acontecimiento ya ocurrió, se distingue la alteración observada de la potencial.
- **I4:** se acredita amenaza o pérdida de una función esencial, continuidad, solvencia, seguridad, integridad, acceso indispensable o viabilidad; o una alteración sistémica cuyo alcance está documentado. Una pérdida económica grande por sí sola no satisface este marcador si no se conecta con esas consecuencias.

Estos marcadores no crean umbrales numéricos universales. La evidencia puede ser documental, operativa o cuantitativa, pero debe permitir observar la condición afectada, la población/unidad y la consecuencia. Si «local», «material», «amplia», «central» o «esencial» no puede explicarse en relación con la unidad declarada, no se presenta como hecho demostrado: se limita el alcance o se usa INDETERMINADA.

Para cada nivel asignado se deben contestar las fronteras adyacentes que existan: I0 solo se contrasta con I1; I4 solo con I3; I1, I2 e I3 se contrastan con sus dos niveles vecinos. Si no puede demostrarse por qué la evidencia cruza una frontera aplicable, no se asigna el nivel superior. Si tampoco puede justificarse el nivel inferior, se registra INDETERMINADA cuando la laguna afecta la clasificación.

**Unidad y denominador:** términos como «amplia», «central», «sistémica» o «esencial» siempre deben referirse a una unidad de análisis declarada. Si se afirma que una exposición representa una parte amplia de un conjunto, debe conservarse el denominador y la fuente cuando existan. Si no hay denominador fiable, no se inventa un porcentaje ni se usa esa afirmación como único fundamento.

**Escenarios condicionados:** cuando el efecto depende de una condición no confirmada, se clasifica el impacto potencial dentro de un escenario explícito (por ejemplo, «si se activa la pausa de retiros»). La condición pendiente se registra aparte. La intensidad del escenario no expresa la probabilidad de que la condición ocurra. Si no es posible definir un escenario coherente o su mecanismo, la intensidad queda INDETERMINADA.

### 3.5 Resolución de exposiciones y mecanismos contradictorios

Aplicar este orden, sin promediar ni seleccionar automáticamente el valor máximo:

1. Delimitar una unidad de análisis, una población expuesta y un escenario. No mezclar, en una sola clasificación, efectos de entidades o segmentos distintos.
2. Separar hechos confirmados, condiciones pendientes, hipótesis del mecanismo y evidencia contraria.
3. Comprobar si cada eslabón esencial del mecanismo está respaldado. Una exposición grande no compensa un mecanismo no demostrado.
4. Si el mecanismo es verificable para una parte limitada de la exposición, clasificar esa parte por separado y no extrapolarla.
5. Si dos mecanismos válidos producen severidades distintas, registrar evaluaciones separadas por mecanismo/escenario y conservar la dirección MIXTA cuando corresponda.
6. Si la contradicción afecta un eslabón esencial y no puede resolverse con la evidencia disponible, usar INDETERMINADA para esa unidad/escenario; explicar qué dato resolvería la incertidumbre.

Ejemplos de aplicación obligatoria:

- **Exposición amplia, mecanismo débil:** no asignar I3/I4 por el tamaño de la exposición. Si el canal no está acreditado, usar INDETERMINADA; si solo se acredita un canal indirecto y acotado, evaluar I1 para ese escenario.
- **Severidad potencial alta, condición muy incierta:** describir el escenario condicional y su intensidad potencial por separado de la condición pendiente. No reducir automáticamente la intensidad ni convertirla en probabilidad. Si el escenario carece de mecanismo sustentado, usar INDETERMINADA.
- **Efectos distintos por segmento:** producir clasificaciones separadas por segmento. No compensar un efecto negativo para un segmento con uno positivo para otro.
- **Mitigación disponible pero no confirmada:** no tratarla como efectiva hasta demostrar disponibilidad, capacidad y acceso para la población expuesta.
- **Evidencia contradictoria sobre alcance o severidad:** conservar ambas fuentes, su fecha y alcance; no resolver por autoridad aparente, mayoría de fuentes ni reacción del precio sin una regla de credibilidad aprobada.

### 3.6 Protocolo de evaluación con un único responsable humano

SINAYXA opera con un único participante humano. Por tanto, la evaluación metodológica primaria corresponde al propietario del proyecto; no se exige ni se presupone un segundo evaluador humano.

La reproducibilidad y el control crítico se apoyan en dos artefactos separados:

1. **Evaluación primaria humana:** el propietario registra y sella su juicio sobre el paquete congelado antes de consultar la crítica de IA.
2. **Revisión adversarial asistida por IA:** después, una IA recibe el mismo paquete, sin conocer la conclusión primaria, preferiblemente en un contexto aislado, y busca omisiones, inferencias no justificadas, contradicciones, ambigüedades y alternativas.

La IA es una herramienta auxiliar, no una persona, no un segundo evaluador humano, no un voto y no una fuente de acuerdo interevaluador. El propietario conserva la autoridad para aceptar, rechazar o dejar sin resolver cada hallazgo, con justificación y referencias a la evidencia.

Se registran por separado los resultados originales, el paquete/hash, las fechas, el prompt, el producto/modelo/versión cuando estén disponibles, las limitaciones de aislamiento y la resolución humana. Si el contexto no puede aislarse o falta un metadato, se declara expresamente; no se inventa independencia ni información.

Las diferencias humano–IA se clasifican como evidencia omitida, interpretación, alcance/unidad, ambigüedad del anclaje, error temporal, inferencia no respaldada de IA o diferencia no material. Nunca se promedian niveles ni se presenta el resultado como consenso.

**Límite de validación:** este procedimiento permite trazabilidad y crítica adversarial en un proyecto de un solo humano. No mide fiabilidad interevaluador, acuerdo entre humanos ni validez empírica. Una segunda pasada del mismo humano solo puede describirse como consistencia intraevaluador. El protocolo operativo y su ficha están definidos en [single-human-ai-assisted-evaluation-protocol.md](../governance/single-human-ai-assisted-evaluation-protocol.md).

La batería de la sección 9 comprueba que el procedimiento no dependa de participantes inexistentes y que la revisión de IA se mantenga en su rol auxiliar. Los resultados esperados son criterios de prueba, no resultados observados.

## 4. Horizontes temporales propuestos

Se propone una convención común de ventanas para facilitar el registro y la comparación. Los límites son convenciones de clasificación, no umbrales derivados de una ley estadística. La evidencia específica del mecanismo puede justificar además una fecha o ventana concreta.

| Horizonte | Ventana operativa propuesta | Uso |
| --- | --- | --- |
| INMEDIATO | Desde el momento de referencia hasta 24 horas | Efectos que pueden transmitirse dentro de la misma sesión o del siguiente día; por ejemplo, interrupción operativa, anuncio inesperado con ejecución inmediata o cambio de acceso ya efectivo. |
| CORTO | Más de 24 horas y hasta 7 × 24 horas | Efectos cuya transmisión requiere varios días, confirmación próxima, ejecución inicial o ajuste operativo de corto recorrido. |
| MEDIO | Más de 7 × 24 horas y hasta 90 × 24 horas | Efectos que dependen de implementación, decisiones intermedias, adopción inicial, vencimientos o ajustes que se desarrollan durante semanas o meses. |
| LARGO | Más de 90 × 24 horas | Efectos estructurales, regulatorios, tecnológicos, de adopción o inversión cuyo mecanismo requiere más de un trimestre para materializarse o evaluarse. |
| FECHA/VENTANA CONCRETA | Fecha o intervalo respaldado por fuente | Debe conservarse además de la categoría cuando exista un calendario o hito verificable. No convertir una estimación en fecha confirmada. |
| INDETERMINADO | Sin ventana justificable | No existe base suficiente para estimar cuándo ocurrirá el hito o se transmitirá el efecto. |

**Punto de referencia temporal:** cada horizonte debe indicar su evento de referencia (por ejemplo, primera divulgación pública, decisión oficial, entrada en vigor, activación técnica o ejecución). No se mezclan fechas de publicación, detección, ocurrencia y vigencia.

### 4.1 Referencia temporal y conservación de timestamps

Cada fecha/hora utilizada para asignar un horizonte debe conservar su procedencia y contexto temporal. El registro mínimo propuesto es:

- instante de referencia en formato ISO 8601, con offset explícito (por ejemplo, `2026-11-15T14:30:00Z` o `2026-11-15T09:30:00-05:00`);
- identificador de zona horaria IANA cuando la fuente o el calendario la especifique (por ejemplo, `America/New_York`); el offset por sí solo no identifica todas las reglas históricas de una zona;
- tipo de instante: ocurrencia del acontecimiento, publicación oficial, primera detección, ejecución/entrada en vigor, inicio de transmisión o inicio/fin de la ventana de reacción del precio;
- fuente y evidencia que respaldan el instante, precisión realmente publicada y estado temporal (confirmado, estimado, programado, intervalo o desconocido);
- instante de captura/registro y zona horaria del sistema, sin sustituir con él el instante del acontecimiento.

No convertir fechas sin hora en timestamps exactos, no asumir medianoche ni inferir una zona horaria que la fuente no indique. Si solo se conoce una fecha, conservarla como fecha; si se conoce un intervalo, conservar ambos extremos y su incertidumbre. Cuando se normalice a UTC, preservar también el valor original, el offset/zona de origen y la regla de conversión aplicada.

Los siguientes instantes deben mantenerse diferenciados cuando existan: (a) cuándo ocurrió el hecho; (b) cuándo se publicó oficialmente; (c) cuándo fue detectado por primera vez por el sistema o analista; (d) cuándo se ejecutó, activó o entró en vigor; (e) cuándo comenzó cada etapa de transmisión; y (f) cuándo empieza y termina la ventana de observación del precio. Una publicación posterior no reemplaza la hora de ocurrencia, y una detección tardía no debe presentarse como inicio del acontecimiento.

Si la evidencia temporal es contradictoria, incompleta o solo aproximada, registrar la discrepancia y no elegir una hora exacta sin justificación. El horizonte se calcula desde un instante de referencia explícitamente identificado; si no existe referencia fiable, usar INDETERMINADO.

### 4.2 Tres relojes distintos

1. **Reloj del acontecimiento:** tiempo hasta el hito previsto o tiempo transcurrido desde el hito ocurrido. Se apoya en fechas y ventanas documentadas.
2. **Reloj de transmisión:** tiempo que el mecanismo necesita para modificar la exposición. Debe justificarse por las etapas reales del proceso (condición legal, despliegue, integración, liquidación, cambio de oferta, etc.).
3. **Reloj de reacción del precio:** ventana de observación que se utilizará para estudiar el comportamiento del mercado. Es una decisión de metodología de medición y comparabilidad; no se deriva automáticamente de los dos relojes anteriores.

Para acontecimientos programados, puede existir una fase anticipatoria antes del hito y otra posterior a su materialización. Deben describirse por separado cuando los mecanismos difieran. La fecha programada no demuestra que el acontecimiento vaya a ocurrir.

### 4.3 Límites exactos y cálculo de ventanas

Las ventanas se interpretan como duración transcurrida desde un instante de referencia identificado, no como etiquetas basadas en el cambio de fecha del calendario:

| Categoría | Duración transcurrida desde el instante de referencia |
| --- | --- |
| INMEDIATO | 0 ≤ duración ≤ 24 horas |
| CORTO | 24 horas < duración ≤ 7 × 24 horas |
| MEDIO | 7 × 24 horas < duración ≤ 90 × 24 horas |
| LARGO | duración > 90 × 24 horas |

Los límites son inclusivos en el extremo superior de cada categoría. Por tanto, exactamente 24 horas corresponde a INMEDIATO; exactamente 7 × 24 horas, a CORTO; exactamente 90 × 24 horas, a MEDIO. El instante siguiente a cada límite pertenece a la categoría siguiente. Así no existen solapamientos ni huecos.

Para aplicar la regla:

- identificar el instante de referencia y el instante objetivo o intervalo objetivo;
- calcular la duración transcurrida entre ambos instantes comparables, preservando los valores originales y normalizando a UTC solo para el cálculo;
- no sustituir duración transcurrida por «días naturales» cuando el cambio horario pueda alterar la duración real;
- si solo se conoce una fecha, conservarla como fecha y no asignar una categoría exacta que dependa de una hora desconocida; puede registrarse una ventana posible si sus límites pueden justificarse;
- si el instante de referencia o el objetivo es un intervalo, calcular y conservar el intervalo de duraciones. Si sus extremos caen en categorías distintas, asignar INDETERMINADO como categoría única y conservar en la justificación el conjunto de categorías compatibles; no escoger un único horizonte sin evidencia adicional. Solo podrá usarse una representación multivalor si una implementación futura define explícitamente ese campo y sus reglas;
- una fecha concreta o ventana de calendario se conserva siempre como dato independiente de la categoría operativa.

Las cuatro categorías describen distancias temporales a un hito futuro o la duración prevista de una etapa, según el reloj declarado. Para un hito futuro, la duración se calcula desde el instante de referencia hasta el objetivo y puede clasificarse como horizonte si la evidencia temporal es suficiente. Para un hito ya ocurrido, el cálculo desde el instante del hito hasta la fecha de corte mide exclusivamente el **tiempo transcurrido desde el hito (antigüedad)**; no es un horizonte futuro, no mide la latencia de transmisión y no debe etiquetarse como INMEDIATO/CORTO/MEDIO/LARGO para describir cuánto tardará el impacto. Regístrese en un campo temporal separado, con ambos instantes y su procedencia. La duración transcurrida es no negativa y nunca se obtiene invirtiendo arbitrariamente los extremos ni usando el valor absoluto para ocultar una cronología incoherente. La fecha de corte de la evaluación y el instante de referencia del acontecimiento se conservan por separado. Para un acontecimiento pasado, cualquier horizonte de transmisión restante debe calcularse desde el hito activador pertinente hasta un objetivo futuro; si ese objetivo o la latencia no pueden justificarse, usar INDETERMINADO.

### 4.4 Acontecimientos con varias fases

Un acontecimiento con fases no recibe un único horizonte global si sus fases tienen hitos o mecanismos distintos. Se registra una fila por fase o hito material, con:

- identificador del acontecimiento y de la fase;
- tipo de reloj: acontecimiento, transmisión o reacción del precio;
- instante de referencia, instante objetivo o intervalo y estado temporal;
- horizonte operativo de esa fase;
- mecanismo, exposición y escenario asociados;
- dependencia respecto de fases anteriores y condición necesaria para avanzar;
- fuente y evidencia temporal.

Ejemplo estructural: anuncio → aprobación → entrada en vigor → implementación → adopción. Cada etapa conserva su fecha/ventana y su propio horizonte. No se presume que la aprobación implique entrada en vigor, que la entrada en vigor implique implementación, ni que la implementación implique adopción.

Si varias fases pueden desarrollarse en paralelo, se registran en paralelo. Si una fase depende de otra, se registra la dependencia sin sumar automáticamente sus duraciones. El horizonte de transmisión corresponde al tiempo del mecanismo concreto desde el hito que lo activa; el horizonte del acontecimiento describe el calendario del hito; la ventana de reacción del precio se define y evalúa por separado.

## 5. Dirección e impactos mixtos

La dirección se evalúa por exposición y mecanismo, no por el tono de la noticia:

- **POSITIVA:** el mecanismo documentado puede mejorar una condición relevante para la exposición identificada.
- **NEGATIVA:** el mecanismo documentado puede deteriorar una condición relevante.
- **MIXTA:** existen canales materiales en direcciones opuestas, o el efecto difiere entre activos/segmentos. Deben separarse los canales.
- **NEUTRAL:** el acontecimiento es relevante para el registro, pero no se identifica un cambio neto material en la dimensión evaluada.
- **INDETERMINADA:** la evidencia no permite determinar la dirección.

No se compensan automáticamente efectos positivos y negativos para producir neutralidad. Si no existe base para estimar cuál prevalece, se conserva MIXTA o INDETERMINADA, según corresponda.

## 6. Casos de aplicación

| Escenario | Dirección e intensidad ilustrativas | Horizonte que debe registrarse | Salvaguarda |
| --- | --- | --- | --- |
| Exchange suspende retiros y hay evidencia de afectación material a clientes | NEGATIVA; I2–I4 según alcance, solvencia, duración y alternativas demostradas | Acontecimiento inmediato; transmisión inmediata/corta o indeterminada según causa | No asignar I4 sin evidencia de riesgo de continuidad/solvencia; no extrapolar a exchanges no afectados |
| Se aprueba una norma con entrada en vigor meses después | POSITIVA, NEGATIVA o MIXTA; intensidad según exposición y obligaciones concretas | Hito de aprobación y fecha de entrada en vigor separados; transmisión puede ser media/larga | Aprobación no equivale a entrada en vigor ni a impacto ya materializado |
| Se anuncia una integración técnica con despliegue futuro | Dirección e intensidad indeterminadas hasta acreditar alcance y dependencias; podría ser baja/moderada si hay evidencia suficiente | Fecha prevista y horizonte de despliegue por separado | Anuncio no prueba ejecución, adopción ni demanda |
| Un protocolo sufre un exploit con fondos afectados y contratos pausados | NEGATIVA; intensidad según fondos, alcance, recuperabilidad y continuidad | Acontecimiento inmediato; transmisión inmediata y seguimiento posterior | No inferir contagio a otros protocolos sin evidencia de dependencias |
| Un banco central anuncia una decisión macroeconómica | Dirección puede ser MIXTA o INDETERMINADA; intensidad depende del canal y exposición documentados | Hito de decisión inmediato; transmisión puede abarcar varios horizontes | No deducir dirección cripto solo del signo de la decisión ni de la reacción inicial |
| Se programa un desbloqueo de tokens | Dirección potencial puede ser NEGATIVA, MIXTA o INDETERMINADA; intensidad según cantidad relativa, destinatarios, restricciones y conducta acreditada | Fecha prevista del desbloqueo; transmisión posterior solo si hay mecanismo documentado | Desbloqueo no equivale a transferencia ni venta |

Los intervalos de intensidad en los ejemplos son deliberadamente condicionales: no asignan un nivel final sin los datos de exposición y evidencia requeridos.

## 7. Cambios, reevaluación y trazabilidad

- Cada evaluación debe conservar fecha de evaluación, versión de evidencia utilizada, exposición evaluada, mecanismo, dirección, intensidad, horizontes y justificación.
- Una nueva evidencia puede cambiar la evaluación, pero no sobrescribe la evaluación anterior.
- Si cambia el alcance, la condición, el calendario o la exposición, se registra qué hecho motivó la reevaluación.
- Una revisión de horizonte no implica por sí sola cambio de intensidad; una revisión de intensidad no implica cambio de dirección.
- Los niveles pueden cambiar cuando cambien las condiciones del mecanismo o la evidencia; no se aplica una caducidad automática en este documento (ciclo de vida reservado al Issue #25).
- La reacción observada del precio se registra separadamente y no se usa retrospectivamente para justificar una intensidad potencial que no estaba respaldada por la evidencia disponible en el momento de la evaluación.

## 8. Límites y dependencias

Esta propuesta no decide:

- la rúbrica de credibilidad e independencia de fuentes (#16);
- el estándar probatorio detallado para indicios y filtraciones (#15);
- la medición de reacción real, ventanas de estudio y atribución (#20);
- la comparabilidad histórica y selección de casos (#19);
- expectativas previas e impacto descontado (#24);
- estados, transiciones y caducidad (#25);
- umbrales y severidad de alertas (#17).

Tampoco define puntuación compuesta, pesos, probabilidad, retorno esperado, señales de compra/venta ni causalidad. Esas capacidades requieren decisiones separadas y evidencia de validación.

## 9. Criterios de aceptación propuestos para el Issue #14

- [ ] La matriz cualitativa de exposición, mecanismo, magnitud potencial, persistencia, reversibilidad y alternativas se documenta sin puntuaciones ni ponderaciones.
- [ ] Toda asignación I1–I4 explica el anclaje satisfecho y por qué no corresponden los niveles adyacentes; la ambigüedad no se resuelve mediante cálculos arbitrarios.
- [ ] Los instantes temporales conservan ISO 8601 con offset, zona horaria identificada cuando esté disponible, tipo de instante, fuente y precisión; no se inventan horas ni zonas.
- [ ] El propietario aprueba o modifica los niveles I0–I4 y sus anclajes observables.
- [ ] El propietario aprueba o modifica la regla de indeterminación y confirma que ausencia de evidencia no equivale a impacto nulo.
- [ ] I0 solo se asigna tras una revisión de alcance delimitado que documente unidad, población/segmento, escenario, fecha de corte, fuentes/áreas examinadas y limitaciones; la falta de búsqueda suficiente o las lagunas esenciales obligan a usar INDETERMINADA.
- [ ] El propietario aprueba o modifica las ventanas INMEDIATO (duración ≤24 horas), CORTO (24 horas < duración ≤7 × 24 horas), MEDIO (7 × 24 horas < duración ≤90 × 24 horas) y LARGO (duración >90 × 24 horas), entendidas como convenciones operativas y calculadas como tiempo transcurrido, no como días calendario.
- [ ] Se acepta la separación entre horizonte del acontecimiento, horizonte de transmisión y horizonte de reacción del precio.
- [ ] Para hitos pasados, el tiempo transcurrido/antigüedad se registra por separado y nunca se confunde con el horizonte futuro ni con la latencia de transmisión.
- [ ] Se acepta la separación entre dirección, intensidad y probabilidad, sin puntuaciones ni probabilidades inventadas.
- [ ] Los casos ilustrativos se consideran suficientes y no contradicen el glosario del Issue #13.
- [ ] Se acepta la preservación de evaluaciones anteriores y la prohibición de usar movimientos posteriores del precio como justificación retroactiva.

### 9.1 Batería mínima de pruebas metodológicas

Los siguientes casos son escenarios sintéticos de prueba. Los resultados esperados verifican la aplicación de las reglas; no representan datos de mercado ni precedentes empíricos.

| ID | Evidencia y escenario congelados | Resultado esperado | Error que debe detectar |
| --- | --- | --- | --- |
| T01 | Acontecimiento registrado; tras revisar la exposición y los canales relevantes, la evidencia permite concluir, para la unidad y fecha de corte definidas, que no existe mecanismo material hacia la unidad evaluada. | I0; dirección NEUTRAL únicamente cuando la evidencia también respalde ausencia de cambio direccional material; si la dirección no puede establecerse, INDETERMINADA. | Confundir evidencia suficiente de ausencia de mecanismo material con falta de información. |
| T02 | Exposición pequeña, canal indirecto plausible y efecto potencial acotado; el sustituto operativo está disponible para la población expuesta y su capacidad y acceso están demostrados. | I1 para esa unidad/escenario. | Elevar intensidad solo por el tono de la noticia o presumir que una alternativa documentada es realmente accesible. |
| T03 | Exposición concreta y canal directo respaldados por evidencia; el escenario permite justificar una alteración potencial apreciable pero limitada a una entidad/segmento, sin demostrar amplitud o centralidad. | I2 para esa unidad/escenario. Si el acontecimiento ya ocurrió, registrar por separado el cambio observado. | Interpretar «verificable» como necesariamente «ya materializado» o saltar a I3 sin demostrar amplitud o centralidad. |
| T04 | Exposición amplia o central demostrada y canal respaldado por evidencia; el escenario sustenta una alteración potencial material en una condición relevante, sin acreditar amenaza a función esencial o viabilidad. | I3. Si el acontecimiento ya ocurrió, registrar por separado la alteración observada. | Confundir evidencia del efecto potencial con efecto ya materializado, o materialidad amplia con criticidad I4. |
| T05 | Evidencia sólida de amenaza a continuidad, solvencia, seguridad, integridad, acceso esencial o viabilidad de la unidad evaluada, mediante un mecanismo concreto. | I4. | Asignar I4 por titulares, alarma o tamaño nominal sin mecanismo. |
| T06 | Exposición muy amplia, pero el único canal propuesto es especulativo y carece de eslabones verificables. | INDETERMINADA; no I3/I4. | Permitir que la exposición compense un mecanismo débil. |
| T07 | Escenario en el que se comprometería una función esencial de la unidad evaluada si se cumple una condición técnica aún no confirmada; la vía de compromiso y sus consecuencias están documentadas. | I4 para ese escenario condicional; registrar por separado la condición pendiente y no asignarle una probabilidad sin metodología aprobada. | Confundir severidad potencial del escenario con probabilidad de materialización. |
| T08 | Evidencia de impacto negativo material en un segmento y positivo material en otro, con exposiciones diferenciadas. | Evaluaciones separadas por segmento; dirección MIXTA en el agregado solo si la unidad agregada está definida explícitamente, incluye ambos segmentos y ambos efectos materiales están respaldados. Si no existe esa unidad agregada, no crear una clasificación agregada. | Cancelar efectos por promedio o forzar una intensidad global. |
| T09 | Fuente A afirma afectación amplia; fuente B aporta evidencia contraria relevante y no hay criterio aprobado que resuelva la discrepancia. | Registrar contradicción e INDETERMINADA para el alcance controvertido. | Elegir una fuente sin justificar credibilidad o ignorar evidencia contraria. |
| T10 | Una mitigación se anuncia, pero no se demuestra que esté disponible ni que cubra a la población expuesta. | No reducir intensidad por esa mitigación; registrar disponibilidad no acreditada. | Tratar una promesa como capacidad operativa. |
| T11 | Duración objetivo exactamente 24 h, 7 × 24 h o 90 × 24 h desde una referencia precisa. | INMEDIATO, CORTO y MEDIO, respectivamente. | Error de inclusión/exclusión en límites. |
| T12 | Duración objetivo un instante después de 24 h, 7 × 24 h o 90 × 24 h. | CORTO, MEDIO y LARGO, respectivamente. | Crear huecos o solapamientos en fronteras. |
| T13 | Fuente publica una fecha sin hora ni zona y el resultado depende de la hora exacta. | Conservar fecha; no inventar timestamp ni categoría exacta. | Asumir medianoche o zona local. |
| T14 | Un acontecimiento tiene anuncio, aprobación, entrada en vigor e implementación en fechas distintas. | Registrar cada fase/hito y reloj por separado. | Asignar un único horizonte global o confundir publicación con ejecución. |
| T15 | Un intervalo temporal posible cruza el límite entre dos categorías. | Conservar el intervalo y el conjunto de categorías compatibles; usar INDETERMINADO como categoría única cuando el intervalo cruce categorías. No forzar una sola categoría compatible. | Ocultar incertidumbre temporal. |
| T16 | Un único evaluador humano registra y sella su evaluación primaria; una IA, sin conocer esa conclusión, realiza una crítica estructurada del mismo paquete congelado. | Registrar por separado ambos artefactos, clasificar diferencias y documentar la decisión del humano. La IA no cuenta como segundo evaluador ni produce acuerdo interevaluador. | Exigir una segunda persona inexistente, contar la IA como humano, promediar resultados o afirmar consenso. |
| T17 | La información disponible es incompleta y no permite confirmar ni descartar un mecanismo material hacia la unidad evaluada. | INDETERMINADA, no I0. | Convertir ausencia de datos en evidencia de ausencia de impacto. |
| T18 | En la zona Europe/Madrid, comparar `2026-03-28T12:00:00+01:00` con `2026-03-29T13:00:00+02:00`. Los instantes están separados por exactamente 24 horas reales, aunque la hora local de reloj difiere en 25 horas por el cambio estacional. | INMEDIATO, calculado con instantes comparables/UTC; conservar valores originales, offsets y zona IANA disponible. | Sustituir duración transcurrida por diferencia de horas locales durante un cambio horario. |
| T19 | Con referencia `2026-01-01T00:00:00Z`, una fuente sitúa el hito en `2026-01-01T23:50:00Z` y otra en `2026-01-02T00:10:00Z`; ambas se refieren al mismo hito y no existe criterio aprobado para preferir una. El intervalo posible cruza la frontera de 24 horas. | Registrar ambas fuentes y el intervalo [23 h 50 min, 24 h 10 min]; categoría única INDETERMINADO y categorías compatibles INMEDIATO/CORTO en la justificación. | Elegir una hora sin criterio o esconder la incertidumbre de origen. |

**Condición de aprobación de la batería:** todos los casos deben producir el resultado esperado o una justificación explícita de por qué el caso no permite una clasificación única. Cualquier resultado no previsto obliga a revisar el anclaje o la regla correspondiente antes de considerar cerrada la decisión. La batería debe conservar versión, paquete de evidencia, fecha de corte, evaluación primaria humana sellada, crítica de IA separada y resolución humana. T16 se ejecuta conforme al protocolo de evaluador único; no produce validación interevaluador ni consenso humano.

### 9.2 Criterios adicionales de aceptación

- [ ] Las fronteras I0/I1, I1/I2, I2/I3 e I3/I4 se aplican con las pruebas de suficiencia de la sección 3.4.
- [ ] Una exposición amplia no compensa un mecanismo débil; severidad potencial y condición/probabilidad permanecen separadas.
- [ ] Los efectos heterogéneos se clasifican por unidad, segmento y escenario, sin promedios ni máximos automáticos.
- [ ] Las contradicciones y mitigaciones no verificadas reciben el tratamiento definido en la sección 3.5.
- [ ] Existe un protocolo documentado de evaluación primaria por un único humano y crítica auxiliar de IA; no se afirma acuerdo interevaluador ni consenso humano.
- [ ] Las fronteras temporales son exhaustivas y no solapadas, y sus extremos se prueban mediante T11 y T12; los cambios de horario y la evidencia temporal contradictoria se comprueban mediante T18 y T19.
- [ ] Las fechas sin hora, intervalos y timestamps contradictorios no se convierten en precisión artificial.
- [ ] Los acontecimientos con varias fases conservan un horizonte por hito/fase y distinguen los tres relojes.
- [ ] La batería T01–T19 se ejecuta y sus resultados quedan registrados antes de la aprobación metodológica.

**Gobernanza:** esta versión es una propuesta. Ningún nivel, ventana o criterio se considera aprobado hasta que el propietario lo acepte expresamente. La aprobación documental no autoriza implementación automática; cualquier implementación requerirá un Issue funcional y un PR con pruebas.
