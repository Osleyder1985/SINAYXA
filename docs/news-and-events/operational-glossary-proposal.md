# Glosario operativo: acontecimientos y catalizadores

**Issue:** [#13 — Aprobar definiciones operativas de acontecimiento y catalizador](https://github.com/Osleyder1985/SINAYXA/issues/13)  
**Estado:** propuesta técnica pendiente de decisión expresa del propietario. No sustituye ni modifica la taxonomía aprobada.  
**Ámbito:** semántica del módulo Noticias y acontecimientos. No define captura, persistencia, scoring, alertas ni predicción.

## 1. Definiciones normativas propuestas

### Acontecimiento

Hecho, decisión, cambio, incidente o hito identificable que ocurre, se materializa o alcanza un estado verificable en un momento o intervalo temporal. Puede ser pasado, estar en desarrollo o estar programado para el futuro.

Un acontecimiento debe poder distinguirse de las publicaciones que lo describen y de las afirmaciones que se hacen sobre él. Cuando un proceso tenga fases materialmente diferentes (solicitud, aprobación, entrada en vigor, ejecución, cancelación o resultado), cada fase constituye un hito diferenciado, relacionado con el proceso, y no una reescritura de los hitos anteriores.

### Catalizador

Acontecimiento —o proceso con uno o más hitos identificables— que, según evidencia disponible, tiene un mecanismo de transmisión plausible y documentable capaz de modificar expectativas, restricciones, incentivos, acceso, liquidez, oferta, demanda, riesgo o actividad económica relevante para uno o varios criptoactivos o para el mercado cripto agregado.

La condición de catalizador expresa **relevancia potencial**, no demuestra que el precio haya reaccionado ni que el acontecimiento haya causado un movimiento. La evaluación debe poder resultar positiva, negativa, mixta, neutral o indeterminada; no se presupone dirección.

### Noticia o publicación

Pieza de contenido difundida por una fuente (artículo, comunicado, publicación, documento, entrevista, registro o actualización) que informa, interpreta, anticipa o comenta una afirmación o acontecimiento. Una noticia no es automáticamente un acontecimiento: varias publicaciones pueden referirse al mismo acontecimiento, y una publicación puede contener varias afirmaciones o referirse a varios hitos.

### Hecho observado

Proposición concreta respaldada por evidencia identificable cuyo alcance no excede lo que la evidencia demuestra. Debe registrarse separada de interpretaciones, hipótesis y consecuencias potenciales.

### Afirmación

Proposición atribuida a una persona, entidad, documento o fuente. Puede ser verdadera, falsa, incompleta, ambigua o no verificable. La atribución acredita quién sostiene la afirmación, no la veracidad de su contenido.

### Indicio

Dato o señal pública, identificable y fechable que es compatible con una hipótesis sobre un acontecimiento, pero que por sí solo no la confirma. Debe indicarse qué hipótesis apoya, qué otras explicaciones son posibles y qué evidencia falta.

### Rumor

Afirmación circulante sobre un hecho pasado, actual o futuro cuya procedencia o evidencia no alcanza el estándar de corroboración requerido. La repetición, popularidad o coincidencia con movimientos de precio no eleva su estado probatorio.

### Filtración

Divulgación no oficial de información, documento o contenido que se presenta como no publicado oficialmente o como obtenido antes de su comunicación pública prevista. La etiqueta describe el carácter atribuido a la divulgación, no autentica el documento ni confirma su contenido. Deben conservarse la pieza, procedencia conocida, fecha de publicación/detección, atribución, autenticidad conocida y estado de corroboración. No se debe solicitar, adquirir ni incorporar material obtenido ilícitamente; el registro se limita a evidencia pública y acceso legítimo.

### Acontecimiento programado

Acontecimiento futuro anunciado o registrado en una fuente identificable con fecha o ventana temporal prevista (por ejemplo, publicación de datos, votación, vencimiento, lanzamiento o decisión calendarizada). La programación no prueba que vaya a ocurrir, ni que se ejecute en la fecha prevista. Cancelaciones, aplazamientos y cambios son hitos propios.

### Hipótesis de impacto

Explicación falsable y trazable de cómo un acontecimiento podría afectar a un activo o al mercado, indicando mecanismo, condiciones, horizonte cuando pueda justificarse, evidencia favorable, evidencia contraria y alternativas. No es un hecho ni una conclusión causal.

## 2. Separaciones obligatorias

| Concepto | Qué acredita | Qué no acredita |
| --- | --- | --- |
| Publicación/noticia | Que existe una pieza difundida en una fecha y por una fuente atribuible | Que su contenido sea verdadero o que exista un acontecimiento nuevo |
| Afirmación | Que una fuente sostiene una proposición | Que la proposición esté confirmada |
| Indicio | Que existe una señal compatible con una hipótesis | Que la hipótesis sea cierta |
| Rumor | Que circula una afirmación no suficientemente corroborada | Que el hecho haya ocurrido o vaya a ocurrir |
| Filtración | Que se presenta una divulgación como no oficial/anticipada | Autenticidad, legalidad de obtención o veracidad del contenido |
| Acontecimiento programado | Que existe una programación anunciada o registrada | Que el acontecimiento vaya a materializarse |
| Hecho observado | Que la evidencia respalda una proposición concreta | Causalidad sobre el precio o consecuencias no observadas |
| Catalizador | Que existe relevancia potencial mediante un mecanismo documentable | Reacción de mercado, dirección, magnitud o causalidad demostrada |

## 3. Regla operativa de inclusión

Un registro puede entrar en el universo de investigación cuando cumpla al menos una de estas condiciones:

1. Existe evidencia identificable de un acontecimiento ya materializado o en desarrollo.
2. Existe una programación futura atribuible a una fuente identificable.
3. Existe una afirmación anticipatoria, indicio o posible filtración pública, identificable y fechable, cuyo contenido concreto permite formular una hipótesis investigable.

Para clasificarlo como **catalizador potencial**, además debe poder describirse un mecanismo plausible de transmisión hacia criptoactivos o el mercado cripto. Si no se puede describir sin especulación, se conserva como información no evaluable o se excluye del conjunto de catalizadores, según su naturaleza y la evidencia disponible.

No se establecen umbrales numéricos, puntuaciones ni probabilidades en este glosario. Las dimensiones de materialidad, intensidad y horizonte requieren decisiones metodológicas separadas (#14 y otros Issues).

## 4. Reglas de clasificación

- La categoría principal representa la naturaleza inmediata del acontecimiento, no la consecuencia más llamativa ni la hipótesis de impacto.
- Se permite una categoría principal y cero o más categorías secundarias justificadas por dimensiones materiales del mismo hecho.
- Una publicación repetida por varios medios no crea acontecimientos duplicados.
- Una afirmación nueva sobre el mismo asunto no crea automáticamente un nuevo acontecimiento; sí puede crear una nueva observación o actualización de evidencia.
- Un cambio de estado verificable (por ejemplo, solicitud → aprobación) es un hito nuevo relacionado, no una modificación retroactiva del registro anterior.
- Si la evidencia no permite decidir, el resultado es INDETERMINADO / EVIDENCIA INSUFICIENTE; no se fuerza una categoría ni se completa información ausente.
- Un vínculo temporal entre acontecimiento y precio no demuestra causalidad. Deben mantenerse separadas reacción observada, hipótesis explicativa y atribución causal.



## 4.1 Evaluación de relevancia económica

La relevancia debe justificarse mediante una cadena explícita y revisable, no mediante la notoriedad de la noticia ni por una variación de precio observada:

1. **Exposición:** identificar el activo, protocolo, entidad, infraestructura, jurisdicción o segmento de mercado potencialmente afectado. Si no existe una exposición identificable, no se presume relevancia para un criptoactivo concreto.
2. **Mecanismo:** describir cómo el acontecimiento podría transmitir efectos (por ejemplo, cambios en acceso/custodia, disponibilidad de negociación, oferta circulante, demanda, costes, seguridad, marco jurídico, liquidez o restricciones operativas).
3. **Condiciones:** indicar qué debe cumplirse para que el mecanismo opere y qué hechos podrían impedirlo. Una relación meramente temática o una mención de marca no constituye mecanismo.
4. **Alcance:** distinguir entre impacto directo sobre un activo, impacto indirecto sobre un ecosistema y posible efecto sobre el mercado agregado. No extender a todo el mercado una exposición limitada.
5. **Horizonte:** indicar el horizonte solo cuando pueda justificarse con la naturaleza del mecanismo y la evidencia temporal. Si no puede determinarse, consignar indeterminado; no asignar una ventana arbitraria.
6. **Contraste:** registrar evidencia favorable, evidencia contraria, explicaciones alternativas y datos ausentes. La conclusión puede ser relevante, no relevante o indeterminada.

La materialidad cuantitativa, las escalas de intensidad y los umbrales de clasificación quedan fuera de este Issue y requieren decisiones específicas. Tampoco se inferirá relevancia por el tamaño de un movimiento de precio posterior.

## 4.2 Identidad, agrupación y deduplicación de acontecimientos

La unidad conceptual de agrupación es el **mismo hecho o proceso subyacente**, no la publicación ni la afirmación individual. Para decidir si dos registros pertenecen al mismo acontecimiento se compararán, cuando estén disponibles:

- sujeto o entidad principal afectada;
- acción, decisión o cambio concreto;
- objeto o ámbito afectado;
- jurisdicción/protocolo/mercado pertinente;
- estado o hito del proceso;
- tiempo de ocurrencia o vigencia, diferenciándolo del tiempo de publicación y del tiempo de detección.

Dos publicaciones que describen el mismo hecho y el mismo hito se vinculan a un acontecimiento común, aunque difieran en titular, idioma o interpretación. No se fusionarán automáticamente cuando exista diferencia material en sujeto, acción, objeto, jurisdicción, estado o intervalo temporal.

Una actualización que aporta evidencia adicional sobre el mismo hito se registra como nueva observación o publicación relacionada. Una transición verificable de estado (por ejemplo, propuesta → aprobada → vigente → ejecutada) se representa como hito distinto dentro del mismo proceso, conservando los hitos anteriores. Una rectificación no borra el registro previo: se relaciona con él y deja trazabilidad de la corrección.

Si la identidad no puede resolverse con la evidencia disponible, los registros permanecen provisionalmente separados y relacionados como posible duplicado; no se fuerza una fusión irreversible. Esta regla es semántica y no define todavía claves técnicas, algoritmos de matching ni ventanas temporales.

## 5.1 Casos límite y tratamiento conservador

| Caso | Tratamiento propuesto | Límite que debe respetarse |
| --- | --- | --- |
| Documento anticipatorio que luego resulta falso o manipulado | Mantenerlo como publicación/afirmación con estado contradicho o no autenticado; revisar la hipótesis relacionada | No convertir retrospectivamente la falsedad en acontecimiento real |
| Rumor repetido por múltiples cuentas que citan una misma fuente original | Una afirmación de origen con múltiples republicaciones relacionadas | La repetición no constituye corroboración independiente |
| Dos fuentes independientes confirman solo partes distintas de una afirmación | Marcar únicamente los componentes respaldados como parcialmente corroborados | No elevar toda la afirmación a confirmada |
| Fuente oficial anuncia una decisión, pero su entrada en vigor depende de una condición pendiente | Registrar el anuncio/decisión y el estado condicionado; vigilar la condición como hito posterior | No describir como vigente o ejecutada antes de que ocurra |
| Propuesta regulatoria modificada durante su tramitación | Conservar versiones/hitos relacionados y atribuir cada cambio a su fuente | No presentar la versión inicial como texto final |
| Filtración cuya autenticidad no puede comprobarse | Registrar como posible filtración pública, con autenticidad no verificada, solo si el acceso al material es legítimo | No tratar la etiqueta filtración como prueba ni incorporar material ilícito |
| Evento programado que se aplaza o cancela | Registrar el cambio de programación como nuevo hito y mantener la fecha/estado anterior en el historial | No borrar la programación original ni asumir ejecución |
| Una empresa anuncia una alianza sin compromisos, producto o implementación verificables | Registrar la afirmación/anuncio; evaluar catalizador solo si se identifica exposición y mecanismo concreto | No inferir adopción, ingresos o demanda futura |
| Una noticia coincide con un movimiento de precio, pero existen otros factores simultáneos | Mantener la reacción observada y las hipótesis alternativas separadas | No atribuir causalidad por coincidencia temporal |


## 5. Ejemplos positivos y negativos

| Caso | Tratamiento propuesto | Motivo |
| --- | --- | --- |
| Banco central publica una decisión de tipos | Acontecimiento; catalizador potencial si se documenta el canal de transmisión | Decisión identificable y mecanismo macroeconómico plausible |
| Calendario oficial anuncia fecha de desbloqueo | Acontecimiento programado; no equivale a venta | La programación acredita una fecha prevista, no el destino de los tokens |
| Medio identifica una fuente y reporta conversaciones de una compra | Afirmación atribuida/posible indicio; no compra ejecutada | Conversación no demuestra acuerdo ni ejecución |
| Documento público anterior al anuncio oficial anticipa una decisión | Posible filtración o indicio, con estado no confirmado hasta autenticación/corroboración | La anticipación no elimina incertidumbre |
| Diez medios reproducen el mismo comunicado | Un acontecimiento y múltiples publicaciones | Repetición no es independencia ni multiplicidad de hechos |
| Una celebridad menciona Bitcoin sin acción, decisión o canal económico identificable | Excluir como catalizador | La mención aislada no establece relevancia |
| BTC sube y luego se publica una noticia | No inferir que la noticia causó la subida | Secuencia temporal no prueba causalidad |
| Se anuncia una propuesta regulatoria | Acontecimiento/proceso en estado de propuesta | No describir como norma aprobada o vigente |
| Un exchange anuncia suspensión de retiros | Acontecimiento; catalizador potencial si la afectación y exposición se pueden documentar | Cambio operativo con mecanismo plausible de riesgo/acceso |

## 6. Estados probatorios mínimos y preservación

El estado probatorio debe aplicarse a cada afirmación concreta, no globalmente a una noticia o a un acontecimiento con múltiples afirmaciones:

- PRIMARY_EVIDENCE_SUPPORTED: evidencia primaria respalda el alcance exacto de la afirmación.
- ATTRIBUTED_UNCORROBORATED: afirmación atribuida a una fuente identificable sin corroboración suficiente.
- PARTIALLY_CORROBORATED: solo una parte o detalle está respaldado.
- UNVERIFIED: evidencia insuficiente para confirmar o refutar.
- CONTRADICTED_OR_RETRACTED: evidencia posterior contradice la afirmación o la fuente la rectifica/retira; conservar el historial y la atribución.

Estos identificadores son etiquetas semánticas propuestas, no un contrato de API ni una máquina de estados aprobada. No deben implementarse hasta resolver las decisiones de evidencia y ciclo de vida (#15 y #25).

La confirmación de una afirmación no confirma automáticamente todas las afirmaciones de la misma publicación, el acontecimiento completo ni una hipótesis de impacto.

## 7. Decisiones explícitamente reservadas

Este glosario no resuelve:

- escalas, límites temporales, intensidad o dirección (#14);
- estándar detallado de indicios, rumores y filtraciones (#15);
- credibilidad e independencia de fuentes (#16);
- severidad y reglas de alertas (#17);
- latencia y frecuencia de vigilancia (#18);
- comparabilidad histórica (#19);
- medición de reacción y atribución (#20);
- expectativas e impacto descontado (#24);
- estados y caducidad del ciclo de vida (#25);
- relaciones y efectos combinados (#26).

## 8. Criterios de aceptación para el Issue #13

- [ ] El propietario acepta o modifica las definiciones de acontecimiento y catalizador.
- [ ] El propietario acepta o modifica las distinciones entre publicación, hecho, afirmación, indicio, rumor, filtración y acontecimiento programado.
- [ ] Se acepta la regla de relevancia basada en mecanismo documentable, sin inferir causalidad a partir del precio.
- [ ] Se aceptan las reglas de inclusión, exclusión, clasificación múltiple y no duplicación.
- [ ] Los ejemplos positivos y negativos se consideran suficientes y coherentes con la taxonomía existente.
- [ ] Las decisiones reservadas permanecen en sus Issues especializados.

**Gobernanza:** este documento es una propuesta para revisión. Su incorporación a una rama o PR no equivale a decisión humana ni autoriza cerrar el Issue #13. Solo el propietario puede aprobar las definiciones.
