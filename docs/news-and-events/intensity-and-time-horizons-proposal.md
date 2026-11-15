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
| I0 | SIN IMPACTO MATERIAL IDENTIFICADO | Con la evidencia disponible no se identifica un mecanismo material hacia la exposición evaluada. No significa que el acontecimiento no exista. Si faltan datos esenciales, usar INDETERMINADA y no I0. |
| I1 | BAJA | Existe un mecanismo plausible, pero la exposición identificada es limitada, indirecta o fácilmente sustituible; el efecto esperado sobre operaciones, acceso, incentivos, liquidez, oferta, demanda o riesgo sería acotado según la evidencia disponible. |
| I2 | MODERADA | Existe exposición concreta y un mecanismo directo o indirecto verificable; el efecto podría alterar de forma apreciable una condición relevante para el activo, protocolo, entidad o segmento, aunque su alcance esté limitado por condiciones, duración o alternativas disponibles. |
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

## 4. Horizontes temporales propuestos

Se propone una convención común de ventanas para facilitar el registro y la comparación. Los límites son convenciones de clasificación, no umbrales derivados de una ley estadística. La evidencia específica del mecanismo puede justificar además una fecha o ventana concreta.

| Horizonte | Ventana operativa propuesta | Uso |
| --- | --- | --- |
| INMEDIATO | Desde el momento de referencia hasta 24 horas | Efectos que pueden transmitirse dentro de la misma sesión o del siguiente día; por ejemplo, interrupción operativa, anuncio inesperado con ejecución inmediata o cambio de acceso ya efectivo. |
| CORTO | Más de 24 horas y hasta 7 días naturales | Efectos cuya transmisión requiere varios días, confirmación próxima, ejecución inicial o ajuste operativo de corto recorrido. |
| MEDIO | Más de 7 días y hasta 90 días naturales | Efectos que dependen de implementación, decisiones intermedias, adopción inicial, vencimientos o ajustes que se desarrollan durante semanas o meses. |
| LARGO | Más de 90 días | Efectos estructurales, regulatorios, tecnológicos, de adopción o inversión cuyo mecanismo requiere más de un trimestre para materializarse o evaluarse. |
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
- [ ] El propietario aprueba o modifica las ventanas INMEDIATO (hasta 24 h), CORTO (>24 h–7 días), MEDIO (>7–90 días) y LARGO (>90 días), entendidas como convenciones operativas.
- [ ] Se acepta la separación entre horizonte del acontecimiento, horizonte de transmisión y horizonte de reacción del precio.
- [ ] Se acepta la separación entre dirección, intensidad y probabilidad, sin puntuaciones ni probabilidades inventadas.
- [ ] Los casos ilustrativos se consideran suficientes y no contradicen el glosario del Issue #13.
- [ ] Se acepta la preservación de evaluaciones anteriores y la prohibición de usar movimientos posteriores del precio como justificación retroactiva.

**Gobernanza:** esta versión es una propuesta. Ningún nivel, ventana o criterio se considera aprobado hasta que el propietario lo acepte expresamente. La aprobación documental no autoriza implementación automática; cualquier implementación requerirá un Issue funcional y un PR con pruebas.
