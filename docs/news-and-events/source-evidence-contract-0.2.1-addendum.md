# Addendum lógico propuesto — contrato de evidencia y procedencia 0.2.1

- Base: contrato lógico 0.2.0 de la PR #85.
- Issue: #78.
- Estado: PROPUESTA TÉCNICA CORRECTIVA — PENDIENTE DE VALIDACIÓN Y APROBACIÓN.
- Compatibilidad: no modifica los catálogos ni los significados aprobados en #15 y #16.

## 1. Objetivo

Cerrar cinco brechas de cobertura identificadas en la revisión de 0.2.0. La versión 0.2.1 añade estructuras explícitas para demostrar vías independientes complejas, acotar la corroboración directa, seguir copias y derivados sujetos a eliminación, acreditar capturas archivísticas concretas y documentar migraciones sin pérdida histórica.

Este addendum no autoriza persistencia productiva, captura de fuentes reales, crawling ni conservación de contenido.

## 2. Independencia: cobertura exacta de las vías

La evaluación INDEPENDIENTE debe cubrir exactamente las unidades incluidas en la evaluación, con una vía ORIGEN_DIRECTO sustentada por cada source_version_id. Las vías deben aplicar a la misma claim_component_version_id y assessment_cutoff.

Cada vía debe terminar en un origen identificado, terminal y distinto. La evidencia de cada vía debe:

- pertenecer a la versión de fuente dependiente que la vía representa;
- estar vinculada a la evaluación de independencia;
- estar disponible al corte mediante SINAYXA_OBSERVATION o INDEPENDENT_ARCHIVE con su atestación válida;
- no compartir el mismo origen terminal con otra vía de la evaluación.

Dos versiones de un mismo source_id no son dos fuentes independientes. La relación ANÁLISIS_SEPARADO_SOBRE_DATOS_COMUNES puede describir replicación analítica, pero no demuestra independencia del origen de los datos. Cada proceso analítico separado debe tener identidad de proceso, referencia de método, evidencia de salida, componente y corte temporal propios. La colección analysis_processes registra process_id, dataset_origin_id, claim_component_version_id, method_reference, output_evidence_ref, available_at, assessment_cutoff y recorded_at; el validador exige que la salida esté vinculada a una pieza y a su disponibilidad verificada. Si dos procesos usan un dataset común, la replicación analítica puede registrarse sin elevar la independencia del origen de datos. Si el origen común o las vías no pueden reconstruirse, el estado de independencia de fuentes permanece DESCONOCIDA. La independencia o dependencia no se propaga a otros componentes, versiones o cortes.

## 3. Corroboración: alcance de una fuente primaria

La autenticidad de una pieza demuestra, como máximo, la autenticidad de la pieza examinada. No demuestra automáticamente la verdad de cada proposición que contiene.

La base EVIDENCIA_PRIMARIA_DIRECTA solo puede utilizarse cuando:

- la fuente es PRIMARIA para el componente evaluado;
- la pieza está AUTENTICADA;
- el acceso es PÚBLICO_LEGÍTIMO o PRIVADO_AUTORIZADO;
- la base de conocimiento es OBSERVACIÓN_DIRECTA o REGISTRO_ORIGINAL;
- existe un claim_evidence_link SUPPORTING para la versión exacta del componente con scope_note que identifica el acto directamente acreditado;
- la evidencia estaba disponible al corte.

Una declaración institucional puede corroborar que la institución emitió esa declaración. No corrobora por sí sola el hecho externo que la declaración relata si el emisor no lo observó ni lo registró originalmente. El componente y scope_note deben limitar el alcance.

Cuando participe cualquier fuente no primaria en el conjunto de apoyo, CORROBORADA requiere CORROBORACION_INDEPENDIENTE o AMBAS y evaluación INDEPENDIENTE revisada que cubra todas las unidades de apoyo. No se admite mezclar una unidad no primaria en una conclusión basada exclusivamente en evidencia primaria directa.

## 4. Atestación de captura archivística

Se añade la colección archive_attestations. Cada registro contiene:

- archive_attestation_id: identificador opaco.
- evidence_id y source_version_id: vínculo obligatorio con la pieza y versión exactas preservadas.
- captured_content_hash y hash_algorithm: SHA-256 del contenido capturado; debe coincidir con evidence_items.integrity_check.observed_digest.
- archive_service: nombre o identificador del servicio archivístico.
- capture_record_reference: referencia verificable al registro de captura concreto.
- captured_at: instante UTC de la captura acreditada.
- imported_at: instante UTC en que SINAYXA importó el registro, si procede.
- recorded_at: instante UTC de registro en SINAYXA.
- integrity_result: MATCH, MISMATCH, NOT_CHECKED o UNAVAILABLE.
- capture_record_verified: booleano que indica si el registro concreto de captura fue comprobado.
- verification_method: ARCHIVE_API_RETRIEVAL, SIGNATURE_OR_DIGEST_CHECK, INDEPENDENT_RECORD_REVIEW u OTHER.
- verified_at y verified_by_role: instante UTC y rol responsable de la verificación.
- content_authenticity: UNKNOWN o NOT_ASSESSED.
- content_truth: UNKNOWN o NOT_ASSESSED.

Cada evidence_availability con availability_basis INDEPENDENT_ARCHIVE debe referenciar un archive_attestation_id. La atestación debe identificar el mismo evidence_id y source_version_id de la disponibilidad, y su captured_content_hash SHA-256 debe coincidir tanto con expected_digest como con observed_digest de una integrity_check con algorithm SHA-256 y result MATCH; checked_at debe ser posterior a captured_at y anterior o igual a recorded_at. La captura debe estar acreditada, la integridad del registro debe ser MATCH, la verificación debe registrar método, rol e instante, y captured_at no puede ser posterior a verified_at ni a available_at; available_at no puede superar assessment_cutoff. Una misma atestación no puede reutilizarse para otra pieza o versión.

La atestación demuestra evidencia temporal sobre una captura archivística concreta, no autenticidad del autor, legitimidad del acceso original, integridad del contenido fuera de la copia examinada ni veracidad factual. Si falta cualquiera de los elementos exigidos, la disponibilidad histórica se conserva como UNKNOWN; no se sustituye por SOURCE_STATED.

## 5. Inventario de copias y eliminación verificable

Se añade la colección retention_copy_records. Cada copia o derivado se identifica por:

- copy_id: identificador opaco.
- retention_id: registro de retención al que pertenece.
- subject_ref: sujeto lógico del contenido.
- copy_kind: PRIMARY, REPLICA, CACHE, EXPORT, TEMPORARY, DERIVATIVE o BACKUP.
- parent_copy_id: copia de la que deriva, o null si es raíz.
- state: PRESENT, DELETE_PENDING o DELETED.
- recorded_at: instante UTC del último estado registrado.
- verified_at: instante UTC de verificación de eliminación, solo cuando state=DELETED.
- verification_reference: referencia mínima a la evidencia de verificación, solo cuando state=DELETED.
- scheduled_disposition_at: fecha prevista cuando una política de ciclo de vida/backup lo requiera; no equivale a eliminación verificada.

Las referencias forman un grafo acíclico de copias y derivados. Una transición de estado debe tener exactamente un evento de auditoría correlacionado, identificando copy_id, estado anterior, nuevo estado, actor por rol, instante y motivo. La transición de disposition del retention_record también requiere un evento correlacionado con retention_id, subject_ref, from_disposition, to_disposition y acción coherente. DELETED es terminal y solo puede seguir a DELETE_PENDING.

DELETE_PENDING bloquea el uso analítico nuevo de esa copia desde el instante de transición. Cada claim_assessment registra assessed_at, distinto de assessment_cutoff. El validador rechaza una evaluación creada después de la primera solicitud de eliminación cuando usa la evidencia afectada; el corte histórico no se confunde con la hora de ejecución de la evaluación. DELETED requiere que todas las copias dentro del alcance declarado estén DELETED y tengan verified_at y verification_reference. Una copia o backup pendiente, un derivado no inventariado o una verificación ausente impide declarar la eliminación completa del alcance.

La restauración de un backup no puede reintroducir material terminalmente eliminado a un ámbito de análisis sin reconciliar antes el estado de supresión. El contrato no exige eliminación física instantánea de backups ni fija plazos universales: se conserva la política aplicable y el estado real verificable.

Los eventos de eliminación no deben conservar contenido, hashes, URLs ni metadatos que permitan reconstruir o reidentificar material protegido. La referencia de verificación también debe someterse a minimización y revisión de exposición.

## 6. Manifiesto de migración

Se añade la colección migration_records. Cada migración contiene:

- migration_id: identificador único.
- source_contract_version y target_contract_version.
- migrator_version.
- executed_at: instante UTC.
- input_sha256 y output_sha256: hashes del payload canónico de entrada y salida, excluyendo la colección migration_records. La exclusión evita una referencia circular cuando el manifiesto de migración se incluye en el propio paquete; todos los demás campos y colecciones forman parte del digest.
- rules_applied: lista no vacía de identificadores de reglas de migración.
- result: PASS o REJECTED.
- loss_report: lista de pérdidas o incompatibilidades; debe estar vacía para PASS.
- source_snapshot_ref y target_snapshot_ref: referencias resolubles a snapshots inmutables de los paquetes de origen y destino, sin duplicar el contenido del paquete dentro del manifiesto. Los snapshots se validan respectivamente con sus JSON Schema versionados. Se excluye migration_records del digest canónico para evitar autorreferencia; el snapshot destino no puede contener manifiestos anidados.

La migración debe resolver source_snapshot_ref con el esquema de su versión y target_snapshot_ref con el esquema objetivo. El validador integral debe resolver ambas referencias mediante un mecanismo explícito, comprobar sus hashes canónicos, verificar la preservación recursiva de todos los campos históricos y ejecutar la validación semántica del destino. Una referencia sin contenido resoluble y verificable no basta para declarar PASS. La resolución es externa al contrato y no impone motor, proveedor ni forma de almacenamiento. No puede modificar ni eliminar identificadores, referencias, estados probatorios, atribución, autenticidad, acceso, factores, independencia, cortes temporales, versiones, evidencias, alternativas, incertidumbre, límites, decisiones de retención ni eventos históricos.

No puede completar datos desconocidos mediante inferencias ni convertir DESCONOCIDA en un estado positivo. Los campos que la versión destino no pueda representar deben bloquear la migración o conservarse mediante una regla de compatibilidad explícita y verificable; nunca pueden descartarse silenciosamente.

contract_version y methodology_version son independientes. Cambiar la versión del contrato no reescribe la versión metodológica de una evaluación histórica. Una migración se considera determinista cuando el mismo paquete de entrada, versión del migrador y reglas produce el mismo paquete canónico de salida y el mismo output_sha256.

Una migración con pérdida, referencias rotas, cambios semánticos históricos o hashes inconsistentes debe resultar REJECTED.

### 6.1. Preservación de tiempos de evaluación históricos desconocidos

assessed_at es un dato temporal distinto de assessment_cutoff y recorded_at. En paquetes 0.2.0, claim_assessments no contiene un campo equivalente; factor_assessments sí dispone de assessed_at y su valor debe preservarse. Por tanto, el migrador no puede derivarlo de created_at, recorded_at, assessment_cutoff ni de executed_at.

En 0.2.1, assessed_at permanece como propiedad obligatoria en ambas colecciones. En claim_assessments admite null para representar el dato no disponible en el origen; en factor_assessments conserva la semántica y el valor de 0.2.0:

- un timestamp UTC no nulo representa el instante de ejecución conocido y debe respetar las reglas temporales aplicables;
- en claim_assessments, null representa que el instante histórico de evaluación no está disponible en la fuente;
- factor_assessments mantiene su timestamp UTC histórico y no se transforma en null;
- omitir la propiedad es inválido;
- el instante de migración se registra exclusivamente en migration_records.executed_at.

Esta regla conserva la distinción entre desconocimiento y ausencia accidental del campo. No modifica assessment_cutoff, recorded_at ni la metodología histórica.

## 7. Criterios de conformidad 0.2.1

- JSON Schema Draft 2020-12 define las colecciones y catálogos cerrados nuevos.
- El validador semántico comprueba integridad referencial, temporalidad, cobertura completa, transiciones, grafos acíclicos de copias y preservación de historial.
- Fixtures sintéticos positivos, negativos y fronterizos cubren las cinco áreas.
- CI ejecuta todos los validadores y pruebas sobre el mismo HEAD.
- La matriz de verificación se actualiza con referencias a pruebas y runs reales.
- Ninguna área se declara cerrada por documentación solamente.

La conformidad sintética demuestra que los paquetes satisfacen las reglas representadas; no demuestra verdad empírica, legalidad de un acceso real ni cumplimiento legal de una política de retención concreta.
