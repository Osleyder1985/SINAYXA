# Propuesta de contrato lógico de afirmaciones, fuentes, evidencia y procedencia

- **Issue:** #78
- **Consumidor funcional:** #4
- **Dependencias metodológicas:** #15 y #16 (cerrados)
- **Versión de propuesta:** 0.2.0 (evolución de 0.1.0; pendiente de aprobación expresa)
- **Estado:** PROPUESTA TÉCNICA 0.2.0 — PENDIENTE DE APROBACIÓN EXPRESA
- **Alcance:** contrato lógico neutral respecto al motor de persistencia; no es un esquema físico ni una autorización de captura.

## 1. Objetivo y límites

Definir una representación mínima, versionable y auditable para enlazar afirmaciones, componentes, fuentes, versiones de piezas, evidencias, relaciones de procedencia y evaluaciones. El contrato debe implementar los significados aprobados en #15 y #16 sin crear taxonomías probatorias paralelas.

Esta propuesta no selecciona PostgreSQL, documentos JSON, almacenamiento de objetos ni otra tecnología. Tampoco implementa crawling, captura, vigilancia, evaluación automatizada de credibilidad o clasificación de verdad.

## 2. Principios normativos heredados

1. Los estados probatorios, atribución, autenticidad, identidad, acceso e independencia son dimensiones separadas conforme a #15.
2. Los diez factores cualitativos, sus cinco estados y la revisión humana obligatoria se reutilizan exactamente como quedaron aprobados en #16.
3. La independencia se evalúa por componente. INDEPENDIENTE requiere evidencia positiva de vías separadas; DEPENDIENTE requiere una relación material demostrable; DESCONOCIDA no se transforma en independencia por ausencia de vínculos conocidos.
4. Una republicación, traducción, sindicación o cita no crea un nuevo origen. Un análisis separado sobre datos comunes puede ser replicación analítica, pero no un segundo origen del dato.
5. Toda evaluación conserva evidencia favorable, evidencia contraria, alternativas pertinentes, límites y corte temporal.
6. Ningún estado descriptivo de #16 sustituye un estado probatorio de #15. No hay score, pesos, probabilidades ni ranking.

## 3. Modelo lógico propuesto

### 3.1 Claim

Representa una proposición evaluable, no una noticia completa ni una conclusión del sistema.

Campos mínimos:

- `claim_id`: identificador estable y opaco.
- `claim_version`: versión inmutable de la formulación.
- `proposition`: texto preciso de la proposición.
- `scope`: alcance material y jurisdiccional cuando corresponda.
- `valid_time_start` y `valid_time_end`: periodo al que se refiere la proposición, si se conoce.
- `recorded_at`: instante UTC en que SINAYXA registra esta versión.
- `supersedes_claim_version_id`: versión anterior, si existe.

Una reformulación material crea una nueva versión. No se modifica retrospectivamente la proposición usada en una evaluación histórica.

### 3.2 Claim component

Divide una proposición en componentes verificables sin obligar a descomponerla artificialmente.

Campos mínimos:

- `claim_component_id`, `claim_id`.
- `component_key`: clave estable, por ejemplo entity, date, amount, approval, execution o intent.
- `proposition_fragment`: fragmento concreto evaluado.
- `scope`: alcance exacto del componente.
- `recorded_at` y versión.

Una evaluación limitada a amount no puede confirmar entity, date, approval ni execution. Si no existe descomposición útil, se registra un componente explícito `whole_claim`.

### 3.3 Source

Representa un origen informativo, no una publicación concreta.

Campos mínimos:

- `source_id`: identificador interno opaco; nunca debe contener nombre, correo, teléfono ni otro dato identificativo.
- `created_at` y `recorded_at`.

La entidad Source no guarda una clasificación universal de credibilidad, tipo o función. Estos atributos se evalúan en la relación con cada afirmación/componente y en el corte temporal correspondiente.

### 3.4 Source version

Representa una publicación, documento, registro, versión o pieza concreta atribuida a una fuente.

Campos mínimos:

- `source_version_id`, `source_id`.
- `version_label` o identificador de versión.
- `canonical_reference`: URI solo cuando su conservación y acceso sean legítimos.
- `published_at`, `first_detected_at`, `retrieved_at`: instantes distintos; cada uno puede ser UNKNOWN.
- `content_reference`: referencia a copia preservada únicamente cuando esté permitido.
- `content_hash` y `hash_algorithm`: integridad de la copia, no autenticidad ni veracidad.
- `supersedes_source_version_id`: versión anterior, si existe.
- `recorded_at`.

Las versiones son inmutables. Una rectificación crea otra versión y se vincula al componente corregido; no elimina la anterior.

### 3.4.1 Source identity assessment

La identidad y su visibilidad pueden cambiar con el tiempo. Se registran como evaluación versionada, no como verdad global mutable:

- `source_identity_assessment_id`, `source_id`, `assessment_cutoff`.
- `identity`: IDENTIFICADA, ANÓNIMA_PARA_EL_PÚBLICO, ANÓNIMA_PARA_SINAYXA, SEUDÓNIMA o DESCONOCIDA.
- `anonymous_to_public`, `anonymous_to_publisher`, `anonymous_to_sinayxa`.
- `identity_verified_by_publisher`, `identity_verified_by_sinayxa`.
- `verification_evidence_refs`, `limitations`, `recorded_at`.

La identidad real de fuentes protegidas no se almacena. Una garantía del editor no equivale a verificación por SINAYXA.

### 3.5 Evaluation unit

Conserva exactamente la unidad metodológica aprobada en #16:

`(claim_id, claim_component_id, source_id, source_version, access_path, assessment_cutoff)`

Campos obligatorios:

- Los seis elementos anteriores; `source_version` referencia de forma estable a `source_version_id`, no a un texto de versión reutilizable.
- `assessment_unit_id`: identificador opaco.
- `access_path`: referencia tipada a cómo se obtuvo la pieza, sin confundirla con la legalidad del acceso.
- `assessment_cutoff`: timestamp ISO 8601 en UTC.
- `methodology_version`.
- `source_type`, `source_subtype`, `knowledge_basis`, `institutional_character` y `dissemination`: valores aprobados en #16, evaluados para esta afirmación/componente y esta versión/corte.

La clasificación primaria/secundaria/terciaria depende de la relación de la pieza con la proposición concreta. No se copia como atributo permanente de Source. La identidad se representa mediante una evaluación versionada separada para evitar que una verificación posterior cambie retroactivamente lo que SINAYXA conocía en el corte original.

La base legítima de acceso se conserva aparte con los estados de #15: PÚBLICO_LEGÍTIMO, PRIVADO_AUTORIZADO, SOSPECHA_DE_ACCESO_NO_AUTORIZADO o NO_DETERMINADO. Un acceso sospechoso no se convierte en autorizado por el mero hecho de disponer de una copia.

### 3.6 Evidence item y claim-evidence link

`Evidence item` identifica una pieza o referencia probatoria; `claim-evidence link` especifica qué componente respalda, contradice o contextualiza.

Evidence item:

- `evidence_id`, `source_version_id` cuando exista.
- `factor_dimensions`: dimensiones de #16 a las que esta pieza puede aportar evidencia; cada referencia usada por un factor debe coincidir con la dimensión evaluada.
- `evidence_kind`: documento, registro, declaración, observación, dataset, análisis u otro tipo tipado.
- `information_nature`: AFIRMACIÓN, INDICIO, RUMOR, POSIBLE_FILTRACIÓN, PUBLICACIÓN_OFICIAL o HECHO_OBSERVADO, según #15. Describe la naturaleza de la pieza/señal, no su estado probatorio.
- `content_reference` o referencia externa, si su uso es legítimo.
- `integrity_check`: resultado técnico de integridad de la copia (`algorithm`, `expected_digest`, `observed_digest`, `checked_at`, `result` = MATCH, MISMATCH, NOT_CHECKED o UNAVAILABLE). No acredita autoría, autenticidad ni veracidad.
- `authenticity_status`: estados exactos de #15.
- `access_status`: estados exactos de #15.
- `recorded_at`.

Claim-evidence link:

- `claim_id`, `claim_component_id`, `evidence_id`.
- `evidence_role`: SUPPORTING, CONTRARY o CONTEXTUAL.
- `scope_note`, `limitations` y referencia de evaluación.

Una pieza puede relacionarse con varios componentes mediante enlaces separados. La autenticidad de una pieza no demuestra automáticamente la verdad de todo su contenido. Un hash solo acredita estabilidad/integridad de la copia examinada.

### 3.6.1 Evidence availability

Cada disponibilidad probatoria se registra por pieza, unidad de evaluación y versión exacta de afirmación/componente. El registro contiene `available_at`, `availability_basis` (SINAYXA_OBSERVATION, INDEPENDENT_ARCHIVE, SOURCE_STATED o UNKNOWN), una referencia trazable y `recorded_at`. Si la disponibilidad es desconocida, `available_at` y la referencia quedan nulos y la base es UNKNOWN. Una pieza solo puede sustentar un factor o una evaluación si existe un registro de disponibilidad para la unidad exacta y `available_at` no supera `assessment_cutoff`. La mera fecha de publicación declarada no sustituye una observación sustentada.

### 3.7 Provenance node y provenance edge

El grafo debe permitir nodos de tipo SOURCE_VERSION, EVIDENCE_ITEM, DOCUMENT, DATASET, INTERMEDIARY, INFORMANT o UNKNOWN_ORIGIN. Los identificadores de informantes son pseudónimos no reversibles y no almacenan identidad confidencial. `UNKNOWN_ORIGIN` es un nodo marcador sin identidad ni contenido atribuido; permite representar una procedencia no reconstruida sin crear aristas huérfanas.

Cada arista se orienta **desde el nodo dependiente hacia su antecedente/origen** y contiene:

- `edge_id`.
- `dependent_node_id`, `origin_node_id`. La arista se interpreta como `dependent_node_id → origin_node_id`; no se admiten alias alternativos en el paquete JSON.
- `relation_type`: ORIGEN_DIRECTO, CITA_DE, SINDICADA_DE, DERIVADA_DE, DOCUMENTO_COMÚN, CONTACTO_COMÚN, ORIGEN_NO_DETERMINADO o ANÁLISIS_SEPARADO_SOBRE_DATOS_COMUNES.
  - `ORIGEN_NO_DETERMINADO` debe apuntar a un nodo `UNKNOWN_ORIGIN`; no representa evidencia de que exista una fuente concreta ni autoriza inferir independencia.
- `claim_component_id`: alcance concreto.
- `evidence_refs`: piezas que justifican la relación.
- `recorded_at`, `valid_from`, `valid_to`, cuando proceda.

Las aristas se conservan aunque formen ciclos. El ciclo se marca para revisión y no se cuenta como un origen adicional. Una misma pareja de fuentes puede ser dependiente para un componente e independiente para otro.

### 3.8 Source factor assessment

Una evaluación por fuente, componente y corte temporal contiene exactamente las diez dimensiones de #16:

- RELATION_WITH_FACT.
- ACCESS_AND_PROXIMITY.
- SUBJECT_COMPETENCE.
- TRANSPARENCY_TRACEABILITY.
- RELEVANT_ACCURACY_HISTORY.
- CORRECTIONS_ACCOUNTABILITY.
- INCENTIVES_CONFLICTS.
- INTERNAL_CONSISTENCY.
- CONTRARY_EVIDENCE.
- TEMPORAL_ADEQUACY.

Cada factor contiene:

- `factor_assessment_id`, `assessment_unit_id`, `dimension`.
- `status`: SUSTENTADA, LIMITADA, DESFAVORABLE, DESCONOCIDA o NO_APLICA.
- `justification`.
- `supporting_evidence_refs`, `contrary_evidence_refs`.
- `limitations`, `assessed_at`, `methodology_version`.
- `human_review_status`.

La justificación y las referencias son obligatorias. No se admiten score, weight, probability ni rank. DESCONOCIDA exige indicar qué evidencia no está disponible; NO_APLICA exige explicar por qué la dimensión no resulta pertinente.

### 3.9 Independence assessment

Campos mínimos:

- `independence_assessment_id`.
- `claim_id`, `claim_component_id`, `assessment_unit_ids`.
- `status`: INDEPENDIENTE, DEPENDIENTE o DESCONOCIDA.
- `supporting_evidence_refs`, `dependency_edge_refs`.
- `rationale`, `limitations`, `assessment_cutoff`.
- `methodology_version`, `human_review_status`, `reviewed_at`.

Reglas:

- INDEPENDIENTE exige evidencia positiva y trazable de vías separadas para el componente.
- DEPENDIENTE exige al menos una relación material demostrada.
- DESCONOCIDA se conserva cuando no se demuestra ninguna de las dos situaciones.
- La independencia del proceso analítico y la independencia del origen de los datos son relaciones distintas.

### 3.10 Claim component assessment y revisión histórica

La conclusión probatoria se conserva en una entidad separada de las evaluaciones de fuente:

- `claim_assessment_id`, `claim_id`, `claim_component_id`.
- `evidentiary_status`: exclusivamente estados aprobados en #15.
- `attribution_status`: ATRIBUIDA, NO_ATRIBUIDA o NO_DETERMINADA.
- `supporting_evidence_refs`, `contrary_evidence_refs`.
- `alternatives`, `uncertainty`, `limitations`.
- `assessment_cutoff`, `methodology_version`, `human_review_status`.
- `supersedes_assessment_id`, si una evaluación posterior sustituye la vigente.

Cada reevaluación crea un registro nuevo. No se sobrescriben estado histórico, evidencia ni razonamiento anteriores.

## 4. Matriz de trazabilidad con #4, #15 y #16

|Requisito|Entidades/campos del contrato|Base normativa|
|---|---|---|
|#4 — conservar afirmación y separar sus componentes verificables|Claim, Claim component, Claim component assessment|#15: estado por proposición; #16: evaluación por afirmación/componente|
|#4 — identificar origen y publicaciones derivadas|Source, Source version, Source identity assessment|#15: atribución/identidad separadas; #16: tipo, subtipo, base de conocimiento y difusión|
|#4 — reconstruir republicaciones, citas y origen común|Provenance node/edge, Independence assessment|#15: no contar republicaciones; #16: genealogía y dependencia por componente|
|#4 — conservar correcciones, versiones y evidencia retirada lícitamente|Source version, Claim-evidence link, historial de evaluaciones|#15: preservar versiones y no elevar retroactivamente estados|
|#4 — evaluar factores de fuente sin reputación global|Source factor assessment|#16: diez factores, cinco estados descriptivos, justificación y revisión humana|
|#4 — enlazar soporte, contradicción y contexto por componente|Evidence item, Claim-evidence link, Claim component assessment|#15: estados probatorios y evidencia favorable/contraria; #16: alcance por componente|
|#4 — conservar resultados indeterminados|DESCONOCIDA, NO_RESUELTA, NO_DETERMINADA, UNKNOWN según dimensión|#15/#16: incertidumbre explícita; no convertir ausencia en independencia o falsedad|
|#15 — naturaleza, estado probatorio, atribución, autenticidad, acceso e identidad separados|Evidence item, Claim component assessment, Source identity assessment, Evaluation unit|Vocabulario exacto aprobado en #15|
|#16 — independencia, diez factores y unidad de evaluación exacta|Evaluation unit, Independence assessment, Source factor assessment|Vocabulario y reglas aprobados en #16|

La matriz no crea estados nuevos. Cada valor se interpreta únicamente en la dimensión indicada; los estados de una dimensión no sustituyen ni elevan los de otra.

## 5. Integridad y semántica de datos

1. Toda referencia debe resolver a una entidad existente; no se aceptan aristas, evidencias ni evaluaciones huérfanas.
2. Toda evaluación debe enlazar un claim, un componente, una fuente, una versión y un corte UTC.
3. Las referencias de evidencia favorable y contraria deben estar tipadas y no pueden intercambiarse silenciosamente.
4. La independencia se valida por componente; no se propaga a otros componentes.
5. Los nodos de procedencia y las unidades de evaluación deben versionarse.
6. Los ciclos se conservan y detectan; no generan corroboración adicional.
7. Las correcciones preservan versiones previas y delimitan componentes afectados.
8. UNKNOWN/DESCONOCIDA es un valor explícito de incertidumbre. NULL solo representa ausencia de un campo opcional cuando el contrato lo permita. NO_APLICA requiere justificación y no equivale a desconocido.
9. Todos los timestamps de auditoría y corte se almacenan como instantes UTC; la zona original puede conservarse como metadato separado.
10. No existe una propiedad agregada de credibilidad global.

## 5. Privacidad, acceso y conservación

- `source_id` debe ser opaco y no permitir inferir la identidad de una fuente confidencial.
- No almacenar nombres reales, datos de contacto, claves de identidad ni detalles reidentificadores de fuentes protegidas.
- No copiar contenido privado o restringido sin autorización verificable.
- Si solo puede conservarse una referencia, registrar explícitamente que el contenido no está preservado.
- La retención y eliminación de copias se decidirán según condiciones de acceso, privacidad y obligaciones legales; el historial metodológico no autoriza conservar material ilícito.
- Los registros de auditoría deben documentar quién/qué proceso realizó un cambio sin revelar identidades confidenciales.

## 6. Decisiones recomendadas para aprobación

1. Aprobar este modelo lógico como contrato neutral, sin decidir todavía el motor de persistencia.
2. Mantener entidades separadas para source, source_version, evidence_item, provenance_edge y claim assessment.
3. Usar identificadores opacos estables y versiones inmutables.
4. Usar el grafo tipado y orientado desde dependencia hacia origen.
5. Mantener la unidad de evaluación exacta de #16.
6. Mantener los estados de #15 y #16 sin alias ni agregación.
7. Exigir revisión humana antes de aceptar evaluaciones de credibilidad o independencia.
8. No almacenar identidades confidenciales ni habilitar captura real en esta fase.

## 7. Preguntas que requieren decisión expresa

- ¿Se aprueba el conjunto de entidades y sus límites?
- ¿Se aprueba la orientación de aristas desde dependiente hacia origen?
- ¿Se aprueba el versionado inmutable de piezas y evaluaciones?
- ¿Se aprueba la separación entre Evidence item, claim-evidence link y Claim component assessment?
- ¿Se aprueba mantener el contrato neutral respecto a la base de datos y seleccionar tecnología en una decisión posterior?
- ¿Qué política de retención debe regir las copias legítimas y sus referencias?
- ¿Se aprueba registrar `information_nature` en Evidence item con los valores exactos de #15, separado de `evidentiary_status`?
- ¿Se aprueba el nodo marcador `UNKNOWN_ORIGIN` para aristas cuyo origen no puede reconstruirse?

## 8. Criterios de salida de #78

- Contrato lógico aprobado y versionado.
- Matriz de trazabilidad con #4, #15 y #16.
- Especificación de integridad referencial y semántica de UNKNOWN/NULL/NO_APLICA.
- Fixture de contrato con casos positivos, negativos y fronterizos.
- CI limpio en el HEAD definitivo.
- Decisión expresa del propietario registrada en #78.

Hasta entonces, #4 está desbloqueado metodológicamente, pero no se implementan persistencia, captura ni automatización.

## 9. Especificación temporal normativa (v0.2.0)

Los campos temporales no son intercambiables. Todos los instantes normalizados se expresan en ISO 8601 UTC con sufijo Z. Cuando la fuente aporta una fecha con zona u offset distinto, se conserva además la representación original en original_timestamps; la normalización no debe destruir el texto, zona ni precisión originales.

| Campo | Significado normativo | No significa |
| --- | --- | --- |
| valid_time_start / valid_time_end | Intervalo del mundo real al que se refiere la proposición o componente. | Fecha de publicación o fecha de registro. |
| published_at | Instante declarado o verificable de publicación de esa versión. | Primera vez que SINAYXA la vio. |
| first_publicly_observed_at | Primera observación pública sustentada por una referencia/archivo independiente identificable. | Fecha necesariamente conocida por SINAYXA en ese momento. |
| first_detected_at | Primer instante en que SINAYXA detectó esa versión; exige evidencia de observación o registro de captura. | Fecha de publicación si no existe evidencia de publicación. |
| retrieved_at | Instante en que SINAYXA obtuvo la pieza mediante una vía legítima. | Primera detección ni fecha del acontecimiento. |
| recorded_at | Instante en que el registro/versionado se incorporó al sistema. | Fecha del hecho o de la publicación. |
| available_at | Instante en que una pieza estuvo disponible por la vía de acceso de la unidad, sustentado por una referencia de observación. | Fecha de publicación no verificada ni fecha de recuperación posterior. |
| availability_basis | Base de conocimiento de esa disponibilidad: observación SINAYXA, archivo independiente, declaración de fuente o desconocida. | Prueba automática de autenticidad o legalidad. |
| assessment_cutoff | Límite temporal de la información que podía utilizarse en una evaluación concreta. | Fecha de ejecución actual ni fecha de la fuente. |
| valid_from / valid_to | Vigencia atribuida a una relación de procedencia, si puede establecerse. | Momento de registro de la arista. |

Reglas:

1. Un valor temporal desconocido se representa como null únicamente en campos declarados opcionales; se conserva el motivo de desconocimiento en limitations o en la observación temporal aplicable. No se inventa una fecha.
2. Una fecha parcial no se transforma en un instante exacto. original_timestamps.precision conserva YEAR, MONTH, DAY, MINUTE, SECOND, MILLISECOND o UNKNOWN.
3. first_detected_at y first_publicly_observed_at son distintos. Una publicación anticipada puede ser detectada por SINAYXA antes de un anuncio oficial posterior; el anuncio posterior no modifica el corte histórico anterior.
4. No se exige que published_at preceda siempre a first_detected_at: puede haber timestamps de publicación corregidos, contenido republicado o evidencias de primera observación distintas. La discrepancia debe conservarse y explicarse, no normalizarse silenciosamente.
5. Cuando ambos son conocidos, retrieved_at no puede preceder a first_detected_at para la misma adquisición. Una excepción exige modelar una captura/importación histórica distinta, no alterar el timestamp.
6. El corte de evaluación es inclusivo: solo puede utilizar evidencia disponible en o antes de assessment_cutoff. Evidencia posterior crea una nueva evaluación; nunca reescribe la anterior.
7. La correlación temporal no demuestra causalidad. El contrato solo registra secuencia y límites de conocimiento.

## 10. Contrato formal e integridad semántica (v0.2.0)

El esquema normativo se encuentra en schemas/source-evidence-contract-0.2.0.schema.json y usa JSON Schema Draft 2020-12. El paquete raíz contiene colecciones tipadas para afirmaciones, componentes, fuentes, versiones, evaluaciones, evidencias, enlaces, nodos/aristas de procedencia, factores, independencia, evaluaciones probatorias, retención y auditoría.

El esquema define tipos, campos requeridos, catálogos cerrados, límites básicos y rechazo de propiedades adicionales. El validador semántico complementario comprueba las relaciones que JSON Schema no puede expresar por sí solo:

- unicidad de identificadores dentro de cada colección;
- integridad referencial y coherencia claim/componente;
- correspondencia entre fuente y versión en la unidad de evaluación;
- referencias de evidencia, factores y evaluaciones;
- orientación dependiente → origen y destino UNKNOWN_ORIGIN para ORIGEN_NO_DETERMINADO;
- reglas positivas para INDEPENDIENTE y DEPENDIENTE;
- igualdad de digests para MATCH y desigualdad para MISMATCH;
- secuencia de detección/adquisición y validez de intervalos;
- disponibilidad de cada pieza por unidad y exclusión de evidencia posterior al corte;
- correspondencia de evidencia de factores con su dimensión exacta;
- restricciones de retención y autorización;
- prohibición de campos de score, weight, probability, rank e identidad confidencial.

Los ciclos entre nodos diferentes se conservan. La detección de ciclos no elimina aristas ni añade orígenes; todo ciclo debe quedar disponible para revisión. Una arista no puede apuntarse a sí misma.

### 10.1 Reglas de evaluación probatoria y no herencia

1. Claim component assessment es la única entidad que contiene evidentiary_status; los estados de factor de #16 y de independencia no pueden sustituirlo.
2. CONTRADICHA requiere líneas de evidencia materialmente incompatibles y trazables en ambos sentidos; dos relatos no autenticados o dos etiquetas incompatibles no bastan.
3. REFUTADA requiere evidencia contraria directa y pertinente respecto al componente exacto. Refutar autenticidad de un documento no refuta automáticamente el hecho subyacente.
4. CORROBORADA exige evidencia favorable suficiente para el alcance del componente. Cuando la base sea secundaria, la independencia debe estar demostrada para ese mismo componente y corte; la cantidad de publicaciones no sustituye esa prueba.
5. PARCIALMENTE_CORROBORADA exige identificar el alcance respaldado y no respaldado. No eleva automáticamente otros componentes.
6. NO_CORROBORADA y NO_RESUELTA no significan falsedad. La ausencia de evidencia no se transforma en evidencia contraria.
7. Una evaluación nueva es un registro nuevo que referencia la anterior mediante supersedes_assessment_id; no se modifica la evaluación histórica.
8. Los estados finales no se derivan automáticamente de una regla numérica. Se conserva la justificación humana, evidencia favorable/contraria, alternativas, incertidumbre, limitaciones y corte temporal.

## 11. Política de conservación y ciclo de vida (v0.2.0)

La política predeterminada es **no conservar copias del contenido**. Se conserva una referencia y metadatos mínimos solo cuando su registro sea legítimo y no exponga material protegido.

La conservación de contenido requiere conjuntamente:

- base de acceso/conservación verificada (legal_basis_status=VERIFIED);
- propósito concreto y necesario;
- responsable funcional identificable por rol, no por datos personales innecesarios;
- fecha de revisión y vencimiento revisable;
- alcance de contenido autorizado y controles de acceso adecuados;
- registro de auditoría de la decisión.

No se fija un plazo universal. El vencimiento se determina por la base jurídica, jurisdicción, licencia, autorización y propósito aplicables. Una autorización pendiente, sospechosa o no establecida no permite conservar una copia.

Al vencer o perderse la base legítima:

1. restringir la copia cuando sea necesario para impedir uso adicional;
2. evaluar si corresponde eliminarla;
3. eliminar el contenido cuando la obligación/condición aplicable lo exija;
4. registrar un evento no identificativo de eliminación, sin conservar una copia del contenido ni datos que permitan reconstruir una fuente protegida;
5. mantener solo referencias/metadatos que sigan siendo legítimos.

Un hash, una URL, un identificador o un log también pueden revelar información protegida; no se consideran automáticamente inocuos. La política de retención no autoriza adquirir, descargar ni conservar material privado o ilícitamente obtenido.

## 12. Interoperabilidad y evolución

- El formato canónico de intercambio es JSON UTF-8 validable con JSON Schema Draft 2020-12.
- contract_version identifica la versión semántica del contrato; no se reutiliza para versionar metodología #15/#16.
- Los identificadores son opacos, estables y no contienen datos personales ni secretos.
- Las versiones de afirmaciones, piezas y evaluaciones son inmutables; una corrección crea una nueva versión y referencia explícitamente a la anterior.
- Las propiedades no declaradas se rechazan en el esquema 0.2.0. La evolución compatible añade una versión nueva del esquema o una migración explícita; no se amplía silenciosamente un catálogo cerrado.
- Las fechas se serializan como strings ISO 8601 UTC; los valores originales y su precisión se preservan en observaciones separadas.
- No se prescribe base de datos, motor de grafo, almacenamiento de objetos ni arquitectura de despliegue.

## 13. Evidencia de conformidad y límites

Esquema formal: schemas/source-evidence-contract-0.2.0.schema.json.  
Fixture sintético: tests/fixtures/contracts/source-evidence-contract-v0.2.0.json.  
Validador de integridad semántica: scripts/validation/validate_source_evidence_contract.ps1.  
Pruebas de mutación negativa y ciclo positivo: scripts/validation/test_source_evidence_contract.ps1.  
Validación Draft 2020-12 y compatibilidad #15/#16: scripts/validation/validate_source_evidence_contract_schema.py.  
Dependencias de validación fijadas: requirements-contract-validation.txt.

La conformidad estructural y semántica demuestra que el paquete cumple el contrato y sus invariantes. No demuestra que las afirmaciones sintéticas sean verdaderas, que una fuente real sea creíble, que el acceso a una fuente concreta sea legal ni que una evaluación automatizada pueda sustituir revisión humana.

La aprobación de esta versión requiere que CI valide el esquema formal, ejecute el validador y rechace todas las mutaciones negativas. El estado metodológico de #15 y #16 permanece inalterado; la propuesta 0.2.0 sigue pendiente de aprobación expresa.

## 14. Resolución propuesta de las decisiones de §7

| Pregunta de decisión | Resolución técnica propuesta en v0.2.0 | Estado |
| --- | --- | --- |
| Entidades y límites | Mantener las entidades separadas tal como se especifican en §§3 y 10; Evaluation unit, Source identity assessment y Evidence availability son estructuras explícitas, no duplicados de Source o Evidence item. | PROPUESTA |
| Orientación del grafo | dependent_node_id → origin_node_id; el nodo dependiente apunta a su antecedente. | PROPUESTA |
| Versionado | Inmutable para formulaciones, piezas y evaluaciones; toda corrección crea una versión/registro nuevo y enlaza el anterior. | PROPUESTA |
| Separación de evidencia | Evidence item, claim-evidence link y Claim component assessment permanecen separados. | PROPUESTA |
| Neutralidad tecnológica | JSON Schema define intercambio lógico; no se selecciona motor ni esquema físico. | PROPUESTA |
| Retención | No conservar contenido por defecto; conservar solo con base verificada, propósito necesario, responsable por rol, revisión y vencimiento. No fijar duración universal. | PROPUESTA |
| Naturaleza de la pieza | Reutilizar exactamente los valores de #15, separados del estado probatorio. | PROPUESTA |
| Origen desconocido | Usar UNKNOWN_ORIGIN como nodo marcador no identificativo para evitar aristas huérfanas; no inferir independencia. | PROPUESTA |

Estas resoluciones son parte de la propuesta 0.2.0 y no constituyen aprobación metodológica ni autorización para tratar datos reales. La aprobación expresa del propietario sigue siendo un criterio de salida de #78.

## 15. Identidad de versiones y alcance exacto de las evaluaciones (v0.2.0)

Los identificadores estables de una afirmación o componente no bastan para reconstruir qué formulación exacta fue evaluada. Por ello, cada versión posee un identificador opaco propio:

- claim_id identifica la afirmación a lo largo de su historia;
- claim_version_id identifica una formulación inmutable concreta;
- claim_component_id identifica el componente a lo largo de su historia;
- claim_component_version_id identifica una formulación inmutable concreta del componente.
- source_id identifica el origen mediante un UUID opaco con prefijo src_; no admite nombres, correos ni datos de contacto.

Cada componente versionado referencia exactamente a una versión de la afirmación. La unidad de evaluación aprobada en #16 conserva sus seis elementos originales y añade referencias explícitas a claim_version_id y claim_component_version_id para impedir que una evaluación histórica se interprete contra una formulación posterior.

Los enlaces de evidencia, aristas de procedencia, evaluaciones de independencia y evaluaciones probatorias también quedan vinculados a esas versiones exactas. La relación supersedes debe apuntar a una versión anterior del mismo objeto lógico; nunca puede apuntar a sí misma ni a otra afirmación/componente.

Una modificación material crea una nueva versión. Una corrección de un componente no altera los demás componentes ni invalida automáticamente sus evaluaciones.

## 16. Cobertura obligatoria de factores y revisión humana

Cada evaluation_unit debe contener exactamente una evaluación para cada una de las diez dimensiones aprobadas en #16. No se permite omitir una dimensión, duplicarla ni sustituirla por un factor nuevo. NO_APLICA y DESCONOCIDA se utilizan cuando corresponda, con justificación y límites.

Cada factor conserva human_review_status y reviewed_at. Un estado PENDING no puede presentarse como evaluación revisada. Las conclusiones INDEPENDIENTE o DEPENDIENTE requieren revisión humana registrada; DESCONOCIDA puede permanecer pendiente.

Las conclusiones probatorias CORROBORADA, PARCIALMENTE_CORROBORADA, CONTRADICHA y REFUTADA requieren revisión humana registrada. Una evaluación pendiente no puede consumirse como conclusión final.

Para CORROBORADA basada en fuentes secundarias o terciarias, todas las unidades de fuente que sustentan el componente deben quedar cubiertas por una evaluación de independencia INDEPENDIENTE revisada, vinculada a la misma versión de afirmación y componente. Una evaluación de independencia de otro componente no puede reutilizarse.

Estas restricciones son validaciones de integridad y flujo de revisión; no son una puntuación, regla probabilística ni automatización de la verdad.

## 17. Correcciones de conformance v0.2.0 — revisión posterior

La auditoría de la primera implementación identificó dos invariantes que debían probarse expresamente:

- Los identificadores estables claim_id y claim_component_id se repiten legítimamente a través de versiones; la unicidad se aplica a claim_version_id y claim_component_version_id. El validador debe aceptar versiones sucesivas del mismo objeto lógico y rechazar solo duplicados de versión.
- INDEPENDIENTE requiere al menos dos identidades de fuente distintas y evidencia positiva vinculada a esas fuentes; dos versiones de una misma fuente no constituyen independencia. DEPENDIENTE requiere una arista material, sustentada y aplicable a la versión exacta del componente; UNKNOWN_ORIGIN por sí solo no demuestra dependencia.

La batería amplía sus pruebas positivas y negativas para proteger ambos invariantes. Estas reglas no modifican la metodología aprobada en #15/#16; hacen ejecutables sus restricciones dentro del contrato 0.2.0.
