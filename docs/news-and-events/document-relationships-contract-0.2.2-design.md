# Especificación de diseño — relaciones documentales (candidata 0.2.2)

- Issue: #146
- Estado: PROPUESTA DE DISEÑO; no es contrato aprobado ni schema normativo.
- Base examinada: contrato 0.2.1 propuesto en PR #85.
- Objetivo: modelar relaciones declaradas entre documentos/versiones distintas sin confundirlas con versiones de una misma fuente ni con procedencia/citación.
- Restricción: no modificar 0.2.1, #15, #16 ni PR #85.

## 1. Problema y alcance

El contrato 0.2.1 representa versiones sucesivas de una misma fuente mediante `source_versions.supersedes_source_version_id`, y relaciones de procedencia mediante `provenance_edges`. Ninguna de esas estructuras expresa una relación documental tipada entre dos documentos distintos, con atribución, alcance y tiempo de conocimiento consultable.

La propuesta incorpora una colección opcional y explícita en una versión futura del contrato. No duplica documentos, afirmaciones ni evidencias: los extremos y evidencias son referencias a objetos ya definidos en el expediente.

Fuera de alcance: descubrimiento automático, crawling, scraping, clasificación automática de verdad/credibilidad, predicción, señales de trading, inferencia causal, autenticación automática de documentos y migración automática de relaciones narrativas.

## 2. Unidad semántica y dirección

Una fila representa **una aserción de relación documental**, no una verdad absoluta.

- `declaring_document_version_id`: documento/version que declara o materializa la relación.
- `target_document_version_id`: documento/version sobre el que recae la relación.
- La dirección es siempre desde el documento declarante hacia el documento objetivo.
- Los dos extremos deben existir en el mismo expediente y ser distintos.
- La aserción debe incluir evidencia que permita localizar la declaración o justificar explícitamente que se trata de una inferencia analítica.
- Una declaración de un emisor prueba que el emisor declaró esa relación; no certifica automáticamente la verdad de todos los datos del documento declarante.

Ejemplo: si el documento B declara que corrige A, B es el declarante y A el objetivo. No invertir la dirección para acomodar una consulta.

## 3. Vocabulario controlado inicial

| Tipo | Significado mínimo | No implica |
| --- | --- | --- |
| `AMENDS` | El documento declarante modifica formalmente el objetivo | Que todo el objetivo quede invalidado |
| `CORRECTS` | El declarante identifica y corrige un error del objetivo | Que el resto del objetivo sea incorrecto |
| `WITHDRAWS` | El declarante retira el objetivo o una parte identificada | Que exista una versión sustituta correcta |
| `REPLACES` | El declarante sustituye el objetivo para un alcance definido | Que la sustitución sea completa si el alcance es parcial |
| `DECLARES_NON_RELIANCE_ON` | El declarante comunica que no debe confiarse en el objetivo/alcance | Que se conozca cuál es el valor correcto |
| `CLARIFIES` | El declarante aclara el sentido o alcance del objetivo | Que lo corrija o lo retire |

La taxonomía es provisional. Una misma pareja de documentos puede tener más de una relación si cada aserción tiene evidencia y alcance diferenciables; aserciones contradictorias no se sobrescriben: se conservan y requieren estado de conflicto/revisión.

## 4. Modelo lógico propuesto

Colección: `document_relationship_assertions`.

| Campo | Tipo/obligación | Regla |
| --- | --- | --- |
| `relationship_assertion_id` | string, requerido | Identidad estable, única |
| `declaring_document_version_id` | ref, requerido | Debe existir |
| `target_document_version_id` | ref, requerido | Debe existir y diferir del declarante |
| `relationship_type` | enum, requerido | Uno de los seis tipos iniciales |
| `attribution_kind` | enum, requerido | `ISSUER_STATEMENT`, `REGULATOR_STATEMENT`, `THIRD_PARTY_REPORT`, `ANALYST_INFERENCE`, `UNKNOWN` |
| `declaring_actor_ref` | ref/null | Actor que declara; no inferir identidad |
| `declaring_actor_role` | string/null | Rol documentado, no texto libre con PII |
| `affected_scope` | array, requerido | Uno o más identificadores de claims, secciones, notas, estados financieros o alcance textual verificable |
| `unaffected_scope` | array | Partes expresamente excluidas de la rectificación; vacío si no consta |
| `supporting_evidence_refs` | array, requerido | Al menos una referencia para una declaración institucional/documental |
| `contrary_evidence_refs` | array | Puede estar vacío; nunca borrar evidencia contraria |
| `asserted_effective_from` | timestamp/null | Inicio de efecto que el declarante afirma; no confundir con publicación |
| `asserted_effective_to` | timestamp/null | Fin afirmado, si existe |
| `declaring_document_published_at` | timestamp/null | Publicación del documento declarante |
| `first_detected_at` | timestamp/null | Primera detección por analista/sistema |
| `retrieved_at` | timestamp/null | Recuperación del artefacto |
| `recorded_at` | timestamp UTC, requerido | Momento de incorporación al expediente; controla cuándo SINAYXA pudo conocer la aserción |
| `review_status` | enum, requerido | `UNREVIEWED`, `IN_REVIEW`, `ACCEPTED_AS_DECLARED`, `DISPUTED`, `REJECTED`, `INCONCLUSIVE` |
| `rationale` | string, requerido | Motivo y límites de la revisión |
| `limitations` | array | Límites explícitos |
| `recorded_by` | string, requerido | Rol/identidad operativa permitida por política |
| `supersedes_relationship_assertion_id` | ref/null | Nueva aserción corrige el registro anterior; no elimina el anterior |

### 4.1 Reglas de alcance

- `affected_scope` identifica exactamente qué parte del documento se declara afectada.
- `unaffected_scope` solo se llena cuando el documento o evidencia identifica expresamente partes no afectadas.
- No inferir que lo no mencionado está validado, correcto o unaffected.
- Si el alcance no puede delimitarse, usar un valor explícito `SCOPE_UNSPECIFIED`/estado de alcance desconocido (decisión final de vocabulario pendiente); no convertirlo en corrección total.
- Las referencias de scope deben poder resolverse a secciones/claims o incluir localizadores verificables; no basta una etiqueta libre ambigua.

### 4.2 Atribución y revisión

Atribución, tipo de relación y revisión son dimensiones independientes:

- `ISSUER_STATEMENT` no equivale a corroboración independiente.
- `THIRD_PARTY_REPORT` no se atribuye al emisor salvo evidencia.
- `ANALYST_INFERENCE` debe declarar método, evidencia favorable/contraria y alternativas; no se presenta como declaración oficial.
- `ACCEPTED_AS_DECLARED` significa que se acepta que el documento hizo esa declaración, no que el contenido sustantivo sea verdadero.
- `REJECTED` conserva la aserción y su motivo; no la borra.

## 5. Tiempo y consultas históricas

Deben mantenerse separados:

1. tiempo de publicación del documento declarante;
2. tiempo efectivo que el declarante afirma para la relación;
3. primera detección;
4. recuperación;
5. registro en SINAYXA.

La vista `as_of` se determina por `recorded_at <= knowledge_cutoff`. El tiempo efectivo declarado se muestra como una afirmación separada y no hace que SINAYXA conozca retroactivamente la relación.

Una relación publicada/detectada después del corte histórico no puede aparecer en la reconstrucción de lo que SINAYXA sabía en ese corte, aunque el declarante diga que surtía efecto desde una fecha anterior. La corrección puede modificar la interpretación actual del pasado, pero no reescribir la evaluación histórica anterior.

No exigir orden cronológico artificial entre primera detección y recuperación si el artefacto fue detectado por un canal y recuperado posteriormente; sí exigir que cada timestamp tenga semántica definida y que `recorded_at` no anteceda a la disponibilidad real del registro en SINAYXA.

## 6. Integridad y grafo

El validador semántico deberá comprobar:

- IDs únicos; extremos existentes y diferentes.
- Evidencias referenciadas existentes, vinculadas al documento declarante o a la inferencia, y disponibles al corte de evaluación.
- Tipo, atribución y estado de revisión dentro de catálogos.
- Scope no vacío; referencias resolubles; no solapamiento contradictorio entre afectado/no afectado sin una explicación explícita.
- `supersedes_relationship_assertion_id` existe, no se auto-referencia, pertenece a la misma relación/extremos/scope compatible y avanza en tiempo de registro.
- No se sobrescriben aserciones; una revisión posterior crea un nuevo registro.
- Relaciones dirigidas de corrección/sustitución/retiro no forman ciclos. La regla de ciclo debe probarse por tipo; no asumir que toda relación documental tiene semántica transitiva.
- Una cadena A←B←C conserva cada arista y sus ámbitos; no inferir que C corrige todos los aspectos de A por transitividad.
- Aserciones contradictorias sobre la misma pareja/tipo/scope se preservan y quedan DISPUTED/INCONCLUSIVE hasta revisión; no se elige una automáticamente.
- No convertir `supersedes_source_version_id` ni `provenance_edges` en relación documental.

## 7. Compatibilidad, versión y migración

- No añadir propiedades a 0.2.1: su schema rechaza propiedades adicionales y su versión es constante.
- Candidato: schema y validador independientes para `0.2.2`; la numeración queda sujeta a política de versionado explícita.
- 0.2.1 sigue validándose con su schema/validador sin cambios.
- Consumidor que no soporte 0.2.2 debe rechazar la versión con error explícito; no ignorar la colección ni degradar a 0.2.1.
- Conversión 0.2.1→0.2.2 puede crear colección vacía si no hay relaciones documentales estructuradas.
- No extraer automáticamente relaciones desde texto libre, orden cronológico o similitud.
- Si hay posibles relaciones narrativas, emitir informe de migración con elementos pendientes de revisión; no marcar conversión sin pérdida semántica.
- Exportación/importación round-trip debe preservar IDs, extremos, scope, atribución, evidencias, estados, tiempos e historial.
- Hashes y manifiestos de migración no sustituyen la validación semántica ni demuestran autenticidad factual.

## 8. Fixtures sintéticos y aceptación

Los casos en `document-relationship-fixtures-v0.2.2.json` son fixtures de diseño, no payloads conformes a un schema 0.2.2 aún inexistente. Incluyen:

- RTI: declaración de no confianza y presentación posterior, manteniendo cada documento distinto.
- Yak: enmienda de alcance parcial; no ampliar la corrección a todas las secciones.
- cadena de tres documentos;
- atribución de tercero;
- contradicción;
- relación posterior al corte;
- extremos inexistentes/idénticos, ciclo y duplicado;
- ausencia de relación inferida por cronología.

Criterio de salida de esta fase: revisión de la semántica, fixtures trazables a los documentos públicos y matriz de aceptación aprobada. Solo entonces implementar schema y validador.

## 9. Fuentes públicas de los ejemplos

- RTI International Metals, 8-K: [SEC filing](https://www.sec.gov/Archives/edgar/data/1068717/000119312513412581/d618235d8k.htm)
- RTI International Metals, 10-K/A: [SEC filing](https://www.sec.gov/Archives/edgar/data/1068717/000119312513436550/d616897d10ka.htm)
- Yak Communications, 10-Q/A: [SEC filing](https://www.sec.gov/Archives/edgar/data/1084544/000119312506085760/d10qa.htm)

Estos documentos sirven para comprobar qué declaró el emisor y el alcance que el propio documento describe. No se presentan como verificación independiente de la verdad de todos los datos subyacentes.

### 9.1 Límites documentales comprobados para RTI

El 8-K de 27-oct-2013 (Item 4.02) informa que Amendment No. 1 al 10-K fue presentado el 24-sep-2013, comunica la conclusión del Comité de Auditoría de que los estados financieros de 2012 previamente presentados ya no debían ser objeto de confianza y anuncia que serían reexpresados mediante Amendment No. 2. El 8-K describe un error computacional adicional en las hojas de cálculo utilizadas para preparar Amendment No. 1 y cuantifica preliminarmente un exceso de USD 1.5 millones en ventas netas e ingreso operativo respecto de Amendment No. 1.

Amendment No. 2 identifica tanto el 10-K original (presentado el 22-feb-2013) como Amendment No. 1 (presentado el 24-sep-2013), y declara que los estados financieros previamente emitidos no debían seguir siendo objeto de confianza. También describe la reexpresión de estados financieros y disclosures relacionados y revisiones a Items 1, 1A, 6, 7, 8, 9A y 15. La propia nota indica que determinados datos intermedios de 2011 permanecen sin cambios respecto a Amendment No. 1.

Implicaciones de modelado:
- El 8-K es el documento que comunica la conclusión y la intención de presentar Amendment No. 2; no es el filing correctivo anual en sí.
- Registrar por separado las relaciones de Amendment No. 2 hacia el 10-K original y hacia Amendment No. 1.
- Conservar los periodos/cifras expresamente no modificados; no ampliar la corrección a todo el historial financiero.

### 9.2 Límites documentales comprobados para Yak

El 10-Q/A Amendment No. 1 declara que modifica estados financieros y notas, revisiones a Item 2 (MD&A) e Item 4 (Controls and Procedures), y que ninguna otra información del Report queda enmendada por ese documento. También declara que el amendment habla desde la fecha original del Report, salvo las certificaciones, y que no actualiza otros eventos posteriores salvo lo indicado.

Implicaciones de modelado:
- El alcance afectado debe limitarse a estados financieros/notas y Items 2 y 4 identificados en la nota explicativa.
- La declaración de que «ninguna otra información» queda enmendada puede conservarse como alcance expresamente no afectado, pero no significa que esa información haya sido verificada o sea correcta.
- La fecha efectiva que el declarante atribuye al amendment no sustituye los tiempos de publicación, detección, recuperación o registro de SINAYXA.
