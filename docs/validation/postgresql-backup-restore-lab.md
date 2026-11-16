# Laboratorio sintético de backup y restore de PostgreSQL

## Objetivo

Validar `pg_dump` y `pg_restore` con una instancia PostgreSQL efímera, aislada y datos exclusivamente sintéticos. Amplía el laboratorio filesystem de #93; no sustituye las validaciones externas de #89.

## Entorno y límites

- Imagen fijada a PostgreSQL `postgres:16.3`.
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

La comprobación `cleanup` solo puede ser `PASS` si las consultas al daemon Docker terminan correctamente y confirman que tanto el contenedor temporal como el volumen anónimo de datos PostgreSQL ya no existen. El arnés identifica el volumen montado en `/var/lib/postgresql/data` antes de la limpieza y verifica su ausencia después de `docker rm -v`. Si Docker no responde, no puede identificarse el volumen o cualquiera de los dos recursos permanece, el reporte global debe ser `FAIL`; la ausencia de respuesta nunca se interpreta como prueba de eliminación.

## Límites de evidencia

No demuestra backup físico del clúster ni PITR, independencia física de backups externos, WORM/Object Lock, eliminación física, reconciliación de snapshots externos ni migración productiva. Un PASS cubre exclusivamente el ensayo PostgreSQL sintético y no cierra #88, #89, #91 ni las áreas C/D/E.
