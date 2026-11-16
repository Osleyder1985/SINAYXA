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

Dos versiones de un mismo source_id no son dos fuentes independientes. La relación ANÁLISIS_SEPARADO_SOBRE_DATOS_COMUNES puede describir replicación analítica, pero no demuestra independencia del origen de los datos. Si el origen común o las vías no pueden reconstruirse, el estado permanece DESCONOCIDA. La independencia o dependencia no se propaga a otros componentes, versiones o cortes.

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
- archive_service: nombre o identificador del servicio archivístico.
- capture_record_reference: referencia verificable al registro de captura concreto.
- captured_at: instante UTC de la captura acreditada.
- imported_at: instante UTC en que SINAYXA importó el registro, si procede.
- recorded_at: instante UTC de registro en SINAYXA.
- integrity_result: MATCH, MISMATCH, NOT_CHECKED o UNAVAILABLE.
- capture_record_verified: booleano que indica si el registro concreto de captura fue comprobado.
- content_authenticity: UNKNOWN o NOT_ASSESSED.
- content_truth: UNKNOWN o NOT_ASSESSED.

Cada evidence_availability con availability_basis INDEPENDENT_ARCHIVE debe referenciar un archive_attestation_id. La captura debe estar acreditada, la integridad debe ser MATCH y captured_at no puede ser posterior a available_at; available_at no puede superar assessment_cutoff.

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

Las referencias forman un grafo acíclico de copias y derivados. Una transición de estado debe tener exactamente un evento de auditoría correlacionado, identificando copy_id, estado anterior, nuevo estado, actor por rol, instante y motivo.

DELETE_PENDING bloquea el uso analítico nuevo de esa copia desde el instante de transición. DELETED requiere que todas las copias dentro del alcance declarado estén DELETED y tengan verified_at y verification_reference. Una copia o backup pendiente, un derivado no inventariado o una verificación ausente impide declarar la eliminación completa del alcance.

La restauración de un backup no puede reintroducir material terminalmente eliminado a un ámbito de análisis sin reconciliar antes el estado de supresión. El contrato no exige eliminación física instantánea de backups ni fija plazos universales: se conserva la política aplicable y el estado real verificable.

Los eventos de eliminación no deben conservar contenido, hashes, URLs ni metadatos que permitan reconstruir o reidentificar material protegido. La referencia de verificación también debe someterse a minimización y revisión de exposición.

## 6. Manifiesto de migración

Se añade la colección migration_records. Cada migración contiene:

- migration_id: identificador único.
- source_contract_version y target_contract_version.
- migrator_version.
- executed_at: instante UTC.
- input_sha256 y output_sha256: hashes de los paquetes canónicos de entrada y salida.
- rules_applied: lista no vacía de identificadores de reglas de migración.
- result: PASS o REJECTED.
- loss_report: lista de pérdidas o incompatibilidades; debe estar vacía para PASS.

La migración debe validar el paquete de origen con el esquema de su versión y el destino con el esquema objetivo. No puede modificar ni eliminar identificadores, referencias, estados probatorios, atribución, autenticidad, acceso, factores, independencia, cortes temporales, versiones, evidencias, alternativas, incertidumbre, límites, decisiones de retención ni eventos históricos.

No puede completar datos desconocidos mediante inferencias ni convertir DESCONOCIDA en un estado positivo. Los campos que la versión destino no pueda representar deben bloquear la migración o conservarse mediante una regla de compatibilidad explícita y verificable; nunca pueden descartarse silenciosamente.

contract_version y methodology_version son independientes. Cambiar la versión del contrato no reescribe la versión metodológica de una evaluación histórica. Una migración se considera determinista cuando el mismo paquete de entrada, versión del migrador y reglas produce el mismo paquete canónico de salida y el mismo output_sha256.

Una migración con pérdida, referencias rotas, cambios semánticos históricos o hashes inconsistentes debe resultar REJECTED.

## 7. Criterios de conformidad 0.2.1

- JSON Schema Draft 2020-12 define las colecciones y catálogos cerrados nuevos.
- El validador semántico comprueba integridad referencial, temporalidad, cobertura completa, transiciones, grafos acíclicos de copias y preservación de historial.
- Fixtures sintéticos positivos, negativos y fronterizos cubren las cinco áreas.
- CI ejecuta todos los validadores y pruebas sobre el mismo HEAD.
- La matriz de verificación se actualiza con referencias a pruebas y runs reales.
- Ninguna área se declara cerrada por documentación solamente.

La conformidad sintética demuestra que los paquetes satisfacen las reglas representadas; no demuestra verdad empírica, legalidad de un acceso real ni cumplimiento legal de una política de retención concreta.
