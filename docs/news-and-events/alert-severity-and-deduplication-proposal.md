# Propuesta metodológica: severidad, emisión y deduplicación de alertas

**Issue:** [#17 — Definir umbrales, severidad y deduplicación de alertas](https://github.com/Osleyder1985/SINAYXA/issues/17)  
**Estado:** propuesta pendiente de aprobación expresa del propietario.  
**Consumidor futuro:** requisito funcional de generación de alertas por importancia e impacto potencial.  
**Dependencias metodológicas:** estándar probatorio #15; intensidad y horizontes #14 (pendiente de aprobación); credibilidad e independencia #16 (pendiente de aprobación).  
**Ámbito:** reglas de decisión y ciclo de vida de alertas. No implementa vigilancia, captura, entrega por canales, predicción ni señales de trading.

## 1. Decisiones que se solicitan

Aprobar o modificar expresamente:

1. La separación entre importancia/severidad potencial, urgencia temporal, estado probatorio y confianza/limitaciones de la evaluación.
2. Una taxonomía de severidad descriptiva y sus criterios.
3. Las condiciones para emitir, actualizar, suprimir, agrupar y resolver alertas.
4. La identidad de evento/afirmación usada para deduplicar sin ocultar acontecimientos distintos.
5. El tratamiento de indicios, rumores, filtraciones, contradicciones, desmentidos y cambios de estado.
6. Los umbrales cuantitativos, ventanas de supresión y canales, que no deben fijarse sin evidencia, política operativa y aprobación separada.

## 2. Invariantes probatorios y de seguridad

- Una alerta es una notificación de una evaluación, no una nueva evidencia ni una declaración de verdad.
- Debe mostrar el estado probatorio exacto definido por #15 y nunca sustituirlo por severidad, reputación, confianza o número de fuentes.
- La severidad describe la importancia potencial del acontecimiento para el ámbito/activo y el horizonte indicados; no expresa probabilidad de ocurrencia ni certeza de la información.
- Un rumor o indicio puede merecer una alerta de vigilancia si el riesgo potencial y la urgencia lo justifican, pero debe quedar rotulado de forma visible como no confirmado y no corroborado según corresponda.
- La ausencia de alerta no demuestra que un acontecimiento no exista.
- La repetición, viralidad, número de publicaciones o reacción del precio no incrementan por sí solos severidad ni corroboración.
- No deduplicar por similitud textual únicamente.
- No suprimir una rectificación, desmentido, contradicción o cambio material por una regla de ruido.
- No emitir señales de compra/venta ni recomendaciones financieras.
- No aplicar límites, puntuaciones, ventanas o probabilidades arbitrarias.

## 3. Modelo conceptual: cuatro ejes independientes

Toda decisión de alerta debe conservar cuatro ejes separados:

|Eje|Qué responde|No debe confundirse con|
|---|---|---|
|Severidad|¿Qué importancia potencial tendría el hecho para el activo/ámbito considerado?|Veracidad, probabilidad o certeza|
|Urgencia|¿Cuánto tiempo queda para que la información sea útil o para que ocurra el hito?|Severidad o antigüedad de un hecho pasado|
|Estado probatorio|¿Qué estado tiene la afirmación conforme al estándar #15?|Severidad, popularidad o credibilidad|
|Alcance/incertidumbre|¿Qué activos, componentes, fuentes, límites y alternativas están implicados?|Un score agregado|

La evaluación de #14 puede aportar horizonte e intensidad cuando sea aprobada. Mientras permanezca pendiente, no deben tratarse sus categorías propuestas como contrato operativo. La propuesta #16 tampoco puede considerarse aprobada ni automatizarse.

## 4. Severidad cualitativa propuesta

Se proponen cinco etiquetas para revisión, sin puntuación numérica:

|Nivel propuesto|Criterio general|Tratamiento esperado|
|---|---|---|
|CRÍTICA|Posible afectación inmediata y extraordinaria a la continuidad, integridad, acceso, solvencia, legalidad o funcionamiento esencial del activo/mercado; requiere atención humana prioritaria|Notificación prioritaria solo si existe evidencia suficiente del alcance y una ruta de escalamiento aprobada|
|ALTA|Posible cambio material en fundamentos, disponibilidad, regulación, seguridad, estructura de mercado o exposición del activo|Notificación destacada con evidencia, límites y urgencia|
|MEDIA|Acontecimiento potencialmente relevante, pero de alcance acotado, efecto condicionado o confirmación incompleta|Notificación ordinaria o agrupada si no pierde oportunidad|
|BAJA|Información de contexto, evolución incremental o impacto potencial limitado|Registro y resumen; notificación individual solo si política/canal lo justifica|
|INFORMATIVA|Actualización documental, aclaración, contexto o cambio sin impacto material demostrado|Incorporar al historial; no requiere alerta urgente|

Los niveles son etiquetas operativas propuestas, no afirmaciones de impacto demostrado. Cada nivel exige una justificación vinculada a un mecanismo plausible, alcance, activo afectado, horizonte y evidencia. «CRÍTICA» no significa «verdadera» ni «probable».

### 4.1 Factores para justificar severidad

Evaluar separadamente, sin sumar puntos:

- magnitud potencial del cambio o exposición;
- alcance: activo, protocolo, contraparte, mercado o jurisdicción;
- reversibilidad y duración potencial;
- carácter esencial del servicio o función afectada;
- proximidad del hito o ventana de decisión;
- existencia de medidas de mitigación o alternativas;
- evidencia favorable, evidencia contraria y escenarios alternativos;
- sensibilidad de la conclusión a supuestos no verificados.

No se asigna severidad por precio/volumen posterior ni por cobertura mediática. La reacción de mercado se registra en su propio análisis temporal y no se usa para validar retrospectivamente la alerta.

## 5. Urgencia temporal separada

La urgencia debe derivarse de fechas y ventanas verificables:

- **INMINENTE:** existe un plazo/hito futuro próximo y documentado que requiere atención antes de su ocurrencia.
- **PRÓXIMA:** existe un hito futuro documentado, pero queda margen operativo.
- **SIN_PLAZO_INMEDIATO:** no se identifica un hito futuro próximo; puede ser relevante por su alcance.
- **PASADA:** el acontecimiento ya ocurrió; registrar antigüedad como dato descriptivo, nunca asignar horizonte futuro a partir de esa antigüedad.
- **DESCONOCIDA:** la cronología no puede establecerse con evidencia suficiente.

Estos nombres son propuestas. No se fijan límites en horas/días porque no hay calibración ni aprobación. Un acontecimiento pasado puede seguir siendo importante si sus consecuencias persisten, pero eso requiere evidencia sobre persistencia/estado actual, no usar su antigüedad como urgencia futura.

## 6. Estado probatorio y tratamiento de información no confirmada

La alerta debe reproducir el estado de la afirmación conforme al estándar #15. Como mínimo:

- conservar exactamente el estado vigente;
- enlazar la afirmación y las piezas que lo sustentan;
- identificar fuentes dependientes y desconocidas sin contarlas como corroboración independiente;
- mostrar contradicciones y alternativas relevantes;
- distinguir la publicación oficial de la veracidad de cada afirmación que contiene;
- indicar qué parte del acontecimiento está corroborada y qué parte no.

Reglas propuestas:

1. Un indicio o rumor puede generar una alerta de vigilancia de severidad potencial MEDIA/ALTA/CRÍTICA solo cuando se documente por qué la atención temprana es útil y se explicite que el estado no está confirmado.
2. La severidad no puede elevar el estado probatorio.
3. Una fuente anónima, una publicación viral o una filtración no corroborada no se convierte en confirmada por recibir una alerta.
4. Si no puede justificarse el mecanismo o el alcance, mantener registro sin alerta individual o usar una categoría de observación pendiente de política aprobada.
5. Una contradicción o desmentido relevante debe poder generar una actualización visible, no eliminar la alerta anterior.
6. No mostrar una conclusión más categórica que la evidencia subyacente.

## 7. Emisión: condiciones de decisión propuestas

Emitir una alerta solo si concurren todos estos controles:

1. Existe una afirmación/evento identificable con ID estable y versión.
2. Hay evidencia enlazada y fecha de corte explícita.
3. Se identifica al menos un activo/ámbito afectado o se declara explícitamente que está por determinar.
4. La severidad propuesta tiene justificación específica y no depende solo de popularidad o movimiento de precio.
5. El estado probatorio y la incertidumbre se muestran sin pérdida.
6. La urgencia se justifica con timestamps/hitos o se marca DESCONOCIDA.
7. La alerta no es un duplicado exacto de una emisión previa sin cambio material.
8. La política del canal y del destinatario autoriza el envío.

Si falla un control, el sistema puede conservar el evento en investigación/cola, pero no debe inventar datos para completar la alerta.

## 8. Identidad y deduplicación

La deduplicación se realiza en niveles distintos. No confundir la misma noticia, la misma afirmación y el mismo acontecimiento.

### 8.1 Identidades conceptuales

- **event_id:** identidad del acontecimiento del mundo real, si puede establecerse.
- **claim_id:** proposición concreta sobre el acontecimiento.
- **source_item_id:** publicación, documento o registro exacto.
- **alert_id:** emisión individual, inmutable.
- **alert_group_id:** agrupación de alertas relacionadas para navegación/resumen, sin fusionar evidencia ni afirmaciones.

Una publicación puede contener varias afirmaciones; varias publicaciones pueden referirse a un mismo evento; un evento puede generar afirmaciones contradictorias. Por tanto, una única clave basada en URL o título es insuficiente.

### 8.2 Reglas de deduplicación propuestas

|Caso|Decisión|
|---|---|
|Misma URL y misma versión, reingestada sin cambio|No emitir de nuevo; actualizar metadatos de captura|
|Misma publicación con corrección material/versionado nuevo|Crear actualización vinculada a la alerta previa|
|Varios medios reproducen el mismo cable|Una afirmación/cadena de origen; adjuntar referencias dependientes sin multiplicar alertas|
|Fuentes independientes aportan evidencia nueva sobre la misma afirmación|Actualizar la evaluación de la afirmación y emitir solo si el cambio es material|
|Dos afirmaciones distintas sobre el mismo evento|Mantener claims separados; pueden compartir event_id y alert_group_id|
|Dos eventos similares en fechas o jurisdicciones distintas|No deduplicar como uno; mantener event_id diferentes salvo evidencia de identidad común|
|Rumor y posterior confirmación|Mantener la secuencia de estados y versiones; no borrar la alerta inicial|
|Desmentido de una afirmación|Nueva actualización enlazada; no suprimir la historia previa|
|Citas circulares o republicaciones|Registrar la genealogía; no contar como nueva corroboración|

La coincidencia de texto, símbolo, entidad o ventana temporal solo genera candidatos a agrupación. No basta para fusionar eventos.

### 8.3 Clave candidata y revisión humana

Se propone una clave compuesta conceptual con entidad/activo, tipo de evento, sujeto/objeto, ámbito/jurisdicción, intervalo temporal del hecho y proposición normalizada. La clave no debe calcularse solo con texto libre ni usarse como decisión final irreversible.

- Coincidencia exacta de identificadores y versión: duplicado técnico.
- Coincidencia parcial: candidato a relación, requiere comparación de afirmaciones.
- Identidad de evento incierta: conservar separados y enlazar como relacionados.
- Contradicción material: mantener claims separados, aunque compartan evento.

## 9. Actualizaciones materiales y ciclo de vida

Estados de ciclo de vida propuestos para la alerta, separados del estado probatorio de la afirmación:

- **BORRADOR:** construida, aún no elegible para emisión.
- **EMITIDA:** notificación enviada/registrada.
- **ACTUALIZADA:** existe una nueva versión material; se conserva la anterior.
- **RESUELTA:** la condición de seguimiento definida para la alerta terminó o el evento quedó cerrado según evidencia.
- **SUPRIMIDA:** no se envía por una regla explícita; se conserva motivo, actor, regla y timestamp.
- **CANCELADA:** emisión invalidada por error operativo o duplicación técnica demostrada; nunca usar para ocultar una contradicción o rectificación.

Una actualización material puede estar justificada por:

- cambio del estado probatorio;
- evidencia primaria nueva o corroboración independiente real;
- contradicción/desmentido relevante;
- cambio de alcance, activo afectado o mecanismo;
- cambio de severidad o urgencia con justificación;
- corrección de fecha, importe, entidad o componente material;
- cambio de escenario que altere la evaluación.

No justificar una actualización por un nuevo artículo que solo reproduce lo ya conocido, cambios estilísticos, incremento de menciones o fluctuación de precio sin vínculo probatorio.

Cada emisión/actualización conserva timestamp, versión de evaluación, regla aplicada, evidencias, destinatario/canal, resultado de entrega si existe y relación con alertas anteriores.

## 10. Supresión, agrupación y control de ruido

- La supresión solo aplica a duplicados técnicos o a reglas de política explícitas y aprobadas.
- Nunca suprimir actualizaciones de estado probatorio, desmentidos, rectificaciones o cambios materiales sin registrar una excepción visible.
- Una ventana de silencio/cooldown no puede ocultar una actualización material; debe permitir excepción prioritaria.
- No se fijan ventanas de minutos/horas/días sin datos de volumen, latencia, coste de notificación y riesgo de omisión.
- La agrupación es presentación, no fusión de registros probatorios.
- Una agrupación debe mostrar cantidad de afirmaciones y eventos distintos, y permitir abrir cada uno.
- El resumen no puede convertir varios eventos relacionados en una sola afirmación ni ocultar desacuerdos.

## 11. Ejemplos sintéticos de decisión

Todos los escenarios son ficticios; no constituyen calibración ni pruebas ejecutadas.

|Caso|Entrada|Decisión propuesta|
|---|---|---|
|A01|La misma publicación se captura dos veces sin cambio|Duplicado técnico; no reenviar|
|A02|Tres portales reproducen el mismo cable|Agrupar referencias dependientes; no crear tres corroboraciones|
|A03|Un regulador publica una resolución oficial|Alerta según alcance/urgencia; estado probatorio limitado al acto publicado|
|A04|Aparece rumor no corroborado de vulnerabilidad con posible exposición grave|Posible alerta de vigilancia rotulada NO CONFIRMADA; severidad justificada aparte|
|A05|El rumor recibe un desmentido documentado|Actualización visible; conservar rumor y desmentido con sus fuentes|
|A06|Una fuente independiente aporta documento primario nuevo|Reevaluar afirmación; actualizar si cambia materialmente el estado|
|A07|El precio cae tras una noticia|No elevar severidad ni corroboración por la caída; analizar reacción aparte|
|A08|Dos eventos del mismo tipo afectan a activos distintos|Alertas separadas; posible grupo común|
|A09|Una noticia corrige importe o fecha esencial|Nueva versión/actualización; conservar la anterior|
|A10|Se publica otra nota sin evidencia nueva|No reenviar; adjuntar referencia si aporta contexto|
|A11|Un hito futuro se acerca y el riesgo potencial no cambia|Urgencia puede cambiar con evidencia temporal; severidad no cambia automáticamente|
|A12|Un evento pasado sigue produciendo efectos|Mantener antigüedad separada; nueva alerta solo por evidencia de persistencia/cambio actual|
|A13|Dos claims contradictorios describen el mismo evento|Claims separados, evento relacionado; no resolver por mayoría|
|A14|El sistema no puede determinar si dos publicaciones comparten fuente|Independencia DESCONOCIDA; no deduplicar como corroboración independiente|
|A15|La alerta se suprime por política de canal|Conservar registro, motivo, regla, actor y hora; la supresión no cambia el estado probatorio|

## 12. Umbrales cuantitativos y calibración

No se proponen umbrales numéricos en esta versión porque faltan:

- distribución observada de eventos por fuente, activo y tipo;
- medición de duplicados verdaderos y falsos;
- coste de alertas omitidas frente a ruido;
- latencias de captura, análisis y entrega;
- capacidad operativa y política por canal/destinatario;
- validación fuera de muestra de las reglas.

Antes de fijar thresholds o cooldowns se requiere un conjunto histórico etiquetado, protocolo preregistrado, métricas de precisión/recobrado por clase y análisis de costes. No optimizar solo por reducir notificaciones: una política que silencia eventos críticos puede parecer eficiente y ser insegura.

## 13. Criterios de aceptación propuestos para #17

- [ ] Severidad, urgencia, estado probatorio e incertidumbre son ejes independientes.
- [ ] La taxonomía de severidad tiene criterios y ejemplos observables.
- [ ] Se define la identidad de evento, afirmación, pieza, alerta y grupo.
- [ ] Se distinguen duplicado técnico, republicación, nueva evidencia, nuevo claim y nuevo evento.
- [ ] Se definen cambios materiales que justifican actualización.
- [ ] Rumores, indicios, contradicciones y desmentidos conservan el estado probatorio y su historial.
- [ ] Supresión y agrupación no borran ni fusionan registros probatorios.
- [ ] Umbrales numéricos y cooldowns quedan pendientes de datos y aprobación, sin valores arbitrarios.
- [ ] Los ejemplos A01–A15 se convierten en fixtures sintéticos positivos/negativos/fronterizos tras la aprobación.
- [ ] Cada decisión es auditable: regla, versión, evidencias, timestamps, motivo y actor.
- [ ] El propietario aprueba expresamente la metodología y sus límites.

## 14. Límites pendientes

Esta propuesta no aprueba todavía:

- nombres definitivos de estados/campos;
- umbrales numéricos de severidad, importancia, envío o supresión;
- ventanas de cooldown;
- canales, horarios, destinatarios o escalamiento;
- reglas automáticas de correlación de eventos;
- scoring, probabilidades o modelos predictivos;
- integración con precios, ejecución de órdenes o recomendaciones de trading.

Los umbrales y canales requieren decisiones separadas con evidencia operacional. El documento es una propuesta metodológica; no habilita el requisito funcional de alertas.

## 15. Registro de decisión

**Estado: PROPUESTA NO APROBADA.**

La integración de este documento solo establece una base para revisión. El Issue #17 permanecerá abierto hasta que el propietario resuelva las decisiones metodológicas, apruebe los criterios y se conviertan los ejemplos en pruebas verificables. No se implementarán alertas productivas a partir de esta propuesta sin esa aprobación.
