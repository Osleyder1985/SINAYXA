# Registro operativo de acontecimientos — Issue #2

**Estado:** registro inicial en PR #101, endurecimiento en PR #102, conflictos/decisiones en PR #103 y evaluaciones/manifiestos en PR #104 y artefactos fuente/evidencia en PR #105 (todas DRAFT y apiladas; ninguna fusionada).  
**Persistencia:** PostgreSQL local 18.7.  
**Uso autorizado:** entrada explícita del operador y datos sintéticos de validación.  
**Fuera de alcance:** captura automática, crawling, vigilancia, scraping, fuentes reales y servicios externos.

## 1. Capacidades implementadas

- Crear un registro de acontecimiento con identificador estable, descripción, activos relacionados, fuentes conocidas y fecha de creación.
- Añadir referencias de fuentes posteriores sin reescribir el registro original.
- Anexar afirmaciones temporales versionadas (ACTUAL, SCHEDULED, ESTIMATED, UNKNOWN).
- Validar cada paquete con JSON Schema Draft 2020-12 y las invariantes semánticas del contrato 1.0.0.
- Consultar qué versiones estaban registradas a un corte UTC y recuperar el historial completo.
- Registrar conflictos entre afirmaciones del mismo acontecimiento y anexar decisiones humanas con evidencia favorable/contraria, alcance, justificación y limitaciones.
- Reconstruir el estado del conflicto desde su historial append-only y consultar decisiones conocidas en un corte de inserción UTC.
- Derivar estados temporales bajo demanda y generar manifiestos SHA-256 con canonicalización RFC 8785.
- Conservar bytes exactos de fuentes y evidencias suministrados por el operador, con SHA-256, licencia y estado de autorización.
- Exportar artefactos verificando longitud y hash antes de escribir.
- Impedir mediante triggers SQL la modificación o eliminación de las nueve tablas de registro.

Las consultas históricas utilizan el instante real de incorporación asignado por PostgreSQL (`inserted_at`), no una fecha de acontecimiento ni un timestamp de registro declarado por el cliente. Las afirmaciones también reciben `recorded_at` desde PostgreSQL. Esto evita que una entrada posterior se haga pasar por información conocida antes.

## 2. Preparación local (PowerShell)

Instalar PostgreSQL 18.7 y Python 3.12 en el entorno local autorizado. Crear una base de datos local vacía y establecer la cadena de conexión en la sesión:

```powershell
python -m pip install --requirement requirements-temporal-contract-validation.txt
$env:SINAYXA_DATABASE_URL = "postgresql://USUARIO:CONTRASENA@localhost:5432/sinayxa"
python -m scripts.news_and_events.register_event init
```

La inicialización aplica en orden las migraciones SQL numeradas (`0001`, `0002`, `0003`, etc.). La migración `0002_temporal_conflicts.sql` añade conflictos/decisiones; `0003_temporal_assessments_manifests.sql` añade evaluaciones/manifiestos; `0004_source_evidence_artifacts.sql` añade almacenamiento local de fuentes/evidencias; `0005_append_only_truncate_guard.sql` bloquea TRUNCATE en las nueve tablas append-only. Las migraciones son idempotentes. La base de datos y sus credenciales permanecen bajo control local del operador.

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

El campo `recorded_at` del JSON se conserva por compatibilidad con el contrato, pero la API lo sustituye por `clock_timestamp()` de PostgreSQL. El cliente no puede elegir ni retrotraer el instante en que la afirmación entra en el registro.

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

El corte debe expresarse en UTC con sufijo Z. Una afirmación cuyo recorded_at sea posterior al corte queda excluida.

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

El manifiesto calcula SHA-256 de la versión exacta del esquema, del módulo de reglas y del resultado serializado mediante RFC 8785. También registra la versión IANA TZDB, las versiones de afirmaciones incluidas/excluidas, las referencias de evidencia y decisiones, y las versiones declaradas de reglas y software.

**El estado se declara `PARTIALLY_REPRODUCIBLE`, no `REPRODUCIBLE`**, mientras no se conserven el contenido de las fuentes, el contenido de la evidencia, la verificación del build exacto y una instantánea completa del entorno de ejecución. Los identificadores y hashes no sustituyen los documentos fuente ni permiten reconstruir datos que nunca fueron almacenados.

## 8. Artefactos locales de fuentes y evidencias

El registro puede conservar los bytes exactos de una fuente y de los fragmentos/evidencias derivados. El operador suministra los archivos; SINAYXA no realiza descargas, crawling ni captura automática.

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

Cada artefacto conserva el contenido byte por byte, SHA-256, longitud, media type, licencia, estado de uso y metadatos de procedencia. La exportación verifica longitud y SHA-256 antes de escribir el archivo y se niega a sobrescribir un destino existente.

`usage_status` solo admite `SYNTHETIC` o `AUTHORIZED`. Los artefactos `AUTHORIZED` requieren `authorization_ref`; una evidencia vinculada a una fuente no puede ampliar ni contradecir su licencia ni su estado de autorización. `authorization_ref` es una referencia declarada por el operador, no una validación jurídica automática; el operador debe verificar la autorización y conservar su soporte. El contenido se guarda en PostgreSQL (`BYTEA`) y no se impone un límite de tamaño adicional en la aplicación.

Los manifiestos incluyen los hashes de los artefactos disponibles antes del `assessment_cutoff`. Una referencia cuyo contenido no exista o haya sido incorporado después del corte se identifica en `missing_components`; no se incorpora retrospectivamente al resultado.

## 9. Límites conocidos de esta primera entrega

- No existe aún interfaz gráfica, API HTTP ni integración con proveedores de noticias.
- La consulta devuelve el historial temporal conocido; no calcula por sí sola un dictamen de credibilidad, intensidad, impacto o causalidad.
- Los triggers protegen contra UPDATE/DELETE/TRUNCATE ordinarios dentro de la base de datos. No equivalen a WORM externo, Object Lock ni resistencia frente a un administrador privilegiado o pérdida del host.
- No se ha validado todavía instalación local en Windows del propietario ni operación con datos reales.

## 10. Validación automatizada

La escritura de una nueva afirmación bloquea la fila del acontecimiento (`SELECT ... FOR UPDATE`) durante la lectura del historial y la inserción. Esto serializa la asignación de versiones por acontecimiento cuando existen varios escritores concurrentes; la restricción única de `(event_id, version)` permanece como defensa adicional.

La suite de integración comprueba `UPDATE`, `DELETE` y `TRUNCATE` en las nueve tablas append-only (`events`, `event_sources`, `temporal_assertions`, `temporal_conflicts`, `conflict_decisions`, `temporal_assessments`, `reproducibility_manifests`, `source_artifacts` y `evidence_artifacts`), la re-ejecución de las cinco migraciones, los diez defaults de timestamps de registro basados en reloj real y los 18 triggers de inmutabilidad, dos escritores concurrentes que intentan anexar la misma versión, el ciclo de decisiones, transiciones inválidas y cortes históricos.

El workflow `.github/workflows/event-registry-validation.yml` ejecuta el validador y regresiones del contrato y pruebas de integración contra PostgreSQL 18.7 fijado por digest. La suite cubre registro, versionado, consultas históricas, conflictos, decisiones, rechazo de secuencias/transiciones inválidas, concurrencia, idempotencia de migraciones y protección append-only de las nueve tablas, almacenamiento de artefactos, evaluaciones temporales y generación de manifiestos RFC 8785.

La ejecución satisfactoria de CI demuestra el comportamiento del laboratorio sintético; no demuestra disponibilidad operativa local ni veracidad de acontecimientos reales.
