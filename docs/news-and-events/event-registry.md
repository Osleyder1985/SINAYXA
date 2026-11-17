# Registro operativo de acontecimientos — Issue #2

**Estado:** primera implementación en PR #106 (DRAFT), sobre el contrato temporal 1.0.0 integrado en main mediante PR #90.  
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

## 6. Límites conocidos de esta primera entrega

- No existe aún interfaz gráfica, API HTTP ni integración con proveedores de noticias.
- La consulta devuelve el historial temporal conocido; no calcula por sí sola un dictamen de credibilidad, intensidad, impacto o causalidad.
- El modelo de conflictos, decisiones, evaluaciones y manifiestos está definido en el contrato, pero sus operaciones de escritura no forman parte de esta primera vertical.
- Los triggers bloquean UPDATE/DELETE por fila y TRUNCATE por sentencia dentro de la base de datos. No equivalen a WORM externo, Object Lock ni resistencia frente a un administrador privilegiado o pérdida del host.
- No se ha validado todavía instalación local en Windows del propietario ni operación con datos reales.

## 7. Validación automatizada

El workflow .github/workflows/event-registry-validation.yml ejecuta el validador y regresiones del contrato y pruebas de integración contra PostgreSQL 18.7 fijado por digest. La suite incluye registro, nueva versión, consulta histórica, rechazo de secuencia discontinua y rechazo de modificaciones del registro.

La ejecución satisfactoria de CI demuestra el comportamiento del laboratorio sintético; no demuestra disponibilidad operativa local ni veracidad de acontecimientos reales.
