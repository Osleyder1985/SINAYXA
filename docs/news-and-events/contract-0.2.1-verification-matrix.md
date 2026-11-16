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

### Regla propuesta

La independencia se evalúa por componente, corte y conjunto exacto de unidades. Deben distinguirse la independencia de observación/adquisición, la independencia del origen de datos y la independencia del proceso analítico. INDEPENDIENTE exige vías separadas positivamente sustentadas para todas las unidades cubiertas. Dos publicaciones o dos versiones de una fuente no crean dos identidades. El uso de un dataset común no demuestra independencia del origen. La procedencia incompleta conserva DESCONOCIDA.

| ID | Escenario | Resultado esperado |
|---|---|---|
| IND-01 | Dos fuentes observan separadamente el mismo hecho, con orígenes terminales distintos y evidencia disponible al corte | INDEPENDIENTE admisible |
| IND-02 | Dos publicaciones citan o reproducen el mismo documento | DEPENDIENTE si la relación está demostrada |
| IND-03 | Dos versiones de un mismo source_id | No puede ser INDEPENDIENTE |
| IND-04 | Dos análisis independientes sobre un dataset común | Replicación analítica; no independencia del origen de datos |
| IND-05 | Procedencia incompleta y ninguna relación demostrada | DESCONOCIDA |
| IND-06 | Dos vías convergen en un mismo origen terminal | No puede ser INDEPENDIENTE |
| IND-07 | Una unidad carece de vía trazable disponible al corte | DESCONOCIDA |
| IND-08 | Dependencia demostrada para un componente, pero no para otro | No propagar la dependencia entre componentes |

### Pruebas obligatorias

- Rechazar INDEPENDIENTE con menos de dos source_id distintos.
- Rechazar dos versiones de la misma fuente como vías independientes.
- Rechazar evidencia de vía no disponible al assessment_cutoff.
- Rechazar vías que convergen en un mismo origen terminal.
- Rechazar la reutilización de una evaluación para otro componente, versión o corte.
- Aceptar la representación separada de replicación analítica y origen de datos.
- Conservar DESCONOCIDA si la evidencia no permite decidir.

## 3. Área B — Corroboración y suficiencia probatoria

### Regla propuesta

Autenticidad, atribución, legitimidad de acceso, naturaleza de la pieza, relación con el componente y suficiencia probatoria son dimensiones distintas. Una fuente primaria auténtica puede acreditar directamente el acto que realizó o el documento que emitió, pero no convierte automáticamente en verdadero todo el contenido declarado.

| ID | Escenario | Resultado esperado |
|---|---|---|
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

### Pruebas obligatorias

- CORROBORADA por vía primaria directa exige AUTENTICADA, acceso legítimo, pertinencia directa y OBSERVACIÓN_DIRECTA o REGISTRO_ORIGINAL.
- El alcance describe el acto directamente acreditado; no se infiere verdad de afirmaciones externas.
- CORROBORADA por fuentes no primarias exige independencia revisada de todas las unidades de apoyo para el mismo componente y corte.
- Rechazar bases de corroboración incompatibles con tipo y base de conocimiento.
- Mantener integridad, autenticidad, atribución y suficiencia como dimensiones no intercambiables.
- Mantener revisión humana, alternativas y limitaciones.

## 4. Área C — Eliminación verificable y propagación a copias

### Regla propuesta

Registrar una solicitud no demuestra que la eliminación terminó. El modelo debe representar el alcance lógico de conservación: copia primaria, réplica, caché, exportación, temporal, derivado y backup. DELETE_PENDING bloquea el uso analítico nuevo desde la transición. DELETED solo se declara cuando se verifica la eliminación de todas las copias dentro del alcance declarado. No se fijan plazos legales ni se afirma eliminación instantánea de backups sujetos a ciclos técnicos.

| ID | Escenario | Resultado esperado |
|---|---|---|
| RET-01 | RETAIN pasa a DELETE_PENDING | Pendiente y no disponible para análisis nuevo |
| RET-02 | Copia primaria eliminada, réplica no eliminada | No declarar DELETED global |
| RET-03 | Caché o exportación derivada sigue accesible | No declarar DELETED global |
| RET-04 | Backup sujeto a expiración documentada | Mantener pendiente para ese alcance hasta verificación |
| RET-05 | Todas las copias del alcance verificadas como eliminadas | DELETED admisible |
| RET-06 | No existe inventario suficiente de derivados | No declarar eliminación completa |
| RET-07 | Evidencia utilizada tras DELETE_PENDING | Rechazar nueva evaluación posterior a la transición |
| RET-08 | Intento de volver a RETAIN después de DELETED | Rechazar sobre el mismo ciclo de vida |
| RET-09 | Hash, URL o log puede revelar fuente protegida | No asumir que el metadato es inocuo |

### Pruebas obligatorias

- Representar copias y derivados mediante sujetos de disposición vinculados a un alcance lógico, sin imponer proveedor o motor.
- Cada transición tiene exactamente un evento correlacionado: origen, destino, actor por rol, instante y motivo.
- DELETE_PENDING no equivale a DELETED.
- DELETED exige evidencia de finalización para todas las copias del alcance.
- Alcance incompleto o copia no verificada impide declarar eliminación global.
- El evento no conserva contenido, digest, URL ni metadatos reidentificadores.
- La restauración de backup no puede reintroducir silenciosamente material terminalmente eliminado; requiere reconciliación/supresión antes de exponerlo.
- Los plazos de backup describen la política aplicable, no una garantía inventada.

## 5. Área D — Confiabilidad de archivos independientes y procedencia temporal

### Regla propuesta

INDEPENDENT_ARCHIVE identifica una base de observación externa, no garantiza automáticamente autenticidad, integridad ni disponibilidad. La fecha archivada solo respalda disponibilidad histórica cuando existen referencias trazables a la captura, al mecanismo archivístico y a la integridad del registro. La confiabilidad del archivo y la disponibilidad temporal son dimensiones separadas.

| ID | Escenario | Resultado esperado |
|---|---|---|
| ARC-01 | Captura identificable, timestamp, referencia verificable e integridad coincidente | Puede sustentar disponibilidad temporal, no autenticidad por sí sola |
| ARC-02 | Timestamp sin mecanismo de captura verificable | UNKNOWN |
| ARC-03 | Captura posterior al assessment_cutoff | No disponible para ese corte |
| ARC-04 | Digest distinto del contenido examinado | MISMATCH |
| ARC-05 | Servicio archivístico conocido, pero captura concreta no verificable | No presumir integridad de la pieza |
| ARC-06 | Captura histórica importada posteriormente | Separar captured_at, imported_at y recorded_at |
| ARC-07 | Fecha declarada por la fuente sin archivo/observación | SOURCE_STATED no acredita disponibilidad |
| ARC-08 | Archivo preserva versión luego modificada | Mantener versiones inmutables y evaluar la pieza exacta |

### Pruebas obligatorias

- No convertir INDEPENDENT_ARCHIVE en autenticidad AUTENTICADA.
- No aceptar fecha declarada como prueba de disponibilidad histórica.
- Requerir referencia de captura y evidencia de integridad para disponibilidad archivística verificada.
- Rechazar evidencia posterior al corte.
- Preservar por separado captura, primera observación, importación, recuperación y registro.
- Si integridad o procedencia no pueden verificarse, conservar UNKNOWN/DESCONOCIDA.

## 6. Área E — Evolución y migración sin pérdida histórica

### Regla propuesta

contract_version y methodology_version son dimensiones independientes. Una migración no puede cambiar el significado de una evaluación, completar desconocidos mediante inferencias, cambiar estados históricos ni destruir referencias. Debe ser explícita, trazable, determinista y validada antes/después.

| ID | Escenario | Resultado esperado |
|---|---|---|
| MIG-01 | Migración 0.2.0 → 0.2.1 del fixture base | Migración válida y esquema destino PASS |
| MIG-02 | Campo nuevo obligatorio sin fuente para derivarlo | Bloquear o preservar UNKNOWN mediante regla explícita; nunca inventar |
| MIG-03 | Migración cambia DESCONOCIDA a INDEPENDIENTE | Rechazar |
| MIG-04 | Migración altera assessment_cutoff o evidencia histórica | Rechazar |
| MIG-05 | Migración descarta campo desconocido con información | Rechazar pérdida silenciosa |
| MIG-06 | Migración repetida sobre mismo input | Resultado determinista, sin duplicación |
| MIG-07 | Cambia metodología, contrato permanece | Preservar metodología histórica |
| MIG-08 | Cambia contrato, metodología permanece | Cambiar contract_version sin alterar methodology_version |
| MIG-09 | No puede preservarse ID o referencia | Fallo cerrado |

### Pruebas obligatorias

- Manifiesto con migration_id, versiones origen/destino, versión del migrador, instante, reglas, resultado y referencias a hashes de entrada/salida.
- Validar origen con esquema original y destino con esquema objetivo.
- Comparar invariantes: IDs, referencias, estados, cortes, versiones, evidencia, independencia, historial y retención.
- Prohibir inferencias para completar datos ausentes.
- Exigir tratamiento explícito de campos desconocidos.
- Probar determinismo y ausencia de duplicados.
- No reescribir methodology_version al migrar contract_version.

## 7. Registro de cierre

| Área | Regla | Positivo | Negativo | Fronterizo | CI mismo HEAD | Estado |
|---|---|---|---|---|---|---|
| A — Independencia | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | ABIERTA |
| B — Corroboración | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | ABIERTA |
| C — Eliminación | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | ABIERTA |
| D — Archivo | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | ABIERTA |
| E — Migración | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | ABIERTA |

## 8. Fuera de alcance

- Selección de base de datos, motor de grafos o almacenamiento de objetos.
- Persistencia productiva o captura real.
- Automatización de decisiones de credibilidad o veracidad.
- Plazos legales universales sin análisis jurisdiccional y contractual.
- Afirmar eliminación física inmediata de backups cuando la política técnica no lo permite.
- Cambiar #15/#16 sin decisión expresa y trazable.
