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

**No corroborada no significa falsa; no confirmada no significa irrelevante; no observada no significa inexistente.** La falta de evidencia suficiente no justifica por sí sola EXCLUIR.

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

## 2. Matriz de trazabilidad de los 36 escenarios

| Fila | Cobertura de Issue #1 | Positivo | Negativo |
|---:|---|---|---|
| 1 | Política monetaria y bancos centrales | MAC-P | MAC-N |
| 2 | Economía mundial y mercados financieros | ECO-P | ECO-N |
| 3 | Regulación, legislación y política pública | REG-P | REG-N |
| 4 | Productos de inversión y acceso regulado | ETF-P | ETF-N |
| 5 | Adopción y actividad institucional o empresarial | INS-P | INS-N |
| 6 | Acuerdos comerciales y financieros | COM-P | COM-N |
| 7 | Exchanges, intermediarios e infraestructura de mercado | EXC-P | EXC-N |
| 8 | Tecnología, protocolos e infraestructura blockchain | TEC-P | TEC-N |
| 9 | Geopolítica y acontecimientos internacionales | GEO-P | GEO-N |
| 10 | DeFi | DeFi-P | DeFi-N |
| 11 | Stablecoins y dinero tokenizado | Stablecoins-P | Stablecoins-N |
| 12 | Tokenomics y oferta | Tokenomics-P | Tokenomics-N |
| 13 | Minería y validación | Minería-P | Minería-N |
| 14 | Gobernanza y estructura de ecosistemas | Gobernanza-P | Gobernanza-N |
| 15 | Custodia, pagos y adopción de infraestructura | Custodia-P | Custodia-N |
| 16 | Ciberseguridad | Ciberseguridad-P | Ciberseguridad-N |
| 17 | Materias primas, energía y tecnología fuera del sector | Materias primas/energía/tecnología-P | Materias primas/energía/tecnología-N |
| 18 | Filtraciones e información anticipatoria | Filtraciones-P | Filtraciones-N |

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
- **Salida:** EXCLUIR como catalizador cripto dentro del alcance evaluado.
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
- **Salida:** EXCLUIR como acontecimiento o avance regulatorio; conservar la declaración atribuida si es trazable.
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
- **Salida:** EXCLUIR la publicación como acontecimiento ETF confirmado; conservarla como contenido especulativo trazable. No declarar falso un expediente que no se haya podido verificar.
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
- **Salida:** EXCLUIR como compra, inversión o adopción ejecutada; conservar la declaración atribuida si es trazable.
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
- **Salida:** EXCLUIR como catalizador EXC.
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
- **Salida:** EXCLUIR como catalizador TEC.
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
- **Salida:** EXCLUIR como catalizador GEO en el contexto evaluado.
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
- **Entrada/objeto:** acontecimiento/observación de mercado. Se observa oscilación transitoria sin evidencia de problema en reservas, redenciones, liquidez, solvencia o funcionamiento.
- **Salida:** EXCLUIR como catalizador stablecoin en el supuesto delimitado; familia stablecoins.
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
- **Entrada/objeto:** acontecimiento/transferencia. Dirección transfiere tokens, sin evidencia de cambio de oferta, venta, distribución, desbloqueo o incentivos.
- **Salida:** EXCLUIR como acontecimiento de tokenomics solo si evidencia suficiente permite establecer que no existe cambio material. Para afirmar movimiento interno, probar control común.
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
- **Entrada/objeto:** acontecimiento/observación de red. El ajuste de dificultad sigue el mecanismo automático previsto y no hay evidencia de cambio anómalo de operación, seguridad, costes o capacidad.
- **Salida:** EXCLUIR como catalizador anómalo solo si la normalidad está acreditada; familia minería/validación.
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
- **Salida:** EXCLUIR como hito de gobernanza; conservar publicación atribuida si es trazable.
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
- **Salida:** EXCLUIR como integración efectiva; si la publicación es trazable, conservarla como afirmación no corroborada y no como servicio disponible.
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
- **Salida:** EXCLUIR como incidente confirmado; conservar alerta y análisis como publicaciones relacionadas.
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
- **Salida:** EXCLUIR como catalizador de esa familia.
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
- **Salida:** EXCLUIR la afirmación como evidencia del acontecimiento alegado; conservar la publicación y rectificación/análisis como objetos separados.
- **Evidencia mínima:** publicación original y análisis del documento o rectificación fiable que demuestre manipulación/atribución falsa.
- **INDETERMINADO si:** solo falta corroboración, la fuente es anónima o no se ha probado falsedad.
- **No inferir:** que una filtración es fabricada por ser anónima o no corroborada.

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
- **Entrada/objeto:** caso A: alerta sin explotación demostrada; caso B: explotación respaldada por evidencia técnica/transaccional.
- **Salida:** A registrar como alerta/vulnerabilidad con estado correspondiente, sin declarar exploit; B INCLUIR como exploit confirmado.
- **Categoría/familia:** TEC principal + familia ciberseguridad; EXC secundaria si afecta a intermediario/infraestructura de mercado.
- **Evidencia mínima:** aviso técnico para A; evidencia reproducible de explotación para B.
- **INDETERMINADO si:** componente, versión, exposición o explotación no pueden resolverse.
- **No inferir:** pérdidas, fondos robados o explotación desde la mera existencia de una vulnerabilidad.

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
A: recorrido de los 36 IDs y 10 BND contra los dos documentos normativos; comprobación de objeto, decisión, categoría/familia, evidencia mínima, condición de INDETERMINADO y no-inferencias. Resultado: cobertura íntegra; no se detectaron contradicciones normativas bloqueantes en los casos. Se mantienen expresamente pendientes la revisión humana independiente y las validaciones automatizadas del repositorio.

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

**Estado de ejecución de revisiones:** las revisiones A y B se ejecutaron sobre los 46 escenarios y sus resultados están resumidos arriba y en la tabla de registro. Son dos pasadas analíticas del mismo asistente, no dos revisores independientes. Por tanto, satisfacen únicamente la revisión asistida interna; la revisión humana independiente exigida por el Issue sigue pendiente.

## 7. Registro de revisión y discrepancias

| Revisión | Responsable/tipo | Alcance | Resultado | Evidencia |
|---|---|---|---|---|
| A | Asistente — revisión de consistencia | 36 casos + 10 fronteras | COMPLETADA; sin defectos bloqueantes detectados | Recorrido normativo descrito en §6 |
| B | Mismo asistente — revisión adversarial separada | 36 casos + 10 fronteras | COMPLETADA; sin defectos bloqueantes adicionales | Recorrido adversarial descrito en §6; no es independiente de A |
| Independiente | Revisor humano distinto | 36 casos + 10 fronteras | PENDIENTE | Requiere revisión externa independiente |

Las discrepancias se registrarán por ID, decisión inicial, regla/evidencia en conflicto, resolución y cambio aplicado. No se forzará consenso cuando la salida correcta sea INDETERMINADO.

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
- [x] Revisión A y B asistidas completadas y registradas; no equivalen a dos revisores humanos independientes.
- [ ] Revisión humana independiente completada.
- [x] Referencias internas a los dos documentos normativos comprobadas contra los archivos existentes en `main`.
- [ ] Validaciones automatizadas/documentales del repositorio ejecutadas; no se declaran como realizadas.

## 10. Referencias

- [Issue #1 — Definir taxonomía y cobertura de catalizadores](https://github.com/Osleyder1985/SINAYXA/issues/1)
- [Issue #29 — Completar pruebas positivas y negativas de la taxonomía](https://github.com/Osleyder1985/SINAYXA/issues/29)
- [Taxonomía de catalizadores](catalyst-taxonomy.md)
- [Matriz de resultados esperados](catalyst-taxonomy-validation.md)
