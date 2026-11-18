# Laboratorio sintético de backup y restore de PostgreSQL

## Objetivo

Validar `pg_dump` y `pg_restore` con una instancia PostgreSQL efímera, aislada y datos exclusivamente sintéticos. Amplía el laboratorio filesystem de #93; no sustituye las validaciones externas de #89.

## Entorno y límites

- Imagen de PostgreSQL `postgres:18.7`; el arnés descarga el tag de release concreto, resuelve el `RepoDigest` del artefacto y ejecuta el contenedor por referencia inmutable `repository@sha256:...`.
- El reporte conserva tag, digest, plataforma, versión esperada y versiones reales de servidor/cliente. La ejecución falla si servidor o cliente no corresponden a 18.7.
- El tag es un mecanismo de resolución, no la referencia usada para ejecutar el contenedor.
- Un contenedor temporal y tres bases: origen, restauración y repetición.
- El contenedor se elimina al finalizar, incluso si una comprobación falla.
- No conecta a bases externas ni a bases reales de SINAYXA.
- No usa credenciales reales, datos personales, fuentes reales, buckets ni servicios administrados.
- La descarga inicial de la imagen requiere acceso al registro Docker. Las operaciones de prueba se ejecutan contra el contenedor local.
- El workflow CI usa un runner efímero de GitHub Actions para ejecutar el mismo arnés; esto no equivale a una prueba en el equipo local del propietario.

## Comprobaciones

1. Arranque y disponibilidad del contenedor.
2. Dataset determinista con claves, identidad, restricciones, índices y relaciones.
3. Backup en formato custom, versión, tamaño y SHA-256.
4. Restauración mediante `pg_restore`.
5. Comparación de esquema, datos, cardinalidades, encoding y zona horaria.
6. Rechazo de un archivo deliberadamente truncado.
7. Segunda restauración y comparación de resultados.
8. Eliminación del contenedor y comprobación de limpieza.

## Resultado

El reporte JSON clasifica la ejecución como `LAB_SYNTHETIC` y cada comprobación como `PASS`, `FAIL` o `NOT_RUN`. La limpieza se desglosa en `container_cleanup` y `volume_cleanup`; `cleanup` solo será PASS si ambas comprobaciones son PASS. Un fallo aborta el ensayo y produce un reporte `FAIL`.

La comprobación `cleanup` solo puede ser `PASS` si las consultas al daemon Docker terminan correctamente y confirman que tanto el contenedor temporal como el volumen anónimo de datos PostgreSQL ya no existen. El arnés lee `PGDATA` desde el contenedor en ejecución, inspecciona todos los mounts Docker y localiza el volumen anónimo cuyo destino contiene `PGDATA`. Esto contempla el cambio de la imagen oficial PostgreSQL 18 (`PGDATA=/var/lib/postgresql/18/docker`, volumen `/var/lib/postgresql`) y evita asumir la ruta histórica `/var/lib/postgresql/data`. El reporte registra `PGDATA` y el destino del volumen, y verifica la desaparición del volumen identificado después de `docker rm -v`. Si Docker no responde, no puede identificarse el volumen o cualquiera de los dos recursos permanece, el reporte global debe ser `FAIL`; la ausencia de respuesta nunca se interpreta como prueba de eliminación.

El arnés normaliza exclusivamente las líneas de guardia `\\restrict` y `\\unrestrict` que PostgreSQL 18 genera con tokens aleatorios en cada volcado. No elimina ni omite sentencias DDL, datos, restricciones o índices de la comparación.

## Evidencia de ejecución PostgreSQL 18.7

Ejecución CI: [run #43937072219](https://github.com/Osleyder1985/SINAYXA/actions/runs/43937072219) — **SUCCESS**.

- Imagen: `postgres:18.7`; referencia de ejecución: `postgres@sha256:2ea8630df176ad090ec92136dee850397c5af8781e4bcf2e4162593691c61bbc`.
- Plataforma: `linux/amd64`.
- Docker Engine/CLI: `29.10.0` / `29.10.0`, fijados con `docker/setup-docker-action` v5 por commit `3f1ab1ab0e29231562e4db4ca600c1a49653bac6`; el arnés rechaza cualquier otra versión.
- Servidor y cliente: PostgreSQL 18.7.
- `PGDATA=/var/lib/postgresql/18/docker`; volumen anónimo montado en `/var/lib/postgresql`.
- Dataset sintético: 3 activos y 4 observaciones.
- Backup custom: 5.980 bytes; SHA-256 `52cb1250653716c6d10072847392a1bc5da57a3fb37b1b2c06599d4fb627a813`.
- Diez comprobaciones: **10/10 PASS**, incluidas integridad, restauración repetida, rechazo del dump truncado y eliminación del contenedor/volumen.
- Reporte: artefacto `postgresql-synthetic-lab-43937072219`; `status=PASS`, `synthetic_data_only=true`, `production_data_used=false`, `external_database_connections=false`.

Security/dependency gate: [run #43937072696](https://github.com/Osleyder1985/SINAYXA/actions/runs/43937072696) — SUCCESS. Gitleaks, npm audit y OSV PR scan SUCCESS; OSV full SKIPPED, no contabilizado como PASS.

Esta evidencia sustituye la versión 16.3 como prueba de referencia para la ejecución actual del laboratorio, pero no demuestra ejecución en el equipo local del propietario ni cierra las brechas externas de #89.

## Reconciliación de disposiciones posteriores al backup — Issue #113

El arnés amplía el ensayo con un caso sintético separado del backup:

1. El backup se genera cuando existen tres activos sintéticos y cuatro observaciones.
2. Una disposición posterior `DELETE\t3` se conserva en un ledger temporal independiente, que no forma parte del backup.
3. La restauración permanece inaccesible para el rol consumidor: se revoca `CONNECT` a `PUBLIC` y no se concede al consumidor antes de validar el ledger.
4. Con el ledger válido y la referencia resoluble, se eliminan el activo y sus observaciones relacionadas; repetir la operación conserva el mismo estado final.
5. Solo después se concede acceso al consumidor. Este observa dos activos y no puede consultar el activo dispuesto.
6. Una única función `reconcile_and_open` se usa en los cuatro escenarios. Comprueba existencia del ledger, formato estricto, resolución de referencia y postcondiciones; solo concede `CONNECT` y permisos de lectura después de reconciliar correctamente.
7. La misma función rechaza un ledger ausente, uno malformado y una referencia desconocida. Cada rechazo se verifica mediante un intento de conexión del consumidor, que debe continuar denegado.
8. La misma función procesa por segunda vez el ledger válido y comprueba que el estado resultante no cambia.
9. Antes de exponer la base, se comparan los campos exactos de los dos activos y tres observaciones no afectados, no solo sus cardinalidades.

El reporte versión 1.3.0 registra por separado `restore_gate_before_reconciliation`, `restore_reconciliation`, `missing_ledger_fail_closed`, `invalid_ledger_fail_closed`, `unknown_reference_fail_closed`, `reconciliation_gate_function` y `preserve_unaffected_records`.

**Interpretación:** esto prueba la secuencia de control de acceso y reconciliación mediante una única función del arnés en una instancia PostgreSQL efímera con ledger sintético. No es una implementación de producción ni prueba persistencia o autenticidad del ledger. No demuestra que un ledger externo sea duradero, independiente, autenticado o resistente a alteraciones; tampoco elimina el backup original ni sus copias. No es evidencia de borrado físico ni cierra #89 o el Área C de #88.

## Límites de evidencia

No demuestra backup físico del clúster ni PITR, independencia física de backups externos, WORM/Object Lock, eliminación física, reconciliación de snapshots externos ni migración productiva. Un PASS cubre exclusivamente el ensayo PostgreSQL sintético y no cierra #88, #89, #91 ni las áreas C/D/E.
