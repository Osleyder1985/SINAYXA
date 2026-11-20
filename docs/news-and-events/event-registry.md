# Registro operativo de acontecimientos — Issue #2

**Estado:** registro base (#106), concurrencia/inmutabilidad (#108), conflictos/decisiones (#109), evaluaciones/manifiestos (#110) y almacenamiento de artefactos/endurecimiento TRUNCATE (#111) integrados en `main`.  
**Persistencia:** PostgreSQL local 18.7.  
**Uso autorizado:** entrada explícita del operador; datos sintéticos y archivos reales solo cuando el operador disponga de autorización aplicable.  
**Fuera de alcance:** obtención automática de fuentes reales, crawling, vigilancia, scraping y servicios externos.

## 1. Capacidades implementadas

- Crear un registro de acontecimiento con identificador estable, descripción, activos relacionados, fuentes conocidas y fecha de creación.
- Añadir referencias de fuentes posteriores sin reescribir el registro original.
- Anexar afirmaciones temporales versionadas (ACTUAL, SCHEDULED, ESTIMATED, UNKNOWN). PostgreSQL asigna `recorded_at` mediante `clock_timestamp()` y persiste el mismo instante en `inserted_at`; el cliente no puede retrotraer cuándo el registro conoció la afirmación.
- Validar cada paquete con JSON Schema Draft 2020-12 y las invariantes semánticas del contrato 1.0.0.
- Consultar qué versiones estaban registradas a un corte UTC y recuperar el historial completo.
- Registrar conflictos entre afirmaciones del mismo acontecimiento y decisiones humanas con evidencia favorable/contraria, alcance, justificación y limitaciones.
- Reconstruir el estado de cada conflicto desde decisiones append-only y consultar el historial conocido en un corte de inserción UTC.
- Derivar estados temporales bajo demanda y generar manifiestos SHA-256 con canonicalización RFC 8785.
- Conservar y verificar bytes originales de fuentes y evidencias suministrados explícitamente por el operador.
- Impedir UPDATE/DELETE y TRUNCATE en las nueve tablas append-only del registro.

Las consultas históricas utilizan `inserted_at`, asignado por PostgreSQL al incorporar cada fila, y no la fecha del acontecimiento ni el `recorded_at` declarado en el payload. Así, una validación lenta no puede hacer aparecer una afirmación antes de que la fila exista realmente en el registro.

## 2. Preparación local (PowerShell)

Instalar PostgreSQL 18.7 y Python 3.12 en el entorno local autorizado. Crear una base de datos local vacía y establecer la cadena de conexión en la sesión:

```powershell
python -m pip install --requirement requirements-temporal-contract-validation.txt
$env:SINAYXA_DATABASE_URL = "postgresql://USUARIO:CONTRASENA@localhost:5432/sinayxa"
python -m scripts.news_and_events.register_event init
```

La inicialización aplica en orden las migraciones SQL numeradas (`0001`, `0002`, `0003`, etc.). `0002_temporal_conflicts.sql` añade conflictos y decisiones; `0003_temporal_assessments_manifests.sql` añade evaluaciones y manifiestos. Las migraciones son idempotentes. La base de datos y sus credenciales permanecen bajo control local del operador.

## 3. Registrar un acontecimiento

Crear un archivo JSON, por ejemplo event.json:

```json
{
  "event_id": "event-protocol-release-001",
  "description": "Lanzamiento programado de una actualización de protocolo (ejemplo sintético).",
  "affected_asset_refs": ["asset-example"],
  "source_refs": ["source-calendar-example"],
  "created_at": "2026-11-16T12:00:00Z"
}
```

Ejecutar:

```powershell
python -m scripts.news_and_events.register_event create-event --input .\event.json
```

Las referencias iniciales se conservan con el registro. Una fuente conocida posteriormente se incorpora sin modificar el acontecimiento original:

```powershell
python -m scripts.news_and_events.register_event add-source --event-id event-protocol-release-001 --source-ref source-follow-up-example
```

## 4. Añadir una afirmación temporal

Crear assertion-v1.json:

```json
{
  "temporal_assertion_id": "event-protocol-release-001-v1",
  "event_id": "event-protocol-release-001",
  "version": 1,
  "temporal_role": "SCHEDULED",
  "precision": "DAY",
  "interval_start": {"value": "2026-12-10T00:00:00Z", "inclusive": true},
  "interval_end": {"value": "2026-12-10T23:59:59Z", "inclusive": true},
  "approximation": false,
  "original_value": "2026-12-10",
  "original_timezone": "UTC",
  "original_offset": "+00:00",
  "normalized_start_utc": "2026-12-10T00:00:00Z",
  "normalized_end_utc": "2026-12-10T23:59:59Z",
  "source_ref": "source-calendar-example",
  "evidence_ref": "evidence-calendar-example",
  "retrieved_at": "2026-11-16T12:03:00Z",
  "recorded_at": "2026-11-16T12:04:00Z",
  "supersedes_assertion_id": null,
  "published_at": "2026-11-16T12:01:00Z",
  "first_observed_at": "2026-11-16T12:02:00Z"
}
```

Anexar la versión:

```powershell
python -m scripts.news_and_events.register_event append-assertion --input .\assertion-v1.json
```

Si la agenda cambia, se añade una segunda afirmación con version: 2, un nuevo temporal_assertion_id y supersedes_assertion_id apuntando a la versión inmediatamente anterior. No se edita ni se elimina la primera versión.

## 5. Consultar historia y cortes temporales

Historial completo:

```powershell
python -m scripts.news_and_events.register_event history --event-id event-protocol-release-001
```

Información conocida en un instante concreto:

```powershell
python -m scripts.news_and_events.register_event show-as-of --event-id event-protocol-release-001 --cutoff-utc 2026-11-16T12:03:30Z
```

El corte debe expresarse en UTC con sufijo Z. La consulta excluye las filas cuya inserción real (`inserted_at`) sea posterior al corte, aunque su `recorded_at` de payload se haya asignado unos microsegundos antes durante la validación.

## 6. Registrar conflictos y decisiones

Un conflicto enlaza al menos dos afirmaciones temporales del mismo acontecimiento. El registro inicial siempre se crea en estado `OPEN`; el estado posterior se reconstruye a partir del historial inmutable de decisiones.

Crear `conflict.json`:

```json
{
  "conflict_id": "conflict-event-001",
  "event_id": "event-protocol-release-001",
  "assertion_refs": [
    "event-protocol-release-001-v1",
    "event-protocol-release-001-v2"
  ],
  "disputed_component": "DATE",
  "classification": "DIRECT_CONTRADICTION",
  "status": "OPEN"
}
```

El campo `recorded_at` lo asigna PostgreSQL. Registrar:

```powershell
python -m scripts.news_and_events.register_event create-conflict --input .\conflict.json
```

Una decisión debe identificar la transición, las afirmaciones consideradas, la evidencia favorable y contraria, el alcance, la justificación, las limitaciones, el actor, la versión de reglas y el corte de evaluación. Ejemplo de transición a revisión:

```json
{
  "decision_id": "conflict-event-001-decision-1",
  "conflict_id": "conflict-event-001",
  "from_status": "OPEN",
  "to_status": "UNDER_REVIEW",
  "assertion_refs": [
    "event-protocol-release-001-v1",
    "event-protocol-release-001-v2"
  ],
  "supporting_evidence_refs": [],
  "contrary_evidence_refs": [],
  "scope": "Revisión de la discrepancia temporal",
  "rationale": "Las dos afirmaciones requieren revisión.",
  "limitations": "No se establece todavía una conclusión factual.",
  "actor_ref": "operator-id",
  "decided_at": "2026-11-17T12:00:00Z",
  "assessment_cutoff": "2026-11-17T11:59:00Z",
  "rules_version": "temporal-review-1.0.0",
  "supersedes_decision_id": null
}
```

Anexar la decisión:

```powershell
python -m scripts.news_and_events.register_event append-decision --input .\decision.json
```

Para pasar a `RESOLVED`, el contrato exige evidencia de apoyo, justificación, alcance y limitaciones explícitos. Reabrir un conflicto previamente resuelto exige referenciar la decisión que se sustituye. Una transición inválida o una secuencia con estados incompatibles se rechaza sin alterar el historial.

Consultar el historial:

```powershell
python -m scripts.news_and_events.register_event conflict-history --conflict-id conflict-event-001
```

Consultar qué decisiones ya estaban incorporadas al registro en un corte UTC:

```powershell
python -m scripts.news_and_events.register_event conflict-history --conflict-id conflict-event-001 --cutoff-utc 2026-11-17T12:30:00Z
```

La hora `decided_at` representa la hora declarada de la decisión; PostgreSQL conserva además `inserted_at`, que representa cuándo se incorporó realmente al registro. Los valores por defecto usan `clock_timestamp()` y no `transaction_timestamp()`, para que una transacción larga no retrotraiga artificialmente la hora de incorporación. Las consultas históricas filtran por `inserted_at`, evitando mostrar decisiones que todavía no estaban registradas en el corte consultado. El estado actual se deriva de las decisiones visibles y no se reescribe en el registro inicial del conflicto.

## 7. Evaluaciones temporales y manifiestos de reproducibilidad

Una evaluación se ejecuta únicamente cuando el operador la solicita. El archivo `assessment.json` identifica el acontecimiento, el corte UTC y las afirmaciones/decisiones que deben considerarse:

```json
{
  "assessment_id": "assessment-event-001",
  "event_id": "event-protocol-release-001",
  "assessment_cutoff": "2026-11-17T12:30:00Z",
  "assertion_refs": [
    "event-protocol-release-001-v1",
    "event-protocol-release-001-v2"
  ],
  "conflict_decision_refs": [],
  "rules_version": "temporal-assessment-rules-1.0.0",
  "software_version": "sinayxa-registry-build-20261117"
}
```

Crear la evaluación:

```powershell
python -m scripts.news_and_events.register_event create-assessment --input .\assessment.json
```

El sistema calcula `derived_temporal_state` a partir de las afirmaciones seleccionadas y el corte (`PAST`, `ONGOING`, `FUTURE` o `UNDETERMINED`). PostgreSQL asigna `recorded_at`; no se acepta como verdadero un timestamp de registro enviado por el cliente. La evaluación rechaza acontecimientos, afirmaciones o decisiones cuya inserción real en el registro sea posterior al corte.

Consultar la evaluación:

```powershell
python -m scripts.news_and_events.register_event show-assessment --assessment-id assessment-event-001
```

Para generar un manifiesto, crear `manifest-request.json`:

```json
{
  "manifest_id": "manifest-event-001",
  "assessment_id": "assessment-event-001",
  "excluded_assertions": []
}
```

Ejecutar:

```powershell
python -m scripts.news_and_events.register_event create-manifest --input .\manifest-request.json
python -m scripts.news_and_events.register_event show-manifest --manifest-id manifest-event-001
```

El manifiesto calcula SHA-256 de la versión exacta del esquema, del módulo de reglas y del resultado serializado mediante RFC 8785. Exige además que cada afirmación incorporada al registro antes del corte quede clasificada como incluida o excluida con una razón; no permite omisiones silenciosas. Los timestamps `recorded_at`/`created_at` e `inserted_at` se fijan al mismo instante de reloj de PostgreSQL. También registra la versión IANA TZDB, las versiones de afirmaciones incluidas/excluidas, las referencias de evidencia y decisiones, y las versiones declaradas de reglas y software.

El manifiesto declara `NOT_REPRODUCIBLE` si falta algún artefacto de fuente/evidencia requerido en el corte; declara `PARTIALLY_REPRODUCIBLE` cuando esos bytes están presentes pero aún faltan la verificación del build exacto y la instantánea completa del entorno. No declara `REPRODUCIBLE` mientras falten esos componentes. Los identificadores y hashes no sustituyen los documentos fuente ni permiten reconstruir datos que nunca fueron almacenados.

## 8. Artefactos locales de fuentes y evidencias

El registro puede conservar los bytes exactos de una fuente y de los fragmentos/evidencias derivados. El operador suministra los archivos y declara el estado de uso; los archivos reales requieren autorización aplicable. SINAYXA no realiza descargas, crawling ni captura automática.

Ejemplo de `source-metadata.json`:

```json
{
  "source_ref": "source-report-001",
  "source_uri": "urn:sinayxa:synthetic:report-001",
  "title": "Synthetic source report",
  "publisher": "SINAYXA test fixture",
  "media_type": "application/json",
  "license_ref": "SYNTHETIC-TEST-DATA",
  "usage_status": "SYNTHETIC",
  "metadata": {
    "fixture": "local-validation"
  }
}
```

Registrar los bytes originales:

```powershell
python -m scripts.news_and_events.register_event register-source-artifact --input .\source-metadata.json --file .\source-report.json
```

Ejemplo de `evidence-metadata.json`:

```json
{
  "evidence_ref": "evidence-report-001",
  "source_ref": "source-report-001",
  "evidence_type": "EXTRACT",
  "media_type": "text/plain",
  "extraction_method": "manual-synthetic",
  "extraction_version": "1.0.0",
  "location_hint": "page 2, paragraph 4",
  "license_ref": "SYNTHETIC-TEST-DATA",
  "usage_status": "SYNTHETIC",
  "metadata": {
    "fixture": "local-validation"
  }
}
```

Registrar la evidencia y exportar después los bytes exactos:

```powershell
python -m scripts.news_and_events.register_event register-evidence-artifact --input .\evidence-metadata.json --file .\evidence-extract.txt
python -m scripts.news_and_events.register_event export-source-artifact --source-ref source-report-001 --output .\source-export.json
python -m scripts.news_and_events.register_event export-evidence-artifact --evidence-ref evidence-report-001 --output .\evidence-export.txt
```

Cada artefacto conserva el contenido byte por byte, SHA-256, longitud, media type, licencia, estado de uso y metadatos de procedencia. `captured_at` indica cuándo el operador incorporó los bytes al registro; no sustituye la fecha de publicación (`published_at`) ni afirma cuándo se obtuvo originalmente la fuente. `captured_at`, `recorded_at` e `inserted_at` comparten el mismo instante asignado por PostgreSQL. La exportación verifica longitud y SHA-256 antes de escribir el archivo y se niega a sobrescribir un destino existente.

`usage_status` solo admite `SYNTHETIC` o `AUTHORIZED`. Los artefactos `AUTHORIZED` requieren `authorization_ref`; una evidencia vinculada a una fuente no puede ampliar ni contradecir su licencia ni su estado de autorización. `authorization_ref` es una referencia declarada por el operador, no una validación jurídica automática; el operador debe verificar la autorización y conservar su soporte. El contenido se guarda en PostgreSQL (`BYTEA`) y no se impone un límite de tamaño adicional en la aplicación.

Los manifiestos incluyen los hashes y timestamps reales `inserted_at` de los artefactos disponibles antes del `assessment_cutoff`. Una referencia cuyo contenido no exista o haya sido incorporado después del corte se identifica en `missing_components`; no se incorpora retrospectivamente al resultado.

La integración persistente del contrato lógico 0.2.1 (claims, componentes, versiones de fuente, procedencia y evaluaciones por afirmación) no está implementada por estas cinco migraciones. Su mapeo y evolución controlada se siguen en [Issue #153](https://github.com/Osleyder1985/SINAYXA/issues/153); no deben simularse con metadatos JSONB libres ni con una segunda base de eventos.

## 9. Límites conocidos de esta entrega

- No existe aún interfaz gráfica, API HTTP ni integración con proveedores de noticias.
- La consulta devuelve el historial temporal conocido; no calcula por sí sola un dictamen de credibilidad, intensidad, impacto o causalidad.
- El manifiesto declara `NOT_REPRODUCIBLE` si faltan bytes de artefactos requeridos en el corte; cuando están presentes, permanece `PARTIALLY_REPRODUCIBLE` hasta verificar build exacto y snapshot completo del entorno.
- Los triggers bloquean UPDATE/DELETE por fila y TRUNCATE por sentencia en las nueve tablas dentro de la base de datos. No equivalen a WORM externo, Object Lock ni resistencia frente a un administrador privilegiado o pérdida del host.
- No se ha validado todavía instalación local en Windows del propietario ni operación con datos reales.

## 10. Validación automatizada

El workflow `.github/workflows/event-registry-validation.yml` ejecuta el validador, las regresiones del contrato y las pruebas de integración contra PostgreSQL 18.7 fijado por digest. La suite cubre registro, versionado, consultas históricas por `inserted_at`, conflictos, decisiones, evaluaciones, manifiestos, artefactos, autorización, integridad SHA-256, transiciones inválidas, concurrencia, idempotencia de las cinco migraciones y protección UPDATE/DELETE/TRUNCATE en las nueve tablas.

La escritura de afirmaciones bloquea la fila del acontecimiento con `SELECT ... FOR UPDATE`, serializando la asignación de versiones entre conexiones concurrentes para el mismo evento. La restricción única `(event_id, version)` sigue siendo una defensa adicional. La suite verifica dos escritores independientes, idempotencia de las cinco migraciones, 18 triggers de inmutabilidad y diez defaults `clock_timestamp()`.

La ejecución satisfactoria de CI demuestra el comportamiento del laboratorio sintético; no demuestra disponibilidad operativa local ni veracidad de acontecimientos reales.
