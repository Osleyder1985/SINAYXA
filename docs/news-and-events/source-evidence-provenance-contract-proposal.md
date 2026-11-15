# Propuesta de contrato lógico de afirmaciones, fuentes, evidencia y procedencia

- **Issue:** #78
- **Consumidor funcional:** #4
- **Dependencias metodológicas:** #15 y #16 (cerrados)
- **Versión de propuesta:** 0.1.0
- **Estado:** PROPUESTA TÉCNICA NO APROBADA
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
- `source_type`: PRIMARIA, SECUNDARIA, TERCIARIA o DESCONOCIDA.
- `source_subtype`: catálogo aprobado en #16.
- `knowledge_basis`: catálogo aprobado en #16.
- `institutional_character`: OFICIAL, NO_INSTITUCIONAL o DESCONOCIDO.
- `dissemination`: ORIGINAL, SINDICADA, REPUBLICADA, TRADUCIDA, RESUMIDA, ANÁLISIS_PROPIO, COMPILACIÓN o DESCONOCIDA.
- `identity`: valores aprobados en #15/#16.
- `identity_visibility`: visibilidad frente al público, editor y SINAYXA; las verificaciones de un tercero no se transfieren automáticamente.
- `created_at` y `recorded_at`.

La clasificación de tipo se refiere a la relación de la fuente con la afirmación/componente concreto, no a una reputación universal de un dominio o persona. Si el tipo varía por componente, se registra en la relación de evaluación y no se fuerza una etiqueta global.

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

### 3.5 Evaluation unit

Conserva exactamente la unidad metodológica aprobada en #16:

`(claim_id, claim_component_id, source_id, source_version, access_path, assessment_cutoff)`

Campos obligatorios:
- Los seis elementos anteriores.
- `assessment_unit_id`: identificador opaco.
- `access_path`: referencia tipada a cómo se obtuvo la pieza, sin confundirla con la legalidad del acceso.
- `assessment_cutoff`: timestamp ISO 8601 en UTC.
- `methodology_version`.

La base legítima de acceso se conserva aparte con los estados de #15: PÚBLICO_LEGÍTIMO, PRIVADO_AUTORIZADO, SOSPECHA_DE_ACCESO_NO_AUTORIZADO o NO_DETERMINADO. Un acceso sospechoso no se convierte en autorizado por el mero hecho de disponer de una copia.

### 3.6 Evidence item y claim-evidence link

`Evidence item` identifica una pieza o referencia probatoria; `claim-evidence link` especifica qué componente respalda, contradice o contextualiza.

Evidence item:
- `evidence_id`, `source_version_id` cuando exista.
- `evidence_kind`: documento, registro, declaración, observación, dataset, análisis u otro tipo tipado.
- `content_reference` o referencia externa, si su uso es legítimo.
- `integrity_status`: resultado de comprobación de integridad de la copia.
- `authenticity_status`: estados exactos de #15.
- `access_status`: estados exactos de #15.
- `recorded_at`.

Claim-evidence link:
- `claim_id`, `claim_component_id`, `evidence_id`.
- `evidence_role`: SUPPORTING, CONTRARY o CONTEXTUAL.
- `scope_note`, `limitations` y referencia de evaluación.

Una pieza puede relacionarse con varios componentes mediante enlaces separados. La autenticidad de una pieza no demuestra automáticamente la verdad de todo su contenido. Un hash solo acredita estabilidad/integridad de la copia examinada.

### 3.7 Provenance node y provenance edge

El grafo debe permitir nodos de tipo SOURCE_VERSION, EVIDENCE_ITEM, DOCUMENT, DATASET, INTERMEDIARY o INFORMANT. Los identificadores de informantes son pseudónimos no reversibles y no almacenan identidad confidencial.

Cada arista se orienta **desde el nodo dependiente hacia su antecedente/origen** y contiene:
- `edge_id`.
- `from_node_id`, `to_node_id`.
- `relation_type`: ORIGEN_DIRECTO, CITA_DE, SINDICADA_DE, DERIVADA_DE, DOCUMENTO_COMÚN, CONTACTO_COMÚN, ORIGEN_NO_DETERMINADO o ANÁLISIS_SEPARADO_SOBRE_DATOS_COMUNES.
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

## 4. Integridad y semántica de datos

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

## 8. Criterios de salida de #78

- Contrato lógico aprobado y versionado.
- Matriz de trazabilidad con #4, #15 y #16.
- Especificación de integridad referencial y semántica de UNKNOWN/NULL/NO_APLICA.
- Fixture de contrato con casos positivos, negativos y fronterizos.
- CI limpio en el HEAD definitivo.
- Decisión expresa del propietario registrada en #78.

Hasta entonces, #4 está desbloqueado metodológicamente, pero no se implementan persistencia, captura ni automatización.
