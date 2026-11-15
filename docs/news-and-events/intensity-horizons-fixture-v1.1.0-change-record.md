# Registro de cambios del fixture sintético de intensidad v1.1.0

## 1. Identificación y relación con versiones anteriores

| Campo | Valor |
| --- | --- |
| Paquete | `SINAYXA-IH-T01-T19-SYNTHETIC-002` |
| Versión | `1.1.0` |
| Fixture | `tests/fixtures/methodology/intensity-horizons/t01-t19-synthetic-evidence-v1.1.0.json` |
| Commit de incorporación del fixture | `3dcac246c91d695a7f773835e76ae532998a9911` |
| Git blob SHA del fixture | `4c5bf467e62cd0b9d86c90cd74a356a03c8bcab5` |
| SHA-256 del contenido | **PENDIENTE DE VERIFICACIÓN LOCAL** |
| Paquete anterior | `SINAYXA-IH-T01-T19-SYNTHETIC-001`, versión `1.0.0` |
| SHA-256 del paquete anterior | `467F5B5236481C0EFDCAFF562DA3D4DFF27EF71C1FCB9D486E19072ABA902D22` |

La versión 1.1.0 es un nuevo artefacto. No reemplaza, edita ni invalida el fixture 1.0.0. Los 19 identificadores T01–T19 se conservan para facilitar la comparación de casos; sus entradas actualizadas pertenecen exclusivamente a la versión 1.1.0.

## 2. Cambios semánticos

### T01 — unidad de análisis acotada

La unidad queda limitada explícitamente a las funciones técnicas y operativas del protocolo ALPHA. Se excluyen el valor de mercado del token público y los canales de reputación, atención y demanda. El inventario técnico, la confirmación de alcance y la revisión de registros operativos respaldan I0 únicamente dentro de esa unidad delimitada.

**Límite:** T01 no permite concluir I0 para el token público, su precio, la percepción del mercado ni la reputación del proyecto. La dirección permanece INDETERMINADA salvo evidencia independiente.

### T03 — consecuencia operativa observable

Se agregan hechos sintéticos concretos: 27 solicitudes de depósito de 11 cuentas institucionales siguen sin acreditarse cuatro horas después de la ventana de procesamiento documentada; los fondos no acreditados no pueden utilizarse como saldo de trading o colateral en el segmento. Se conserva la evidencia de que otros segmentos y funciones permanecen disponibles.

**Límite:** las cantidades y duración son hechos del escenario ficticio, no umbrales universales para I2. La duración futura no se presume.

### T04 — amplitud, función material y límite frente a I4

Se define un inventario completo de cinco aplicaciones: cuatro dependen de la misma ruta del oráculo. Los registros sintéticos describen datos con 38 minutos de antigüedad, incumplimiento de la condición de frescura y suspensión de nuevas operaciones de lending/borrowing en las cuatro aplicaciones. Se documenta por separado que las posiciones existentes siguen consultables, los controles de seguridad conservan un feed secundario y los retiros y el acceso de usuarios siguen disponibles.

**Límite:** I3 se refiere al ecosistema expresamente delimitado. No se extrapola fuera de las cinco aplicaciones ni se infiere I4 cuando no se acredita compromiso de acceso esencial, custodia, liquidación o viabilidad.

### T08 — materialidad independiente por segmento

Para el segmento A se documenta que la integración es la única ruta soportada para el flujo de liquidación definido y que, tras el evento, las solicitudes son rechazadas sin ruta alternativa. Para el segmento B se documenta la limitación previa y registros de transacciones exitosas después de habilitarse la integración. Cada segmento conserva su dirección y su evaluación I2 separada.

**Límite:** no se crea una clasificación agregada porque el paquete no define una unidad agregada ni un denominador común. No se promedian ni cancelan efectos.

### T10 — prueba exclusiva de mitigación

El caso declara `intensity_baseline: NOT_ASSESSED` y `mitigation: UNVERIFIED`. Comprueba únicamente que una mitigación anunciada sin despliegue, capacidad y acceso demostrados no puede reducir una intensidad basal establecida por una evaluación independiente.

**Límite:** T10 no asigna por sí solo I0–I4 y no contiene una intensidad basal implícita.

## 3. Casos preservados

T02, T05–T07, T09, T11–T19 conservan sus entradas y resultados esperados respecto de la versión 1.0.0. T16 permanece BLOCKED y exige dos evaluadores humanos realmente independientes. T11, T12, T13, T14, T15, T18 y T19 conservan los vectores temporales originales.

## 4. Validación automatizada disponible

Se amplió `scripts/validation/validate_intensity_horizon_fixture.ps1` para aceptar los pares de identidad/versión:

- `SINAYXA-IH-T01-T19-SYNTHETIC-001` / `1.0.0`
- `SINAYXA-IH-T01-T19-SYNTHETIC-002` / `1.1.0`

Para la versión 1.1.0, el validador añade comprobaciones de contrato estructural sobre el alcance de T01, los campos probatorios de T03 y T04, las evaluaciones separadas de T08 y la ausencia de intensidad basal en T10. Las comprobaciones verifican presencia y consistencia de campos esperados; **no demuestran por sí mismas la validez metodológica de las clasificaciones**.

Desde la raíz del repositorio, en Windows PowerShell 5.1:

```powershell
.scriptsalidationalidate_intensity_horizon_fixture.ps1 -FixturePath .	estsixturesmethodologyintensity-horizons	01-t19-synthetic-evidence-v1.1.0.json
```

La ejecución local y el SHA-256 del nuevo archivo deben registrarse después de ejecutar el comando. Hasta entonces, el SHA-256 de 1.1.0 permanece pendiente y no se declara PASS local.

## 5. Estados y límites de gobernanza

- Este cambio es una ampliación del paquete sintético, no una aprobación de la propuesta del Issue #14.
- No es ejecución formal de T01–T19 ni evaluación humana independiente.
- No acredita validez empírica, capacidad predictiva ni causalidad.
- No cambia los estados de ejecución de la matriz: T01–T15 y T17–T19 siguen NOT_EXECUTED; T16 sigue BLOCKED.
- Los resultados esperados son oráculos de prueba, no resultados observados.
- Cualquier cambio posterior deberá crear otra versión del paquete y conservar los artefactos anteriores.
