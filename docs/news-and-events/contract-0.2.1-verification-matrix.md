# Matriz de verificación correctiva del contrato lógico 0.2.1

- Issue: #78
- Base normativa: propuesta 0.2.0 de la PR #85.
- Estado: matriz de trabajo; no constituye aprobación metodológica.
- Alcance: cinco áreas de cobertura mediante fixtures sintéticos y validadores deterministas.
- Límites: no selecciona tecnología de persistencia, no habilita captura real y no fija plazos legales universales.

## 1. Criterio general de cierre

Una área solo se declarará CERRADA cuando existan simultáneamente:

1. Regla normativa precisa y compatible con #15/#16.
2. Fixture positivo, negativo y fronterizo.
3. Validación JSON Schema y validación semántica ejecutable.
4. Prueba automatizada integrada en CI.
5. Evidencia de preservación del historial y de las versiones previas.
6. Resultados PASS sobre el mismo commit revisado. Un estado SKIPPED nunca cuenta como PASS.

Esta matriz define qué debe probarse; su mera existencia no cierra ninguna brecha.

## 2. Área A — Independencia en escenarios complejos

### Regla propuesta — independencia

La independencia se evalúa por componente, corte y conjunto exacto de unidades. Deben distinguirse la independencia de observación/adquisición, la independencia del origen de datos y la independencia del proceso analítico. INDEPENDIENTE exige vías separadas positivamente sustentadas para todas las unidades cubiertas. Dos publicaciones o dos versiones de una fuente no crean dos identidades. El uso de un dataset común no demuestra independencia del origen. La procedencia incompleta conserva DESCONOCIDA.

| ID | Escenario | Resultado esperado |
| --- | --- | --- |
| IND-01 | Dos fuentes observan separadamente el mismo hecho, con orígenes terminales distintos y evidencia disponible al corte | INDEPENDIENTE admisible |
| IND-02 | Dos publicaciones citan o reproducen el mismo documento | DEPENDIENTE si la relación está demostrada |
| IND-03 | Dos versiones de un mismo source_id | No puede ser INDEPENDIENTE |
| IND-04 | Dos análisis independientes sobre un dataset común | Replicación analítica; no independencia del origen de datos |
| IND-05 | Procedencia incompleta y ninguna relación demostrada | DESCONOCIDA |
| IND-06 | Dos vías convergen en un mismo origen terminal | No puede ser INDEPENDIENTE |
| IND-07 | Una unidad carece de vía trazable disponible al corte | DESCONOCIDA |
| IND-08 | Dependencia demostrada para un componente, pero no para otro | No propagar la dependencia entre componentes |

### Pruebas obligatorias — área A

- Rechazar INDEPENDIENTE con menos de dos source_id distintos.
- Rechazar dos versiones de la misma fuente como vías independientes.
- Rechazar evidencia de vía no disponible al assessment_cutoff.
- Rechazar vías que convergen en un mismo origen terminal.
- Rechazar la reutilización de una evaluación para otro componente, versión o corte.
- Aceptar la representación separada de replicación analítica y origen de datos.
- Conservar DESCONOCIDA si la evidencia no permite decidir.

## 3. Área B — Corroboración y suficiencia probatoria

### Regla propuesta — corroboración

Autenticidad, atribución, legitimidad de acceso, naturaleza de la pieza, relación con el componente y suficiencia probatoria son dimensiones distintas. Una fuente primaria auténtica puede acreditar directamente el acto que realizó o el documento que emitió, pero no convierte automáticamente en verdadero todo el contenido declarado.

| ID | Escenario | Resultado esperado |
| --- | --- | --- |
| COR-01 | Documento oficial auténtico demuestra que una institución emitió una declaración | Puede corroborar la emisión, no automáticamente su contenido sustantivo |
| COR-02 | La declaración afirma un hecho externo no observado por el emisor | No extender corroboración al hecho externo |
| COR-03 | Documento auténtico posteriormente rectificado | Preservar versiones y evaluar alcance temporal |
| COR-04 | Documento auténtico con contradicción interna material | No declarar corroboración automática |
| COR-05 | Fuente primaria auténtica, pero conocimiento no directo ni registro original | Rechazar EVIDENCIA_PRIMARIA_DIRECTA |
| COR-06 | Fuentes no primarias con independencia revisada para todas las unidades de apoyo | CORROBORACION_INDEPENDIENTE admisible si la evidencia es suficiente |
| COR-07 | Independencia desconocida o pendiente | Rechazar CORROBORADA basada en independencia |
| COR-08 | Evidencia respalda solo parte del componente | PARCIALMENTE_CORROBORADA con ambos alcances delimitados |
| COR-09 | Hash coincidente sin autenticación ni atribución | No elevar autenticidad ni estado probatorio |
| COR-10 | Acceso privado no autorizado o no determinado | No admitirlo como base de corroboración legítima |

### Pruebas obligatorias — área B

- CORROBORADA por vía primaria directa exige AUTENTICADA, acceso legítimo, pertinencia directa y OBSERVACIÓN_DIRECTA o REGISTRO_ORIGINAL.
- El alcance describe el acto directamente acreditado; no se infiere verdad de afirmaciones externas.
- CORROBORADA por fuentes no primarias exige independencia revisada de todas las unidades de apoyo para el mismo componente y corte.
- Rechazar bases de corroboración incompatibles con tipo y base de conocimiento.
- Mantener integridad, autenticidad, atribución y suficiencia como dimensiones no intercambiables.
- Mantener revisión humana, alternativas y limitaciones.

## 4. Área C — Eliminación verificable y propagación a copias

### Regla propuesta — eliminación

Registrar una solicitud no demuestra que la eliminación terminó. El modelo debe representar el alcance lógico de conservación: copia primaria, réplica, caché, exportación, temporal, derivado y backup. DELETE_PENDING bloquea el uso analítico nuevo desde la transición. DELETED solo se declara cuando se verifica la eliminación de todas las copias dentro del alcance declarado. No se fijan plazos legales ni se afirma eliminación instantánea de backups sujetos a ciclos técnicos.

| ID | Escenario | Resultado esperado |
| --- | --- | --- |
| RET-01 | RETAIN pasa a DELETE_PENDING | Pendiente y no disponible para análisis nuevo |
| RET-02 | Copia primaria eliminada, réplica no eliminada | No declarar DELETED global |
| RET-03 | Caché o exportación derivada sigue accesible | No declarar DELETED global |
| RET-04 | Backup sujeto a expiración documentada | Mantener pendiente para ese alcance hasta verificación |
| RET-05 | Todas las copias del alcance verificadas como eliminadas | DELETED admisible |
| RET-06 | No existe inventario suficiente de derivados | No declarar eliminación completa |
| RET-07 | Evidencia utilizada tras DELETE_PENDING | Rechazar nueva evaluación posterior a la transición |
| RET-08 | Intento de volver a RETAIN después de DELETED | Rechazar sobre el mismo ciclo de vida |
| RET-09 | Hash, URL o log puede revelar fuente protegida | No asumir que el metadato es inocuo |

### Pruebas obligatorias — área C

- Representar copias y derivados mediante sujetos de disposición vinculados a un alcance lógico, sin imponer proveedor o motor.
- Cada transición tiene exactamente un evento correlacionado: origen, destino, actor por rol, instante y motivo.
- DELETE_PENDING no equivale a DELETED.
- DELETED exige evidencia de finalización para todas las copias del alcance.
- Alcance incompleto o copia no verificada impide declarar eliminación global.
- El evento no conserva contenido, digest, URL ni metadatos reidentificadores.
- La restauración de backup no puede reintroducir silenciosamente material terminalmente eliminado; requiere reconciliación/supresión antes de exponerlo.
- Los plazos de backup describen la política aplicable, no una garantía inventada.

## 5. Área D — Confiabilidad de archivos independientes y procedencia temporal

### Regla propuesta — archivos archivísticos

INDEPENDENT_ARCHIVE identifica una base de observación externa, no garantiza automáticamente autenticidad, integridad ni disponibilidad. La fecha archivada solo respalda disponibilidad histórica cuando existen referencias trazables a la captura, al mecanismo archivístico y a la integridad del registro. La confiabilidad del archivo y la disponibilidad temporal son dimensiones separadas.

| ID | Escenario | Resultado esperado |
| --- | --- | --- |
| ARC-01 | Captura identificable, timestamp, referencia verificable e integridad coincidente | Puede sustentar disponibilidad temporal, no autenticidad por sí sola |
| ARC-02 | Timestamp sin mecanismo de captura verificable | UNKNOWN |
| ARC-03 | Captura posterior al assessment_cutoff | No disponible para ese corte |
| ARC-04 | Digest distinto del contenido examinado | MISMATCH |
| ARC-05 | Servicio archivístico conocido, pero captura concreta no verificable | No presumir integridad de la pieza |
| ARC-06 | Captura histórica importada posteriormente | Separar captured_at, imported_at y recorded_at |
| ARC-07 | Fecha declarada por la fuente sin archivo/observación | SOURCE_STATED no acredita disponibilidad |
| ARC-08 | Archivo preserva versión luego modificada | Mantener versiones inmutables y evaluar la pieza exacta |

### Pruebas obligatorias — área D

- No convertir INDEPENDENT_ARCHIVE en autenticidad AUTENTICADA.
- No aceptar fecha declarada como prueba de disponibilidad histórica.
- Requerir referencia de captura y evidencia de integridad para disponibilidad archivística verificada.
- Rechazar evidencia posterior al corte.
- Preservar por separado captura, primera observación, importación, recuperación y registro.
- Si integridad o procedencia no pueden verificarse, conservar UNKNOWN/DESCONOCIDA.

## 6. Área E — Evolución y migración sin pérdida histórica

### Regla propuesta — migración

contract_version y methodology_version son dimensiones independientes. Una migración no puede cambiar el significado de una evaluación, completar desconocidos mediante inferencias, cambiar estados históricos ni destruir referencias. Debe ser explícita, trazable, determinista y validada antes/después.

| ID | Escenario | Resultado esperado |
| --- | --- | --- |
| MIG-01 | Migración 0.2.0 → 0.2.1 del fixture base | Migración válida y esquema destino PASS |
| MIG-02 | Campo nuevo obligatorio sin fuente para derivarlo | Bloquear o preservar UNKNOWN mediante regla explícita; nunca inventar |
| MIG-03 | Migración cambia DESCONOCIDA a INDEPENDIENTE | Rechazar |
| MIG-04 | Migración altera assessment_cutoff o evidencia histórica | Rechazar |
| MIG-05 | Migración descarta campo desconocido con información | Rechazar pérdida silenciosa |
| MIG-06 | Migración repetida sobre mismo input | Resultado determinista, sin duplicación |
| MIG-07 | Cambia metodología, contrato permanece | Preservar metodología histórica |
| MIG-08 | Cambia contrato, metodología permanece | Cambiar contract_version sin alterar methodology_version |
| MIG-09 | No puede preservarse ID o referencia | Fallo cerrado |

### Pruebas obligatorias — área E

- Manifiesto con migration_id, versiones origen/destino, versión del migrador, instante, reglas, resultado y referencias a hashes de entrada/salida.
- Validar origen con esquema original y destino con esquema objetivo.
- Comparar invariantes: IDs, referencias, estados, cortes, versiones, evidencia, independencia, historial y retención.
- Prohibir inferencias para completar datos ausentes.
- Exigir tratamiento explícito de campos desconocidos.
- Probar determinismo y ausencia de duplicados.
- No reescribir methodology_version al migrar contract_version.

## 7. Registro de evidencia y cierre

### Evidencia integrada en CI

- HEAD verificado para esta ejecución: `96947640dfdea07994a6a3e56800eea6f102a7fe`.
- PowerShell quality gate: [run 43787120227](https://github.com/Osleyder1985/SINAYXA/actions/runs/43787120227) — SUCCESS.
- Security and dependency quality gate: [run 43787120479](https://github.com/Osleyder1985/SINAYXA/actions/runs/43787120479) — SUCCESS.
- Suite semántica 0.2.1: 56 tests — PASS (incluye las tres pruebas fronterizas añadidas en `f631a26`).
- JSON Schema Draft 2020-12: PASS.
- Fixture 0.2.1 y validador semántico: PASS.
- Auditoría npm, Gitleaks y OSV PR: SUCCESS. Los pasos SKIPPED no se contabilizan como PASS.
- Artefacto de evidencia PowerShell: [powershell-validation-evidence-43787120227](https://github.com/Osleyder1985/SINAYXA/actions/runs/43787120227).

### Trazabilidad actual por área

| Área | Cobertura positiva/representación | Rechazos negativos | Fronterizos o límites observados | Estado |
| --- | --- | --- | --- | --- |
| A — Independencia | `test_independent_distinct_observation_paths_pass`; `test_021_package_accepts_independent_distinct_terminal_origins`; `test_distinct_analysis_processes_over_common_dataset_are_representable` | `test_independence_rejects_two_versions_of_same_source`; `test_independence_rejects_shared_terminal_origin`; `test_independence_rejects_late_path_evidence`; `test_independence_rejects_missing_source_path`; `test_021_package_rejects_independence_from_analyses_over_common_dataset`; `test_021_package_rejects_independent_status_without_integrated_origin_paths` | Dataset común y replicación analítica se representan por separado; falta trazar explícitamente todos los escenarios IND-01–IND-08 a casos y resultados individuales. | ABIERTA |
| B — Corroboración | `test_primary_statement_scope_passes_only_for_direct_act`; `test_021_package_accepts_primary_corroboration_only_for_directly_observed_act`; `test_021_package_accepts_corroboration_from_reviewed_independent_sources` | `test_primary_evidence_from_unrelated_source_cannot_corroborate`; `test_primary_authenticity_does_not_allow_unsupported_external_claim`; `test_secondary_corroboration_rejects_incomplete_review`; `test_021_package_rejects_independent_corroboration_without_reviewed_independence`; `test_021_package_rejects_primary_corroboration_overclaim` | AMBAS exige simultáneamente prueba primaria directa para las unidades primarias e independencia revisada de todas las unidades de apoyo; falta trazabilidad completa de COR-01–COR-10 y de los casos parciales/contradictorios. | ABIERTA |
| C — Eliminación | `test_deleted_requires_every_copy_and_derivative_verified`; `test_reference_only_retains_no_content_after_verified_copy_deletion`; `test_021_delete_pending_copy_inventory_passes_schema_and_semantics`; `test_021_package_accepts_deletion_after_every_copy_and_replica_is_verified` | `test_deleted_rejects_unverified_backup`; `test_retention_rejects_missing_copy_transition`; `test_delete_pending_requires_outstanding_copy_inventory`; `test_021_deleted_scope_rejects_uninventoried_replica`; `test_021_package_rejects_new_assessment_after_delete_pending`; `test_021_orphan_copy_audit_event_is_rejected` | Se comprueban copias/backup, réplica no inventariada y bloqueo posterior a DELETE_PENDING. `test_deleted_copy_cannot_be_restored_to_present` añade rechazo de restauración directa DELETED→PRESENT; siguen faltando reconciliación segura de backup restaurado y pruebas explícitas de exposición/reidentificación de referencias de auditoría. | ABIERTA |
| D — Archivo | `test_archive_capture_verified_for_cutoff_passes_without_authenticating_content`; `test_021_archive_attestation_is_required_and_does_not_authenticate_content` | `test_archive_timestamp_without_capture_proof_is_rejected`; `test_archive_capture_after_cutoff_is_rejected`; `test_archive_cannot_promote_authenticity`; `test_021_orphan_archive_attestation_is_rejected`; `test_021_archive_integrity_mismatch_is_not_verified_availability` | Se separan captura, importación y corte temporal; falta mapear explícitamente ARC-01–ARC-08, incluidos primera observación/recuperación y versión archivada modificada. | ABIERTA |
| E — Migración | `test_migration_preserves_historical_records_and_versions`; `test_migration_canonical_output_hash_is_deterministic`; `test_021_migration_manifest_is_schema_valid_and_lossless` | `test_migration_rejects_dropped_unknown_source_field`; `test_migration_rejects_historical_status_change`; `test_021_package_rejects_migration_with_incorrect_snapshot_digest`; `test_021_successful_migration_cannot_report_data_loss` | Se valida snapshot origen/destino, determinismo y pérdida. Se añadió un migrador ejecutable 0.2.0→0.2.1 con replay determinista, preservación de cardinalidades y desconocidos explícitos; su nueva prueba integrada queda pendiente de CI. `test_migration_rejects_methodology_version_rewrite` y `test_021_package_rejects_unresolvable_migration_snapshot_reference` cubren además reescritura metodológica y referencias no resolubles. MIG-03/04 y comparación integral de invariantes mantienen cobertura pendiente. | ABIERTA |

### Decisión de cierre

La ejecución histórica sobre `9694764` demuestra que el arnés integrado funcionaba y que los 56 tests pasaban en ese HEAD; la suite ampliada a 59 casos también quedó registrada como pendiente de CI en una iteración posterior. El migrador 0.2.0→0.2.1 y las pruebas nuevas de MIG-02/MIG-06 se incorporaron después; sus resultados no se consideran PASS hasta concluir CI sobre el HEAD actualizado. **No demuestra todavía que cada escenario normativo de la matriz esté cubierto**. Las cinco áreas permanecen ABIERTAS hasta añadir los casos fronterizos restantes, ejecutar de nuevo ambos gates sobre un único HEAD y verificar la preservación histórica. No se infiere aprobación metodológica ni se autoriza merge.

### Trazabilidad individual de escenarios (estado verificable)

La siguiente asignación vincula cada escenario de la matriz con pruebas de la suite correctiva. Una prueba negativa que rechaza un estado no demuestra por sí sola que el contrato represente correctamente el estado alternativo esperado; los huecos se mantienen explícitos.

| Escenario | Prueba directamente relacionada | Resultado de cobertura |
| --- | --- | --- |
| IND-01 | `test_independent_distinct_observation_paths_pass`; `test_021_package_accepts_independent_distinct_terminal_origins` | Positivo cubierto |
| IND-02 | `test_independence_rejects_shared_terminal_origin` | Rechazo de origen convergente; falta caso explícito de republicación/cita |
| IND-03 | `test_independence_rejects_two_versions_of_same_source` | Rechazo cubierto |
| IND-04 | `test_distinct_analysis_processes_over_common_dataset_are_representable`; `test_021_package_rejects_independence_from_analyses_over_common_dataset` | Separación de replicación y origen cubierta |
| IND-05 | `test_021_package_accepts_unknown_independence_when_provenance_is_incomplete` | Representación positiva de DESCONOCIDA validada contra esquema y semántica, sin afirmar independencia ni dependencia |
| IND-06 | `test_independence_rejects_shared_terminal_origin` | Rechazo cubierto |
| IND-07 | `test_independence_rejects_missing_source_path`; `test_021_package_rejects_independent_status_without_integrated_origin_paths`; `test_021_package_accepts_unknown_independence_when_provenance_is_incomplete` | Rechaza INDEPENDIENTE y representa DESCONOCIDA cuando la procedencia no permite decidir |
| IND-08 | `test_021_package_accepts_evidenced_dependency_for_exact_component`; `test_021_package_rejects_dependency_edge_without_evidence`; `test_021_package_rejects_dependency_edge_from_another_component` | La arista debe coincidir en componente y versión; se rechaza una arista asociada a otro componente |
| COR-01 | `test_primary_statement_scope_passes_only_for_direct_act`; `test_021_package_accepts_primary_corroboration_only_for_directly_observed_act` | Emisión/acto directo cubierto |
| COR-02 | `test_primary_authenticity_does_not_allow_unsupported_external_claim`; `test_021_package_rejects_primary_corroboration_overclaim` | Sobreafirmación rechazada |
| COR-03 | — | **Brecha:** rectificación posterior y conservación/versionado temporal |
| COR-04 | — | **Brecha:** contradicción interna material |
| COR-05 | `test_primary_statement_scope_passes_only_for_direct_act` | Alcance directo cubierto; falta mutación específica de base de conocimiento no directa |
| COR-06 | `test_021_package_accepts_corroboration_from_reviewed_independent_sources` | Positivo cubierto |
| COR-07 | `test_secondary_corroboration_rejects_incomplete_review`; `test_021_package_rejects_independent_corroboration_without_reviewed_independence` | Rechazo cubierto |
| COR-08 | — | **Brecha:** estado parcial con alcance sustentado y no sustentado delimitados |
| COR-09 | — | **Brecha:** hash/integridad coincidente sin autenticidad ni atribución |
| COR-10 | `test_ambas_requires_independence_even_when_primary_evidence_exists` | No cubre por sí sola acceso ilegítimo; **brecha** de acceso privado no autorizado/no determinado |
| RET-01 | `test_delete_pending_requires_outstanding_copy_inventory`; `test_021_package_rejects_new_assessment_after_delete_pending` | Pendiente y bloqueo analítico cubiertos |
| RET-02/03 | `test_deleted_requires_every_copy_and_derivative_verified`; `test_021_deleted_scope_rejects_uninventoried_replica` | Copias/derivados incompletos rechazados |
| RET-04 | `test_deleted_rejects_unverified_backup` | Backup no verificado rechazado; falta política de expiración documentada y reconciliación de restauración |
| RET-05 | `test_021_package_accepts_deletion_after_every_copy_and_replica_is_verified` | Positivo cubierto |
| RET-06 | `test_021_deleted_scope_rejects_uninventoried_replica` | Inventario incompleto rechazado |
| RET-07 | `test_021_package_rejects_new_assessment_after_delete_pending` | Rechazo cubierto |
| RET-08 | `test_deleted_copy_cannot_be_restored_to_present` | Rechazo de transición terminal directa cubierto; restauración/reconciliación de backup sigue abierta |
| RET-09 | — | **Brecha:** minimización y riesgo de reidentificación en referencias/eventos |
| ARC-01 | `test_archive_capture_verified_for_cutoff_passes_without_authenticating_content`; `test_021_archive_attestation_is_required_and_does_not_authenticate_content` | Captura/integridad temporal cubiertas |
| ARC-02/05 | `test_archive_timestamp_without_capture_proof_is_rejected`; `test_021_orphan_archive_attestation_is_rejected` | Falta de prueba de captura rechazada |
| ARC-03 | `test_archive_capture_after_cutoff_is_rejected` | Rechazo cubierto |
| ARC-04 | `test_021_archive_integrity_mismatch_is_not_verified_availability` | Mismatch no se considera disponibilidad verificada |
| ARC-06 | `test_archive_import_cannot_predate_capture` | Orden temporal de importación cubierto; primera observación/recuperación no está diferenciada |
| ARC-07 | — | **Brecha:** SOURCE_STATED separado de disponibilidad demostrada |
| ARC-08 | — | **Brecha:** versión archivada modificada y conservación inmutable |
| MIG-01 | `test_021_migration_manifest_is_schema_valid_and_lossless` | Migración sintética válida cubierta |
| MIG-02 | `test_021_real_020_to_021_migration_is_deterministic_without_duplicates`; `test_021_historical_assessed_at_null_is_preserved_for_claim_and_factor` | Representa `claim_assessments.assessed_at=null` sin inferir fecha; conserva los timestamps existentes de `factor_assessments`. La clave sigue siendo obligatoria. |
| MIG-03/04 | `test_migration_rejects_historical_status_change` | Cambio de estado histórico rechazado; corte/evidencia requieren trazabilidad individual |
| MIG-05 | `test_migration_rejects_dropped_unknown_source_field` | Pérdida silenciosa de campo rechazada |
| MIG-06 | `test_021_real_020_to_021_migration_is_deterministic_without_duplicates` | Ejecuta dos veces el migrador real con la misma entrada/plan, compara paquete y snapshots completos, verifica cardinalidades y rechaza reentrada sobre 0.2.1. |
| MIG-07 | `test_migration_rejects_methodology_version_rewrite` | Reescritura metodológica rechazada |
| MIG-08 | `test_migration_preserves_historical_records_and_versions` | Preservación de versiones cubierta; cambio aislado de contract_version necesita caso específico |
| MIG-09 | `test_021_package_rejects_unresolvable_migration_snapshot_reference` | Referencia no resoluble rechazada |

## 8. Fuera de alcance

- Selección de base de datos, motor de grafos o almacenamiento de objetos.
- Persistencia productiva o captura real.
- Automatización de decisiones de credibilidad o veracidad.
- Plazos legales universales sin análisis jurisdiccional y contractual.
- Afirmar eliminación física inmediata de backups cuando la política técnica no lo permite.
- Cambiar #15/#16 sin decisión expresa y trazable.
