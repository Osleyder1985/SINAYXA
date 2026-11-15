# Propuesta metodológica: latencia y límites de vigilancia por fuente

**Issue:** [#18 — Establecer objetivos de latencia y límites de vigilancia por fuente](https://github.com/Osleyder1985/SINAYXA/issues/18)  
**Requisito funcional relacionado:** [#7 — Vigilar continuamente las fuentes de información](https://github.com/Osleyder1985/SINAYXA/issues/7)  
**Estado:** propuesta pendiente de aprobación expresa del propietario.  
**Ámbito:** medición y gobernanza de la vigilancia. No implementa captura, polling, streaming, scraping ni alertas.

## 1. Decisiones solicitadas

1. Adoptar una medición descompuesta de latencia, en lugar de una única cifra ambigua.
2. Clasificar los mecanismos de acceso por sus características verificadas: push/webhook/stream, API consultada, feed, página consultada, descarga por lotes y recepción manual.
3. Establecer una ficha versionada de capacidad y restricciones por fuente.
4. Diferenciar objetivos internos, límites publicados por el proveedor y latencias observadas.
5. Definir comportamiento ante rate limits, fallos, retrasos, cambios de términos y pérdida de cobertura.
6. Aprobar objetivos de servicio solo después de medir una muestra representativa y verificar las condiciones de uso.

## 2. Principios no negociables

- «Vigilancia continua» describe el objetivo funcional; no autoriza prometer captura instantánea ni cobertura permanente.
- No acceder a una fuente sin identificar método permitido, términos aplicables, autenticación, límites y restricciones.
- La disponibilidad técnica de un endpoint no equivale a autorización para usarlo.
- No eludir autenticación, paywalls, CAPTCHA, controles anti-bot, límites, bloqueos ni restricciones técnicas.
- No sustituir una fuente por otra sin registrar la pérdida de cobertura y el cambio de procedencia.
- No inferir la hora real de publicación a partir de la hora de captura.
- No presentar una latencia desconocida como cero ni imputar timestamps ausentes.
- Los límites publicados por la fuente prevalecen sobre la frecuencia interna deseada.
- Un fallo de vigilancia debe generar un estado de cobertura degradada; no debe interpretarse como ausencia de acontecimientos.
- Conservar zona horaria, precisión, semántica y procedencia de cada timestamp.

## 3. Modelo de latencia

Registrar por separado los siguientes momentos, cuando existan y sean fiables:

|Métrica|Definición|
|---|---|
|t_event|Momento del acontecimiento real|
|t_publication|Momento en que la fuente publica o hace disponible el elemento|
|t_source_update|Última actualización declarada por la fuente|
|t_first_seen|Primera observación registrada por el sistema|
|t_captured|Finalización de la captura|
|t_processed|Finalización del procesamiento/normalización|
|t_available|Momento en que el registro queda disponible para consumo interno|

Derivaciones:

- Latencia de publicación: t_publication − t_event, solo si ambos tiempos son fiables y comparables.
- Latencia de detección observable: t_first_seen − t_publication.
- Latencia de captura: t_captured − t_first_seen.
- Latencia de procesamiento: t_processed − t_captured.
- Latencia interna total: t_available − t_first_seen.

La diferencia entre acontecimiento y publicación no debe atribuirse al sistema de vigilancia. Si el momento real del acontecimiento no está disponible, la latencia de publicación queda como no cuantificada.

### 3.1 Reglas temporales

- Almacenar timestamps normalizados en UTC y preservar el valor/offset original suministrado por la fuente.
- Registrar precisión y semántica: hora exacta, fecha sin hora, hora aproximada, actualización o captura.
- No convertir una fecha sin hora en una hora ficticia.
- Si los relojes no están sincronizados o los timestamps son incoherentes, marcar la medición como no fiable.
- Mantener separados el momento del hecho, publicación, primera observación y procesamiento.
- Las correcciones de timestamps generan una nueva versión auditable; no sobrescribir la medición original.

## 4. Clasificación de mecanismos

|Mecanismo|Ventaja potencial|Limitación que debe medirse|
|---|---|---|
|Webhook/push|Entrega iniciada por el proveedor|Soporte, autenticación, reintentos, expiración y garantías|
|Stream/API en tiempo real|Puede reducir el intervalo de detección|Cuotas, conexión, reconexión, orden, duplicados y disponibilidad|
|API consultada|Contrato estructurado potencialmente estable|Intervalo, cuotas, paginación y retraso de actualización|
|RSS/Atom/feed|Formato simple|Frecuencia de actualización, caché, omisiones y timestamps|
|Página/portal|Puede cubrir publicaciones sin API|Cambios de estructura, términos, caché y riesgo de bloqueo|
|Descarga por lotes|Adecuada para históricos o publicaciones periódicas|Retraso inherente al lote y ventanas sin datos|
|Recepción manual|Útil cuando no existe automatización autorizada|No constituye vigilancia continua|

La clasificación no implica que estos mecanismos estén disponibles ni permitidos para una fuente concreta.

## 5. Ficha obligatoria por fuente

Cada fuente debe disponer de un registro versionado con:

- source_id estable, proveedor, tipo y ámbito temático/geográfico.
- URL/base endpoint y documentación oficial aplicable.
- Entidad responsable, cuando pueda identificarse.
- Método permitido, autenticación y cuotas.
- Términos, licencia, política de uso y fecha de revisión.
- Restricciones de almacenamiento, retención, transformación y redistribución.
- Condiciones de uso comercial/no comercial y territorio.
- Frecuencia de actualización declarada, si existe.
- Cobertura, exclusiones conocidas, timestamps y zona horaria.
- Procedimiento de cambios/deprecación e incidencias.
- Fecha de última verificación, evidencia documental y responsable.
- Estado de autorización propuesto: AUTHORIZED, CONDITIONAL, PENDING, RESTRICTED o PROHIBITED.
- Estado operativo propuesto: ACTIVE, DEGRADED, PAUSED, UNAVAILABLE o RETIRED.

Los estados propuestos no sustituyen decisiones legales ni los estados probatorios del estándar #15. Si una condición de uso no está clara, la fuente permanece PENDING y no se automatiza.

## 6. Matriz operativa

La matriz fuente/método/frecuencia/latencia/límites debe distinguir:

|Campo|Contenido requerido|
|---|---|
|Fuente y método|Identificador y método autorizado|
|Frecuencia permitida|Límite del proveedor y referencia|
|Frecuencia configurada|Parámetro realmente desplegado|
|Latencia observada|Distribución, periodo y muestra|
|Cobertura|Tipos de publicaciones y exclusiones|
|Límites|Cuotas, términos, disponibilidad y retención|
|Fallos|Errores, frecuencia y duración|
|Estado|Activo, degradado, pausado o no disponible|
|Revisión|Fecha, responsable y evidencia|

Si no hay despliegue o mediciones, utilizar NOT_MEASURED / NOT_CONFIGURED; no rellenar con objetivos hipotéticos.

## 7. Medición y sesgos

Medir por fuente y mecanismo:

- número de observaciones válidas;
- distribución de latencia (mediana, p90, p95 y p99 cuando el tamaño de muestra lo permita);
- latencias de captura y procesamiento por separado;
- disponibilidad observada y periodos de degradación;
- errores, timeouts, respuestas parciales y rate limits;
- elementos omitidos o descubiertos tarde, cuando exista referencia independiente;
- duplicados técnicos y cambios de versión;
- cobertura por tipo de contenido y periodo;
- porcentaje de timestamps ausentes, ambiguos o no fiables.

Publicar N, periodo, zona horaria, exclusiones y método de cálculo. No comparar fuentes con definiciones de timestamp o cobertura incompatibles.

Sesgos a controlar:

- Medir solo elementos detectados produce sesgo de supervivencia y no revela lo que nunca se detectó.
- La hora de primera captura depende del intervalo y disponibilidad del mecanismo.
- Cachés intermedias pueden separar hora observada y hora de publicación.
- Una fuente puede publicar retrospectivamente; conservar fecha del hecho y fecha de publicación.
- Una ventana sin publicaciones no demuestra que el mecanismo esté sano.
- No inferir cobertura completa desde una muestra de páginas o endpoints.

## 8. Frecuencia y objetivos de servicio

No se establece una frecuencia universal. La frecuencia objetivo por fuente debe respetar:

1. términos, licencia, límites y documentación oficial;
2. mecanismo realmente disponible y autorizado;
3. capacidad técnica y coste sostenible;
4. criticidad del contenido para el caso de uso;
5. latencia observada y riesgo de omisión;
6. decisión aprobada y versionada del propietario.

Un objetivo interno es una meta medible, no una garantía del proveedor. Documentar por separado objetivo de detección, disponibilidad, recuperación, cobertura, tolerancia a retrasos y excepciones. Aprobar objetivos después de medir. No asignar valores en segundos/minutos sin evidencia.

## 9. Rate limits, errores y recuperación

- Respetar Retry-After, cuotas y documentación del proveedor.
- Ante rate limit, reducir o detener consultas según las instrucciones; no rotar identidades/IPs para eludir límites.
- Reintentar solo errores transitorios identificados, con política limitada y compatible con el contrato.
- No reintentar indefinidamente errores permanentes, autorización denegada, recurso eliminado o términos pendientes.
- Usar backoff y jitter solo cuando estén permitidos y justificados.
- Mantener checkpoint/cursor cuando la fuente lo soporte y el contrato permita su uso.
- Recuperar el intervalo perdido solo si existe mecanismo histórico autorizado.
- Registrar recuperación completa, parcial o imposible; no rellenar huecos con contenido inferido.
- No declarar ACTIVE hasta comprobar que el mecanismo volvió a entregar datos y evaluar la cobertura.
- Si cambian API, formato, términos o política, pausar el método afectado hasta revisar compatibilidad y autorización.

## 10. Estados de cobertura

Estados operativos propuestos:

- ACTIVE: mecanismo autorizado y comprobaciones recientes satisfactorias.
- DEGRADED: funciona parcialmente, presenta retrasos o cobertura incompleta.
- PAUSED: suspendida por política, mantenimiento o revisión.
- UNAVAILABLE: no se puede acceder o el proveedor está indisponible.
- RETIRED: fuente/método retirado, reemplazado o ya no autorizado.

Cada cambio registra causa, intervalo afectado, evidencia, responsable, impacto en cobertura y recuperación. El consumidor debe distinguir «no se detectaron publicaciones», «no hubo consulta», «fuente no disponible», «captura fallida», «histórico irrecuperable» y «fuente no autorizada». Ninguno equivale a ausencia de acontecimientos.

## 11. Autorización y condiciones de uso

Antes de habilitar una fuente, revisar y conservar evidencia de:

- términos vigentes y fecha/versión;
- permiso para automatización y frecuencia;
- autenticación y cuotas;
- derechos de almacenamiento, retención, transformación y redistribución;
- uso comercial/no comercial y territorio;
- contenido de terceros, atribución y revocación.

La disponibilidad pública no se interpreta como licencia de extracción o redistribución.

## 12. Escenarios sintéticos

Los siguientes casos son ejemplos de diseño, no mediciones ni pruebas ejecutadas:

|Caso|Situación|Respuesta exigida|
|---|---|---|
|L01|API publica límite de consultas|No superar límite; conservar referencia|
|L02|HTTP 429 con Retry-After|Respetar tiempo indicado y registrar degradación|
|L03|Feed se actualiza con retraso|Medir retraso; no atribuirlo al procesamiento interno|
|L04|Fuente no incluye timestamp de publicación|Latencia de detección NOT_MEASURED|
|L05|Fuente deja de responder|UNAVAILABLE/DEGRADED; no reportar ausencia de eventos|
|L06|Recuperación sin endpoint histórico|Registrar intervalo perdido como irrecuperable|
|L07|API cambia formato|Pausar normalización y revisar antes de reanudar|
|L08|Términos prohíben automatización|Pausar hasta revisión/autorización|
|L09|Canales reflejan publicación con retrasos distintos|Conservar procedencia y tiempos por fuente|
|L10|Procesamiento tardío tras captura|Separar latencia de detección y procesamiento|
|L11|Publicación retrospectiva|Conservar fecha del hecho y publicación|
|L12|No hubo publicaciones durante una ventana|Verificar mecanismo; no inferir salud ni ausencia|
|L13|Timestamp sin zona horaria|Marcar ambigüedad; no asignar UTC por suposición|
|L14|Respuesta parcial|Registrar cobertura parcial y checkpoint autorizado|
|L15|Cuota excedida por error de configuración|Detener/reducir según proveedor y registrar incidente|

## 13. Criterios de aceptación propuestos

- [ ] Latencias de publicación, detección, captura, procesamiento y disponibilidad separadas.
- [ ] Timestamps conservan semántica, zona horaria, precisión y procedencia.
- [ ] Cada fuente tiene ficha versionada de autorización, método, límites y cobertura.
- [ ] La matriz distingue frecuencia permitida, configurada y observada.
- [ ] Percentiles y objetivos solo se publican con muestra suficiente.
- [ ] No hay frecuencias ni SLA universales sin evidencia.
- [ ] Rate limits, fallos, pausas y recuperación tienen reglas auditables.
- [ ] La pérdida de cobertura nunca se representa como ausencia de eventos.
- [ ] Se revisan términos, licencias y derechos antes de automatizar cada fuente.
- [ ] L01–L15 se convierten en fixtures positivos/negativos/fronterizos tras aprobación.
- [ ] El propietario aprueba expresamente metodología y límites.

## 14. Límites pendientes

Esta propuesta no selecciona ni autoriza fuentes concretas, fija frecuencias/SLA/reintentos universales, demuestra cobertura en tiempo real, habilita scraping/captura/redistribución, garantiza recuperación histórica ni implementa vigilancia productiva. La autorización de una fuente y la aprobación de esta metodología son decisiones distintas.

## 15. Registro de decisión

**Estado: PROPUESTA NO APROBADA.**

La integración solo establece una base revisable. El Issue #18 permanecerá abierto hasta aprobar decisiones, documentar fuentes/métodos concretos y ejecutar pruebas verificables. No habilita el requisito funcional #7.
