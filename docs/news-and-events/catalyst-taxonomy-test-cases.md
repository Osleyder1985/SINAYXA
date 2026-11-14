# Casos de prueba de la taxonomía de catalizadores

**Issue:** [#29 — Completar pruebas positivas y negativas de la taxonomía](https://github.com/Osleyder1985/SINAYXA/issues/29)  
**Normativa base:** [catalyst-taxonomy.md](catalyst-taxonomy.md) y [catalyst-taxonomy-validation.md](catalyst-taxonomy-validation.md)  
**Naturaleza:** especificación documental de escenarios y oráculos esperados. No implementa un clasificador ni acredita hechos reales.

## 1. Propósito y reglas de evaluación

Este documento convierte los 36 escenarios obligatorios del Issue #29 y sus 10 casos de frontera en pruebas reproducibles. Los 36 escenarios conservan exactamente un positivo y un negativo para cada una de las nueve categorías principales y las nueve familias transversales. Los casos BND complementan esa matriz y no la sustituyen.

La unidad de evaluación se declara en cada caso: **publicación/fuente**, **afirmación**, **acontecimiento** o **hito**. Estos objetos están relacionados, pero no son equivalentes. Una publicación puede probar que una afirmación fue difundida sin probar el hecho afirmado. Un hito posterior no reescribe la evidencia ni el conocimiento disponibles en una fecha anterior.

### 1.1 Decisiones

- **INCLUIR:** el objeto evaluado es trazable, satisface la cobertura taxonómica y tiene relevancia potencial explicada mediante un mecanismo plausible. No exige reacción de precio observada ni causalidad demostrada.
- **EXCLUIR:** la evidencia permite concluir que el objeto examinado no satisface el criterio pertinente: por ejemplo, duplicado sin novedad, contenido irrelevante, cambio cosmético o afirmación demostrablemente falsa.
- **INDETERMINADO:** falta evidencia necesaria para resolver existencia, atribución, alcance, clasificación o relevancia. Se identifica el dato exacto que falta.
- **NO APLICA:** campo que no corresponde al escenario. **DESCONOCIDO:** dato aplicable que no está disponible. No se sustituyen por inferencias.

**No corroborada no significa falsa; no confirmada no significa irrelevante; no observada no significa inexistente.** La falta de evidencia suficiente no justifica por sí sola EXCLUIR. Cuando se excluya el acontecimiento alegado pero la publicación o transacción sí exista, se conserva ese objeto y se identifica exactamente qué afirmación/hecho se excluye. **NINGUNA** significa que no se asigna categoría principal al supuesto catalizador no acreditado; no significa borrar la publicación, observación o evidencia de su circulación.

### 1.2 Contrato de entrada común

Cada escenario debe interpretarse con estos campos:

| Campo | Contenido esperado |
|---|---|
| ID y cobertura | Identificador estable; categoría principal o familia transversal de la fila que se prueba |
| Objeto | PUBLICACIÓN, AFIRMACIÓN, ACONTECIMIENTO o HITO |
| Supuesto neutral | Hechos disponibles sin anticipar la decisión que se debe probar |
| Tiempo y jurisdicción | Fecha/hora de ocurrencia, publicación, primera detección, anuncio oficial y ejecución, cuando apliquen; jurisdicción; desconocidos explícitos |
| Fuente y procedencia | Fuente identificada, referencia verificable y naturaleza primaria/secundaria; no inventar independencia |
| Estado de evidencia | Confirmada por evidencia primaria, atribuida a fuente identificada, parcialmente corroborada, no corroborada o posteriormente desmentida |
| Entidades y exposición | Activos, protocolos, empresas, sectores o jurisdicciones solo si la evidencia los identifica |
| Mecanismo | Canal potencial y vínculo directo, indirecto o condicional; indicar si es hipotético o si existe efecto observado |
| Incertidumbre | Datos ausentes y evidencia adicional necesaria para resolverlos |

### 1.3 Contrato de salida común

La evaluación debe registrar: decisión; objeto y estado; una categoría principal (o NINGUNA); etiqueta transversal explícita cuando corresponda; categorías secundarias justificadas o NINGUNA; mecanismo y tipo de vínculo; evidencia concreta; incertidumbre; regla aplicada y alternativas descartadas; y no-inferencias relevantes.

La familia transversal **no sustituye** la categoría principal. Un caso transversal debe devolver ambas etiquetas. Las categorías secundarias solo se asignan si existe una dimensión adicional material respaldada.

### 1.4 Reglas normativas identificadas para trazabilidad

Los siguientes identificadores se utilizan en la matriz de trazabilidad y en la revisión por escenario:

| Regla | Exigencia verificable |
|---|---|
| R-OBJ | Separar PUBLICACIÓN, AFIRMACIÓN, ACONTECIMIENTO e HITO; no convertir una publicación en hecho por sí sola. |
| R-DEC | Aplicar INCLUIR, EXCLUIR o INDETERMINADO según la evidencia; no convertir desconocimiento en exclusión. |
| R-EVID | Identificar evidencia mínima, procedencia y estado de confirmación; conservar la diferencia entre fuente primaria y secundaria. |
| R-CLASS | Asignar categoría principal por la naturaleza inmediata del hecho; usar NINGUNA cuando no exista acontecimiento catalizador clasificable. |
| R-CROSS | Registrar la familia transversal separadamente; no sustituye ni duplica la categoría principal. |
| R-MECH | Explicitar el mecanismo potencial y el vínculo directo, indirecto o condicional; no afirmar causalidad ni reacción no observada. |
| R-TIME | Separar ocurrencia, publicación, primera detección, anuncio oficial y ejecución; preservar el conocimiento disponible en cada momento. |
| R-UNK | Marcar campos aplicables sin datos como DESCONOCIDO y los no aplicables como NO APLICA; identificar qué evidencia resolvería la incertidumbre. |
| R-NOINFER | No inferir venta, pérdida, explotación, adopción, ejecución, titularidad, reacción, dirección de precio ni causalidad sin evidencia específica. |
| R-NEG | EXCLUIR requiere evidencia positiva del supuesto negativo y de la razón de exclusión; si falta información decisiva, usar INDETERMINADO. |
| R-DUP | Varias publicaciones de una misma fuente o que repiten el mismo origen no crean corroboración ni acontecimientos independientes. |
| R-ANT | Registrar información anticipatoria según lo que se sabía en la primera detección; no exigir confirmación posterior ni validarla retrospectivamente. |


## 2. Matriz de trazabilidad de los 36 escenarios

La columna «Reglas normativas» enlaza cada ID con las reglas definidas en §1.4. Las referencias a §3.1 y §3.2 identifican la ficha operativa del escenario; §4 identifica los casos de frontera que ejercitan distinciones adicionales.

| Fila | Cobertura de Issue #1 | Positivo | Negativo | Reglas normativas aplicables |
|---:|---|---|---|---|
| 1 | Política monetaria y bancos centrales | MAC-P | MAC-N | R-OBJ, R-DEC, R-EVID, R-CLASS, R-MECH, R-TIME, R-UNK, R-NOINFER, R-NEG, R-DUP |
| 2 | Economía mundial y mercados financieros | ECO-P | ECO-N | R-OBJ, R-DEC, R-EVID, R-CLASS, R-MECH, R-TIME, R-UNK, R-NOINFER, R-NEG |
| 3 | Regulación, legislación y política pública | REG-P | REG-N | R-OBJ, R-DEC, R-EVID, R-CLASS, R-MECH, R-TIME, R-UNK, R-NOINFER, R-NEG |
| 4 | Productos de inversión y acceso regulado | ETF-P | ETF-N | R-OBJ, R-DEC, R-EVID, R-CLASS, R-MECH, R-TIME, R-UNK, R-NOINFER, R-NEG, R-DUP |
| 5 | Adopción y actividad institucional o empresarial | INS-P | INS-N | R-OBJ, R-DEC, R-EVID, R-CLASS, R-MECH, R-TIME, R-UNK, R-NOINFER, R-NEG |
| 6 | Acuerdos comerciales y financieros | COM-P | COM-N | R-OBJ, R-DEC, R-EVID, R-CLASS, R-MECH, R-TIME, R-UNK, R-NOINFER, R-NEG |
| 7 | Exchanges, intermediarios e infraestructura de mercado | EXC-P | EXC-N | R-OBJ, R-DEC, R-EVID, R-CLASS, R-MECH, R-TIME, R-UNK, R-NOINFER, R-NEG |
| 8 | Tecnología, protocolos e infraestructura blockchain | TEC-P | TEC-N | R-OBJ, R-DEC, R-EVID, R-CLASS, R-MECH, R-TIME, R-UNK, R-NOINFER, R-NEG |
| 9 | Geopolítica y acontecimientos internacionales | GEO-P | GEO-N | R-OBJ, R-DEC, R-EVID, R-CLASS, R-MECH, R-TIME, R-UNK, R-NOINFER, R-NEG |
| 10 | DeFi | DeFi-P | DeFi-N | R-OBJ, R-DEC, R-EVID, R-CLASS, R-CROSS, R-MECH, R-UNK, R-NOINFER, R-NEG |
| 11 | Stablecoins y dinero tokenizado | Stablecoins-P | Stablecoins-N | R-OBJ, R-DEC, R-EVID, R-CLASS, R-CROSS, R-MECH, R-UNK, R-NOINFER, R-NEG |
| 12 | Tokenomics y oferta | Tokenomics-P | Tokenomics-N | R-OBJ, R-DEC, R-EVID, R-CLASS, R-CROSS, R-MECH, R-TIME, R-UNK, R-NOINFER, R-NEG |
| 13 | Minería y validación | Minería-P | Minería-N | R-OBJ, R-DEC, R-EVID, R-CLASS, R-CROSS, R-MECH, R-UNK, R-NOINFER, R-NEG |
| 14 | Gobernanza y estructura de ecosistemas | Gobernanza-P | Gobernanza-N | R-OBJ, R-DEC, R-EVID, R-CLASS, R-CROSS, R-MECH, R-TIME, R-UNK, R-NOINFER, R-NEG |
| 15 | Custodia, pagos y adopción de infraestructura | Custodia-P | Custodia-N | R-OBJ, R-DEC, R-EVID, R-CLASS, R-CROSS, R-MECH, R-TIME, R-UNK, R-NOINFER, R-NEG |
| 16 | Ciberseguridad | Ciberseguridad-P | Ciberseguridad-N | R-OBJ, R-DEC, R-EVID, R-CLASS, R-CROSS, R-MECH, R-TIME, R-UNK, R-NOINFER, R-NEG |
| 17 | Materias primas, energía y tecnología fuera del sector | Materias primas/energía/tecnología-P | Materias primas/energía/tecnología-N | R-OBJ, R-DEC, R-EVID, R-CLASS, R-CROSS, R-MECH, R-UNK, R-NOINFER, R-NEG |
| 18 | Filtraciones e información anticipatoria | Filtraciones-P | Filtraciones-N | R-OBJ, R-DEC, R-EVID, R-CLASS, R-CROSS, R-TIME, R-ANT, R-UNK, R-NOINFER, R-NEG, R-DUP |

## 3. Escenarios principales

### 3.1 Categorías principales

#### MAC-P — Decisión monetaria nueva
- **Entrada/objeto:** acontecimiento/hito. Un banco central publica una decisión de tipos y orientación de política, con fecha y documento oficial identificables.
- **Salida:** INCLUIR; principal MAC; secundarias NINGUNA salvo dimensión económica adicional documentada; mecanismo potencial por liquidez, coste de capital o financiación; vínculo indirecto o condicional según el canal descrito.
- **Evidencia mínima:** decisión y comunicado primarios, fecha efectiva y jurisdicción.
- **INDETERMINADO si:** no se identifica el documento, la autoridad o el contenido de la decisión.
- **No inferir:** reacción del mercado, cambio efectivo de expectativas, dirección del precio cripto ni causalidad sin evidencia separada.

#### MAC-N — Repetición de opinión antigua
- **Entrada/objeto:** publicación/afirmación. Un comentarista reproduce una opinión antigua sobre posibles recortes, sin decisión, dato ni comunicación monetaria nueva.
- **Salida:** EXCLUIR la publicación como nuevo acontecimiento MAC; categoría principal NINGUNA.
- **Evidencia mínima:** publicación original fechada y comparación verificable con el material anterior que demuestra que no añade un hito ni información material nueva.
- **INDETERMINADO si:** no se puede acceder al original o comprobar si el contenido aporta una novedad.
- **No inferir:** que no haya habido decisiones monetarias separadas no mencionadas en la publicación.

#### ECO-P — Dato macroeconómico oficial
- **Entrada/objeto:** acontecimiento/hito. Se publica un dato oficial de inflación o empleo; el contexto documenta un canal potencial hacia condiciones financieras, apetito por riesgo o financiación cripto.
- **Salida:** INCLUIR; principal ECO; mecanismo potencial descrito; vínculo indirecto o condicional.
- **Evidencia mínima:** publicación estadística oficial, período de referencia, hora de publicación y contexto verificable del canal.
- **INDETERMINADO si:** no se identifica la serie, el dato publicado o el canal relevante.
- **No inferir:** que las expectativas cambiaron, que hubo reacción de precio o que el dato causó un movimiento. Registrar reacción observada solo con evidencia independiente.

#### ECO-N — Indicador local sin exposición
- **Entrada/objeto:** acontecimiento/publicación. Un indicador local menor se publica, pero el expediente del caso no identifica exposición ni mecanismo razonable hacia financiación, comercio, energía, divisas o cripto.
- **Salida:** EXCLUIR como catalizador cripto dentro del alcance evaluado; categoría principal NINGUNA para el supuesto catalizador no acreditado; conservar el indicador y su publicación como objetos económicos verificables.
- **Evidencia mínima:** publicación y jurisdicción identificadas más análisis de exposición que sustente la ausencia de un canal plausible en el contexto disponible.
- **INDETERMINADO si:** faltan datos de exposición o contexto económico que podrían cambiar esa conclusión.
- **No inferir:** irrelevancia global a partir de que la noticia no mencione cripto.

#### REG-P — Propuesta normativa identificable
- **Entrada/objeto:** acontecimiento/hito. Una autoridad competente publica una propuesta que, de aprobarse, modificaría obligaciones, acceso o costes de participantes cripto.
- **Salida:** INCLUIR; principal REG; estado PROPUESTA; mecanismo regulatorio potencial; vínculo directo, indirecto o condicional según sujetos y alcance.
- **Evidencia mínima:** expediente, texto o publicación oficial; autoridad, jurisdicción y fase identificables.
- **INDETERMINADO si:** no puede verificarse la autoridad, el texto o la fase procedimental.
- **No inferir:** aprobación, vigencia, aplicación ni cumplimiento futuro.

#### REG-N — Opinión sin acto regulatorio
- **Entrada/objeto:** publicación/afirmación. Un funcionario expresa una opinión general sin propuesta, expediente, procedimiento ni decisión identificable.
- **Salida:** EXCLUIR como acontecimiento o avance regulatorio; categoría principal NINGUNA para el acto regulatorio no acreditado; conservar la declaración atribuida como publicación/afirmación si es trazable.
- **Evidencia mínima:** declaración íntegra, identidad/cargo y contexto; comprobación del procedimiento al que se refiere, si alguno.
- **INDETERMINADO si:** no se puede identificar jurisdicción, autoridad o posible procedimiento relacionado.
- **No inferir:** inexistencia de iniciativas separadas no examinadas.

#### ETF-P — Hito formal de producto cotizado
- **Entrada/objeto:** acontecimiento/hito. Un regulador registra una solicitud o publica una decisión formal relativa a un producto cotizado vinculado a criptoactivos.
- **Salida:** INCLUIR; principal ETF; fase exacta registrada (solicitud, modificación, aprobación, rechazo, suspensión, restricción o lanzamiento).
- **Evidencia mínima:** expediente o resolución oficial, identificador del producto y fecha del hito.
- **INDETERMINADO si:** no se puede consultar el registro competente o determinar jurisdicción/producto.
- **No inferir:** aprobación a partir de solicitud, lanzamiento a partir de aprobación ni flujos de capital.

#### ETF-N — Especulación sin expediente acreditado
- **Entrada/objeto:** publicación/afirmación. Una publicación pregunta si podría existir un ETF, sin afirmar solicitud ni aportar dato nuevo de expediente.
- **Salida:** EXCLUIR la publicación como acontecimiento ETF confirmado; categoría principal NINGUNA para la solicitud/decisión no acreditada; conservarla como contenido especulativo trazable. No declarar falso un expediente que no se haya podido verificar.
- **Evidencia mínima:** publicación original y consulta del registro competente para producto, jurisdicción y período de la afirmación.
- **INDETERMINADO si:** no se identifica o no se puede consultar el registro competente.
- **No inferir:** que la ausencia de evidencia en una consulta incompleta prueba que no existe solicitud.

#### INS-P — Operación institucional ejecutada
- **Entrada/objeto:** acontecimiento. Una empresa comunica mediante documento regulatorio o comunicación corporativa verificable una compra o venta de criptoactivos ya ejecutada.
- **Salida:** INCLUIR; principal INS; distinguir ejecución de intención, negociación o aprobación interna.
- **Evidencia mínima:** documento primario o confirmación corporativa verificable que identifique la operación y su estado.
- **INDETERMINADO si:** solo hay declaración ambigua de intención o no se puede comprobar ejecución.
- **No inferir:** tamaño, fecha, activo o precio de operación que no estén publicados.

#### INS-N — Opinión empresarial genérica
- **Entrada/objeto:** publicación/afirmación. Un ejecutivo comenta el interés de blockchain sin decisión corporativa, activo, inversión, adopción ni cambio verificable.
- **Salida:** EXCLUIR como compra, inversión o adopción ejecutada; categoría principal NINGUNA para la operación no acreditada; conservar la declaración atribuida como publicación/afirmación si es trazable.
- **Evidencia mínima:** declaración íntegra y contexto suficiente para determinar qué se dijo y qué no se afirmó.
- **INDETERMINADO si:** se desconoce si existe una decisión corporativa separada fuera del material examinado.
- **No inferir:** inexistencia de decisiones internas no publicadas ni adopción efectiva.

#### COM-P — Acuerdo firmado con cambio operativo
- **Entrada/objeto:** acontecimiento/hito. Dos empresas anuncian acuerdo firmado de integración, distribución, financiación o servicios que cambia de forma verificable acceso o capacidad de un servicio cripto.
- **Salida:** INCLUIR; principal COM; secundarias solo si una dimensión material adicional está probada.
- **Evidencia mínima:** contrato, comunicado conjunto o confirmación verificable de las partes; alcance, condiciones y estado.
- **INDETERMINADO si:** no se puede establecer si el acuerdo es vinculante, firmado o ejecutable.
- **No inferir:** lanzamiento, adopción de clientes, volumen ni disponibilidad antes de la fecha efectiva.

#### COM-N — Asociación promocional sin compromiso
- **Entrada/objeto:** publicación. Dos empresas aparecen juntas en un evento o material promocional, sin acuerdo, compromiso, integración ni cambio operativo acreditado.
- **Salida:** EXCLUIR como acuerdo comercial; categoría principal NINGUNA.
- **Evidencia mínima:** material original y contexto de las entidades que permita comprobar que no anuncia un compromiso.
- **INDETERMINADO si:** hay indicios de acuerdo fuera del material examinado y no pueden verificarse.
- **No inferir:** relación contractual a partir de logotipos, fotografías o presencia compartida.

#### EXC-P — Incidente material de intermediario
- **Entrada/objeto:** acontecimiento. Un exchange o custodio confirma incidente que interrumpe retiros, compromete fondos o afecta materialmente disponibilidad/solvencia.
- **Salida:** INCLUIR; principal EXC; activos y alcance solo cuando se acrediten.
- **Evidencia mínima:** aviso del operador, autoridad o investigación técnica verificable; intervalo y servicio afectado.
- **INDETERMINADO si:** no se puede verificar autenticidad, alcance o naturaleza del incidente.
- **No inferir:** pérdida definitiva, insolvencia, hackeo, activos afectados o recuperación sin evidencia.

#### EXC-N — Actualización rutinaria sin afectación
- **Entrada/objeto:** acontecimiento/publicación. Un intermediario anuncia actualización rutinaria de interfaz sin cambio de acceso, disponibilidad, riesgo, solvencia u operación.
- **Salida:** EXCLUIR como catalizador EXC; categoría principal NINGUNA para un incidente/afectación no acreditado; conservar la actualización y sus notas como publicación y cambio de interfaz verificable.
- **Evidencia mínima:** notas oficiales de versión y descripción del alcance operativo que respalden que el cambio es cosmético/rutinario.
- **INDETERMINADO si:** no se conoce el efecto real sobre acceso o servicio.
- **No inferir:** ausencia de incidentes distintos no incluidos en la actualización.

#### TEC-P — Actualización de protocolo activada
- **Entrada/objeto:** acontecimiento/hitos relacionados. Un protocolo publica y activa actualización que cambia consenso, seguridad, escalabilidad o funcionamiento económico.
- **Salida:** INCLUIR; principal TEC; registrar anuncio, activación y resultados como hitos distintos.
- **Evidencia mínima:** propuesta o especificación, release/documentación técnica y registro verificable de activación.
- **INDETERMINADO si:** no se puede verificar qué versión se activó o cuándo.
- **No inferir:** éxito, adopción, mejora de rendimiento o ausencia de fallos por el mero anuncio.

#### TEC-N — Cambio cosmético
- **Entrada/objeto:** publicación/acontecimiento. Un proyecto cambia diseño o identidad visual del sitio sin cambio técnico, operativo o económico.
- **Salida:** EXCLUIR como catalizador TEC; categoría principal NINGUNA para un acontecimiento técnico/económico material no acreditado; conservar el cambio cosmético como publicación/actualización verificable.
- **Evidencia mínima:** comparación de versiones y documentación disponible que delimite el cambio a la presentación visual.
- **INDETERMINADO si:** no puede determinarse si el cambio visual acompaña una modificación funcional.
- **No inferir:** que el proyecto no haya realizado otros cambios técnicos independientes.

#### GEO-P — Medida geopolítica con canal económico
- **Entrada/objeto:** acontecimiento. Una medida geopolítica o sanción afecta de forma verificable comercio, energía, flujos de capital o acceso financiero con canal documentable hacia condiciones cripto.
- **Salida:** INCLUIR; principal GEO si el hecho inmediato es geopolítico; secundarias ECO/REG solo si existe dimensión material adicional.
- **Evidencia mínima:** instrumento o comunicación oficial y evidencia del canal económico/financiero relevante.
- **INDETERMINADO si:** falta jurisdicción, alcance de la medida o evidencia de exposición.
- **No inferir:** impacto cripto agregado, activos afectados ni causalidad de precio.

#### GEO-N — Notoriedad sin transmisión acreditada
- **Entrada/objeto:** acontecimiento/publicación. Un hecho diplomático recibe cobertura amplia, pero el análisis del caso no identifica exposición económica, financiera, comercial, energética o regulatoria relevante para cripto.
- **Salida:** EXCLUIR como catalizador GEO en el contexto evaluado; categoría principal NINGUNA para un catalizador cripto no acreditado; conservar el acontecimiento diplomático y las publicaciones como objetos independientes, sin atribuirles transmisión al mercado cripto.
- **Evidencia mínima:** hecho y jurisdicciones identificados; análisis de exposición que sustente ausencia de canal.
- **INDETERMINADO si:** no hay datos suficientes para evaluar exposición o posibles medidas derivadas.
- **No inferir:** que un hecho internacional carece de consecuencias futuras por no tenerlas demostradas en el momento.

### 3.2 Familias transversales obligatorias

En cada caso de esta sección se exige tanto la categoría principal como la etiqueta transversal indicada.

#### DeFi-P — Exploit confirmado en protocolo DeFi
- **Entrada/objeto:** acontecimiento. Evidencia técnica o transaccional confirma exploit y exposición de protocolo, colateral, liquidez o fondos.
- **Salida:** INCLUIR; TEC principal + familia DeFi; EXC secundaria solo si afecta también a intermediario/infraestructura de mercado.
- **Evidencia mínima:** análisis técnico reproducible, transacciones verificables o confirmación del protocolo.
- **INDETERMINADO si:** solo existe alerta, sin confirmar explotación ni componente afectado.
- **No inferir:** pérdida neta, contagio, protocolo adicional afectado o recuperación sin evidencia.

#### DeFi-N — Ajuste rutinario sin efecto material
- **Entrada/objeto:** acontecimiento. Protocolo modifica parámetro rutinario y documentación/evidencia indica que no cambia materialmente riesgo, liquidez, colateral, funcionamiento ni incentivos.
- **Salida:** EXCLUIR como catalizador DeFi; familia DeFi; categoría principal NINGUNA para el evento irrelevante.
- **Evidencia mínima:** propuesta/cambio y análisis del parámetro y su efecto.
- **INDETERMINADO si:** no se conoce el efecto real sobre riesgo o liquidez.
- **No inferir:** neutralidad por el nombre “rutinario” ni ausencia de efectos no medidos.

#### Stablecoins-P — Disfunción de emisor o redención
- **Entrada/objeto:** acontecimiento. Emisor suspende redenciones, revela insuficiencia de reservas o existe pérdida material de paridad respaldada por evidencia.
- **Salida:** INCLUIR + familia stablecoins; principal según hecho inmediato: INS para reservas/solvencia/redenciones del emisor; TEC para fallo técnico/de protocolo; REG para acto regulatorio.
- **Evidencia mínima:** aviso del emisor/autoridad, informe de reservas o datos verificables de mercado/redenciones.
- **INDETERMINADO si:** no se puede verificar reservas, redenciones, paridad o causa.
- **No inferir:** insolvencia, pérdida definitiva ni alcance de contagio a partir de una cotización aislada.

#### Stablecoins-N — Oscilación ordinaria sin disfunción probada
- **Entrada/objeto:** observación de mercado y publicación/datos asociados. Se observa oscilación transitoria sin evidencia de problema en reservas, redenciones, liquidez, solvencia o funcionamiento.
- **Salida:** EXCLUIR como catalizador stablecoin en el supuesto delimitado; categoría principal NINGUNA para un acontecimiento de disfunción no acreditado; conservar la observación y sus publicaciones como registros de mercado/fuentes; familia transversal STABLECOINS.
- **Evidencia mínima:** datos de mercado con fuente y período más evidencia disponible sobre funcionamiento normal de redenciones/reservas o ausencia de indicios de disfunción.
- **INDETERMINADO si:** datos de paridad, reservas o redenciones son insuficientes.
- **No inferir:** normalidad a partir de una sola cotización ni aplicar umbral numérico no aprobado.

#### Tokenomics-P — Cambio verificable de reglas de oferta
- **Entrada/objeto:** acontecimiento/hito. Protocolo anuncia y ejecuta cambio verificable de emisión, quema, vesting, desbloqueo o incentivos.
- **Salida:** INCLUIR + familia tokenomics; TEC principal para regla/protocolo; distinguir anuncio y ejecución.
- **Evidencia mínima:** documentación del protocolo, contrato o datos on-chain verificables y estado de ejecución.
- **INDETERMINADO si:** no se puede comprobar regla, contrato, cantidad o estado aplicable.
- **No inferir:** venta, distribución a mercado ni presión vendedora por desbloqueo o transferencia aislados.

#### Tokenomics-N — Transferencia sin cambio económico demostrado
- **Entrada/objeto:** observación de transacción on-chain. Una dirección transfiere tokens, sin evidencia de cambio de oferta, venta, distribución, desbloqueo o incentivos.
- **Salida:** EXCLUIR como acontecimiento de tokenomics solo si evidencia suficiente permite establecer que no existe cambio material; categoría principal NINGUNA para una venta/cambio de oferta no acreditados; conservar la transacción como observación on-chain y la atribución como afirmación separada; familia transversal TOKENOMICS Y OFERTA.
- **Evidencia mínima:** datos on-chain, atribución/control de direcciones y documentación de propósito cuando se afirme que es interno.
- **INDETERMINADO si:** control, propósito o destino económico son desconocidos.
- **No inferir:** venta, identidad del titular o cambio de oferta por el mero movimiento.

#### Minería-P — Decisión operativa de minería
- **Entrada/objeto:** acontecimiento. Operador confirma cierre o expansión de instalaciones por costes energéticos, regulación o rentabilidad; exposición operativa documentada.
- **Salida:** INCLUIR + familia minería/validación; principal según hecho inmediato: INS para decisión del operador; ECO para shock energético externo; REG para restricción legal; TEC para cambio de protocolo/consenso.
- **Evidencia mínima:** comunicación del operador o autoridad, instalación/operación identificable y evidencia del factor declarado.
- **INDETERMINADO si:** no se identifica operador, instalación, decisión o causa.
- **No inferir:** variación global de hashrate, seguridad de red o impacto de precio desde una instalación aislada.

#### Minería-N — Ajuste automático ordinario acreditado
- **Entrada/objeto:** observación de red y documentación del protocolo. El ajuste de dificultad sigue el mecanismo automático previsto y no hay evidencia de cambio anómalo de operación, seguridad, costes o capacidad.
- **Salida:** EXCLUIR como catalizador anómalo solo si la normalidad está acreditada; categoría principal NINGUNA para el supuesto de anomalía/catalizador no demostrado; conservar la observación técnica y su contexto; familia transversal MINERÍA Y VALIDACIÓN.
- **Evidencia mínima:** reglas del protocolo y datos contextualizados de dificultad, hashrate, intervalo/producción de bloques y capacidad operativa.
- **INDETERMINADO si:** falta contexto temporal/técnico u operativo. Hashrate es magnitud observada/estimada; no describirlo como parámetro que el protocolo ajusta automáticamente del mismo modo que la dificultad.
- **No inferir:** normalidad ni anomalía a partir de una métrica aislada.

#### Gobernanza-P — Propuesta, voto y ejecución
- **Entrada/objeto:** hitos. Propuesta verificable pasa a votación y obtiene resultado que cambia reglas, liderazgo, roadmap o asignación de recursos.
- **Salida:** INCLUIR + familia gobernanza; TEC principal cuando el cambio corresponde a reglas/protocolo; diferenciar propuesta, votación, resultado y ejecución.
- **Evidencia mínima:** propuesta, registro de votación y prueba de ejecución cuando se afirme que fue ejecutada.
- **INDETERMINADO si:** no se puede verificar validez del proceso, resultado o ejecución.
- **No inferir:** implementación por aprobación ni efectos económicos no observados.

#### Gobernanza-N — Sugerencia informal sin proceso decisorio
- **Entrada/objeto:** publicación/afirmación. Participante publica sugerencia sin propuesta formal, respaldo, proceso de decisión ni efecto verificable.
- **Salida:** EXCLUIR como hito de gobernanza; categoría principal NINGUNA para un proceso decisorio no acreditado; conservar la sugerencia como publicación/afirmación atribuida si es trazable; familia transversal GOBERNANZA solo si el contenido trata efectivamente del ecosistema.
- **Evidencia mínima:** publicación original y contexto del foro/proceso consultado.
- **INDETERMINADO si:** no puede descartarse una propuesta formal paralela.
- **No inferir:** ausencia de debate o decisión fuera del ámbito consultado.

#### Custodia-P — Incorporación o retirada efectiva de servicio
- **Entrada/objeto:** acontecimiento/hito. Banco, custodio o red de pagos confirma incorporación o retirada de servicio cripto que cambia efectivamente acceso.
- **Salida:** INCLUIR + familia custodia/pagos/infraestructura; principal COM, INS o EXC según naturaleza inmediata.
- **Evidencia mínima:** comunicación primaria y confirmación operativa del servicio, alcance y fecha efectiva.
- **INDETERMINADO si:** solo hay anuncio sin fecha, alcance o confirmación de disponibilidad.
- **No inferir:** uso real, número de clientes o volumen transaccionado.

#### Custodia-N — Material promocional o especulación sin procedencia
- **Entrada/objeto:** publicación/afirmación. Se especula sobre integración futura sin fuente identificada ni evidencia verificable de conversaciones, acuerdo o lanzamiento.
- **Salida:** EXCLUIR como integración efectiva; categoría principal NINGUNA para una integración/servicio no acreditado; si la publicación es trazable, conservarla como afirmación no corroborada y no como servicio disponible; familia transversal CUSTODIA/PAGOS solo cuando el contenido trate realmente de ese ámbito.
- **Evidencia mínima:** publicación original y comprobación de que no atribuye conversaciones a fuente identificada ni aporta documentación del proceso.
- **INDETERMINADO si:** existe fuente identificada que confirma conversaciones exploratorias o no puede verificarse si hay proceso paralelo.
- **No inferir:** que una conversación confirmada es irrelevante; en ese caso se clasifica como proceso anticipatorio/en desarrollo, no como integración ejecutada.

#### Ciberseguridad-P — Vulnerabilidad explotada confirmada
- **Entrada/objeto:** acontecimiento. Vulnerabilidad ha sido explotada en sistema cripto; componente y alcance técnico están respaldados.
- **Salida:** INCLUIR + familia ciberseguridad; TEC principal; EXC secundaria si afecta a intermediario/infraestructura de mercado.
- **Evidencia mínima:** informe técnico, aviso del responsable, transacciones o evidencia reproducible de explotación.
- **INDETERMINADO si:** existe alerta pero no se confirma exposición o explotación.
- **No inferir:** pérdida, cantidad robada, fondos recuperados o usuarios afectados sin evidencia.

#### Ciberseguridad-N — Falso positivo demostrado
- **Entrada/objeto:** afirmación/alerta. Auditoría técnica identifica alerta inicial como falso positivo y demuestra que el componente/versión examinado no contiene la vulnerabilidad alegada ni estuvo expuesto.
- **Salida:** EXCLUIR como incidente confirmado; categoría principal NINGUNA para el incidente alegado que no existió en el componente/versión examinados; conservar alerta, informe y análisis como publicaciones/afirmaciones relacionadas; familia transversal CIBERSEGURIDAD.
- **Evidencia mínima:** informe reproducible que identifique componente, versión, método y conclusión.
- **INDETERMINADO si:** solo existe alerta sin análisis suficiente para confirmar o descartar.
- **No inferir:** que todo el sistema está libre de vulnerabilidades distintas.

#### Materias primas/energía/tecnología-P — Shock energético con exposición
- **Entrada/objeto:** acontecimiento. Interrupción documentada del suministro energético eleva costes de operadores de minería identificables o altera condiciones macrofinancieras mediante canal explicado.
- **Salida:** INCLUIR + familia materias primas/energía/tecnología; ECO principal para shock económico/energético; TEC o INS secundarias solo si impacto operativo específico probado.
- **Evidencia mínima:** fuente primaria/sectorial del suministro afectado y datos verificables de exposición o canal macro.
- **INDETERMINADO si:** faltan localización, duración, exposición o datos de transmisión.
- **No inferir:** costes de mineros concretos, cierres ni impacto cripto global sin evidencia.

#### Materias primas/energía/tecnología-N — Producto sin canal cripto
- **Entrada/objeto:** publicación/acontecimiento. Noticia sobre nuevo dispositivo de consumo sin relación demostrable con minería, infraestructura, costes, inflación, liquidez o adopción cripto.
- **Salida:** EXCLUIR como catalizador de esa familia; categoría principal NINGUNA para un canal cripto no acreditado; conservar el producto y la noticia como objetos tecnológicos/comerciales, sin atribuirles exposición cripto.
- **Evidencia mínima:** fuente original y análisis de las características del producto y de los canales de exposición pertinentes.
- **INDETERMINADO si:** faltan detalles técnicos o comerciales que podrían revelar exposición relevante.
- **No inferir:** irrelevancia futura permanente.

#### Filtraciones-P — Información anticipatoria trazable
- **Entrada/objeto:** publicación/afirmación anticipatoria anterior al anuncio oficial; pieza fechada y atribuible a fuente identificada, con contenido concreto.
- **Salida:** INCLUIR como información anticipatoria + familia filtraciones; categoría principal según naturaleza del hecho anticipado; estado no corroborado/atribuido si no existe corroboración.
- **Evidencia mínima:** publicación o documento original, fecha, procedencia y comparación temporal con anuncio oficial si este ya ocurrió.
- **INDETERMINADO si:** no se puede verificar origen, fecha o contenido concreto.
- **No inferir:** veracidad, confirmación oficial ni que el anuncio posterior valide todos los detalles. No exigir anuncio oficial posterior para registrar la señal anticipatoria trazable.

#### Filtraciones-N — Atribución falsa o material manipulado demostrados
- **Entrada/objeto:** publicación/afirmación. Cuenta anónima difunde supuesta filtración y evidencia posterior verificable demuestra manipulación del documento o atribución falsa.
- **Salida:** EXCLUIR la afirmación como evidencia del acontecimiento alegado; categoría principal NINGUNA para el hecho alegado que la evidencia desmiente; conservar la publicación, rectificación y análisis como objetos separados; familia transversal FILTRACIONES solo como clasificación de la afirmación anticipatoria examinada.
- **Evidencia mínima:** publicación original y análisis del documento o rectificación fiable que demuestre manipulación/atribución falsa.
- **INDETERMINADO si:** solo falta corroboración, la fuente es anónima o no se ha probado falsedad.
- **No inferir:** que una filtración es fabricada por ser anónima o no corroborada.

## 3.3 Registro explícito de aplicación del contrato a los 36 escenarios

Este registro complementa las fichas de §3.1 y §3.2. En todos los casos los escenarios son sintéticos: no se inventan nombres propios, fechas concretas, jurisdicciones, cantidades ni activos. «DESCONOCIDO» identifica un campo aplicable que el supuesto no concreta; «NO APLICA» identifica un campo que no corresponde al objeto. La evidencia mínima, el mecanismo, la decisión y las alternativas se desarrollan en la ficha individual del ID.

| ID | Objeto evaluado | Tiempo / jurisdicción | Fuente y procedencia | Estado de evidencia supuesto | Entidades / activos | Mecanismo y vínculo | Desconocidos / alternativas que no se presuponen |
|---|---|---|---|---|---|---|---|
| MAC-P | ACONTECIMIENTO + HITO | Fecha de decisión/publicación: identificable; jurisdicción: banco central competente | Documento y comunicado primarios | Confirmada por evidencia primaria | Banco central; activos concretos DESCONOCIDOS | Liquidez/coste de capital; indirecto o condicional | Magnitud/reacción cripto DESCONOCIDAS; no inferir causalidad |
| MAC-N | PUBLICACIÓN + AFIRMACIÓN | Fecha original: debe verificarse; jurisdicción: NO APLICA si es opinión general | Publicación original y material anterior | Contenido repetido verificable | Comentarista; activos NO APLICA | Sin mecanismo nuevo acreditado | Decisión monetaria nueva DESCONOCIDA; si no puede descartarse, INDETERMINADO |
| ECO-P | ACONTECIMIENTO + HITO | Fecha/hora y período de referencia; jurisdicción de la estadística | Publicación estadística oficial | Confirmada por evidencia primaria | Autoridad estadística; exposición cripto concreta DESCONOCIDA | Condiciones financieras/apetito por riesgo; indirecto o condicional | Reacción y cambio de expectativas DESCONOCIDOS |
| ECO-N | ACONTECIMIENTO + PUBLICACIÓN | Fecha y jurisdicción identificables | Publicación oficial y análisis de exposición | Confirmada en cuanto al dato; relevancia excluida en contexto evaluado | Indicador/sector local; activos cripto DESCONOCIDOS | Canal plausible no acreditado | Exposición global DESCONOCIDA; si faltan datos decisivos, INDETERMINADO |
| REG-P | ACONTECIMIENTO + HITO | Fecha de publicación/fase; jurisdicción identificada | Expediente o texto oficial | Confirmada como propuesta, no como norma vigente | Autoridad y sujetos regulados; activos según expediente | Obligaciones/acceso/costes; directo, indirecto o condicional | Aprobación y vigencia DESCONOCIDAS |
| REG-N | PUBLICACIÓN + AFIRMACIÓN | Fecha y jurisdicción/autoridad a identificar | Declaración íntegra atribuida | Atribuida a fuente identificada | Funcionario; activos NO APLICA salvo mención | Ningún acto regulatorio acreditado | Procedimientos paralelos DESCONOCIDOS |
| ETF-P | ACONTECIMIENTO + HITO | Fecha del registro/decisión; jurisdicción del regulador | Expediente o resolución oficial | Confirmada por evidencia primaria | Producto y solicitante identificables en expediente | Acceso/inversión regulada; condicional según fase | Aprobación, lanzamiento y flujos no se presuponen |
| ETF-N | PUBLICACIÓN + AFIRMACIÓN | Fecha de publicación; jurisdicción/producto deben identificarse | Publicación original; registro competente consultado | Especulación trazable; expediente no acreditado en consulta | Producto alegado; solicitante DESCONOCIDO | No hay mecanismo de solicitud confirmado | Existencia de expediente fuera de consulta: INDETERMINADO |
| INS-P | ACONTECIMIENTO | Fecha de ejecución/publicación según documento; jurisdicción de entidad | Documento regulatorio o comunicación corporativa | Confirmada si la ejecución está documentada | Empresa y activo solo según fuente | Flujos/exposición institucional; directo respecto de la operación, impacto precio no probado | Cantidad/precio si no publicados: DESCONOCIDOS |
| INS-N | PUBLICACIÓN + AFIRMACIÓN | Fecha de declaración; jurisdicción de empresa DESCONOCIDA | Declaración íntegra y contexto | Atribuida; no acredita decisión/operación | Ejecutivo/empresa; activo DESCONOCIDO | Sin operación o adopción demostrada | Decisión separada no pública: DESCONOCIDA |
| COM-P | ACONTECIMIENTO + HITO | Fecha de firma y fecha efectiva si distintas; jurisdicciones de las partes | Contrato/comunicado conjunto/confirmación de partes | Confirmada según evidencia del acuerdo | Empresas y servicio descritos por fuente | Acceso/capacidad del servicio; directo o condicional | Lanzamiento/uso/volumen no se presuponen |
| COM-N | PUBLICACIÓN | Fecha del material; jurisdicción NO APLICA si no se identifica compromiso | Material promocional original | Publicación confirmada; acuerdo no acreditado | Empresas visibles; activos NO APLICA | Sin cambio operativo acreditado | Acuerdo externo DESCONOCIDO; si hay indicios, INDETERMINADO |
| EXC-P | ACONTECIMIENTO + HITO | Intervalo del incidente; jurisdicción del operador | Aviso del operador/autoridad o análisis técnico | Confirmada según evidencia del incidente | Exchange/custodio y servicio; activos solo si identificados | Disponibilidad/solvencia/custodia; directo | Pérdidas/alcance/recuperación DESCONOCIDOS salvo prueba |
| EXC-N | ACONTECIMIENTO + PUBLICACIÓN | Fecha de actualización; jurisdicción del intermediario | Notas oficiales de versión | Confirmada como actualización rutinaria | Intermediario y producto/servicio | Sin canal material de acceso/solvencia acreditado | Incidentes independientes NO APLICA a esta actualización |
| TEC-P | ACONTECIMIENTO + HITOS | Fechas de anuncio y activación separadas; jurisdicción NO APLICA para protocolo descentralizado salvo entidad legal identificada | Propuesta, release y registro de activación | Confirmada por documentación técnica/registro | Protocolo, versión y red; activos afectados según evidencia | Consenso/seguridad/escalabilidad/economía; directo sobre funcionamiento | Resultados de mercado DESCONOCIDOS |
| TEC-N | PUBLICACIÓN + ACONTECIMIENTO | Fecha de cambio; jurisdicción NO APLICA salvo entidad identificada | Versiones/documentación del sitio | Confirmada como cambio cosmético | Proyecto/sitio; activos NO APLICA | Sin mecanismo técnico/económico | Cambios técnicos separados DESCONOCIDOS |
| GEO-P | ACONTECIMIENTO + HITO | Fecha de medida; jurisdicciones afectadas | Instrumento estatal/autoridad y datos del canal | Confirmada por evidencia primaria | Estados/sectores/activos solo si hay exposición | Comercio/energía/capital/acceso; indirecto o condicional | Alcance y efecto cripto no demostrado por defecto |
| GEO-N | ACONTECIMIENTO + PUBLICACIÓN | Fecha y jurisdicciones del hecho | Fuente primaria del hecho y análisis de exposición | Hecho confirmado; canal relevante no acreditado | Estados/partes; activos DESCONOCIDOS | Sin transmisión demostrada en contexto | Consecuencias futuras DESCONOCIDAS |
| DeFi-P | ACONTECIMIENTO | Fecha de explotación/detección; jurisdicción NO APLICA salvo entidad identificada | Informe técnico, protocolo y transacciones verificables | Confirmada por evidencia técnica/transaccional | Protocolo, contratos y activos solo según evidencia | Riesgo/colateral/liquidez/contagio; directo o condicional | Pérdidas y contagio no probados si no hay datos |
| DeFi-N | ACONTECIMIENTO + HITO | Fecha del parámetro; jurisdicción NO APLICA salvo entidad | Propuesta/documentación y análisis técnico | Cambio confirmado; ausencia de efecto material sustentada | Protocolo y parámetro | Sin alteración material acreditada | Efectos no medidos: DESCONOCIDOS; si decisivos, INDETERMINADO |
| Stablecoins-P | ACONTECIMIENTO + HITO | Fecha de suspensión/dato; jurisdicción del emisor/red si identificable | Emisor, reservas, redenciones o datos verificables | Según evidencia primaria/mercado corroborada | Stablecoin, emisor y redes identificables | Redenciones/reservas/paridad/liquidez; directo | Magnitud y duración DESCONOCIDAS salvo prueba |
| Stablecoins-N | OBSERVACIÓN + PUBLICACIÓN | Período de cotización; mercado/plataforma de observación | Datos de mercado y evidencia de reservas/redenciones disponible | Oscilación observada; disfunción no acreditada | Stablecoin y mercado si identificados | No se acredita disfunción material | Reservas/redenciones incompletas => INDETERMINADO |
| Tokenomics-P | ACONTECIMIENTO + HITO | Fechas de anuncio y ejecución/desbloqueo | Documentación de protocolo/contrato/datos on-chain | Confirmada según regla y ejecución | Token, contrato y protocolo | Emisión/quema/vesting/oferta/incentivos; directo | Venta posterior DESCONOCIDA y no inferida |
| Tokenomics-N | OBSERVACIÓN DE TRANSACCIÓN | Fecha/bloque; red identificable | Datos on-chain y atribución si se afirma control común | Transacción confirmada; finalidad puede ser DESCONOCIDA | Direcciones/token; titular DESCONOCIDO si no atribuido | Cambio de oferta/venta no acreditados | Control/propósito desconocidos => INDETERMINADO |
| Minería-P | ACONTECIMIENTO + DECISIÓN OPERATIVA | Fecha de cierre/expansión; jurisdicción/localización del operador | Confirmación del operador y evidencia de coste/regulación | Atribuida/confirmada según fuente | Operador, instalaciones y red; activos según exposición | Coste energético/rentabilidad/capacidad; directo o indirecto | Magnitud de capacidad/efecto precio DESCONOCIDA |
| Minería-N | OBSERVACIÓN DE RED + DOCUMENTACIÓN | Ventana temporal de ajuste; red/protocolo identificable | Regla del protocolo y datos contextualizados | Ajuste ordinario confirmado si datos lo sustentan | Red y parámetros observados | No se acredita anomalía operativa | Hashrate/capacidad/causa DESCONOCIDOS si no hay contexto |
| Gobernanza-P | ACONTECIMIENTO + HITOS | Fechas de propuesta, voto, resultado y ejecución | Propuesta y registro de votación/ejecución | Confirmada por registro oficial del proceso | DAO/protocolo y participantes solo si identificados | Reglas/recursos/hoja de ruta; directo | Efectos no ejecutados no se presuponen |
| Gobernanza-N | PUBLICACIÓN + AFIRMACIÓN | Fecha del mensaje; foro/proceso consultado | Publicación original y contexto del foro | Atribuida; proceso formal no acreditado | Participante y proyecto | Sin decisión formal demostrada | Propuesta paralela DESCONOCIDA |
| Custodia-P | ACONTECIMIENTO + HITO | Fechas de anuncio y disponibilidad efectiva separadas; jurisdicción del proveedor | Comunicación primaria y confirmación operativa | Confirmada solo al verificar estado efectivo | Banco/custodio/red y servicio | Acceso/custodia/pagos; directo | Uso/adopción/volumen DESCONOCIDOS |
| Custodia-N | PUBLICACIÓN + AFIRMACIÓN | Fecha de publicación; jurisdicción del proveedor DESCONOCIDA | Publicación original; fuente atribuida si existe | No corroborada o atribuida según procedencia | Proveedor/contraparte alegados | Conversaciones no equivalen a integración | Proceso paralelo DESCONOCIDO; fuente identificada puede cambiar a INDETERMINADO/en desarrollo |
| Ciberseguridad-P | ACONTECIMIENTO | Fecha de detección/explotación; sistema y jurisdicción si identificables | Informe técnico/aviso responsable/transacciones | Confirmada si explotación reproducible | Componente, versión y protocolo | Explotación/seguridad; directo | Pérdidas/usuarios/recuperación DESCONOCIDOS |
| Ciberseguridad-N | AFIRMACIÓN/ALERTA + INFORME | Fechas de alerta e informe; componente/versión concretos | Alerta original y auditoría reproducible | Falso positivo demostrado solo para alcance examinado | Componente/versión; sistema completo no se presume | No existe vulnerabilidad/exposición en el alcance probado | Otras versiones/sistemas DESCONOCIDOS |
| Materias primas/energía/tecnología-P | ACONTECIMIENTO + HITO | Fecha/ubicación de interrupción; jurisdicción/mercado energético | Fuente primaria/sectorial y datos de exposición | Confirmada según fuente y canal | Energía, operadores mineros o sectores expuestos | Costes/capacidad/condiciones macro; indirecto o condicional | Costes individuales/efecto cripto DESCONOCIDOS sin datos |
| Materias primas/energía/tecnología-N | PUBLICACIÓN + ACONTECIMIENTO | Fecha del producto; jurisdicción/mercado DESCONOCIDOS si no especificados | Fuente original y especificaciones verificables | Producto/publicación confirmados; canal no acreditado | Dispositivo/sector; activos NO APLICA | Sin canal cripto demostrado | Uso futuro o aplicación minera DESCONOCIDOS |
| Filtraciones-P | PUBLICACIÓN + AFIRMACIÓN ANTICIPATORIA | Primera detección, publicación y anuncio oficial separados; jurisdicción según hecho anticipado | Pieza original fechada y fuente identificada | Atribuida/no corroborada en primera detección; nunca elevar retrospectivamente | Entidades/activos según contenido; DESCONOCIDOS si no aparecen | Mecanismo según hecho anticipado; vínculo condicional hasta corroboración | Veracidad/confirmación oficial DESCONOCIDAS al primer registro |
| Filtraciones-N | PUBLICACIÓN + AFIRMACIÓN | Fecha original y fecha de rectificación/análisis; jurisdicción según afirmación | Publicación original y prueba positiva de manipulación/atribución falsa | Posteriormente desmentida solo con evidencia positiva | Cuenta/documento/entidad alegada | Afirmación no sirve como evidencia del hecho alegado | Sin prueba positiva de falsedad => INDETERMINADO, no EXCLUIR como fabricada |

## 4. Casos de frontera BND-01 a BND-10

Los casos de frontera son complementarios. Cada uno prueba una distinción normativa concreta y no altera la correspondencia 1:1 de los 36 casos principales.

#### BND-01 — Solicitud ETF registrada frente a especulación
- **Entrada/objeto:** dos publicaciones: una enlaza expediente oficial de solicitud; otra especula sin expediente ni fuente.
- **Salida:** INCLUIR el hito de solicitud si registro, producto y jurisdicción coinciden; conservar la especulación como afirmación, no como solicitud.
- **Categoría/familia:** ETF; familia transversal NINGUNA salvo que el supuesto añada otra dimensión acreditada.
- **Evidencia mínima:** registro oficial y publicación original.
- **INDETERMINADO si:** no puede consultarse el registro competente o no se identifica producto/jurisdicción.
- **No inferir:** aprobación, lanzamiento ni probabilidad de aprobación.

#### BND-02 — Filtración atribuida sin corroboración
- **Entrada/objeto:** documento o declaración fechada, fuente identificada, anterior al anuncio y sin corroboración independiente al momento de primera detección.
- **Salida:** INCLUIR como anticipatoria con estado ATRIBUIDA o NO CORROBORADA; nunca como hecho confirmado.
- **Categoría/familia:** categoría del hecho anticipado + familia filtraciones.
- **Evidencia mínima:** copia o registro de la pieza original, fecha y atribución verificable.
- **INDETERMINADO si:** origen, fecha o integridad no pueden verificarse.
- **No inferir:** veracidad ni validación retrospectiva por un anuncio posterior.

#### BND-03 — Filtración anónima sin procedencia
- **Entrada/objeto:** publicación anónima sin documento, atribución ni procedencia rastreable.
- **Salida:** INDETERMINADO respecto del acontecimiento alegado; EXCLUIR como evidencia confirmatoria. Solo excluir la afirmación como falsa si aparece prueba positiva de falsedad.
- **Categoría/familia:** ninguna asignación afirmativa; familia filtraciones puede etiquetar la pieza en cuarentena si el registro conserva publicaciones no corroboradas.
- **Evidencia mínima:** publicación original para probar que circuló, no para probar su contenido.
- **INDETERMINADO si:** no existe evidencia adicional de autenticidad o falsedad.
- **No inferir:** que anonimato equivale a falsedad.

#### BND-04 — Conversaciones exploratorias verificadas frente a rumor
- **Entrada/objeto:** caso A: fuente identificada confirma conversaciones exploratorias de custodia; caso B: rumor sin fuente afirma integración.
- **Salida:** A INCLUIR como proceso anticipatorio/en desarrollo, no como integración efectiva. B INDETERMINADO como afirmación no corroborada.
- **Categoría/familia:** categoría según naturaleza inmediata (COM/INS/EXC cuando proceda) + familia custodia/pagos/infraestructura.
- **Evidencia mínima:** declaración atribuida verificable para A; publicación original para registrar B.
- **INDETERMINADO si:** no se puede comprobar la fuente o el contenido de las conversaciones.
- **No inferir:** contrato, fecha de lanzamiento, servicio disponible o adopción.

#### BND-05 — Transferencia con control común probado frente a control desconocido
- **Entrada/objeto:** transacción on-chain; caso A tiene evidencia de control común de direcciones y ausencia de cambio económico; caso B carece de atribución fiable.
- **Salida:** A EXCLUIR como venta/cambio de oferta si no hay otra modificación material. B INDETERMINADO.
- **Categoría/familia:** tokenomics solo si se prueba cambio de oferta/reglas; familia tokenomics cuando corresponda.
- **Evidencia mínima:** transacción, atribución de control y contexto de propósito para A.
- **INDETERMINADO si:** control o propósito desconocidos.
- **No inferir:** venta, titularidad ni intención por el mero movimiento.

#### BND-06 — Desbloqueo on-chain sin venta probada
- **Entrada/objeto:** hito de desbloqueo verificable según contrato/vesting; no hay evidencia de transferencia a exchange o venta.
- **Salida:** INCLUIR desbloqueo como hito de tokenomics si material y documentado; no registrar venta.
- **Categoría/familia:** TEC principal cuando el hecho inmediato sea regla del protocolo + familia tokenomics.
- **Evidencia mínima:** contrato, calendario/regla y transacción o estado de desbloqueo.
- **INDETERMINADO si:** no se puede comprobar que el saldo quedó efectivamente desbloqueado.
- **No inferir:** venta, distribución al mercado o presión vendedora realizada.

#### BND-07 — Dificultad automática frente a caída de hashrate sin contexto
- **Entrada/objeto:** caso A: ajuste de dificultad conforme a regla y datos contextualizados; caso B: caída de hashrate sin causa ni alcance identificados.
- **Salida:** A EXCLUIR como anomalía/catalizador si se acredita normalidad; B INDETERMINADO.
- **Categoría/familia:** minería/validación como familia; TEC solo si hay cambio técnico/protocolo material.
- **Evidencia mínima:** regla del protocolo y series/contexto de dificultad, hashrate, bloques y capacidad.
- **INDETERMINADO si:** falta contexto técnico/temporal o causa.
- **No inferir:** que hashrate sea un parámetro ajustado automáticamente como dificultad ni que una caída aislada pruebe pérdida de seguridad.

#### BND-08 — Dato macro sin reacción observada
- **Entrada/objeto:** publicación estadística oficial; mecanismo potencial documentado; no hay datos que acrediten reacción de mercado.
- **Salida:** INCLUIR el acontecimiento macro; registrar reacción como NO OBSERVADA/NO DISPONIBLE.
- **Categoría/familia:** ECO o MAC según hecho inmediato; ninguna familia transversal obligatoria.
- **Evidencia mínima:** publicación oficial y explicación del canal potencial.
- **INDETERMINADO si:** el dato o el canal no se pueden verificar.
- **No inferir:** reacción, cambio de expectativas ni causalidad.

#### BND-09 — Alerta de vulnerabilidad frente a exploit confirmado
- **Entrada/objeto:** caso A: alerta de vulnerabilidad sin evidencia de explotación; caso B: explotación respaldada por evidencia técnica o transaccional reproducible.
- **Salida A:** registrar la alerta como PUBLICACIÓN/AFIRMACIÓN de ciberseguridad, con el estado de evidencia disponible. **No declarar acontecimiento de explotación ni asignar estado EXPLOTADO.** Si la vulnerabilidad y el componente están verificados, conservar el acontecimiento «vulnerabilidad identificada» como tal; su explotación permanece NO DEMOSTRADA.
- **Salida B:** **INCLUIR** el acontecimiento de explotación confirmada como catalizador de ciberseguridad.
- **Categoría/familia:** TEC principal cuando el hecho inmediato sea una vulnerabilidad o explotación técnica; familia transversal CIBERSEGURIDAD. EXC secundaria únicamente si existe afectación material acreditada a un exchange, custodio o intermediario. Para A sin vulnerabilidad verificada, categoría principal NINGUNA y solo registro de la alerta como publicación/afirmación.
- **Evidencia mínima:** A: aviso técnico original con componente/versión y procedencia identificables; para afirmar vulnerabilidad, análisis técnico verificable. B: evidencia reproducible de explotación, transacciones atribuibles o confirmación técnica del responsable.
- **INDETERMINADO si:** no se puede resolver autenticidad de la alerta, componente/versión afectado, exposición o existencia de explotación. La ausencia de prueba de explotación no permite concluir que la alerta sea falsa.
- **No inferir:** pérdidas, fondos robados, usuarios afectados, alcance, explotación o recuperación desde la mera existencia de una vulnerabilidad.

#### BND-10 — Repetición mediática frente a hito posterior
- **Entrada/objeto:** caso A: múltiples medios reproducen la misma fuente original; caso B: aparece una decisión/resultado posterior que cambia el estado del proceso.
- **Salida:** A un acontecimiento/afirmación con varias referencias; B nuevo hito relacionado, con identidad y fecha propias.
- **Categoría/familia:** categoría según hecho inmediato; familia transversal solo si aplica al hecho.
- **Evidencia mínima:** fuentes originales y cronología de publicación; para B, documento/registro del hito posterior.
- **INDETERMINADO si:** no se puede determinar si la nueva publicación aporta un hito material o solo repite.
- **No inferir:** independencia por cantidad de medios ni equivalencia entre hitos sucesivos.

## 5. Reglas de precedencia y casos indeterminados

1. El objeto se clasifica antes de decidir si constituye un acontecimiento: conservar la publicación no obliga a incluir el hecho alegado.
2. La categoría principal se asigna por la naturaleza inmediata del acontecimiento/hito, no por todas sus consecuencias posibles.
3. La etiqueta transversal se registra separadamente y no crea duplicados.
4. Un dato macro oficial puede ser INCLUIDO por mecanismo potencial sin que se haya observado reacción del mercado.
5. Una solicitud, conversación, desbloqueo, vulnerabilidad o propuesta se registra en su fase real; no se eleva a aprobación, integración, venta, exploit o ejecución.
6. La ausencia de un registro solo respalda una conclusión negativa si se identifica el registro competente, jurisdicción, cobertura y período consultado.
7. Repeticiones de una misma fuente no son corroboración independiente.
8. Los estados de evidencia y las decisiones deben conservar la perspectiva temporal: qué se sabía en la primera detección y qué cambió posteriormente.

## 6. Revisión documental

### Revisión A — consistencia normativa asistida
A: recorrido de los 36 IDs y 10 BND contra los dos documentos normativos; comprobación de objeto, decisión, categoría/familia, evidencia mínima, condición de INDETERMINADO y no-inferencias. Resultado: cobertura íntegra; no se detectaron contradicciones normativas bloqueantes en los casos. La revisión A es asistida; no sustituye H-OWNER. Los controles compensatorios definitivos y sus estados se detallan en §6.4–§6.7.

Comprobaciones aplicadas:
- definición de categoría principal y familia transversal;
- separación publicación/afirmación/acontecimiento/hito;
- salida esperada y evidencia mínima;
- condición explícita de INDETERMINADO;
- no-inferencias y límites de causalidad;
- coherencia con la matriz de los 18 casos del documento de validación.

### Revisión B — revisión adversarial asistida
B: recorrido adversarial separado de los 46 casos, buscando exclusiones por mera ausencia de evidencia, confirmaciones retrospectivas de filtraciones, inferencias de venta/pérdida/exploit/adopción/reacción/causalidad, confusión de hitos, categorías principales incorrectas y duplicación por fuentes repetidas. Resultado: las salidas mantienen las cautelas exigidas; los escenarios con datos insuficientes conducen a INDETERMINADO. No se detectaron defectos bloqueantes adicionales. Esta segunda pasada es del mismo asistente y no constituye revisión independiente.

Pruebas adversariales aplicadas:
- conclusiones EXCLUIR sustentadas únicamente en falta de evidencia;
- inclusión que presuponga confirmación oficial posterior;
- inferencias de venta, pérdida, explotación, adopción, reacción o causalidad;
- clasificación principal por consecuencia y no por hecho inmediato;
- uso de categoría transversal como principal;
- campos desconocidos rellenados implícitamente;
- confusión entre repetición y corroboración.

**Estado de ejecución de revisiones:** las revisiones A y B se ejecutaron sobre los 46 escenarios y sus resultados están resumidos arriba y en la tabla de registro. Son dos pasadas analíticas del mismo asistente, no dos revisores independientes. Por tanto, satisfacen únicamente la revisión asistida interna; la revisión humana del propietario H-OWNER sigue pendiente; no se exige ni se simula una segunda persona independiente para este alcance interno conforme a la política aprobada.

### 6.3 Validaciones programáticas puntuales del documento

Se ejecutaron comprobaciones deterministas sobre el texto recuperado de GitHub desde la rama de trabajo, sin modificar `main`. Resultado: **12/12 comprobaciones aprobadas**.

| Comprobación | Resultado |
|---|---|
| Presencia exacta de los 36 IDs principales, sin duplicados | PASS — 36/36 |
| Correspondencia de los 36 IDs en el registro de aplicación del contrato | PASS — 36/36 |
| Filas de la matriz de trazabilidad | PASS — 18/18 |
| Casos de frontera | PASS — 10/10 |
| Campos obligatorios en las 46 fichas (entrada, salida, evidencia, indeterminación y no-inferencias) | PASS — 46/46 |
| Categoría principal NINGUNA explícita en los 18 escenarios negativos | PASS — 18/18 |
| Identificadores de reglas normativas definidos | PASS — 12/12 |
| Delimitadores de bloques de código Markdown balanceados | PASS |
| Consistencia del número de columnas en las tablas detectadas | PASS — 5 grupos de tablas |
| Existencia de los dos documentos normativos enlazados en `main` | PASS — 2/2 |
| Resolución de enlaces Markdown relativos a documentos locales | PASS — 4/4 |
| Salidas separadas A/B en BND-09 | PASS |

**Límites de esta validación histórica:** las 12 comprobaciones fueron puntuales sobre el contenido descargado y no equivalen a la suite versionada añadida ahora ni a una validación semántica completa de Markdown. La nueva suite y el validador todavía no se han ejecutado en un entorno Python disponible. No se ejecutó `markdownlint`, no se ejecutó `git diff --check` en un clon local y no se creó ni modificó workflow CI. La consulta de GitHub Actions para el commit de validación no devolvió ejecuciones asociadas. El Issue excluye expresamente implementar CI en este alcance.

## 7. Registro de revisión y discrepancias

| Revisión | Responsable/tipo | Alcance | Resultado | Evidencia |
|---|---|---|---|---|
| A | Asistente — revisión de consistencia interna | 36 casos + 10 fronteras | COMPLETADA; no cuenta como revisión humana independiente | Recorrido normativo descrito en §6 |
| B | Mismo asistente — revisión adversarial separada | 36 casos + 10 fronteras | COMPLETADA; no cuenta como revisión humana independiente ni es independiente de A | Recorrido adversarial descrito en §6 |
| H-OWNER | Propietario — revisión humana | 36 casos + 10 fronteras | PENDIENTE | Debe registrar decisión, evidencia, fecha, SHA y discrepancias por ID |
| AI-ADVERSARIAL | Asistente — revisión adversarial asistida | 36 casos + 10 fronteras | COMPLETADA para SHA `60e66f919b88148c05348a27f185b64eba2c6c77`; no independiente | Revisadas cobertura, contratos, exclusiones, indeterminación, temporalidad, clasificación y gobernanza; A/B históricas conservadas |
| AUTO-VALIDATION | Scripts deterministas versionados | Cobertura, contratos, estructura y enlaces | PENDIENTE de ejecución reproducible | Registrar commit, versión Python, comandos, salida y código de retorno |
| ADVERSARIAL-TEST | Tests de mutación M-01…M-12 | Fixtures aislados | PENDIENTE de ejecución | Cada mutación requiere oráculo y resultado; manual review si no automatizable |

Las discrepancias se registrarán por ID, decisión inicial, regla/evidencia en conflicto, resolución y cambio aplicado. No se forzará consenso cuando la salida correcta sea INDETERMINADO.

### 7.1 Registro H-OWNER — revisión humana del propietario

Este registro está deliberadamente pendiente. Debe completarlo el propietario tras revisar personalmente cada caso. La aprobación de la política no equivale a haber revisado los 46 escenarios.

| ID | Decisión H-OWNER | Evidencia/observación | Discrepancia y resolución | Fecha | Estado |
|---|---|---|---|---|---|
| MAC-P | APROBAR CON LA MEJORA PROPUESTA | Decisión expresa del propietario: aprueba el escenario con la mejora recomendada de contemplar también decisiones de mantener tipos cuando la orientación o comunicación modifica expectativas. Observaciones: ninguna. | Mejora incorporada como requisito de redacción; no se registra discrepancia adicional. | 2026-11-14 | REGISTRADA; revisión realizada sobre commit `024de6ab1b23a2db6a4f2b390a44ce85c5b0a5df` |
| MAC-N | APROBAR CON LA MEJORA PROPUESTA | Decisión expresa del propietario: aprueba el escenario con la mejora recomendada de evaluar por separado la posible relevancia de una nueva difusión cuando aporte información material, cambie la atribución, el contexto o el alcance. Observaciones: ninguna. | Mejora incorporada como requisito de redacción; no se registra discrepancia adicional. | 2026-11-14 | REGISTRADA; revisión realizada sobre commit `024de6ab1b23a2db6a4f2b390a44ce85c5b0a5df` |
| ECO-P | APROBAR CON LA MEJORA PROPUESTA | Decisión expresa del propietario: aprueba el escenario con la mejora recomendada de registrar valor publicado, consenso previo si existe, valor anterior y revisiones, sorpresa macroeconómica cuando sea comparable, contexto de expectativas, mecanismo de transmisión potencial a cripto y reacción observada separada. La falta de consenso no excluye el acontecimiento; se registra DESCONOCIDO. Observaciones: ninguna. | Mejora incorporada como requisito de redacción; no se registra discrepancia adicional. | 2026-11-14 | REGISTRADA; revisión del escenario realizada sobre commit `024de6ab1b23a2db6a4f2b390a44ce85c5b0a5df` |
| ECO-N | APROBAR CON LA MEJORA PROPUESTA | Decisión expresa del propietario: aprueba el escenario con la mejora de limitar la exclusión al alcance geográfico, económico y temporal evaluado; examinar canales directos, indirectos y efectos de segundo orden; documentar canales examinados y evidencia; utilizar INDETERMINADO cuando falte información decisiva; permitir reclasificación ante nueva evidencia. Observaciones: ninguna. | Mejora incorporada como requisito de redacción; la ausencia de conexión identificada no se tratará como prueba absoluta de inexistencia. | 2026-11-14 | REGISTRADA; revisión realizada sobre el contenido del escenario disponible en el blob `8c8785c10d8b5ab5985f2ca86cd3252381e03a17` |
| REG-P | APROBAR CON LA MEJORA PROPUESTA | Decisión expresa del propietario: aprueba el escenario con la mejora de registrar autoridad competente, jurisdicción, texto y versión oficial, fase procedimental exacta, plazos y consultas, sujetos/activos/servicios afectados, posibles efectos directos e indirectos y respuestas o modificaciones posteriores; distinguir siempre propuesta de obligación vigente. Observaciones: ninguna. | La existencia de una propuesta puede modificar expectativas aunque no llegue a aprobarse; no inferir aprobación, vigencia ni consecuencias ciertas. | 2026-11-14 | REGISTRADA; revisión realizada sobre el contenido del escenario disponible en el blob `9b762d94956e94480067dabf51b4592b4c97072f` |
| REG-N | APROBAR CON LA MEJORA PROPUESTA | Decisión expresa del propietario: aprueba el escenario con la mejora de identificar funcionario, cargo, autoridad y competencia; conservar declaración original, fecha, contexto y fuente; distinguir opinión personal, comentario institucional, intención política y anuncio formal; verificar expedientes o procedimientos oficiales; no atribuir decisiones no anunciadas; admitir señal anticipatoria solo con evidencia suficiente y vincular acontecimientos posteriores sin fusionar registros. Observaciones: ninguna. | La declaración puede ser señal anticipatoria, pero no acredita por sí sola una actuación regulatoria formal ni su futura adopción. | 2026-11-14 | REGISTRADA; revisión realizada sobre el contenido del escenario disponible en el blob `e9e243726d8d5d1e9c793d46c75291427a784b69` |
| ETF-P | APROBAR CON LA MEJORA PROPUESTA | Decisión expresa del propietario: aprueba el escenario con la mejora de identificar producto, emisor, solicitante, bolsa, subyacente, autoridad y jurisdicción; distinguir solicitud, revisión, aplazamiento, aprobación, rechazo, autorización de negociación y lanzamiento; registrar fechas y condiciones; no inferir demanda ni flujos; analizar activos relacionados y expectativas previas cuando haya evidencia. Observaciones: ninguna. | Aprobación regulatoria, lanzamiento, entradas de capital y efecto sobre el precio son hechos distintos; no inferir unos de otros. | 2026-11-14 | REGISTRADA; revisión realizada sobre el contenido del escenario disponible en el blob `f6e18435eeac5d30822ceaa496f20ea310a6c3f8` |
| ETF-N | APROBAR CON LA MEJORA PROPUESTA | Decisión expresa del propietario: aprueba el escenario con la mejora de identificar publicación original, autor, fecha, gestora, producto, activo y jurisdicción; consultar registros oficiales y documentar fuentes, momento y resultado; distinguir ausencia de evidencia de evidencia de inexistencia; conservar afirmaciones relevantes pendientes de verificación y actualizar ante nueva evidencia; vincular movimientos de precio sin presumir causalidad. Observaciones: ninguna. | Una búsqueda sin resultados no demuestra que la solicitud no exista; el estado debe ser INDETERMINADO cuando la cobertura de fuentes sea insuficiente. | 2026-11-14 | REGISTRADA; revisión realizada sobre el contenido del escenario disponible en el blob `030a09679e5aaee305515dfea7a60e7a758c63a1` |
| INS-P | APROBAR CON LA MEJORA PROPUESTA | Decisión expresa del propietario: aprueba el escenario con la mejora de identificar entidad, relaciones corporativas y fuente primaria; distinguir operaciones ejecutadas, transferencias, compromisos, autorizaciones e intenciones; registrar cantidad, precio y fecha solo con evidencia; separar tenencia directa e indirecta; comprobar novedad frente a expectativas; evitar doble conteo; documentar incertidumbre de titularidad, custodia y atribución; separar hecho de hipótesis de impacto. Observaciones: ninguna. | Una transferencia a una dirección atribuida no demuestra por sí sola compra, titularidad económica ni control por la entidad. | 2026-11-14 | REGISTRADA; revisión realizada sobre el contenido del escenario disponible en el blob `b436e12bbf34c3b6a7e17fdc2d733d0dc7c2994f` |
| INS-N | APROBAR CON LA MEJORA PROPUESTA | Decisión expresa del propietario: aprueba el escenario con la mejora de identificar ejecutivo, cargo y capacidad de comprometer a la empresa; conservar declaración original, fecha, medio y contexto; distinguir interés personal, exploración, intención, propuesta interna y decisión formal; verificar autorizaciones y comunicaciones posteriores cuando existan; no inferir operaciones ni cantidades; vincular declaraciones y operaciones posteriores sin fusionarlas; evaluar novedad informativa. Observaciones: ninguna. | Las declaraciones anticipatorias pueden afectar expectativas sin demostrar compra ni decisión corporativa aprobada. | 2026-11-14 | REGISTRADA; revisión realizada sobre el contenido del escenario disponible en el blob `e4e04eda56dc8352222d023b152a51851ec88f9f` |
| COM-P | APROBAR CON LA MEJORA PROPUESTA | Decisión expresa del propietario: aprueba el escenario con la mejora de identificar partes y relaciones corporativas; distinguir contrato firmado, memorando, piloto, alianza y anuncio; registrar productos, servicios, redes, activos, territorio, alcance, duración y condiciones; diferenciar anuncio, integración, lanzamiento y uso efectivo; verificar exclusividad y compromisos; analizar canales potenciales sin presumir beneficios; evitar duplicados y registrar cancelaciones, cambios o retrasos. Observaciones: ninguna. | La comunicación comercial no demuestra por sí sola implementación, adopción, volumen ni impacto económico material. | 2026-11-14 | REGISTRADA; revisión realizada sobre el contenido del escenario disponible en el blob `385e2c3057ecb59fa6991df1a616ca818e16a4a1` |
| COM-N | PENDIENTE | — | — | — | PENDIENTE |
| EXC-P | PENDIENTE | — | — | — | PENDIENTE |
| EXC-N | PENDIENTE | — | — | — | PENDIENTE |
| TEC-P | PENDIENTE | — | — | — | PENDIENTE |
| TEC-N | PENDIENTE | — | — | — | PENDIENTE |
| GEO-P | PENDIENTE | — | — | — | PENDIENTE |
| GEO-N | PENDIENTE | — | — | — | PENDIENTE |
| DeFi-P | PENDIENTE | — | — | — | PENDIENTE |
| DeFi-N | PENDIENTE | — | — | — | PENDIENTE |
| Stablecoins-P | PENDIENTE | — | — | — | PENDIENTE |
| Stablecoins-N | PENDIENTE | — | — | — | PENDIENTE |
| Tokenomics-P | PENDIENTE | — | — | — | PENDIENTE |
| Tokenomics-N | PENDIENTE | — | — | — | PENDIENTE |
| Minería-P | PENDIENTE | — | — | — | PENDIENTE |
| Minería-N | PENDIENTE | — | — | — | PENDIENTE |
| Gobernanza-P | PENDIENTE | — | — | — | PENDIENTE |
| Gobernanza-N | PENDIENTE | — | — | — | PENDIENTE |
| Custodia-P | PENDIENTE | — | — | — | PENDIENTE |
| Custodia-N | PENDIENTE | — | — | — | PENDIENTE |
| Ciberseguridad-P | PENDIENTE | — | — | — | PENDIENTE |
| Ciberseguridad-N | PENDIENTE | — | — | — | PENDIENTE |
| Materias primas/energía/tecnología-P | PENDIENTE | — | — | — | PENDIENTE |
| Materias primas/energía/tecnología-N | PENDIENTE | — | — | — | PENDIENTE |
| Filtraciones-P | PENDIENTE | — | — | — | PENDIENTE |
| Filtraciones-N | PENDIENTE | — | — | — | PENDIENTE |
| BND-01 | PENDIENTE | — | — | — | PENDIENTE |
| BND-02 | PENDIENTE | — | — | — | PENDIENTE |
| BND-03 | PENDIENTE | — | — | — | PENDIENTE |
| BND-04 | PENDIENTE | — | — | — | PENDIENTE |
| BND-05 | PENDIENTE | — | — | — | PENDIENTE |
| BND-06 | PENDIENTE | — | — | — | PENDIENTE |
| BND-07 | PENDIENTE | — | — | — | PENDIENTE |
| BND-08 | PENDIENTE | — | — | — | PENDIENTE |
| BND-09 | PENDIENTE | — | — | — | PENDIENTE |
| BND-10 | PENDIENTE | — | — | — | PENDIENTE |

### 7.2 Registro AI-ADVERSARIAL y AUTO-VALIDATION

Se aplica el modelo **SINGLE-HUMAN REVIEW WITH COMPENSATING CONTROLS**, aprobado por el propietario e integrado mediante PR #31. Este modelo compensatorio no equivale a dos revisiones humanas independientes. La revisión A/B histórica se conserva como evidencia asistida ya realizada, no independiente. La revisión adversarial final se registró el 2026-11-14 contra el SHA `60e66f919b88148c05348a27f185b64eba2c6c77`, con alcance de 46/46 casos. Se comprobaron cobertura, contratos, salidas, categorías NINGUNA en negativos, INDETERMINADO, evidencia, no-inferencias, temporalidad, etiquetado transversal y prohibición de falsa independencia. Resultado: no se detectaron defectos bloqueantes adicionales en la revisión documental. Esta revisión es asistida por el mismo asistente; no es humana ni independiente y no valida la verdad de fuentes externas. Estado: **COMPLETADA — ASSISTED, NOT INDEPENDENT**.

Se incorporan el validador `scripts/news_and_events/validate_taxonomy_test_cases.py` y su suite `tests/news_and_events/test_taxonomy_test_cases_validation.py`, bajo la [política de revisión de participante único](../governance/single-human-review-control.md). Requieren Python 3.10 o superior y utilizan exclusivamente la biblioteca estándar. Comandos canónicos:

```bash
python -m unittest discover -s tests/news_and_events -v
python scripts/news_and_events/validate_taxonomy_test_cases.py
```

Las pruebas de mutación M-01…M-12 deben demostrar que cada fixture defectuoso es rechazado por su oráculo. Un defecto semántico no automatizable se marca MANUAL_REVIEW_REQUIRED, nunca PASS automático. No se declara ejecutado ningún comando hasta registrar realmente su salida.

Estados de conformidad permitidos:

- `PASS — SINGLE-HUMAN COMPENSATING CONTROLS`: únicamente cuando H-OWNER, AI-ADVERSARIAL, AUTO-VALIDATION y ADVERSARIAL-TEST estén ejecutados, documentados y sin defectos bloqueantes.
- `PASS WITH LIMITATION — EXTERNAL REVIEW PENDING`: controles compensatorios ejecutados, pero una revisión externa exigible o recomendada para el uso previsto sigue pendiente; el uso afectado no se autoriza si la revisión es obligatoria.
- `NOT CONFORMANT`: falta un control obligatorio o existe un defecto bloqueante.
- `INDEPENDENT HUMAN REVIEW VERIFIED`: reservado exclusivamente a dos personas humanas distintas, con identidades y evidencias separadas verificables. No se asigna en este proyecto mientras no existan esas dos revisiones.

La aprobación del propietario de la política no es una revisión de los 46 casos ni una revisión externa. A/B son dos pasadas del mismo asistente y no equivalen a dos revisiones humanas independientes.

### 7.3 Registro de riesgo residual

| Riesgo | Estado inicial | Control | Evidencia de cierre |
|---|---|---|---|
| R-01 Sesgo de confirmación | ABIERTO | H-OWNER + AI-ADVERSARIAL + mutaciones | 46 decisiones y resultados adversariales |
| R-02 Omisión de cobertura | CONTROLABLE | Validador de IDs, pares y matriz | Salida AUTO-VALIDATION |
| R-03 Contradicción estructural | CONTROLABLE | Contratos y reglas deterministas | Tests positivos y negativos |
| R-04 Evidencia insuficiente | ABIERTO | Revisión de INDETERMINADO | Justificación H-OWNER y casos adversariales |
| R-05 Confusión temporal/ontológica | ABIERTO | Revisión de objetos/fechas y fixtures | Resultados de pruebas y registro por ID |
| R-06 Falsa independencia | CONTROLADO POR POLÍTICA | Roles separados; no falsear independencia | A/B conservadas; H-OWNER identificada |
| R-07 Falsa reproducibilidad | CONTROLABLE | Scripts, comandos y salidas versionados | Commit, versión Python, salida y código de retorno |

**Estado actual:** la política está integrada; H-OWNER, revisión adversarial final y pruebas automatizadas/mutacionales aún no se declaran completadas.

## 8. Límites y supuestos

- Los escenarios son sintéticos y prueban reglas documentales; no afirman que los hechos hayan ocurrido.
- No se mide rendimiento predictivo, precisión, recall, impacto, intensidad, duración ni probabilidad.
- No se implementa búsqueda/captura de noticias, evaluación de fuentes, detección automática de filtraciones, deduplicación, grafo, clasificador, ranking, señales ni CI.
- No se demuestra causalidad entre acontecimientos y precios.
- La ausencia de datos se conserva como desconocida; la evidencia necesaria depende de la jurisdicción, protocolo, entidad y fase.
- Los ejemplos no sustituyen el juicio documentado ni autorizan ampliar el alcance de la taxonomía.

## 9. Criterios de conformidad para este documento

- [x] Se enumeran los 36 IDs originales: un positivo y un negativo por cada una de las 18 filas.
- [x] Se enumeran los 10 casos BND-01 a BND-10.
- [x] Cada escenario contiene entrada/objeto, decisión, clasificación, evidencia mínima, condición de indeterminación y no-inferencias.
- [x] Los casos transversales exigen etiqueta de familia además de categoría principal.
- [x] Se aplican las correcciones normativas de ECO-P, ETF-N, INS-N, Custodia-N, Filtraciones-P, Tokenomics-N y Minería-N.
- [x] Se distinguen publicación, afirmación, acontecimiento e hito.
- [x] Se explicita EXCLUIR frente a INDETERMINADO.
- [x] Revisión A y B asistidas completadas y registradas históricamente; no equivalen a revisores humanos independientes.
- [x] Política de participante único aprobada e integrada mediante PR #31; no se afirma independencia humana.
- [ ] H-OWNER completada para los 46 casos con evidencia por ID.
- [ ] AI-ADVERSARIAL final registrada para el SHA candidato.
- [ ] AUTO-VALIDATION versionada ejecutada y con salida reproducible.
- [ ] Pruebas adversariales M-01…M-12 ejecutadas o justificadas como MANUAL_REVIEW_REQUIRED.
- [x] Referencias internas a los dos documentos normativos comprobadas contra los archivos existentes en `main`.
- [x] Comprobaciones programáticas puntuales de estructura y cobertura ejecutadas sobre el contenido recuperado de la rama; alcance y límites registrados en §6.3.
- [ ] Markdown lint y validaciones CI del repositorio ejecutadas; no se declaran como realizadas.

## 10. Referencias

- [Issue #1 — Definir taxonomía y cobertura de catalizadores](https://github.com/Osleyder1985/SINAYXA/issues/1)
- [Issue #29 — Completar pruebas positivas y negativas de la taxonomía](https://github.com/Osleyder1985/SINAYXA/issues/29)
- [Taxonomía de catalizadores](catalyst-taxonomy.md)
- [Matriz de resultados esperados](catalyst-taxonomy-validation.md)
