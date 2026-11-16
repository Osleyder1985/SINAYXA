# ADR-0001 — Entorno para validar eliminación, archivo y migración

- **Estado:** PROPUESTA PARA REVISIÓN; no aprobada como selección tecnológica.
- **Fecha:** 2026-11-16.
- **Issue:** [#91](https://github.com/Osleyder1985/SINAYXA/issues/91).
- **Dependencias:** [#78](https://github.com/Osleyder1985/SINAYXA/issues/78), [#88](https://github.com/Osleyder1985/SINAYXA/issues/88), [#89](https://github.com/Osleyder1985/SINAYXA/issues/89).
- **Ámbito:** laboratorio aislado con datos sintéticos para preparar las pruebas C/D/E. No define persistencia de producción.

## 1. Contexto y problema

El contrato lógico 0.2.1 está aprobado por el propietario, pero las garantías de retención/eliminación, archivo físico inmutable y migración representativa no quedan demostradas por fixtures, hashes o CI. El Issue #89 exige evidencia de operación real y el #91 exige definir primero un entorno y criterios sin seleccionar un proveedor por inferencia.

SINAYXA debe separar al menos dos clases de datos:

1. **Estado estructurado:** afirmaciones, referencias, evaluaciones, versiones, relaciones, cortes temporales y estados de retención.
2. **Objetos de evidencia:** contenido binario o exportaciones archivadas, identificados por versión y digest.

La separación lógica no obliga a elegir ahora dos productos concretos. Sí permite evaluar por separado la capacidad de eliminar registros estructurados y la capacidad de preservar objetos bajo retención WORM.

## 2. Restricciones no negociables

- Datos exclusivamente sintéticos en el laboratorio.
- Sin captura de fuentes reales, crawling, vigilancia ni ingestión automática.
- Sin persistencia productiva, cuentas nuevas, despliegues ni recursos de pago.
- Sin credenciales reales ni datos personales.
- Sin afirmar que una interfaz S3-compatible garantiza por sí misma WORM.
- Mantener `UNKNOWN` / `NOT_VERIFIED` si la evidencia operacional no demuestra el resultado.
- El contrato aprobado no autoriza una política legal de retención ni prevalece sobre obligaciones de eliminación.
- Toda prueba debe poder repetirse sobre un identificador de release/commit, configuración y conjunto de datos fijados.

## 3. Alternativas de entorno

### A. Laboratorio local/autogestionado

**Composición candidata (no seleccionada):**

- PostgreSQL local para registros estructurados.
- Servicio de objetos S3-compatible autogestionado para objetos de prueba, si la implementación concreta demuestra versionado y Object Lock.
- Volúmenes y backups separados para simular primario, réplica, exportación y backup.

**Qué permite probar:**

- Migraciones repetibles y comparación de invariantes.
- Exportación/restauración de PostgreSQL mediante herramientas nativas.
- Flujos de eliminación de filas, objetos y copias bajo control del laboratorio.
- Pruebas de API de retención y versionado con objetos sintéticos.

**Qué NO demuestra por sí solo:**

- Que un operador con control del host no pueda alterar almacenamiento subyacente.
- Independencia física entre primario y backup si comparten host/disco.
- WORM resistente al administrador del proveedor o al operador de infraestructura.
- SLA, durabilidad geográfica o controles de un servicio administrado.

**Riesgos/costes:** carga operativa, actualizaciones, hardening, almacenamiento, energía y necesidad de aislar copias. No se ha calculado coste porque no se ha definido hardware, volumen ni retención.

### B. Servicios administrados

**Composición candidata (no seleccionada):**

- PostgreSQL administrado, con exportación lógica verificable.
- Almacenamiento de objetos administrado con versionado y retención WORM por versión (por ejemplo, S3 Object Lock como referencia de capacidad).
- Exportación de evidencias de configuración, permisos, versión de objeto y fechas de retención.

**Qué permite probar:**

- Controles de retención del servicio y permisos específicos.
- Consultas de metadatos de retención por versión de objeto.
- Separación de responsabilidades entre aplicación y plano de almacenamiento, en la medida documentada por el proveedor.
- Pruebas de exportación y restauración contra un servicio real, cuando exista autorización.

**Qué NO demuestra por sí solo:**

- Que se hayan cubierto todas las copias, cachés, exportaciones y backups.
- Que un delete lógico equivalga a eliminación física inmediata.
- Que un objeto bloqueado pueda borrarse antes de expirar la retención.
- Que la restauración de backup reconcilie automáticamente las disposiciones de eliminación.
- Que el coste sea aceptable o que el servicio esté disponible bajo las condiciones de cuenta, región y jurisdicción del proyecto.

**Riesgos/costes:** cargos por almacenamiento, solicitudes, recuperación, transferencia, replicación y retención; dependencia de proveedor; configuración irreversible o difícil de revertir. No se calculan importes sin región, volumen, operaciones, periodo y cuenta definidos.

### C. Híbrido

PostgreSQL local/autogestionado para el laboratorio de migración y un servicio de objetos administrado para la prueba WORM, o viceversa.

**Ventaja:** separa las pruebas que necesitan portabilidad de base de datos de las que necesitan evidencia de controles de almacenamiento administrado.

**Riesgos:** añade transferencia de datos, credenciales, configuración cruzada, superficie de seguridad y costes. Tampoco evita tener que probar la reconciliación de copias.

## 4. Hechos técnicos relevantes y límites

1. PostgreSQL documenta tres familias de backup: SQL dump, backup a nivel de sistema de archivos y archivado continuo/PITR. `pg_dump` produce una exportación consistente de una base individual; `pg_restore` permite restaurar archivos de formato archive. Esto es útil para un ensayo de migración, pero no constituye por sí solo una estrategia completa de backup de clúster ni prueba recuperación operacional integral.
2. AWS S3 Object Lock exige versionado y protege versiones individuales. Una eliminación simple puede crear un delete marker mientras la versión protegida sigue retenida; una eliminación permanente de la versión bloqueada se rechaza. Por tanto, Object Lock no equivale a una función de borrado y puede entrar en conflicto con obligaciones de supresión si se aplica indiscriminadamente.
3. AWS documenta que, una vez habilitado Object Lock en un bucket, no puede deshabilitarse ni suspenderse el versionado. La elección de bucket y política de retención es, por ello, una decisión de alto impacto que exige revisión previa.
4. La documentación de MinIO describe GOVERNANCE y COMPLIANCE, versionado y protección WORM por versión. La existencia de una implementación S3-compatible no demuestra que una instalación concreta tenga configuración segura, controles de operador equivalentes o condiciones de licencia/coste adecuadas. Cualquier candidata autogestionada debe someterse a comprobación de versión, licencia, configuración y prueba adversarial.

Fuentes oficiales consultadas el 2026-11-16:

- [PostgreSQL 18 — Backup and Restore](https://www.postgresql.org/docs/current/backup.html)
- [PostgreSQL 18 — pg_dump](https://www.postgresql.org/docs/current/app-pgdump.html)
- [PostgreSQL 18 — pg_restore](https://www.postgresql.org/docs/18/app-pgrestore.html)
- [AWS S3 — Locking objects with Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html)
- [AWS S3 — Object Lock considerations](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-managing.html)
- [AWS S3 — Configuring Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-configure.html)
- [MinIO — Object Locking](https://min.io/docs/minio/linux/administration/object-management/object-retention.html)

## 5. Matriz de requisitos de #89 y evidencia exigida

| Requisito #89 | Prueba de laboratorio | Evidencia operacional necesaria para cerrar |
| --- | --- | --- |
| C — Inventario de copias | Inventario sintético de primario, réplica, caché, exportación y backup | Inventario real del proveedor y alcance contractual/técnico |
| C — DELETE_PENDING bloquea lecturas | Intentar lectura y evaluación en cada ruta de acceso | Logs/telemetría del sistema objetivo y prueba negativa reproducible |
| C — Eliminación | Borrar datos sintéticos por capa | Resultado por cada copia/versión y confirmación independiente |
| C — Restauración/reconciliación | Restaurar backup sintético que contenga un registro previamente dispuesto | Prueba real de restauración que demuestre supresión antes de exponer datos |
| C — Retención y excepciones | Simular estados y fechas | Política documentada y evidencia del comportamiento real del servicio |
| C — Reidentificación residual | Revisión de campos y referencias sintéticas | Revisión de privacidad/seguridad del conjunto real de metadatos |
| D — WORM por versión | Crear, versionar, intentar sobrescribir/borrar y consultar retención | Metadatos del objeto/versión exactos, permisos, logs y prueba de rechazo en proveedor |
| D — Recuperación e integridad | Recuperar objeto sintético y verificar digest | Recuperación independiente del objeto exacto, versión y digest |
| E — Baseline | Exportar cardinalidades, IDs, relaciones, estados, timestamps y referencias | Baseline firmado/hasheado del entorno representativo |
| E — Migración | Ejecutar migración 0.2.0→0.2.1 y comparar invariantes | Resultado en entorno representativo, vinculado a release/commit |
| E — Fallo/rollback | Interrumpir ensayo y recuperar snapshot | Evidencia de recuperación/rollback del entorno elegido |
| E — Determinismo | Repetir sobre copias idénticas y comparar salida | Logs, hashes y diferencias explicadas |

Los ensayos locales pueden demostrar que el procedimiento de prueba y las herramientas funcionan. No se contabilizarán como evidencia de proveedor ni cerrarán C/D/E.

## 6. Protocolo mínimo de laboratorio propuesto

1. Crear un conjunto de datos totalmente sintético con IDs fijos y un manifiesto de baseline.
2. Incluir objetos con dos o más versiones, una disposición de eliminación, un backup que preceda a esa disposición y registros relacionados.
3. Exportar la base con formato archive de PostgreSQL y registrar versión de cliente/servidor, parámetros y digest.
4. Restaurar en un destino aislado y comparar cardinalidades, IDs, relaciones, estados, timestamps, versiones, referencias y digests.
5. Ejecutar la reconciliación de eliminación antes de habilitar cualquier lectura de la copia restaurada.
6. En un almacenamiento de objetos de prueba, verificar versionado, retención por versión, permisos y rechazo de borrado/sobrescritura antes de la fecha de expiración. No usar modo COMPLIANCE ni crear bucket bloqueado irreversible hasta aprobación explícita del propietario.
7. Conservar logs y manifiestos sintéticos, borrar el laboratorio y comprobar que no queda ningún recurso creado.
8. Repetir desde el mismo baseline y comparar resultados. Cualquier diferencia no explicada produce FAIL.

## 7. Criterios de seguridad y salida

- No se crean recursos externos ni cargos.
- No se habilita Object Lock irreversible en una cuenta o bucket real.
- No se usan datos reales, credenciales, claves ni endpoints productivos.
- No se expone una restauración antes de completar reconciliación.
- El ensayo se aborta si aparece una conexión externa no prevista, datos no sintéticos, costes, retención no reversible o discrepancia de baseline.
- Evidencia guardada: commit, versión de herramientas, configuración saneada, manifiesto, hashes, logs y resultado PASS/FAIL por prueba.
- La prueba se clasifica como **LAB_SYNTHETIC**; la prueba de proveedor como **OPERATIONAL_EXTERNAL**. Nunca se mezclan.

## 8. Evaluación provisional

No se selecciona una alternativa tecnológica en esta ADR. La decisión segura que puede prepararse sin costes ni servicios externos es especificar primero el protocolo reproducible del laboratorio local con datos sintéticos. La selección de implementación concreta (incluidos productos autogestionados) requiere comprobar licencias, versiones, controles y requisitos del equipo; la alternativa administrada requiere región, estimación de uso, términos de retención y aprobación de costes.

**Recomendación para revisión del propietario:** autorizar únicamente la preparación del laboratorio local sintético, sin despliegue ni persistencia productiva. Mantener la selección de proveedor/servicio administrado y cualquier recurso facturable como decisiones posteriores separadas.

## 9. Consecuencias

- #91 seguirá abierto hasta que el propietario revise esta ADR y se resuelvan sus criterios de aceptación.
- #89 seguirá abierto hasta obtener evidencia operacional externa suficiente.
- #88 seguirá abierto; A–E no se cierran por este documento.
- Esta ADR no cambia la aprobación del contrato 0.2.1 ni autoriza merge de PR #85.
- No habilita captura real, crawling, vigilancia, automatización ni persistencia productiva.
