# Propuesta de rúbrica de credibilidad e independencia de fuentes

**Issue:** [#16 — Definir rúbrica de credibilidad e independencia de fuentes](https://github.com/Osleyder1985/SINAYXA/issues/16)  
**Estado:** propuesta metodológica; pendiente de revisión y aprobación expresa del propietario.  
**Dependencia normativa:** [estándar probatorio para indicios, rumores y posibles filtraciones](evidence-standard-for-indicia-rumours-and-leaks.md), aprobado en el Issue #15 e integrado mediante PR #43.  
**Ámbito:** evaluación documentada de fuentes y de la independencia de sus cadenas de información para afirmaciones concretas.  
**No constituye:** implementación, puntuación automática, ranking de medios, probabilidad de verdad ni sustituto del estado probatorio.

## 1. Objetivo y principio rector

La rúbrica define cómo describir de forma reproducible las fortalezas, limitaciones y relaciones de dependencia de una fuente respecto de una afirmación concreta. No pretende decidir si una fuente es «buena» o «mala» de forma universal.

La unidad de evaluación es:

**una fuente o pieza de evidencia + una afirmación delimitada + un ámbito + un momento de evaluación.**

La misma fuente puede ser primaria y altamente pertinente para demostrar que publicó una declaración, secundaria para explicar un hecho que no observó y no pertinente para una afirmación técnica fuera de su competencia. La evaluación debe reflejar esa relación concreta.

Principios:

1. Credibilidad de fuente, calidad de evidencia, autenticidad documental, independencia de origen y estado probatorio de la afirmación son dimensiones separadas.
2. La credibilidad no equivale a verdad. Una fuente fiable puede equivocarse; una fuente con limitaciones puede aportar una pieza auténtica y comprobable.
3. No se infiere independencia por el número de publicaciones, dominios, autores o idiomas.
4. No se asigna una puntuación global ni se suman factores heterogéneos.
5. La ausencia de información se registra como desconocida, no como favorable ni desfavorable.
6. Las evaluaciones deben preservar la evidencia contraria, los conflictos, las rectificaciones y las limitaciones.
7. La rúbrica no cambia los estados probatorios aprobados en el Issue #15 ni relaja sus umbrales.

## 2. Distinciones necesarias

### 2.1 Tipo de fuente, separado de la base de conocimiento

El tipo describe el papel de la fuente en la cadena informativa. La base de conocimiento describe cómo conoce lo que afirma.

| Tipo | Definición operacional | Límite |
| --- | --- | --- |
| **PRIMARIA** | Registro original, dato producido por el sistema observado, documento emitido por el actor pertinente, testimonio de primera mano o evidencia obtenida directamente del hecho. | Solo es primaria respecto de lo que registra, ejecuta, observa o declara directamente. Una declaración oficial prueba que se emitió esa declaración; no valida automáticamente todas sus afirmaciones. |
| **SECUNDARIA** | Fuente que informa, verifica, contextualiza o analiza material primario o testimonios de terceros. | Puede aportar verificación periodística o técnica propia, pero debe explicitarse qué comprobó y qué solo atribuye. |
| **TERCIARIA** | Agregador, índice, resumen, buscador, recopilación o publicación que compila material de otras fuentes. | Útil para descubrir referencias y localizar originales; no constituye corroboración independiente cuando reproduce los mismos orígenes. |
| **DESCONOCIDA** | No hay información suficiente para asignar el papel. | No se fuerza una clasificación. |

La clasificación es relativa a la afirmación. Un explorador de bloques puede ser fuente primaria para el registro visible de una transacción en una cadena concreta, pero no para identificar por sí solo al beneficiario económico real ni demostrar la motivación de la transacción.

### 2.2 Base de conocimiento

Registrar una o varias bases, con justificación:

- **OBSERVACIÓN_DIRECTA:** la fuente afirma haber observado el hecho.
- **REGISTRO_ORIGINAL:** el contenido procede del sistema, expediente o documento que produjo el registro.
- **ACCESO_DIRECTO:** la fuente declara acceso directo a personas, sistemas o documentación pertinente; verificar ese acceso cuando sea posible.
- **TESTIMONIO_DE_TERCEROS:** la fuente informa de lo que otra persona le dijo.
- **DOCUMENTO_DE_TERCEROS:** la fuente basa la afirmación en un documento cuyo origen no controla.
- **ANÁLISIS_REPRODUCIBLE:** la conclusión deriva de un método, datos y pasos que pueden examinarse o repetirse.
- **ANÁLISIS_NO_REPRODUCIBLE:** se presenta una conclusión sin detalle suficiente para repetirla.
- **OPINIÓN_O_INTERPRETACIÓN:** valoración o inferencia, no observación directa del hecho.
- **DESCONOCIDA:** base no declarada o no verificable.

No convertir una afirmación de acceso directo en acceso comprobado. Registrar por separado «declarado por la fuente» y «verificado por SINAYXA».

### 2.3 Identidad y anonimato

La identidad es una dimensión independiente del tipo y de la base de conocimiento:

- **IDENTIFICADA:** identidad conocida y verificable para el análisis.
- **SEUDÓNIMA:** se usa un identificador persistente, sin identidad civil verificada.
- **ANÓNIMA_PARA_EL_PÚBLICO:** el medio o intermediario puede conocer la identidad, pero no la divulga públicamente.
- **ANÓNIMA_PARA_SINAYXA:** SINAYXA no conoce la identidad, aunque el editor pudiera conocerla.
- **DESCONOCIDA:** no se puede establecer ni siquiera el régimen de identidad.

No intentar descubrir ni registrar datos personales innecesarios de fuentes confidenciales. Un identificador interno no revelador solo se utilizará si el acceso y la conservación son legítimos. La anonimidad no es, por sí sola, evidencia a favor ni en contra.

## 3. Rúbrica multidimensional de evaluación

Cada factor se evalúa individualmente. Los valores propuestos son **FAVORABLE**, **LIMITADO**, **ADVERSO** o **DESCONOCIDO**; se admite **NO_APLICA** cuando el factor no corresponde al tipo de pieza. Cada valor exige una explicación y una referencia a la evidencia. No se calcula una media ni una puntuación compuesta.

| Factor | FAVORABLE | LIMITADO | ADVERSO | DESCONOCIDO |
| --- | --- | --- | --- | --- |
| **Acceso y proximidad** | La fuente demuestra observación o acceso directo pertinente al hecho. | Acceso parcial, mediado o limitado a una fase/segmento. | Se demuestra que la fuente no tenía el acceso que afirmaba o que su relato es de oídas presentado como directo. | No hay base para evaluar acceso. |
| **Competencia pertinente** | Competencia demostrable en el dominio y tarea concretos; se puede examinar el trabajo relevante. | Competencia general o experiencia no específica para la afirmación. | Error técnico material demostrado, fuera de competencia o método incompetente en el ámbito evaluado. | No hay información suficiente. |
| **Trazabilidad y procedencia** | Autoría/entidad, fecha, versión, URL/documento original y cadena de obtención están identificados y pueden revisarse. | Algunos elementos faltan, pero el origen principal puede reconstruirse parcialmente. | Procedencia materialmente falsa, manipulada o atribuida de forma engañosa. | No puede reconstruirse el origen. |
| **Transparencia del método** | Expone datos, fuentes, supuestos, limitaciones y pasos suficientes para revisión o reproducción. | Expone parte del método, pero omite elementos relevantes. | Oculta o falsea deliberadamente elementos esenciales del método, o se demuestra manipulación. | No hay información metodológica. |
| **Rendición de cuentas** | Identidad/editor responsable y mecanismo verificable de rectificación o respuesta. | Responsabilidad parcial o difícil de comprobar. | Se demuestra suplantación, evasión deliberada de responsabilidad o ausencia de rectificación ante un error material confirmado, cuando era exigible. | No se conoce. |
| **Historial pertinente** | Historial verificable y relevante de aciertos, errores y rectificaciones en el mismo ámbito y tipo de afirmación. | Historial mixto o limitado en alcance/periodo. | Patrón documentado de errores materiales repetidos o falsedades en el mismo ámbito, no rectificados o reiterados tras corrección. | Historial insuficiente o no investigado. |
| **Incentivos y conflictos** | Incentivos relevantes declarados y evaluables; no se identifica conflicto material no gestionado. | Existe interés o conflicto que puede influir, pero su efecto no está determinado. | Conflicto material no declarado o incentivo que se vincula a una distorsión demostrable de la afirmación. | No hay datos suficientes. |
| **Soporte de la afirmación** | La pieza respalda directamente el componente exacto evaluado. | Respalda solo parte, indirectamente o con reservas explícitas. | El contenido no respalda lo que se le atribuye o contradice materialmente la proposición. | No puede examinarse el contenido o su alcance. |
| **Ajuste temporal** | La fuente es contemporánea al hecho o explica de forma verificable su cronología. | Publicación tardía, retrospectiva o con marcas temporales incompletas, pero aún útil con límites. | Se demuestra que la cronología atribuida es imposible o se alteró de forma material. | Fecha o secuencia no verificable. |

### 3.1 Reglas de interpretación

- **FAVORABLE no significa verdadero.** Describe una característica que aumenta la posibilidad de examinar o confiar en la contribución concreta.
- **LIMITADO no significa falso.** Identifica un alcance menor o una reserva que debe acompañar la afirmación.
- **ADVERSO requiere evidencia positiva.** No se asigna por sospecha, anonimato, desacuerdo, ideología, nacionalidad, tamaño del medio o falta de popularidad.
- **DESCONOCIDO no equivale a neutral ni a desfavorable.** Es una laguna explícita y debe conservarse.
- Una fuente puede tener factores favorables y adversos simultáneamente. Se presentan todos; no se cancelan mediante una suma.
- El historial se limita al ámbito pertinente. Un error en una materia no invalida automáticamente una fuente en otra.
- No tener historial verificable es DESCONOCIDO, no FAVORABLE ni ADVERSO.
- Un conflicto de interés se registra, pero no invalida automáticamente un documento primario o un dato comprobable.
- Una rectificación transparente puede ser evidencia favorable de rendición de cuentas, aunque el error original siga siendo relevante para el historial.
- La autenticidad de una pieza se registra según el estándar del Issue #15; no se deduce del prestigio de quien la publica.

## 4. Independencia de fuentes y genealogía de información

### 4.1 Unidad de análisis

La independencia no es una propiedad permanente de un medio o de una persona. Es una relación **entre dos cadenas de evidencia, respecto de una afirmación concreta**.

Se mantienen los tres estados aprobados por el estándar del Issue #15:

- **INDEPENDIENTE:** existe evidencia verificable de que las cadenas de obtención son distintas y no dependen materialmente de una misma fuente originaria para el componente evaluado.
- **DEPENDIENTE:** las referencias derivan del mismo comunicado, documento, testigo, intermediario, agencia, publicación original, feed o cadena de citas, sin corroboración separada del componente.
- **DESCONOCIDA:** no hay información suficiente para decidir si los orígenes son separados.

No inferir INDEPENDIENTE por diferencias de marca, dominio, idioma, autor, formato, hora de publicación o número de republicaciones.

### 4.2 Relaciones que deben registrarse

Cuando sean conocidas, representar las relaciones entre piezas y fuentes:

- **REPRODUCE:** copia o republica un contenido anterior.
- **TRADUCE_O_RESUME:** deriva de una publicación previa en otro idioma o formato.
- **CITA:** atribuye explícitamente la información a otra fuente.
- **CITA_EN_CADENA:** obtiene la información de una fuente que, a su vez, cita otra.
- **SINDICADA_POR:** distribución de un mismo despacho o contenido por varios medios.
- **COMPARTE_FUENTE_ORIGINAL:** las fuentes obtuvieron la información de la misma persona, entidad o intermediario.
- **COMPARTE_DOCUMENTO:** las fuentes analizan el mismo documento o archivo de origen.
- **ACCESO_SEPARADO_VERIFICADO:** cada fuente demuestra acceso distinto al hecho o registro.
- **ANÁLISIS_SEPARADO:** análisis realizado por separado, aunque pueda usar los mismos datos.
- **RELACIÓN_DESCONOCIDA:** no se pudo reconstruir la genealogía.

Registrar la relación y su evidencia. No inventar un grafo completo cuando solo se conoce un vínculo.

### 4.3 Sindicación, citas y origen común

Las siguientes situaciones son **DEPENDIENTES** para corroborar la afirmación subyacente:

1. Varios medios reproducen un despacho de una misma agencia.
2. Varias publicaciones citan un comunicado o publicación original común.
3. Una noticia cita otra noticia y las posteriores citan a la segunda.
4. Distintas cuentas traducen, resumen o copian el mismo mensaje.
5. Dos periodistas citan a la misma fuente anónima, salvo que se demuestre que obtuvieron corroboración separada del hecho.
6. Varias publicaciones se basan en el mismo documento no autenticado.
7. Un agregador recoge referencias sin verificar su origen.

La repetición puede demostrar difusión o atención, pero no crea corroboración adicional.

### 4.4 Análisis separado sobre datos comunes

Si dos analistas ejecutan por separado un método reproducible sobre el mismo conjunto de datos:

- registrar **ANÁLISIS_SEPARADO**;
- registrar que el dato de origen es común;
- no contar el análisis como una segunda fuente independiente del hecho que originó los datos;
- sí puede aportar replicación analítica de una interpretación o cálculo, si los métodos, versiones y resultados se conservan y las limitaciones se declaran.

Dos exploradores que muestran la misma transacción de la misma cadena no son dos orígenes independientes del registro. Dos análisis separados de esa transacción pueden verificar de manera independiente una interpretación técnica, pero no duplican la evidencia primaria.

### 4.5 Casos en los que puede declararse independencia

Puede declararse **INDEPENDIENTE** cuando la documentación permite verificar, por ejemplo:

- dos observadores distintos con acceso directo separado al mismo hecho;
- dos registros originales producidos por sistemas diferentes, sin derivación entre ellos, que documentan el mismo componente;
- un registro oficial y una evidencia operacional obtenida por otra cadena independiente, cuando ambos respaldan la misma proposición;
- dos investigaciones periodísticas que documentan acceso separado a fuentes distintas y evidencia propia, no solo una declaración de sus editores.

Si solo se conoce que las publicaciones son diferentes, el estado es **DESCONOCIDA**, no INDEPENDIENTE.

### 4.6 Fuentes anónimas

La independencia entre fuentes anónimas solo se reconoce si existe base verificable para distinguir sus orígenes. Dos medios que dicen haber consultado «fuentes familiarizadas con el asunto» no prueban independencia si no se puede establecer que no comparten informante, intermediario o documento.

Puede conservarse la afirmación de independencia que hace el editor como **declaración atribuida**, pero no convertirla automáticamente en verificación de SINAYXA. No solicitar identidades confidenciales ni información protegida para completar el registro.

## 5. Fuentes por contexto y límites de autoridad

| Contexto | Qué puede aportar | Qué no debe inferirse automáticamente |
| --- | --- | --- |
| Organismo regulador, tribunal o banco central | Existencia, contenido y fecha de sus actos, documentos y declaraciones oficiales. | Que todas las afirmaciones, previsiones o interpretaciones incluidas sean correctas o que sus efectos futuros ya se hayan materializado. |
| Empresa, exchange o protocolo implicado | Sus propias decisiones, comunicados, datos operativos y explicaciones atribuibles. | Neutralidad, independencia o ausencia de incentivos comerciales. |
| Medio periodístico | Reporte, entrevistas, documentos y comprobaciones que el artículo describa. | Que varias publicaciones sean independientes o que una fuente anónima esté verificada por SINAYXA. |
| Investigador, analista o académico | Método, análisis, datos, interpretación y límites de su especialidad. | Que una opinión sea observación primaria o que la competencia se extienda a cualquier materia. |
| Datos on-chain, repositorios y telemetría | Registros técnicos dentro del alcance, integridad y cobertura del sistema. | Identidad real, motivación, control económico o causalidad no demostrada. |
| Comunidad, redes sociales y testigos | Observaciones, señales tempranas, capturas o testimonios que pueden abrir una línea de investigación. | Autenticidad, representatividad, conocimiento directo o corroboración por popularidad. |
| Agregador o recopilador | Descubrimiento, localización y panorama de referencias. | Corroboración independiente si las entradas proceden de fuentes comunes. |

La fuente oficial puede tener autoridad sobre su propio acto y, simultáneamente, un interés institucional en cómo describe sus consecuencias. Registrar ambas cosas sin anular una por la otra.

## 6. Contradicciones, errores y rectificaciones

1. Evaluar la afirmación exacta, no una reputación general.
2. Registrar por separado la versión original, la rectificación, el momento de cada una y el alcance corregido.
3. Una corrección explícita no borra el historial del error, pero sí debe reconocerse como evidencia de rendición de cuentas.
4. La falta de rectificación solo es adversa cuando el error material está demostrado, la fuente tuvo oportunidad razonable de conocerlo y el contexto hacía esperable una corrección; no inferir mala fe por silencio aislado.
5. Una fuente que contradice otra no queda desacreditada por el mero desacuerdo. Evaluar evidencia, acceso, competencia, procedencia y alcance de ambas.
6. El estado **CONTRADICHA**, **REFUTADA** o **NO_RESUELTA** se asigna conforme al estándar aprobado del Issue #15; esta rúbrica no crea nuevos estados.
7. Un documento no autenticado no se convierte en evidencia contradictoria suficiente solo porque contradiga una declaración oficial.

## 7. Registro mínimo por evaluación

Cada evaluación debe permitir reconstruir quién afirmó qué, sobre qué evidencia, con qué limitaciones y en qué fecha. Como mínimo:

- identificador estable de fuente y de pieza;
- identificador y texto exacto/paráfrasis fiel de la afirmación evaluada;
- tipo de fuente y base de conocimiento;
- identidad y condición de anonimato, sin datos personales innecesarios;
- fecha de publicación, detección y captura, conservadas por separado;
- URL, referencia, versión o hash cuando exista y sea legítimo conservarlo;
- método y cadena de obtención conocidos;
- resultado de cada factor de la rúbrica y justificación basada en evidencia;
- conflictos e incentivos identificados, declarados o desconocidos;
- historial pertinente examinado, periodo y límites de búsqueda;
- relaciones de dependencia con otras piezas y fuentes;
- estado de independencia por cada par/cadena relevante;
- componentes de la afirmación respaldados, no respaldados o contradichos;
- limitaciones, información no disponible y alternativas;
- versión de la rúbrica, fecha de evaluación y responsable/revisor.

No rellenar un campo con una conjetura. Utilizar DESCONOCIDO o NO_DISPONIBLE y explicar qué impide resolverlo.

## 8. Ejemplos de aplicación

| Caso | Situación | Evaluación correcta |
| --- | --- | --- |
| E01 | Diez sitios reproducen literalmente un despacho de una agencia. | Diez referencias; una cadena originaria conocida. DEPENDIENTE. La cantidad no aumenta corroboración. |
| E02 | Tres medios citan el mismo comunicado corporativo. | DEPENDIENTE para el contenido del comunicado. El comunicado es primario para el acto de publicación de la empresa, no para todas sus afirmaciones. |
| E03 | Un medio cita a otro, y cinco cuentas citan al primero. | Citas en cadena; DEPENDIENTE. Preservar la genealogía conocida. |
| E04 | Dos medios afirman tener fuentes anónimas, pero no hay información sobre si comparten informante. | DESCONOCIDA. No afirmar independencia ni dependencia sin evidencia del origen común. |
| E05 | Dos fuentes anónimas son verificadas como personas distintas con acceso directo separado. | Puede ser INDEPENDIENTE para el componente al que ambas tuvieron acceso; preservar anonimato y evidencia de separación sin revelar identidades. |
| E06 | Dos analistas calculan por separado una métrica usando el mismo dataset público. | ANÁLISIS_SEPARADO; dato de origen común. Replicación analítica posible, no segunda fuente independiente del dataset. |
| E07 | Una entidad publica oficialmente que aprobó una propuesta. | Fuente primaria para el acto de aprobación, si el documento es auténtico. No confirma por sí sola la ejecución ni el impacto en mercado. |
| E08 | Un investigador publica un análisis reproducible con código, datos y limitaciones. | Puede ser favorable en transparencia y reproducibilidad para esa tarea. La conclusión sigue necesitando examen de datos, método y alcance. |
| E09 | Una fuente anónima afirma un hecho y no existe corroboración. | Identidad limitada/desconocida; acceso y competencia según evidencia disponible. NO_CORROBORADA o NO_RESUELTA conforme al estándar #15; anonimato no equivale a falsedad. |
| E10 | Un medio corrige públicamente una fecha incorrecta y conserva nota de actualización. | El error permanece en el historial; la rectificación es evidencia favorable de rendición de cuentas. La afirmación corregida se evalúa con la evidencia actual. |
| E11 | Un exchange publica datos de reservas de su propia entidad. | Fuente primaria para lo que publicó y para datos bajo su control; incentivo/conflicto institucional debe registrarse. No equivale automáticamente a auditoría independiente. |
| E12 | Un explorador de bloques y dos webs muestran la misma transacción a partir del mismo nodo/API. | Mismo origen de datos o infraestructura; no contar tres fuentes independientes. La integridad y cobertura del registro se evalúan aparte. |
| E13 | Un medio reputado informa una afirmación técnica fuera de su especialidad y no muestra evidencia. | Marca o reputación general no suplen competencia específica ni soporte de la afirmación; registrar limitaciones. |
| E14 | Una fuente tiene un conflicto comercial declarado, pero aporta un contrato firmado y verificable. | El conflicto se conserva; el contrato puede ser evidencia primaria de su contenido y existencia si se autentica. El conflicto no invalida automáticamente el documento. |

## 9. Prohibiciones y salvaguardas

- No producir una puntuación total, estrellas, porcentaje de credibilidad, probabilidad de verdad o ranking global de fuentes.
- No entrenar ni presentar un clasificador automático de credibilidad con esta propuesta.
- No inferir credibilidad por nacionalidad, ideología, afiliación, popularidad, idioma, tamaño o reputación genérica.
- No confundir publicación oficial, autenticidad documental, verdad del contenido y efecto real.
- No contar republicaciones, traducciones, citas o syndication como corroboración adicional.
- No considerar independiente un análisis de datos comunes para probar la independencia del dato original.
- No revelar ni intentar descubrir identidades de fuentes confidenciales.
- No adquirir ni preservar material mediante acceso no autorizado.
- No convertir DESCONOCIDO en una conclusión favorable o adversa.
- No modificar los estados probatorios, criterios de CONTRADICHA/REFUTADA ni límites de legalidad del Issue #15.

## 10. Pruebas de consistencia requeridas antes de aprobar

La rúbrica deberá superar, como mínimo, estos controles de escritorio y sintéticos:

1. **C01 — Reproducción masiva:** 100 republicaciones de un único original no aumentan el número de orígenes independientes.
2. **C02 — Citas en cadena:** una cadena A→B→C conserva el origen A y no se cuenta como tres corroboraciones.
3. **C03 — Fuente común no visible:** dos publicaciones distintas con posible fuente común permanecen DESCONOCIDA si no hay prueba de independencia ni dependencia.
4. **C04 — Anonimato:** dos fuentes anónimas no se consideran independientes por aparecer en medios distintos.
5. **C05 — Acceso separado:** dos observadores con acceso directo distinto y documentado pueden evaluarse como INDEPENDIENTES para la afirmación pertinente.
6. **C06 — Análisis replicado:** dos análisis independientes sobre el mismo dataset se registran como replicación analítica y no como independencia del origen de datos.
7. **C07 — Autoridad oficial:** una publicación oficial confirma el acto de publicación, no automáticamente la veracidad de todos sus detalles.
8. **C08 — Conflicto declarado:** el interés comercial se registra sin invalidar automáticamente la evidencia primaria verificable.
9. **C09 — Historial ausente:** falta de historial se registra DESCONOCIDO, no FAVORABLE.
10. **C10 — Rectificación:** se conserva el error original y se registra la corrección como rendición de cuentas.
11. **C11 — Competencia específica:** una fuente competente en un área no recibe automáticamente evaluación favorable en otra.
12. **C12 — No agregación:** factores favorables y adversos permanecen visibles; ninguna suma puede ocultar una limitación crítica.

Estas pruebas verifican consistencia del contrato propuesto. No demuestran validez empírica, calibración, exactitud predictiva ni acuerdo interevaluador.

## 11. Relación con el estándar aprobado del Issue #15

La propuesta implementa conceptualmente la reserva del Issue #15: independencia de origen, credibilidad, fuentes primarias/secundarias, anonimato y corroboración detallada se desarrollan aquí sin cambiar las categorías probatorias aprobadas.

Compatibilidad obligatoria:

- **CORROBORADA** exige evidencia primaria auténtica y pertinente para la proposición concreta, o corroboración independiente suficiente según la relación de origen documentada.
- **PARCIALMENTE_CORROBORADA** limita la conclusión a los componentes respaldados.
- **NO_CORROBORADA** no equivale a REFUTADA.
- **CONTRADICHA**, **REFUTADA** y **NO_RESUELTA** mantienen las definiciones y límites del estándar #15.
- La etiqueta POSIBLE_FILTRACIÓN no eleva la credibilidad ni la independencia.
- El movimiento del precio no corrobora una noticia ni una fuente.

Si se detecta una contradicción con el estándar #15, prevalece el estándar aprobado y se debe abrir una decisión de cambio separada; no se resuelve silenciosamente en esta rúbrica.

## 12. Decisiones aún no aprobadas

Esta propuesta no fija:
- ponderaciones entre factores;
- umbrales para un supuesto nivel global de credibilidad;
- una escala numérica;
- una jerarquía universal de medios o instituciones;
- reglas de clasificación automática;
- un modelo de aprendizaje automático;
- una cantidad mínima universal de fuentes;
- una regla de corroboración que ignore el alcance específico de la afirmación.

Cualquier decisión futura sobre estos puntos requerirá evidencia, pruebas y aprobación expresa en un Issue separado.

## 13. Criterios de aceptación vinculados al Issue #16

- La rúbrica contiene factores, semántica, límites y justificación obligatoria.
- Tipo de fuente, base de conocimiento e identidad están separados.
- La independencia se evalúa por afirmación y cadena de evidencia, no por número de publicaciones.
- Sindicación, republicación, traducción, citas cruzadas, fuente común, anonimato y análisis sobre datos comunes tienen tratamiento explícito.
- Existen ejemplos independientes, dependientes y desconocidos.
- Se documentan rectificaciones, conflictos, historial insuficiente, fuentes oficiales y contradicciones.
- La propuesta conserva los estados y salvaguardas del Issue #15.
- El propietario revisa y aprueba expresamente la metodología antes de cerrar el Issue o implementar automatización.

**Estado final del documento:** propuesta para revisión. No es una política aprobada, no autoriza scoring ni automatización y no cambia el estado probatorio de ninguna afirmación real.
