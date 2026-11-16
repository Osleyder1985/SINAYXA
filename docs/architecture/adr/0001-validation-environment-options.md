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

## 8. Matriz de decisión y datos aún no evaluados

La comparación siguiente evita asignar puntuaciones o pesos sin datos del equipo, volumen, región, jurisdicción y periodo de retención. El estado NOT_ASSESSED significa que no existe evidencia suficiente en esta ADR; no equivale a cumplimiento ni a incumplimiento.

| Criterio de #91 | Local/autogestionado | Administrado | Híbrido | Evidencia necesaria antes de decidir |
| --- | --- | --- | --- | --- |
| Evidencia técnica de exportación/restauración | DOCUMENTABLE; requiere ensayo local | NOT_ASSESSED para proveedor concreto | NOT_ASSESSED | Prueba repetible sobre versiones fijadas |
| Eliminación de primario, réplicas y backups | PARCIAL; depende del control de todas las copias | NOT_ASSESSED | NOT_ASSESSED | Inventario real y prueba de reconciliación |
| WORM por objeto/versión | NOT_ASSESSED para implementación concreta | NOT_ASSESSED para cuenta/región concreta | NOT_ASSESSED | Prueba de retención, permisos y rechazo de borrado |
| Coste total | NOT_ASSESSED | NOT_ASSESSED | NOT_ASSESSED | Hardware/energía/operación o región, volumen, solicitudes, transferencia y retención |
| Límites gratuitos y cargos al excederlos | NOT_ASSESSED | NOT_ASSESSED | NOT_ASSESSED | Tarifas y condiciones oficiales vigentes de cada candidato |
| Disponibilidad desde el entorno de desarrollo | NOT_ASSESSED | NOT_ASSESSED | NOT_ASSESSED | Prueba de conectividad y compatibilidad desde el equipo objetivo |
| Portabilidad y dependencia de proveedor | Mayor control; esfuerzo operativo propio | Depende de formatos/API y condiciones de salida | Riesgo mixto | Exportación completa y restauración fuera del candidato |
| Jurisdicción y ubicación de datos | Depende de ubicación física y administración | Depende de región, contrato y subprocesadores | Depende de ambas capas | País/región, residencia, términos y obligaciones aplicables |
| Reversibilidad | Alta para laboratorio desechable; no asumir para WORM | Puede ser limitada por retención/versionado | Depende de cada componente | Ensayo de rollback y condiciones de terminación |

### Regla de decisión

No se calculará una puntuación total mientras existan criterios críticos NOT_ASSESSED. Antes de seleccionar una alternativa, el propietario deberá fijar:

- equipo y sistema operativo donde se ejecutará el laboratorio;
- jurisdicción y residencia de datos exigidas;
- volumen sintético, número de versiones y periodo de retención de ensayo;
- presupuesto máximo y tolerancia a cargos;
- nivel de evidencia requerido para cada prueba.

La matriz es una comparación de estado de evidencia, no una selección tecnológica. Los valores DOCUMENTABLE o PARCIAL tampoco sustituyen la ejecución de la prueba correspondiente.

### 8.1 Comparación de candidatos concretos (documentación oficial consultada el 2026-11-16)

Esta comparación reduce la indeterminación tecnológica sin seleccionar proveedor, región, licencia de producción ni modalidad de despliegue. Separa el motor relacional del almacén de objetos: no son alternativas intercambiables.

| Capa | Candidato local/autogestionado | Candidato administrado | Hechos verificables y límites |
| --- | --- | --- | --- |
| Base relacional | PostgreSQL 16.3 en contenedor aislado, coherente con el laboratorio #96 | Amazon RDS for PostgreSQL | PostgreSQL 16 documenta SQL dump, backup filesystem y archivado continuo/PITR como familias distintas; `pg_dump` cubre una base individual, no todos los objetos globales del clúster. RDS documenta backups automáticos y PITR dentro del periodo de retención configurado, de 0 a 35 días para una instancia. No equivale a WORM ni a reconciliación de eliminaciones. |
| Objetos/versiones/WORM | MinIO AIStor Free, despliegue single-node | Amazon S3 con Object Lock | Ambos documentan versionado y retención por versión. En ambos, un DELETE sin version ID puede crear un delete marker mientras la versión protegida permanece retenida. Por tanto, ocultar la versión actual no prueba borrado físico ni eliminación terminal. |
| Modelo de operación | Autogestión del host, discos, copias, actualizaciones, permisos y reloj/NTP | Servicio administrado y controles IAM/políticas del proveedor | El local facilita experimentos aislados y control de configuración, pero no independencia física frente al administrador del host. El administrado aporta controles de servicio, pero exige comprobar región, permisos, contratos, logs, copias y comportamiento real. |
| Licencia/límites publicados | MinIO AIStor Free: gratuito para despliegue single-node. La edición MinIO OSS AGPLv3 anterior está EOL y ya no recibe mantenimiento ni parches. Multi-node: Enterprise Lite sujeto a suscripción y límite publicado inferior a 400 TiB; precio exacto no publicado en la página consultada. | AWS S3/RDS: pago por uso; el coste depende de región y consumo. La elegibilidad Free Tier depende de fecha/plan de alta y límites aplicables; no debe suponerse gratuita para esta cuenta. | No se puede tratar MinIO OSS antiguo como una alternativa mantenida equivalente a AIStor Free. No se presupone que el proyecto tenga una suscripción MinIO ni créditos AWS. |
| Reversibilidad | Contenedor/volúmenes desechables para pruebas; los datos/volúmenes deben inventariarse y destruirse explícitamente | S3 Object Lock: una vez habilitado en bucket, no puede deshabilitarse ni suspenderse el versionado | No crear bucket real con Object Lock durante esta fase. Compliance puede impedir la eliminación incluso al administrador/root durante el periodo de retención. |
| Coste | No monetizado: hardware, discos, energía, mantenimiento, respaldo externo y horas operativas | No monetizado: horas de instancia RDS, almacenamiento, backups/snapshots, solicitudes, recuperación, transferencia, replicación y características de gestión de S3 | Faltan región, clase de almacenamiento, instancia, GB-mes, requests, transferencia, retención y número de versiones. No hay base para una cifra mensual responsable. |

#### Riesgos específicos de los candidatos

1. **Amazon S3 Object Lock:** requiere versionado y protege una versión concreta, no todas las versiones futuras por defecto salvo que se configure una política adecuada. Un DELETE simple puede crear un delete marker; la versión bloqueada permanece. En GOVERNANCE existe bypass mediante permisos especiales; COMPLIANCE impide eliminar la versión protegida antes del vencimiento incluso para root. Habilitar Object Lock no puede revertirse deshabilitando el control o suspendiendo versionado. Por su irreversibilidad, queda excluido de cualquier ensayo real sin decisión expresa.
2. **Amazon RDS for PostgreSQL:** la retención de backups automáticos documentada para una instancia es de 0 a 35 días; el PITR se limita a la ventana de backup. AWS factura, entre otros, horas de instancia, almacenamiento, I/O/IOPS cuando aplique, backups/snapshots y transferencia. Estos backups no se consideran por ello un repositorio WORM.
3. **MinIO AIStor:** la edición gratuita publicada es single-node. La edición OSS previa aparece como no mantenida/EOL; no debe recomendarse para un despliegue nuevo que requiera parches de seguridad. AIStor documenta WORM y versionado, pero los delete markers no eliminan las versiones retenidas. Además, la documentación indica que la expiración de todas las versiones no está disponible en buckets con Object Lock; el diseño de eliminación y retención debe probarse por versión y no inferirse de compatibilidad S3.
4. **PostgreSQL 16.3 local:** el laboratorio #96 demuestra backup/restore custom en un contenedor efímero, no PITR ni recuperación de clúster. La propia documentación distingue `pg_dump` de `pg_dumpall` y del archivado continuo; el protocolo de #89 debe declarar qué nivel de recuperación pretende probar.

#### Matriz de evaluación por candidato

| Criterio | PostgreSQL 16.3 + MinIO AIStor Free single-node | Amazon RDS for PostgreSQL + Amazon S3 Object Lock |
| --- | --- | --- |
| Exportación/restauración relacional | DOCUMENTADO; laboratorio PostgreSQL #96 PASS para backup custom/restore | DOCUMENTADO por RDS; ejecución en cuenta/región SIN VERIFICAR |
| WORM por versión | DOCUMENTADO por AIStor; instalación, versión/licencia y prueba adversarial SIN VERIFICAR | DOCUMENTADO por S3; cuenta/región/bucket y prueba adversarial SIN VERIFICAR |
| Eliminación de todas las versiones/copies | REQUIERE PRUEBA; delete marker no equivale a eliminación | REQUIERE PRUEBA; delete marker no elimina versión bloqueada |
| Coste numérico total | NOT_ASSESSED; single-node Free no elimina costes de hardware/operación/backup | NOT_ASSESSED; depende de región, instancia, storage, requests, transfer y retención |
| Límite gratuito | AIStor Free publicado como single-node; no se asume soporte multi-node gratuito | Free Tier sujeto a fecha de alta/plan y límites; no se asume elegibilidad |
| Disponibilidad en el equipo objetivo | NOT_ASSESSED; requiere comprobar despliegue y compatibilidad en Windows 11/Docker del entorno real | NOT_ASSESSED; requiere comprobar conectividad, región y condiciones de acceso |
| Jurisdicción/residencia | NOT_ASSESSED; depende de ubicación física y administración del host | NOT_ASSESSED; requiere región elegida, términos y subprocesadores |
| Reversibilidad | Alta para contenedor efímero sin Object Lock; retención WORM cambia el perfil | Limitada una vez habilitado Object Lock en bucket; no usar sin aprobación |
| Dependencia de proveedor | Menor dependencia de servicio, mayor carga de operación y licencia AIStor | Dependencia de APIs, precios, región y condiciones AWS |

#### Conclusión comparativa no vinculante

- Para **validar migraciones relacionales y procedimientos de backup/restore sin cargos externos**, el candidato local PostgreSQL 16.3 ya tiene evidencia sintética de ejecución mediante #96. Esto no lo convierte en arquitectura productiva recomendada.
- Para **ensayar controles administrados de retención por versión**, Amazon S3 Object Lock es un candidato documentado, pero su irreversibilidad y conflicto potencial con supresión impiden habilitarlo sin diseño de retención aprobado y autorización explícita.
- Para **WORM autogestionado**, MinIO AIStor es el candidato actual documentado; la antigua edición OSS ya no es una opción mantenida. AIStor Free está limitado a single-node, de modo que no acredita independencia física de copias ni alta disponibilidad.
- El **híbrido** podría separar PostgreSQL local de S3 administrado, pero añade transferencia, credenciales, coste y dos planos de administración. No se justifica antes de conocer requisitos de residencia, volumen y presupuesto.

No se asignan pesos ni puntuaciones: los criterios críticos de coste, jurisdicción, disponibilidad en el entorno objetivo y recuperación operacional siguen NOT_ASSESSED. No se recomienda desplegar ni crear cuenta/recursos a partir de esta comparación.

Fuentes oficiales actualizadas:

- [PostgreSQL 16 — Backup and Restore](https://www.postgresql.org/docs/16/backup.html)
- [PostgreSQL 16 — pg_dump](https://www.postgresql.org/docs/16/app-pgdump.html)
- [AWS — S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html)
- [AWS — Configuring S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-configure.html)
- [AWS — Object Lock considerations](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-managing.html)
- [AWS — Amazon RDS for PostgreSQL pricing](https://aws.amazon.com/rds/postgresql/pricing/)
- [AWS — RDS backup retention period](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.BackupRetention.html)
- [MinIO AIStor — Object Locking and Immutability](https://docs.min.io/aistor/administration/object-locking-and-immutability/)
- [MinIO AIStor — Object Deletion](https://docs.min.io/aistor/administration/objects-and-versioning/object-delete/)
- [MinIO — Subscriptions and pricing](https://www.min.io/pricing)

## 9. Evaluación provisional

No se selecciona una alternativa tecnológica en esta ADR. La decisión segura que puede prepararse sin costes ni servicios externos es especificar primero el protocolo reproducible del laboratorio local con datos sintéticos. La selección de implementación concreta (incluidos productos autogestionados) requiere comprobar licencias, versiones, controles y requisitos del equipo; la alternativa administrada requiere región, estimación de uso, términos de retención y aprobación de costes.

**Recomendación para revisión del propietario:** autorizar únicamente la preparación del laboratorio local sintético, sin despliegue ni persistencia productiva. Mantener la selección de proveedor/servicio administrado y cualquier recurso facturable como decisiones posteriores separadas.

## 10. Consecuencias

- #91 seguirá abierto hasta que el propietario revise esta ADR y se resuelvan sus criterios de aceptación.
- #89 seguirá abierto hasta obtener evidencia operacional externa suficiente.
- #88 seguirá abierto; A–E no se cierran por este documento.
- Esta ADR no cambia la aprobación del contrato 0.2.1 ni autoriza merge de PR #85.
- No habilita captura real, crawling, vigilancia, automatización ni persistencia productiva.

## 11. Política obligatoria de versiones del laboratorio

El laboratorio utilizará exclusivamente versiones **estables de disponibilidad general (GA)** y mantenidas en la fecha de preparación de cada ejecución. «Última versión» no significa usar una versión Beta, Alpha, Preview o Release Candidate. Si el último número publicado es pre-release, se utilizará la última versión GA compatible y mantenida, dejando constancia de la excepción.

### Referencia de versiones consultada el 2026-11-16

| Componente | Referencia estable identificada | Política de selección |
| --- | --- | --- |
| PostgreSQL | **18.7** (GA, 2026-11-12) | Usar la última versión menor de la rama estable 18. PostgreSQL 19 RC 2 no se considera GA y queda excluido. |
| MinIO AIStor Server | Imagen oficial `quay.io/minio/aistor/minio`; la documentación oficial indica que `latest` corresponde a la última imagen estable | Resolver el release exacto desde el endpoint oficial de releases inmediatamente antes del ensayo; registrar etiqueta de release, digest SHA-256/SHA-256 OCI, SBOM y licencia. No dejar `:latest` en la configuración reproducible final. |
| MinIO AIStor Client (`mc`) | Último release estable oficial disponible en la fecha de ejecución | Resolver y fijar versión exacta, checksum y SBOM si se publica. |
| Docker Engine | **29.9.3** (2026-11-03) como versión estable documentada más reciente en esta revisión | Confirmar actualización estable más reciente antes del ensayo y registrar versión de Engine, CLI, Compose y plataforma. |

Fuentes oficiales de referencia:

- PostgreSQL: [archivo de noticias](https://www.postgresql.org/about/newsarchive/pgsql/) y [sitio oficial](https://www.postgresql.org/).
- Docker Engine: [notas de versión 29](https://docs.docker.com/engine/release-notes/29/).
- AIStor latest stable image: [instalación en contenedor](https://docs.min.io/aistor/installation/container/install/).
- AIStor release metadata/API y artefactos: [documentación de artefactos](https://docs.min.io/aistor/operations/release-artifacts/) y [API oficial de releases](https://dl.min.io/api/releases/aistor/latest).
- AIStor container deployment for development/testing: [despliegue en contenedor](https://docs.min.io/aistor/installation/container/).

### Reglas de reproducibilidad y seguridad

1. Resolver versiones estables antes de ejecutar; no asumir que un número de versión conocido sigue siendo el último.
2. Registrar para cada imagen: nombre completo, tag inmutable de release, digest OCI, plataforma/arquitectura, fecha UTC de descarga y checksum de los artefactos disponibles.
3. No utilizar etiquetas flotantes (`:latest`) en el manifiesto final de ejecución. Pueden usarse únicamente para descubrir la última versión, seguida de resolución y fijación por digest.
4. Conservar SBOM CycloneDX/SPDX y notas de versión cuando el proveedor las publique; registrar explícitamente cuando no estén disponibles.
5. Verificar firmas/checksums según el mecanismo oficial disponible. No inventar una verificación de firma si el proveedor solo publica checksum.
6. Ejecutar comprobaciones de compatibilidad entre servidor, cliente, Docker Engine, Compose y sistema operativo; documentar incompatibilidades y vulnerabilidades conocidas.
7. Actualizar la matriz de versiones si aparece una versión estable más reciente antes de comenzar el ensayo; una vez iniciado, mantener fijados los artefactos para que la ejecución sea reproducible.
8. Registrar por separado la versión de PostgreSQL del laboratorio y la versión histórica 16.3 usada por PR #96. La prueba anterior sigue siendo evidencia válida para el artefacto ensayado, pero no acredita el comportamiento de PostgreSQL 18.7.
9. No instalar ni descargar software automáticamente en el equipo del propietario; la selección y el manifiesto se preparan primero y el despliegue requiere la autorización operacional correspondiente.

### Criterio de aceptación adicional

El protocolo de #89 no puede comenzar hasta que el manifiesto de versiones esté completo, cada imagen esté fijada por digest y las verificaciones de procedencia disponibles estén registradas. Si no se puede acreditar que un componente es estable/mantenido o resolver su digest, el ensayo queda BLOCKED; no se sustituye silenciosamente por una versión antigua ni por un pre-release.

