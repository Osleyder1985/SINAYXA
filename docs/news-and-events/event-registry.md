# Registro operativo de acontecimientos — Issue #2

**Estado:** primera implementación en PR #101 (DRAFT), apilada sobre el contrato temporal 1.0.0 de PR #90.  
**Persistencia:** PostgreSQL local 18.7.  
**Uso autorizado:** entrada explícita del operador y datos sintéticos de validación.  
**Fuera de alcance:** captura automática, crawling, vigilancia, scraping, fuentes reales y servicios externos.

## 1. Capacidades implementadas

- Crear un registro de acontecimiento con identificador estable, descripción, activos relacionados, fuentes conocidas y fecha de creación.
- Añadir referencias de fuentes posteriores sin reescribir el registro original.
- Anexar afirmaciones temporales versionadas (ACTUAL, SCHEDULED, ESTIMATED, UNKNOWN).
- Validar cada paquete con JSON Schema Draft 2020-12 y las invariantes semánticas del contrato 1.0.0.
- Consultar qué versiones estaban registradas a un corte UTC y recuperar el historial completo.
- Impedir mediante triggers SQL la modificación o eliminación de acontecimientos, referencias de fuentes y afirmaciones temporales.

La consulta histórica utiliza recorded_at, no la fecha del acontecimiento. Por tanto, una revisión posterior no aparece en consultas cuyo corte precede a su registro.

## 2. Preparación local (PowerShell)

Instalar PostgreSQL 18.7 y Python 3.12 en el entorno local autorizado. Crear una base de datos local vacía y establecer la cadena de conexión en la sesión:

```powershell
python -m pip install --requirement requirements-temporal-contract-validation.txt
$env:SINAYXA_DATABASE_URL = "postgresql://USUARIO:CONTRASENA@localhost:5432/sinayxa"
python -m scripts.news_and_events.register_event init
```

La migración crea el esquema sinayxa y sus tablas. Puede ejecutarse nuevamente sin duplicar los objetos principales. La base de datos y sus credenciales permanecen bajo control local del operador.

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

La hora `decided_at` representa la hora declarada de la decisión; PostgreSQL conserva además `inserted_at`, que representa cuándo se incorporó realmente al registro. Las consultas históricas filtran por `inserted_at`, evitando mostrar decisiones que todavía no estaban registradas en el corte consultado. El estado actual se deriva de las decisiones visibles y no se reescribe en el registro inicial del conflicto.

## 7. Límites conocidos de esta primera entrega

- No existe aún interfaz gráfica, API HTTP ni integración con proveedores de noticias.
- La consulta devuelve el historial temporal conocido; no calcula por sí sola un dictamen de credibilidad, intensidad, impacto o causalidad.
- Las evaluaciones temporales y los manifiestos de reproducibilidad siguen definidos en el contrato, pero sus operaciones de escritura no forman parte de esta entrega.
- Los triggers protegen contra UPDATE/DELETE ordinarios dentro de la base de datos. No equivalen a WORM externo, Object Lock ni resistencia frente a un administrador privilegiado o pérdida del host.
- No se ha validado todavía instalación local en Windows del propietario ni operación con datos reales.

## 8. Validación automatizada

La escritura de una nueva afirmación bloquea la fila del acontecimiento (`SELECT ... FOR UPDATE`) durante la lectura del historial y la inserción. Esto serializa la asignación de versiones por acontecimiento cuando existen varios escritores concurrentes; la restricción única de `(event_id, version)` permanece como defensa adicional.

La suite de integración comprueba `UPDATE` y `DELETE` en las tres tablas append-only (`events`, `event_sources` y `temporal_assertions`), la re-ejecución de la migración y dos escritores concurrentes que intentan anexar la misma versión. Se espera que solo una escritura sea aceptada.

El workflow .github/workflows/event-registry-validation.yml ejecuta el validador y regresiones del contrato y pruebas de integración contra PostgreSQL 18.7 fijado por digest. La suite incluye registro, nueva versión, consulta histórica, rechazo de secuencia discontinua y rechazo de modificaciones del registro.

La ejecución satisfactoria de CI demuestra el comportamiento del laboratorio sintético; no demuestra disponibilidad operativa local ni veracidad de acontecimientos reales.
