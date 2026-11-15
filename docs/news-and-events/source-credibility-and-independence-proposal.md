# Propuesta metodológica: credibilidad e independencia de fuentes

**Issue:** [#16 — Definir rúbrica de credibilidad e independencia de fuentes](https://github.com/Osleyder1985/SINAYXA/issues/16)  
**Estado:** metodología aprobada expresamente por el propietario el 2026-11-15; contrato ejecutable y pruebas en implementación.  
**Base obligatoria:** [estándar probatorio para indicios, rumores y posibles filtraciones](evidence-standard-for-indicia-rumours-and-leaks.md), aprobado en #15 y fusionado mediante PR #43.  
**Ámbito:** evaluación de procedencia, capacidad informativa, fiabilidad contextual e independencia de cadenas de obtención. No implementa captura, reputación automatizada, puntuación numérica, probabilidad de verdad, causalidad ni señales de trading.

## 1. Decisión metodológica aprobada

Se aprueba una rúbrica cualitativa, multidimensional y trazable para responder por separado:

1. ¿Qué relación tiene esta fuente con la afirmación concreta y con el hecho que dice conocer?
2. ¿Qué evidencia verificable respalda su acceso, competencia, transparencia y comportamiento editorial/documental?
3. ¿Qué limitaciones, incentivos, conflictos o evidencia contraria afectan a esta evaluación?
4. ¿Las referencias que repiten la afirmación proceden de cadenas de obtención realmente independientes?
5. ¿Qué parte exacta de la afirmación queda respaldada por cada origen?

La rúbrica aprobada no asigna una puntuación total a una fuente. La credibilidad es contextual a una afirmación, materia, periodo y modalidad de acceso; no es una propiedad universal ni permanente de un dominio, marca, periodista o persona.

## 2. Invariantes heredados del estándar #15

Estas reglas no se reabren en #16:

- La unidad probatoria es la afirmación concreta, no la publicación completa.
- Naturaleza, estado probatorio, atribución, autenticidad documental, identidad y procedencia son dimensiones separadas.
- Una publicación oficial acredita que la entidad publicó esa pieza, no la verdad automática de todas sus afirmaciones.
- Una fuente primaria puede acreditar directamente el acto o registro que produjo, dentro de su alcance.
- Republicaciones, traducciones, resúmenes, citas cruzadas y fuentes con origen común no multiplican corroboraciones.
- La ausencia de corroboración no prueba falsedad.
- El precio, el volumen de publicaciones y la popularidad no corroboran una noticia.
- No se asignan probabilidades ni puntuaciones de credibilidad.
- No se adquiere material mediante acceso no autorizado ni se expone la identidad confidencial de una fuente.

## 3. Unidad y alcance de evaluación

La evaluación se vincula a una tupla conceptual:

`(claim_id, claim_component_id, source_id, source_version, access_path, assessment_cutoff)`

El tipo de fuente, el subtipo/función, la base de conocimiento, el carácter institucional y la identidad se registran como atributos separados de la evaluación; no se infieren unos de otros.

Debe conservarse como mínimo:

- afirmación y componentes materiales evaluados;
- referencia exacta y versión de la publicación/documento;
- fecha de publicación, fecha de acceso y fecha de corte de la evaluación;
- identidad conocida por SINAYXA y visibilidad de esa identidad para el público, con acceso restringido cuando proceda;
- tipo de fuente (PRIMARIA, SECUNDARIA, TERCIARIA o DESCONOCIDA) relativo a la afirmación y al componente evaluado;
- subtipo/función, base de conocimiento, carácter oficial/institucional y modo de difusión, registrados como atributos separados;
- relación declarada de la fuente con el hecho: observación directa, participación, documento recibido, testimonio indirecto, análisis, comentario o reproducción;
- cadena de obtención conocida y sus incertidumbres;
- evidencias favorables, limitaciones y evidencias contrarias;
- evaluador, justificación y cambios respecto de evaluaciones anteriores.

No se extrapola una evaluación a otras afirmaciones, materias, autores, periodos o publicaciones sin evidencia específica.

### 3.1 Base de conocimiento, separada del tipo de fuente

Además del tipo PRIMARIA/SECUNDARIA/TERCIARIA, registrar cómo se relaciona la fuente con el hecho o con el dato:

- **OBSERVACIÓN_DIRECTA:** afirma haber observado el hecho.
- **REGISTRO_ORIGINAL:** produjo o conserva el registro primario del acto o sistema.
- **ACCESO_DIRECTO_DECLARADO:** afirma acceso directo a personas, sistemas o documentos; distinguir siempre lo declarado de lo verificado por SINAYXA.
- **TESTIMONIO_DE_TERCEROS:** transmite lo dicho por otra persona.
- **DOCUMENTO_DE_TERCEROS:** depende de un documento cuyo origen o custodia no controla.
- **ANÁLISIS_REPRODUCIBLE:** interpreta datos con método, entradas y pasos examinables.
- **OPINIÓN_O_INTERPRETACIÓN:** ofrece una valoración que no equivale a observación del hecho.
- **REPRODUCCIÓN_SIN_VERIFICACIÓN_PROPIA:** reproduce, traduce o resume otra referencia sin corroboración diferenciada demostrada.
- **DESCONOCIDA:** la base de conocimiento no puede establecerse.

Una fuente puede combinar bases distintas para componentes diferentes de una afirmación. No presentar un acceso declarado como acceso verificado ni un análisis como registro original.

## 4. Rúbrica cualitativa aprobada

Cada dimensión se registra por separado con evidencia y justificación. No se suman dimensiones ni se calcula una nota global.

|Dimensión|Pregunta de evaluación|Evidencia pertinente|Límites|
|---|---|---|---|
|Relación con el hecho|¿La fuente observó, ejecutó, registró o participó directamente en el hecho?|Registro original, documento bajo custodia, observación identificable, descripción comprobable del acceso|Declarar acceso directo no demuestra que exista; requiere sustento|
|Acceso y proximidad|¿Cómo pudo conocer la información y qué distancia existe entre la fuente y el hecho?|Cadena de custodia, acceso institucional, testimonio directo, intermediarios identificados|La proximidad no garantiza exactitud ni ausencia de sesgo|
|Competencia temática|¿Tiene conocimiento demostrable para interpretar esta materia concreta?|Experiencia verificable y pertinente, trabajo técnico/documental contrastable|Prestigio general no sustituye competencia específica|
|Transparencia y trazabilidad|¿Permite verificar qué afirma, sobre qué base y con qué límites?|Enlaces, documentos, metodología, atribución, fechas y alcance explícitos|La falta de publicación de material sensible no demuestra falsedad; se registra la limitación|
|Historial de exactitud pertinente|¿Hay un historial documentado y comparable sobre afirmaciones de esta clase?|Afirmaciones anteriores identificables, resultados verificables, rectificaciones y errores documentados|No usar memoria anecdótica, reputación genérica ni muestras seleccionadas retrospectivamente|
|Correcciones y rendición de cuentas|¿Corrige errores de forma visible, oportuna y específica?|Historial de versiones, notas de corrección, retirada explicada, conservación de versiones|Una corrección no invalida automáticamente toda la publicación; tampoco borra el error|
|Incentivos y conflictos|¿Existen intereses económicos, institucionales, personales o estratégicos relevantes?|Patrocinios, propiedad, relaciones declaradas, remuneración, posiciones públicas|El conflicto exige contextualizar y contrastar; no demuestra falsedad|
|Consistencia interna|¿La afirmación es coherente con los datos y documentos presentados por la propia fuente?|Cálculos reproducibles, citas completas, documentos íntegros, coherencia temporal|Coherencia interna no equivale a corroboración externa|
|Evidencia contraria|¿Qué datos verificables contradicen o limitan la afirmación?|Documentos incompatibles, rectificaciones, registros primarios, observaciones contrarias|Debe conservarse incluso cuando perjudique la hipótesis preferida|
|Adecuación temporal|¿La fuente y la pieza corresponden al periodo relevante y permiten establecer la secuencia?|Fecha/versionado original, historial de edición, marcas temporales, desfase de publicación y corte|La publicación tardía o una fecha desconocida limita la cronología; no se completa por inferencia|

### 4.1 Estados descriptivos por dimensión

Para evitar una escala numérica o una falsa precisión, cada dimensión se registra con uno de estos estados descriptivos aprobados:

- **SUSTENTADA:** existe evidencia identificable y pertinente que respalda la evaluación de esa dimensión concreta. Es un estado del factor de la rúbrica, no un estado probatorio de la afirmación ni un sinónimo de CORROBORADA conforme al Issue #15.
- **LIMITADA:** existe evidencia, pero su alcance, actualidad o calidad restringe la conclusión.
- **DESFAVORABLE:** existe evidencia verificable que limita la fuente en esa dimensión o contradice una característica que la fuente se atribuye. Este estado describe un factor de la rúbrica y **no** es el estado probatorio CONTRADICHA de la afirmación conforme al Issue #15.
- **DESCONOCIDA:** la información disponible no permite evaluarla.
- **NO_APLICA:** la dimensión no es pertinente a la relación fuente-afirmación evaluada.

Estos valores están aprobados como estados descriptivos de los factores, no como estados probatorios ni como score. La justificación y referencias son obligatorias; el estado aislado nunca basta.

### 4.2 Resultado de evaluación de la fuente para la afirmación

Se propone que la conclusión sea narrativa y acotada: qué puede aportar la fuente, qué no puede demostrar y qué comprobaciones faltan. No se propone un nivel ordinal de «fuente buena/mala» ni un umbral automático de aceptación.

Una fuente con acceso directo puede ser pertinente y aun así tener incentivos, limitaciones de memoria o evidencia contradictoria. Una fuente secundaria puede aportar análisis competente, pero no convertirse por ello en testigo directo. Una fuente con historial de correcciones puede ser más transparente que otra que nunca publica correcciones; el número de correcciones, sin contexto, no constituye una métrica de fiabilidad.

## 5. Independencia: grafo de procedencia, no conteo de publicaciones

La independencia se evalúa entre cadenas de obtención para una afirmación y un componente concretos, no entre nombres de medios o dominios. El estado de independencia utiliza exactamente los valores **INDEPENDIENTE**, **DEPENDIENTE** y **DESCONOCIDA** del estándar #15; el contexto de la relación explica qué origen o vínculo permanece desconocido. No se introduce un alias adicional.

### 5.1 Relaciones de procedencia aprobadas

Cada referencia secundaria debe enlazarse, cuando se conozca, con su origen inmediato y con el origen primario alegado. Las relaciones de procedencia aprobadas para documentar son:

- **ORIGEN_DIRECTO:** la fuente declara y sustenta acceso propio al hecho o registro.
- **CITA_DE:** reproduce una afirmación atribuida a otra fuente.
- **SINDICADA_DE:** reproduce material distribuido por agencia, proveedor o servicio común.
- **DERIVADA_DE:** resume, traduce, parafrasea o reelabora una publicación anterior.
- **DOCUMENTO_COMÚN:** varias fuentes recibieron el mismo documento o paquete de un intermediario.
- **CONTACTO_COMÚN:** las fuentes dependen del mismo informante, portavoz o grupo de informantes.
- **ORIGEN_NO_DETERMINADO:** no se ha podido reconstruir la cadena.
- **ANÁLISIS_SEPARADO_SOBRE_DATOS_COMUNES:** análisis producido por separado a partir de un mismo conjunto de datos o documento; puede permitir replicación analítica, pero no constituye un segundo origen independiente del dato compartido.

Estas relaciones forman parte de la taxonomía metodológica aprobada.

### 5.2 Clasificación de independencia aprobada

- **INDEPENDIENTE:** hay evidencia positiva de una vía de obtención separada y no se identifica dependencia material común para el componente corroborado.
- **DEPENDIENTE:** hay evidencia de reproducción, sindicación, cita, documento/intermediario común u otra dependencia material.
- **DESCONOCIDA:** la cadena no puede reconstruirse con evidencia suficiente.

Reglas obligatorias aprobadas:

1. Dos dominios, autores o marcas diferentes no prueban independencia.
2. Dos periodistas del mismo medio pueden tener vías distintas, pero debe documentarse la separación; la organización común se registra como posible factor, no como prueba automática de dependencia.
3. Dos medios que citan la misma agencia cuentan como una cadena para la afirmación sindicada.
4. Una publicación que cita a otra no es corroboración independiente de la cita.
5. Una fuente que afirma haber confirmado por separado debe aportar una base verificable de esa comprobación; la frase «confirmado independientemente» no basta.
6. Si la independencia no puede determinarse, se mantiene DESCONOCIDA; no se presume ni se fuerza a INDEPENDIENTE.
7. La independencia de origen no implica competencia, credibilidad ni pertinencia.
8. La independencia se establece para el componente exacto: dos orígenes pueden corroborar fecha y entidad, pero no importe, intención o ejecución.
9. Dos análisis reproducibles sobre un dataset común pueden ser independientes como procesos analíticos, pero permanecen dependientes respecto del origen del dato; registrar ambas relaciones por separado.

## 6. Tipo de fuente y carácter institucional: ejes separados

El **tipo de fuente** se determina por la relación de la pieza con la proposición concreta, no como una reputación permanente de la entidad, medio, dominio o autor. Se propone registrar uno de estos valores:

- **PRIMARIA:** produce, ejecuta, observa directamente o conserva el registro original del acto/hecho evaluado. Incluye subtipos como registro original y testimonio de primera mano. Solo respalda aquello que su posición y el material permiten observar.
- **SECUNDARIA:** obtiene, investiga, contrasta o analiza información procedente de fuentes primarias u otros materiales. La investigación propia puede aportar evidencia nueva si su método y procedencia son trazables; el análisis aporta interpretación, no necesariamente corroboración directa del hecho interpretado.
- **TERCIARIA:** compila, indexa, resume o sintetiza información procedente principalmente de fuentes secundarias, como repertorios, enciclopedias, directorios, agregadores o revisiones de publicaciones. Por sí sola no constituye un nuevo origen primario de las afirmaciones que resume.
- **DESCONOCIDA:** no hay información suficiente para clasificar la relación de la pieza con la proposición.

El tipo puede variar por componente de una afirmación. Un documento oficial puede ser fuente primaria para acreditar que se emitió una resolución, mientras que una explicación de sus consecuencias publicada por esa misma entidad puede requerir evaluación separada. Cuando una pieza contenga contribuciones de tipos distintos, se desglosan por componente o se documenta expresamente la clasificación mixta; no se fuerza una etiqueta única.

### 6.1 Subtipo, base de conocimiento y modo de difusión

Mantener separados del tipo de fuente:

- **Subtipo/función:** registro original, testimonio de primera mano, investigación secundaria, análisis técnico, comentario, compilación o reproducción.
- **Base de conocimiento:** utilizar los valores definidos en 3.1 (OBSERVACIÓN_DIRECTA, REGISTRO_ORIGINAL, ACCESO_DIRECTO_DECLARADO, TESTIMONIO_DE_TERCEROS, DOCUMENTO_DE_TERCEROS, ANÁLISIS_REPRODUCIBLE, OPINIÓN_O_INTERPRETACIÓN, REPRODUCCIÓN_SIN_VERIFICACIÓN_PROPIA o DESCONOCIDA).
- **Carácter institucional:** registrar por separado si la fuente es oficial/institucional y, cuando sea relevante, la entidad, competencia y ámbito de autoridad que invoca. «OFICIAL» no es un cuarto tipo de fuente ni un nivel automático de credibilidad o veracidad.
- **Relación de procedencia:** conservar las relaciones del apartado 5.1, incluida la sindicación, cita, derivación y origen no determinado.

Una publicación reproductora o sindicada no se clasifica automáticamente como terciaria: su tipo depende de su función respecto de la afirmación; su modo de difusión y dependencia se registran por separado. No añade corroboración independiente salvo que aporte comprobación propia diferenciada y demostrable.

No se ordenan PRIMARIA, SECUNDARIA y TERCIARIA en una jerarquía universal de credibilidad. Una fuente primaria puede equivocarse, ser parcial o no tener competencia sobre una consecuencia; una fuente secundaria puede revelar evidencia directa propia; una fuente terciaria puede ser útil para localizar referencias sin constituir un origen adicional. La evaluación depende de la afirmación, el componente y el alcance.

## 7. Fuentes anónimas y confidenciales

Registrar por separado:

- anonimato frente al público;
- anonimato frente al medio/editor;
- anonimato frente a SINAYXA;
- identidad verificada por un tercero, si existe evidencia legítima y utilizable;
- relación declarada con el hecho;
- método de comprobación de identidad y acceso, sin almacenar datos personales innecesarios;
- número de fuentes distintas solo cuando su separación esté sustentada, nunca inferido de expresiones como «varias fuentes».

Para mantener compatibilidad con el estándar #15, la dimensión de identidad debe conservar exactamente sus valores: **IDENTIFICADA**, **ANÓNIMA_PARA_EL_PÚBLICO**, **ANÓNIMA_PARA_SINAYXA**, **SEUDÓNIMA** y **DESCONOCIDA**. Si la identidad es conocida por el editor pero no por SINAYXA, registrar esa circunstancia como metadato de procedencia y no inferir que SINAYXA verificó la identidad.

Reglas aprobadas:

1. Una fuente anónima no se descarta automáticamente, pero la anonimidad reduce la verificabilidad externa y obliga a explicitar límites.
2. Un medio que conoce la identidad no transfiere automáticamente esa verificación a SINAYXA.
3. Varias fuentes anónimas solo cuentan como orígenes separados si existe base verificable para descartar informante, intermediario o documento común.
4. No solicitar ni publicar identidades confidenciales para elevar una clasificación.
5. La evaluación de credibilidad de una fuente anónima no sustituye las reglas probatorias de #15; una sola fuente anónima no convierte por sí sola una afirmación en CORROBORADA.
6. Si la identidad o independencia no puede comprobarse, registrar DESCONOCIDA y preservar la incertidumbre.

## 8. Sindicación, citas cruzadas y fuentes comunes

|Situación|Tratamiento propuesto|
|---|---|
|Cinco medios reproducen un cable de agencia|Una cadena de origen para el contenido reproducido|
|Medio A cita a B y B cita a A|Dependencia circular; no son dos corroboraciones|
|A y B citan el mismo portavoz en ruedas de prensa distintas|Origen común para la afirmación del portavoz; las observaciones adicionales deben separarse|
|A y B reciben el mismo documento de un intermediario|Documento/origen común, salvo verificación independiente adicional|
|A publica un documento y B confirma directamente un registro distinto|Puede haber independencia para el componente que acredita el segundo registro|
|Dos periodistas investigan por separado y documentan métodos distintos|Puede clasificarse INDEPENDIENTE si la separación queda sustentada|
|Se desconoce el origen de una publicación viral|DESCONOCIDA; no contar republicaciones|

La sindicación debe conservar proveedor, identificador del material y versión/fecha cuando estén disponibles. No se presume que una licencia de reproducción convierta al distribuidor en fuente original.

## 9. Contradicciones, rectificaciones y falta de corroboración

- Conservar cada versión, timestamp, alcance y fuente. No sobrescribir la evaluación anterior.
- Una rectificación se atribuye a quien la publicó y se vincula con el componente corregido. No invalida automáticamente los componentes no afectados.
- Un desmentido oficial es una afirmación de la entidad que desmiente; su autoridad institucional y su evidencia subyacente se evalúan por separado.
- Dos fuentes dependientes que discrepan no constituyen dos líneas independientes.
- Dos fuentes independientes que discrepan generan un conflicto a investigar; no se resuelve por mayoría, prestigio, velocidad ni precio.
- Ausencia de corroboración conserva NO_CORROBORADA o NO_RESUELTA conforme al estándar #15; no se transforma en REFUTADA.
- La evidencia contraria debe documentarse aunque la fuente evaluada tenga buen historial o acceso directo.

## 10. Ejemplos sintéticos de aplicación

Todos los ejemplos son ficticios y sirven para probar consistencia del razonamiento, no para demostrar tasas de acierto.

|Caso|Escenario|Evaluación esperada|
|---|---|---|
|S01|Seis portales publican el mismo cable de agencia|Una cadena; cinco reproducciones no elevan independencia|
|S02|Dos medios citan al mismo portavoz anónimo|Origen común; identidad anónima; no hay doble corroboración|
|S03|Un registro regulatorio acredita la presentación de una solicitud|Fuente primaria para la presentación; no acredita aprobación|
|S04|Un medio secundario aporta entrevistas propias y documentos distintos|Posible origen independiente, sujeto a verificar método y procedencia|
|S05|Un analista competente interpreta un contrato público|Competencia analítica potencial; no es testigo de ejecución del contrato|
|S06|Un periodista corrige un importe y conserva versión anterior|Registrar corrección y alcance; reevaluar el importe, no borrar el resto|
|S07|Una fuente anónima afirma participación directa sin evidencia verificable de acceso|Relación declarada, acceso DESCONOCIDO; no corroborada|
|S08|Dos fuentes supuestamente independientes comparten un documento recibido de un intermediario|Dependientes para el contenido del documento|
|S09|Dos reporteros de una misma organización aportan registros obtenidos por vías distintas|La organización común no decide por sí sola; evaluar y documentar la separación|
|S10|Una entidad oficial niega un hecho sin publicar evidencia subyacente|Registrar el desmentido y su atribución; no tratar la negación como refutación automática|
|S11|Una fuente con historial de errores aporta un documento original autenticado|El historial se registra, pero no invalida automáticamente la autenticidad o el contenido acotado del documento|
|S12|Una fuente prestigiosa publica una afirmación sin atribución ni soporte|Prestigio no sustituye evidencia; evaluación limitada/desconocida|
|S13|Un medio cita a otro que cita al primero|Dependencia circular; no hay dos orígenes|
|S14|Dos fuentes independientes confirman entidad y fecha, pero discrepan sobre el importe|Corroboración limitada a entidad/fecha; importe permanece no resuelto|
|S15|Una fuente anónima conocida por el editor aporta una segunda comprobación, pero SINAYXA no puede verificar separación|Independencia DESCONOCIDA para SINAYXA; no inferir independencia desde la garantía editorial|
|S16|Dos analistas reproducen por separado un cálculo con el mismo dataset público|Registrar análisis separados y dataset común; no contar dos orígenes independientes del dato|

## 11. Evidencia mínima y trazabilidad de cada evaluación

Una evaluación no es reproducible si solo contiene una etiqueta. Debe registrar:

1. identificador y versión de la afirmación;
2. fuente y versión exacta de la pieza;
3. fecha de corte;
4. dimensiones evaluadas y estados descriptivos;
5. evidencia favorable y contraria con referencias;
6. cadena de procedencia y relaciones con otras fuentes;
7. justificación por dimensión;
8. límites, incógnitas y comprobaciones pendientes;
9. autor de la evaluación y cambios posteriores.

Cuando un campo no pueda conocerse, se registra como desconocido; no se completa por inferencia. La identidad confidencial, cuando sea legal y necesario conservarla, debe estar separada y protegida con acceso mínimo.

## 12. Controles contra errores metodológicos

La rúbrica debe rechazar, al menos, estos atajos:

- asignar una nota global por prestigio o popularidad;
- convertir años de trayectoria en garantía de exactitud;
- contar republicaciones como corroboraciones;
- inferir independencia a partir de dominios o autores distintos;
- asumir que fuente primaria significa fuente infalible;
- asumir que fuente secundaria significa fuente inferior;
- descartar información solo por anonimato;
- tratar «varias fuentes» como varias identidades u orígenes demostrados;
- convertir una rectificación puntual en falsedad de toda la noticia;
- ignorar evidencia contraria porque la fuente tenga buena reputación;
- confundir independencia con credibilidad;
- convertir la credibilidad de una fuente en estado probatorio de una afirmación;
- inferir causalidad o efecto de mercado a partir de una noticia o su repetición.

## 13. Criterios de aceptación propuestos para #16

- [x] Se aprueba la evaluación multidimensional y contextual, sin nota global ni probabilidades.
- [x] Se aprueban los estados descriptivos por dimensión.
- [x] Se aprueba la representación de cadenas de procedencia y relaciones de dependencia.
- [x] Se distinguen los tipos PRIMARIA, SECUNDARIA y TERCIARIA por su relación con cada afirmación y componente.
- [x] El carácter oficial/institucional, el subtipo/función, la base de conocimiento y el modo de difusión se registran en ejes separados; no se confunden con el tipo de fuente ni con credibilidad.
- [x] Se resuelven explícitamente los casos de anonimato y confidencialidad mediante visibilidad separada ante público, editor y SINAYXA; no se transfieren verificaciones de identidad ni se incorporan identidades confidenciales reales.
- [x] Se resuelven sindicación, citas cruzadas, documentos e informantes comunes mediante grafo de procedencia y S01–S16.
- [x] Se define el tratamiento de contradicciones, rectificaciones y ausencia de corroboración compatible con #15, con estados y componentes separados.
- [x] Los ejemplos S01–S16 se revisan y se convierten en fixture sintético versionado y pruebas positivas/negativas deterministas.
- [x] La evaluación deja trazabilidad de evidencia favorable, contraria, límites y decisión humana obligatoria.
- [x] El propietario aprueba expresamente la versión y el alcance de la rúbrica (registro de decisión enlazado abajo).

## 14. Límites y asuntos que permanecen abiertos

Esta metodología aprobada no decide:

- arquitectura, esquema de base de datos ni nombres definitivos de campos;
- automatización de evaluación, extracción o clasificación;
- pesos, umbrales o scores numéricos;
- probabilidades de veracidad;
- reglas legales de protección de fuentes o secreto profesional;
- política de retención de datos personales;
- evaluación de riesgo de mercado o causalidad.

Los asuntos jurídicos, de privacidad y seguridad deben revisarse por separado antes de tratar datos confidenciales reales. No se deben almacenar identidades sensibles por conveniencia metodológica.

## 15. Registro de decisión

**Estado actual: METODOLOGÍA APROBADA; CONTRATO SINTÉTICO S01–S16 INTEGRADO; AUDITORÍA FINAL DE CIERRE.**

La decisión metodológica expresa del propietario quedó registrada en [el Issue #16](https://github.com/Osleyder1985/SINAYXA/issues/16#issuecomment-6900966461) el 2026-11-15. Se autoriza convertir S01–S16 en fixture y pruebas deterministas dentro del alcance aprobado. La PR #74 integró el contrato de independencia y procedencia; la PR #75 integró las diez dimensiones cualitativas con 160 evaluaciones de factor. La auditoría final de #16 verificará compatibilidad integral con #15 y consistencia documental antes del cierre. La aprobación no autoriza scoring, probabilidades, ranking universal, causalidad ni señales de inversión.
