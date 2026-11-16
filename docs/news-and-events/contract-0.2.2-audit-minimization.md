# Especificación de diseño — contrato 0.2.2: minimización de auditoría

- Issue: #98
- Decisión de origen: #97, aprobada por el propietario el 2026-11-16
- Estado: diseño aprobado para implementación; pendiente de validación técnica
- Base normativa: contrato 0.2.1 propuesto en PR #85
- Compatibilidad: 0.2.0 y 0.2.1 permanecen inmutables

## 1. Objetivo y límites

El contrato 0.2.2 reduce la exposición de los registros mínimos de auditoría mediante vocabularios controlados, identificadores de correlación opacos y rechazo de texto libre. No constituye anonimización exhaustiva, no elimina el riesgo de correlación contextual y no acredita por sí solo borrado físico ni cumplimiento legal.

## 2. Campos del evento mínimo

El evento de auditoría 0.2.2 usará:
- `audit_event_id`: UUID versión 4.
- `subject_ref`: token UUID versión 4 dedicado a correlacionar el sujeto dentro del ámbito de retención; todos los tokens usados se declaran en el registro `audit_subject_tokens` del paquete.
- `retention_id`, `copy_id` y referencias correlacionadas: UUID versión 4 cuando estén presentes.
- `action`: catálogo cerrado de acciones ya definido por 0.2.1.
- `actor_role_code`: código del catálogo de roles 1.0.0.
- `reason_code`: código del catálogo de motivos 1.0.0, sujeto a la acción.
- `occurred_at`: timestamp UTC.
- `actor_role_catalog_version` y `reason_catalog_version`: versión explícita del catálogo aplicado.

Se prohíben `actor_role`, `reason`, propiedades adicionales y cualquier explicación libre en el evento mínimo. No se permiten URLs, emails, direcciones IP, nombres, domicilios, hashes de contenido ni identificadores externos reutilizables en campos de correlación.

## 3. Perímetro de identificadores opacos

La forma sintáctica será UUIDv4 canónico en minúsculas, con bits de versión y variante RFC correspondientes. La generación debe usar un generador criptográficamente seguro; queda prohibido derivar el UUID de nombres, emails, direcciones, IDs externos, hashes de contenido o secuencias predecibles.

El validador puede comprobar formato y unicidad dentro del paquete, pero no puede demostrar matemáticamente que un valor se generó con entropía suficiente. La garantía de generación depende del generador controlado y de su evidencia operativa. La documentación no describirá el patrón UUID como prueba de anonimización.

El token de sujeto se utiliza para correlación interna entre los registros de retención, copias y auditoría. No debe codificar ni derivarse de la identidad externa. Los IDs de dominio preexistentes no se convertirán silenciosamente en tokens.

## 4. Catálogos y evolución

Los catálogos de roles y motivos se versionan de forma independiente y usan códigos estables, no descripciones libres. La descripción humana es documentación del catálogo y nunca se copia al evento.

Cada motivo declara explícitamente las acciones permitidas. Un motivo válido en el catálogo pero no permitido para la acción concreta debe ser rechazado por el validador semántico.

No se reutilizan códigos retirados ni se cambia su significado. Las adiciones incrementan la versión del catálogo conforme a una política documentada. Los eventos conservan la versión exacta de ambos catálogos.

## 5. Tratamiento de datos históricos y migración

La migración 0.2.1 → 0.2.2 es fail-closed:
- Los paquetes que ya contengan identificadores opacos compatibles y referencias coherentes pueden migrarse preservando IDs y relaciones. El migrador genera el registro `audit_subject_tokens` a partir de los `subject_ref` históricos existentes, únicamente cuando todos ya son UUIDv4.
- Los paquetes con IDs semánticos o referencias que revelen IDs externos no pueden recibir UUID aleatorios automáticamente: eso destruiría la trazabilidad si no se conserva una correspondencia. Las conversiones de `actor_role` y `reason` requieren un archivo de mapeo explícito; el migrador no interpreta texto libre.
- No se crea una tabla de correspondencias, servicio de tokenización ni almacén de secretos en esta decisión (la alternativa C no fue aprobada).
- Si el paquete histórico no satisface la política de opacidad y no existe una transformación demostrablemente reversible y autorizada, la migración devuelve REJECTED con un informe de incompatibilidad. El original permanece íntegro bajo su versión de contrato.
- No se inventan roles, motivos, tiempos, autorizaciones ni estados históricos. Un valor no mapeable no se convierte en un código positivo por inferencia.
- El requisito de determinismo se aplica a la misma entrada, migrador, reglas y parámetros explícitos. No se permite generar tokens aleatorios nuevos en cada repetición y declarar determinismo.

La migración no reescribe `methodology_version`, cortes temporales ni evaluaciones históricas.

## 6.1. Migración ejecutable

El migrador `scripts/validation/migrate_source_evidence_contract_0_2_1_to_0_2_2.py` requiere un archivo de mapeo explícito con esta forma:

```json
{
  "actor_roles": {
    "SYNTHETIC_TEST": "SYNTHETIC_TEST"
  },
  "reasons": {
    "texto histórico exacto": "RECORD_CREATED"
  }
}
```

Los ejemplos anteriores son ilustrativos: cada motivo debe corresponder exactamente a la acción histórica y a un código vigente. No se usa coincidencia aproximada, traducción, clasificación semántica ni fallback.

La ejecución requiere `--input`, `--mapping`, `--output`, `--manifest`, `--migration-id`, `--executed-at` y `--source-snapshot-ref`. El instante de ejecución y los metadatos de migración se suministran explícitamente para permitir repetición determinista. Los cuatro archivos deben usar rutas distintas y el destino no puede existir previamente. En caso de rechazo se escribe únicamente el manifiesto; el origen no se modifica y no se genera un paquete de destino.

Los SHA-256 del manifiesto usan JSON canónico UTF-8 con claves ordenadas y separadores compactos. `output_sha256` dentro del registro de migración cubre el paquete transformado antes de añadir ese registro (para evitar autorreferencia); `output_file_sha256` del manifiesto cubre el paquete final completo.

## 7. Explicaciones excepcionales

El evento mínimo no contiene texto libre. Si un proceso necesita una explicación humana, debe residir fuera del evento mínimo, bajo un control de acceso y una política de retención separados, con minimización y revisión de privacidad. Esta especificación no define ni autoriza ese repositorio separado.

## 8. Reglas de validación

1. Rechazar propiedades no declaradas y campos libres heredados.
2. Validar UUIDv4, unicidad local y consistencia referencial de todos los identificadores dentro del perímetro.
3. Validar códigos y versiones de catálogos.
4. Validar compatibilidad entre `action` y `reason_code`.
5. Rechazar URLs, direcciones de correo, IPs, hashes de contenido y patrones de IDs externos en los campos de correlación; esta detección es defensa adicional, no prueba exhaustiva.
6. Rechazar IDs duplicados, referencias rotas, códigos retirados/no reconocidos y migraciones con pérdidas no autorizadas.
7. Preservar sin cambios los esquemas y fixtures históricos 0.2.0/0.2.1.

## 9. Riesgos residuales

- UUIDv4 válido no demuestra por sí solo generación criptográficamente segura.
- Los tokens pueden permitir correlación entre registros que compartan el mismo valor.
- Un paquete completo puede contener contexto que permita reidentificación.
- Los catálogos controlados reducen el canal de texto libre, pero no garantizan anonimización.
- Las pruebas sintéticas no demuestran eliminación física, inmutabilidad WORM ni reconciliación de backups externos.

## 10. Criterios para aceptar la implementación

- JSON Schema 0.2.2 separado y válido Draft 2020-12.
- Migrador 0.2.1 → 0.2.2 con parámetros explícitos, manifiesto SHA-256 y rechazo fail-closed.
- Catálogos 1.0.0 versionados y validados.
- Validador semántico para acciones/motivos y opacidad.
- Migración determinista y fail-closed, con rechazo explícito de IDs históricos incompatibles.
- Pruebas positivas y negativas focalizadas, no una expansión especulativa de la matriz.
- CI verde sobre el mismo HEAD y revisión independiente antes de cualquier merge.
- Issue #97, RET-09 y Área C de #88 permanecen abiertos hasta disponer de evidencia suficiente, incluidas las validaciones externas que correspondan.
