# Propuesta de estándar probatorio para indicios, rumores y posibles filtraciones

**Issue:** [#15 — Establecer estándar probatorio para indicios y filtraciones](https://github.com/Osleyder1985/SINAYXA/issues/15)  
**Estado:** propuesta documental pendiente de revisión y aprobación expresa del propietario.  
**Dependencia:** glosario operativo aprobado en el Issue #13.  
**Relaciones:** Issue #14 (intensidad y horizontes), #16 (credibilidad e independencia de fuentes) y #25 (ciclo de vida y caducidad).  
**Ámbito:** evaluación probatoria de afirmaciones, indicios públicos, rumores y posibles filtraciones en el módulo de noticias y acontecimientos. No implementa captura, scoring, predicción, señales de trading ni decisiones legales.

## 1. Objetivo y principios

Esta propuesta establece cuándo una afirmación puede considerarse atribuida, parcialmente corroborada, corroborada, contradicha, refutada o no resuelta; qué evidencia mínima exige cada tratamiento; y cómo preservar la incertidumbre de la información anticipatoria.

Principios obligatorios:

1. **La unidad de evaluación es la afirmación concreta.** Una publicación puede contener varias afirmaciones con estados probatorios diferentes. No se confirma ni se desmiente una publicación completa por una sola de sus partes.
2. **Naturaleza, estado probatorio, autenticidad y procedencia son dimensiones distintas.** «Rumor», «indicio» y «posible filtración» describen la naturaleza de la información; no son grados automáticos de verdad.
3. **La etiqueta filtración no autentica un documento.** Tampoco demuestra que el contenido sea verdadero, completo, vigente, legalmente obtenido o aprobado.
4. **La corroboración debe respaldar el alcance exacto de la afirmación.** La confirmación de una parte no eleva automáticamente los demás detalles.
5. **La corroboración independiente exige orígenes diferenciados, no cantidad de publicaciones.** Esta propuesta fija solo el filtro mínimo contra republicaciones y fuentes comunes; la rúbrica detallada de independencia, credibilidad y ponderación se reserva al Issue #16.
6. **Una fuente primaria puede confirmar el acto que realizó o publicó.** No confirma automáticamente todas las afirmaciones contenidas en el documento ni sus consecuencias futuras.
7. **La ausencia de confirmación no demuestra falsedad.** La refutación requiere evidencia positiva que contradiga la proposición concreta.
8. **El precio no corrobora la noticia.** Un movimiento de mercado puede motivar una investigación, pero no autentica fuentes, documentos ni acontecimientos.
9. **La preservación no autoriza la adquisición ilícita.** No se solicitará, comprará, descargará ni incorporará material obtenido mediante acceso no autorizado, robo de credenciales, intrusión o elusión de controles.
10. **No se asignan probabilidades ni puntuaciones de credibilidad.** La evaluación de reputación, fiabilidad y ponderación de fuentes corresponde al Issue #16.

## 2. Separación de dimensiones

Cada evaluación debe mantener conceptualmente separadas estas dimensiones. La tabla es una propuesta semántica, no un contrato de API ni una decisión de implementación. `ATRIBUIDA` describe la relación entre una afirmación y una fuente; no es un estado probatorio ni implica que la fuente esté identificada públicamente. `source_identity` conserva por separado cuánto se conoce de esa identidad.

| Dimensión | Valores descriptivos propuestos | Qué responde |
| --- | --- | --- |
| Naturaleza de la información | AFIRMACIÓN, INDICIO, RUMOR, POSIBLE_FILTRACIÓN, PUBLICACIÓN_OFICIAL, HECHO_OBSERVADO | Qué tipo de pieza o señal se está evaluando |
| Estado probatorio | NO_CORROBORADA, PARCIALMENTE_CORROBORADA, CORROBORADA, CONTRADICHA, REFUTADA, NO_RESUELTA | Qué respaldo tiene la afirmación concreta |
| Atribución de la afirmación | ATRIBUIDA, NO_ATRIBUIDA, NO_DETERMINADA | Si la proposición está vinculada a una fuente concreta, sin afirmar que sea verdadera |

| Autenticidad del documento | NO_APLICA, NO_VERIFICADA, AUTENTICADA, DISPUTADA, AUTENTICIDAD_REFUTADA | Si la pieza documental es genuina, sin confundirlo con la verdad de su contenido |
| Identidad de la fuente | IDENTIFICADA, ANÓNIMA_PARA_EL_PÚBLICO, ANÓNIMA_PARA_SINAYXA, SEUDÓNIMA, DESCONOCIDA | Qué se conoce de la identidad y ante quién |
| Independencia de origen | INDEPENDIENTE, DEPENDIENTE, DESCONOCIDA | Si dos referencias proceden de cadenas de información realmente separadas |
| Acceso y procedencia | PÚBLICO_LEGÍTIMO, PRIVADO_AUTORIZADO, SOSPECHA_DE_ACCESO_NO_AUTORIZADO, NO_DETERMINADO | Si existe base legítima conocida para acceder a la evidencia |
| Revisión de información sensible | NO_EVALUADA, POSIBLE_INFORMACIÓN_PRIVILEGIADA, REVISIÓN_LEGAL_REQUERIDA, REVISADA_CON_RESTRICCIONES, EXCLUIDA | Si existen señales que impiden tratar el material como información ordinaria |

### 2.1 Compatibilidad con la taxonomía aprobada

La taxonomía de catalizadores y el glosario aprobado del Issue #13 ya establecen los estados descriptivos **Confirmada por evidencia primaria**, **Atribuida a fuente identificada**, **Parcialmente corroborada**, **No corroborada** y **Posteriormente desmentida**. Los términos técnicos propuestos en este documento no los sustituyen ni autorizan una nueva taxonomía por sí solos.

La correspondencia propuesta es:

| Estado detallado de esta propuesta | Relación con el vocabulario aprobado | Salvaguarda |
| --- | --- | --- |
| CORROBORADA | Refina el principio de confirmación mediante evidencia primaria y/o corroboración independiente. | Registrar siempre la base: evidencia primaria o fuentes secundarias cuya independencia haya sido demostrada. No presentar una corroboración secundaria como «evidencia primaria». |
| PARCIALMENTE_CORROBORADA | Equivale a **Parcialmente corroborada**. | Delimitar exactamente los componentes respaldados y los que siguen sin respaldo. |
| NO_CORROBORADA | Equivale a **No corroborada**. | No convertir ausencia de corroboración en falsedad. |
| Atribución = ATRIBUIDA | Representa **Atribuida a fuente identificada** cuando la identidad sea conocida, o una atribución explícita a fuente anónima cuando no lo sea. | Es una dimensión independiente del estado probatorio. No se incluye en `permitted_evidentiary_states`; una afirmación atribuida puede seguir NO_CORROBORADA o NO_RESUELTA. |
| CONTRADICHA | Refinamiento propuesto para una incompatibilidad probatoria todavía no resuelta. | No equivale automáticamente a **Posteriormente desmentida** ni a REFUTADA. |
| REFUTADA | Refinamiento propuesto cuando evidencia directa y pertinente demuestra que la proposición concreta es falsa. | Solo podrá describirse como **Posteriormente desmentida** cuando la evidencia sea posterior; conservar el alcance exacto refutado. |
| NO_RESUELTA | Indicador propuesto de que la evaluación no permite resolver la discrepancia o insuficiencia. | Es una condición de resolución, no un sinónimo de NO_CORROBORADA ni una conclusión de falsedad. |

Hasta que el propietario apruebe expresamente esta propuesta, las etiquetas y correspondencias de esta tabla son exclusivamente explicativas. Cualquier contrato de datos o interfaz futura deberá conservar el vocabulario aprobado y representar por separado la base probatoria y los refinamientos que se aprueben.

No se debe derivar automáticamente una dimensión de otra. Por ejemplo:

- AUTENTICADA no significa CORROBORADA en cuanto a todas las afirmaciones del documento.
- CORROBORADA no significa que la fuente sea independiente si todas las referencias proceden del mismo origen.
- POSIBLE_FILTRACIÓN no significa que el material sea ilícito ni que sea verdadero.
- PUBLICACIÓN_OFICIAL confirma que la entidad publicó esa pieza; no confirma necesariamente que cada dato declarado sea correcto.
- CONTRADICHA no equivale a REFUTADA si la evidencia disponible solo genera un conflicto pendiente.

## 3. Estándar mínimo por clasificación

### 3.1 Indicio

Un indicio requiere, como mínimo:

- una observación o pieza pública identificable y fechable;
- una descripción precisa de qué hipótesis podría apoyar;
- el vínculo lógico entre la señal y la hipótesis, sin saltos inferenciales;
- al menos una explicación alternativa plausible;
- la evidencia que falta para confirmar o descartar la hipótesis.

Un indicio es compatible con una hipótesis, no una confirmación. Una señal ambigua no se convierte en indicio útil solo por coincidir con un movimiento de precio.

### 3.2 Rumor

Un rumor es una afirmación circulante cuya procedencia o evidencia no alcanza el estándar de corroboración aplicable.

Registro mínimo:

- texto exacto o paráfrasis fiel de la afirmación;
- primera referencia pública identificada y fecha/hora de publicación o detección;
- autor o cuenta atribuida, si se conoce;
- origen primario conocido o indicación explícita de ORIGEN_DESCONOCIDO;
- referencias posteriores y relación de dependencia entre ellas;
- estado probatorio y datos que faltan.

No se inventará un origen cuando no pueda localizarse. La popularidad, el número de republicaciones, la repetición por cuentas influyentes o la coincidencia con el precio no elevan el estado probatorio.

### 3.3 Posible filtración

Se utilizará POSIBLE_FILTRACIÓN cuando una pieza se presente como divulgación no oficial o anticipada respecto de una comunicación pública prevista.

Antes de atribuirle valor probatorio deben separarse estas preguntas:

1. ¿Existe una pieza concreta, identificable y fechable?
2. ¿Cuándo fue publicada, cuándo fue detectada y cuándo fue capturada por SINAYXA?
3. ¿Qué afirma su procedencia y qué parte de esa procedencia puede verificarse?
4. ¿El documento es auténtico, una versión preliminar, una recreación, una captura parcial o una pieza no autenticada?
5. ¿El acceso fue público o autorizado y existen señales de obtención ilícita?
6. ¿Qué afirmaciones específicas respalda el documento y cuáles son inferencias?

La clasificación inicial será **POSIBLE_FILTRACIÓN + NO_CORROBORADA** o **NO_RESUELTA**, según la evidencia disponible. La palabra filtración no eleva el estado probatorio.

Si un anuncio oficial posterior confirma el acontecimiento, se crea o actualiza la afirmación correspondiente con su nueva evidencia. No se reescribe retrospectivamente la situación probatoria que existía antes del anuncio. La existencia del acontecimiento puede quedar confirmada posteriormente mientras la autenticidad, la fecha de origen o la procedencia de la pieza anticipatoria siguen sin resolverse.

### 3.4 Atribución de una afirmación

La atribución se registra en la dimensión independiente `attribution_status` (`ATRIBUIDA`, `NO_ATRIBUIDA` o `NO_DETERMINADA`); no es un estado probatorio ni sustituye a `evidentiary_status`. La identidad de la fuente se registra por separado en `source_identity`. Una afirmación puede estar `ATRIBUIDA` a una fuente anónima y continuar `NO_CORROBORADA` o `NO_RESUELTA`.

La atribución demuestra que una fuente sostiene una proposición, no que sea verdadera. Debe registrarse la fuente, la formulación exacta, la fecha, el contexto y si la fuente habla por conocimiento directo, por documento o por referencia a terceros, cuando esa información esté disponible.

Una declaración oficial confirma que la entidad realizó esa declaración. Para confirmar el hecho subyacente se debe comprobar si la declaración constituye evidencia primaria suficiente para esa proposición concreta o si requiere corroboración adicional.

### 3.5 Parcialmente corroborada

Se aplica cuando la evidencia respalda solo componentes delimitados de una afirmación.

La evaluación debe enumerar:

- componentes respaldados;
- componentes no respaldados;
- componentes contradichos;
- componentes todavía desconocidos.

No se elevará toda la afirmación a CORROBORADA por confirmar un detalle, una fecha o una parte del proceso.

### 3.6 Corroborada

Una afirmación puede considerarse CORROBORADA cuando se cumple una de estas condiciones:

- existe evidencia primaria auténtica y directamente pertinente que respalda el alcance exacto de la proposición; o
- existe corroboración independiente suficiente, con orígenes diferenciados y evidencia que respalda el mismo componente material.

La corroboración no exige dos fuentes en todos los casos: un registro oficial primario puede ser suficiente para confirmar que se aprobó una resolución o que se publicó un anuncio. Sin embargo, esa misma pieza no demuestra por sí sola consecuencias, ejecución, adopción, causalidad o detalles que no documenta. Cuando la conclusión dependa de fuentes secundarias, su independencia deberá evaluarse conforme a la rúbrica del Issue #16; mientras esa independencia no esté demostrada, no se elevará la afirmación a CORROBORADA.

La base de la corroboración debe describirse. No se utilizará CORROBORADA como sinónimo de «muchas fuentes lo dicen».

### 3.7 Contradicha, refutada y no resuelta

- **CONTRADICHA:** existen dos líneas de evidencia materialmente incompatibles, cada una con una base verificable suficiente para ser considerada evidencia pertinente; la discrepancia permanece abierta y no permite decidir cuál versión es correcta. Deben identificarse por separado las proposiciones enfrentadas, su evidencia y el alcance exacto del conflicto. La mera existencia de dos relatos incompatibles no basta.
- **Límite para documentos no autenticados:** un documento cuya autenticidad no está verificada no constituye, por sí solo, evidencia suficiente para asignar CONTRADICHA a la proposición que contiene. Puede registrarse como pieza o alegación pendiente, pero no eleva el caso por encima de NO_CORROBORADA o NO_RESUELTA. Si existe una declaración oficial verificable que niega la proposición y un documento no autenticado que parece contradecirla, se registra la declaración como acto de negación y el documento como no verificado; el estado de la proposición será NO_RESUELTA salvo que otra evidencia verificable sustente ambos lados del conflicto.
- **Fuentes anónimas:** la anonimidad no excluye automáticamente CONTRADICHA, pero exige evidencia verificable de las dos líneas enfrentadas; dos medios que atribuyen versiones incompatibles a fuentes anónimas, sin independencia ni corroboración verificables, no bastan.
- **REFUTADA:** evidencia suficientemente directa y pertinente demuestra que la proposición concreta es falsa o que el documento atribuido no es auténtico. La falsificación de una pieza refuta su autenticidad y las proposiciones que dependan exclusivamente de ella, no automáticamente el hecho subyacente. Debe explicarse qué componente queda refutado y por qué.
- **NO_RESUELTA:** la evidencia es insuficiente, contradictoria, incompleta o inaccesible para decidir. Se conservan las versiones y no se fuerza una conclusión. Es el estado preferible cuando hay relatos incompatibles, pero no se alcanza el umbral probatorio para CONTRADICHA.

La falta de respuesta de una entidad, la ausencia de anuncio oficial o el paso del tiempo no bastan por sí solos para marcar REFUTADA.

## 4. Fuentes anónimas y corroboración independiente

### 4.1 Tratamiento de fuentes anónimas

La anonimidad no demuestra falsedad, pero limita la posibilidad de verificar la atribución y la posición de la fuente.

Cuando la información esté disponible y pueda conservarse legítimamente, registrar:

- si la fuente es anónima para el público, para el medio que publica o también para SINAYXA;
- si la fuente afirma conocimiento directo o información de terceros;
- la función o relación con el asunto, sin revelar datos personales innecesarios;
- qué parte concreta podría conocer por su posición;
- fecha, canal y contexto de la declaración;
- motivaciones, conflictos o limitaciones conocidos, sin presumirlos;
- qué comprobaciones independientes existen y cuáles faltan.

No se publicarán nombres, datos de contacto ni elementos que permitan identificar a una fuente confidencial. Se utilizará un identificador interno no revelador cuando sea necesario mantener continuidad.

Una única fuente anónima, incluso si un medio reputado la cita, no basta por sí sola para que SINAYXA marque una afirmación como CORROBORADA. Puede justificar investigación prioritaria o conservarse como AFIRMACIÓN ATRIBUIDA / NO_CORROBORADA. Cualquier excepción editorial de un medio no se convierte automáticamente en validación independiente de SINAYXA.

La evaluación detallada de reputación, historial y ponderación de la fuente queda reservada al Issue #16.

### 4.2 Independencia de origen

Dos referencias solo podrán considerarse independientes cuando exista base para concluir que sus cadenas de obtención no dependen de una misma fuente originaria.

No cuentan como corroboración independiente:

- diez medios que reproducen el mismo comunicado;
- varias cuentas que citan el mismo mensaje original;
- artículos que se citan entre sí en cadena;
- dos fuentes que recibieron el mismo documento de un único intermediario, sin acceso independiente conocido;
- una noticia y sus republicaciones traducidas o resumidas.

Cuando no pueda determinarse si los orígenes son independientes, registrar INDEPENDENCIA_DESCONOCIDA. No sumar referencias ni asumir independencia. Tampoco basta con que dos publicaciones tengan autores o dominios distintos para afirmar que sus fuentes son independientes.

Esta sección define un filtro mínimo de dependencia evidente, no una rúbrica completa. La clasificación detallada de fuentes primarias/secundarias, relaciones de sindicación, citas cruzadas, acceso directo, credibilidad e independencia corresponde al Issue #16.

La independencia no sustituye la pertinencia: dos fuentes independientes que confirman detalles distintos no confirman automáticamente el conjunto de la afirmación.

## 5. Autenticación y preservación de documentos digitales

La autenticidad del documento y la integridad de la copia preservada son propiedades diferentes.

### 5.1 Comprobaciones de autenticidad

Según el tipo de documento y el acceso legítimo disponible, pueden comprobarse:

- publicación en un dominio o repositorio oficial;
- firma digital o mecanismo verificable de emisión;
- identificador, número de expediente, versión o referencia documental;
- coherencia con registros oficiales y documentos relacionados;
- estructura, formato, fechas y metadatos, como indicios auxiliares;
- confirmación por la entidad emisora o por un canal autorizado;
- contradicciones, alteraciones visibles o ausencia de elementos que deberían estar presentes.

Los metadatos por sí solos no autentican un documento: pueden faltar, cambiar o ser manipulados. Una firma válida acredita determinados aspectos de integridad y atribución criptográfica, no la veracidad de todas las afirmaciones incluidas.

### 5.2 Preservación de evidencia legítima

Para evidencia pública o cuyo acceso esté autorizado, conservar cuando sea posible:

- URL o referencia de origen;
- fecha/hora de publicación, primera detección y captura, en UTC y sin sustituir timestamps originales;
- método de obtención legítimo;
- archivo o contenido original sin modificaciones, cuando su conservación esté permitida;
- hash criptográfico de la copia capturada;
- identificador de versión y relación con copias derivadas;
- persona o proceso que realizó la captura;
- notas sobre integridad, limitaciones y transformaciones posteriores.

El hash permite detectar cambios en la copia desde el momento en que se calculó. **No demuestra quién creó el archivo, cuándo se creó originalmente ni si su contenido es verdadero.**

Las transcripciones, traducciones, OCR, capturas recortadas y resúmenes se conservan como derivados vinculados al original; nunca sustituyen silenciosamente a la pieza fuente.

### 5.3 Material sospechoso o de acceso no autorizado

Si la pieza parece proceder de intrusión, robo, credenciales sustraídas, acceso restringido no autorizado o una divulgación potencialmente ilícita:

- no intentar abrir otros recursos, descargar anexos, eludir controles ni ampliar el acceso;
- no solicitar, comprar, redistribuir ni incorporar el contenido a la base documental ordinaria;
- detener la evaluación sustantiva y marcar REVISIÓN_LEGAL_REQUERIDA;
- no usar el material para generar alertas, recomendaciones o conclusiones de inversión;
- limitar cualquier registro a metadatos mínimos cuya conservación sea legalmente admisible y solicitar asesoramiento jurídico antes de continuar.

La mera disponibilidad de un archivo en Internet no resuelve por sí sola su legalidad, autenticidad ni condición de información pública a efectos regulatorios. Este procedimiento no sustituye asesoramiento legal.

## 6. Salvaguardas frente a información privilegiada y manipulación

SINAYXA no debe solicitar, comprar, inducir ni promover la divulgación de información confidencial o privilegiada. Tampoco debe difundir rumores sabiendo, o cuando existan razones claras para saber, que son falsos o engañosos.

Cuando una pieza pueda ser información precisa no pública con capacidad de afectar significativamente al precio de un criptoactivo, se debe:

1. detener la clasificación ordinaria y marcar POSIBLE_INFORMACIÓN_PRIVILEGIADA;
2. impedir que el material se convierta en señal, recomendación o instrucción de negociación;
3. no redistribuir ni resumir su contenido sustantivo;
4. remitir el caso a revisión jurídica competente antes de cualquier uso posterior;
5. conservar la decisión y sus límites sin emitir una conclusión legal automática.

Como referencia jurídica para el ámbito europeo, el título VI del Reglamento (UE) 2023/1114 (MiCA) regula el abuso de mercado en criptoactivos. Su artículo 86 delimita el ámbito a criptoactivos admitidos a negociación o cuya admisión se haya solicitado y contempla actos en la Unión y en terceros países; los artículos 87, 89 y 90 tratan información privilegiada, operaciones con información privilegiada y comunicación ilícita; el artículo 91 prohíbe la manipulación de mercado, incluida la difusión de rumores falsos o engañosos cuando concurren los elementos previstos por la norma. La aplicabilidad concreta depende del activo, conducta y circunstancias; SINAYXA no determinará por sí mismo la existencia de una infracción.

El Reglamento (UE) n.º 596/2014 sobre abuso de mercado puede ser relevante para instrumentos financieros y supuestos comprendidos en su ámbito. No debe extenderse automáticamente a cualquier criptoactivo.

## 7. Uso del precio y separación de causalidad

Los movimientos de precio, volumen, volatilidad, funding, liquidaciones o actividad on-chain pueden servir para detectar una anomalía y decidir investigar una afirmación. No son corroboración de que la noticia, rumor o filtración sea verdadera.

Se deben registrar por separado:

- hora de publicación de la afirmación;
- hora de primera detección;
- hora de captura por SINAYXA;
- hora del movimiento de mercado observado;
- hora del anuncio o confirmación oficial;
- otras explicaciones y acontecimientos simultáneos.

La secuencia temporal no demuestra que una filtración causara el movimiento. Una anomalía anterior a un anuncio puede ser compatible con varias hipótesis, incluida información anticipatoria, pero no prueba por sí sola que existiera una filtración ni que alguien operara con ella.

## 8. Confirmación, desmentido y preservación del historial

Cada cambio probatorio debe conservar:

- afirmación y alcance exactos evaluados;
- estado anterior y estado nuevo;
- evidencia nueva que motiva el cambio;
- fecha/hora de cambio y responsable;
- qué componentes cambian y cuáles permanecen no resueltos;
- relación con publicaciones, documentos y acontecimientos anteriores.

No se sobrescribe una evaluación anterior. La confirmación posterior no borra que la afirmación estaba sin corroborar en una fecha de corte anterior. Un desmentido posterior tampoco autoriza a borrar la pieza original ni a atribuirle retrospectivamente un estado que no tenía.

Las transiciones, caducidad, cierre y reapertura del ciclo de vida se reservan al Issue #25. Este documento define el significado probatorio de los estados, no su automatización.

## 9. Casos límite propuestos para revisión

| ID | Escenario | Tratamiento esperado | Error que debe evitarse |
| --- | --- | --- | --- |
| E01 | La entidad publica una resolución firmada en su sitio oficial | Corroborar que la resolución fue publicada y qué dispone exactamente; evaluar por separado vigencia y ejecución | Extender la confirmación a consecuencias no documentadas |
| E02 | Una sola fuente anónima afirma que habrá una compra institucional | Afirmación atribuida / NO_CORROBORADA; investigar sin presentarla como operación confirmada | Tratar anonimato o detalle aparente como prueba |
| E03 | Ocho cuentas repiten el mismo mensaje original | Una cadena de origen conocida; no hay ocho corroboraciones | Contar republicaciones como fuentes independientes |
| E04 | Dos fuentes independientes confirman solo fecha y entidad, no importe | PARCIALMENTE_CORROBORADA; importe permanece desconocido | Confirmar todos los detalles |
| E05 | Aparece un supuesto documento filtrado en un canal público, sin firma ni procedencia verificable | POSIBLE_FILTRACIÓN + autenticidad NO_VERIFICADA + NO_CORROBORADA | Tratar apariencia oficial como autenticidad |
| E06 | Un PDF tiene hash estable y metadatos coherentes, pero no hay origen verificable | Integridad de la copia preservada; autenticidad NO_VERIFICADA | Confundir hash o metadatos con autenticidad |
| E07 | Un documento auténtico es un borrador sujeto a aprobación | Autenticar el documento y conservar estado de borrador/condiciones | Presentarlo como decisión aprobada |
| E08 | El anuncio oficial posterior confirma el hecho anticipado días antes | Confirmar el hecho desde la fecha de la evidencia oficial; conservar el estado no corroborado que tenía la pieza anticipatoria antes del anuncio | Reescribir la incertidumbre histórica |
| E09 | La entidad niega una afirmación y existe un documento aparentemente contradictorio aún no autenticado | NO_RESUELTA; registrar la negación como declaración verificable y el documento como pieza no autenticada, sin tratarlo como evidencia suficiente de la proposición | Marcar CONTRADICHA solo por la coexistencia de una negación y un documento no verificado |
| E10 | No existe anuncio oficial después de varias semanas | Mantener NO_CORROBORADA o NO_RESUELTA según evidencia; no marcar REFUTADA solo por silencio | Confundir ausencia de confirmación con falsedad |
| E11 | El precio sube antes de circular un rumor | Registrar la anomalía de mercado por separado; el rumor sigue sin corroborar | Usar el precio como confirmación |
| E12 | Un documento demuestra ser una falsificación | AUTENTICIDAD_REFUTADA; refutar solo las afirmaciones que dependían de esa pieza, salvo evidencia adicional | Generalizar la falsedad a todas las afirmaciones relacionadas |
| E13 | Una filtración parece proceder de una cuenta o repositorio comprometido | Detener evaluación sustantiva, no ampliar acceso y marcar REVISIÓN_LEGAL_REQUERIDA | Descargar, redistribuir o explotar material sospechoso |
| E14 | Un medio cita una fuente anónima que afirma haber participado directamente en una negociación | Registrar atribución, anonimidad y conocimiento declarado; no elevar por sí solo a CORROBORADA | Tratar la descripción del medio como acceso verificable de SINAYXA |
| E15 | Una fuente primaria confirma que se presentó una solicitud, pero no que será aprobada | Corroborar la presentación; aprobación permanece no confirmada | Convertir solicitud en aprobación |
| E16 | Una filtración anticipa un acuerdo, pero el documento solo recoge una propuesta preliminar y no está autenticado ni corroborado por otra vía | Mantener NO_CORROBORADA/NO_RESUELTA; la pieza no acredita por sí sola ni la existencia de la propuesta. Si esta se acredita independientemente, corroborar solo la propuesta y mantener negociación/ejecución separadas | Elevar una pieza no autenticada a corroboración parcial o convertir una propuesta en acuerdo ejecutado |
| E17 | Dos medios publican versiones incompatibles y ambos citan fuentes anónimas distintas, sin corroboración verificable de sus orígenes | NO_RESUELTA; conservar ambas atribuciones sin asumir independencia ni contradicción probatoria suficiente | Convertir versiones incompatibles en CONTRADICHA o resolver por mayoría de publicaciones |
| E18 | Una publicación se rectifica y elimina un dato | Registrar rectificación atribuida y preservar versión anterior; reevaluar solo el componente afectado | Suponer que la rectificación invalida todo el acontecimiento |

Los resultados esperados son criterios de revisión, no pruebas ejecutadas ni afirmaciones sobre acontecimientos reales.

## 10. Criterios de aceptación propuestos para el Issue #15

- [ ] Se distingue la naturaleza de la información del estado probatorio, atribución, autenticidad, procedencia y legalidad de acceso.
- [ ] AFIRMACIÓN ATRIBUIDA se representa como dimensión de atribución y nunca como estado probatorio.
- [ ] Indicio, rumor y posible filtración no se utilizan como sinónimos ni como grados automáticos de veracidad.
- [ ] Cada estado probatorio se aplica a afirmaciones concretas y conserva el alcance respaldado.
- [ ] La corroboración independiente se basa en orígenes diferenciados; republicaciones y fuentes comunes no se cuentan como independencia.
- [ ] Las fuentes anónimas se registran con límites explícitos y sin exponer identidades confidenciales.
- [ ] La autenticación documental separa integridad de copia, autenticidad, procedencia y veracidad del contenido.
- [ ] Los hashes y metadatos no se presentan como prueba suficiente de autoría o autenticidad.
- [ ] La confirmación posterior no reescribe el estado probatorio que existía antes del anuncio oficial.
- [ ] La ausencia de confirmación no se convierte automáticamente en refutación.
- [ ] Los movimientos de precio no se utilizan como corroboración de rumores o filtraciones.
- [ ] Existe un procedimiento de parada y revisión jurídica para material potencialmente ilícito o información privilegiada.
- [ ] Se preservan versiones, contradicciones, rectificaciones y estados históricos sin sobrescritura.
- [ ] CONTRADICHA exige dos líneas de evidencia materialmente incompatibles con base verificable; un documento no autenticado o relatos anónimos sin corroboración no bastan por sí solos.
- [ ] Los casos E01–E18 cubren fuentes anónimas, documentos no autenticados, corroboración parcial, independencia, falsificación, confirmación posterior y salvaguardas legales.
- [ ] Se mantiene la separación con los Issues #16 (credibilidad/ponderación de fuentes) y #25 (ciclo de vida/caducidad).
- [ ] El propietario aprueba o modifica expresamente los criterios y el estándar probatorio antes de cualquier implementación.

## 11. Referencias y límites de aplicación

1. **Reuters — Standards and Values.** Referencia editorial para priorizar exactitud sobre velocidad, atribución honesta, preferencia por fuentes identificadas, contraste de fuentes anónimas, evaluación de posición/motivo, búsqueda de evidencia contraria y tratamiento diferenciado de rumores. Es una política editorial de Reuters, no una norma jurídica universal: [Reuters Standards and Values](https://reutersagency.com/about/standards-values/)
2. **NISTIR 8387 — Digital Evidence Preservation: Considerations for Evidence Handlers (2022).** Referencia técnica para preservación de evidencia digital, integridad, documentación de origen y gestión de copias. No convierte un hash en prueba de autenticidad o veracidad: [NISTIR 8387](https://doi.org/10.6028/NIST.IR.8387)
3. **Reglamento (UE) 2023/1114 (MiCA), título VI, artículos 86–91.** Referencia jurídica primaria sobre ámbito, información privilegiada, operaciones con información privilegiada, comunicación ilícita y manipulación de mercado en criptoactivos comprendidos en su ámbito: [Reglamento (UE) 2023/1114](https://eur-lex.europa.eu/eli/reg/2023/1114/oj)
4. **Reglamento (UE) n.º 596/2014 sobre abuso de mercado.** Referencia complementaria para instrumentos y conductas comprendidos en su ámbito; no debe aplicarse automáticamente a todo criptoactivo: [Reglamento (UE) n.º 596/2014](https://eur-lex.europa.eu/eli/reg/2014/596)

Estas referencias sustentan controles de prudencia y preservación. No sustituyen asesoramiento jurídico, no resuelven por sí solas la admisibilidad de una fuente y no demuestran que una afirmación concreta sea verdadera.

## 12. Gobernanza

Esta versión es una propuesta. No aprueba automáticamente estados probatorios, umbrales, reglas de corroboración ni tratamiento legal. No implementa clasificación automática ni recomienda operaciones. Cualquier implementación requerirá un Issue funcional, un PR separado y pruebas sobre casos aprobados por el propietario.
