# Registro de ejecución de T01–T19

## 1. Propósito y estado

Este documento registra la ejecución verificable de la batería metodológica definida en [la propuesta de intensidad y horizontes temporales](intensity-and-time-horizons-proposal.md).

**Estado vigente tras la adaptación v1.2.0:** T01–T15 y T17–T19 permanecen **NOT_EXECUTED**; T16 también está **NOT_EXECUTED** y dispone de un protocolo ejecutable para un único evaluador humano con crítica auxiliar de IA. La revisión lógica de escritorio no equivale a ejecutar la batería. No se deben convertir resultados esperados en resultados observados.

Este registro no aprueba la metodología ni autoriza su implementación. Es un instrumento de trazabilidad para la evaluación y posterior decisión del propietario.

## 2. Identificación de la ejecución

Completar antes de ejecutar cada ciclo:

| Campo | Valor |
| --- | --- |
| ID de ejecución | PENDIENTE |
| Versión/commit de la propuesta | PENDIENTE |
| SHA del archivo de propuesta | PENDIENTE |
| Versión de este protocolo | PENDIENTE |
| Fecha y hora de congelación del paquete (ISO 8601) | PENDIENTE |
| Fecha y hora de corte de evaluación (ISO 8601) | PENDIENTE |
| Unidad de análisis | PENDIENTE |
| Escenario evaluado | PENDIENTE |
| Inventario de evidencias y fuentes | PENDIENTE |
| Hash del paquete congelado | PENDIENTE |
| Responsable de custodia del paquete | PENDIENTE |
| Método/herramienta de cálculo temporal, si aplica | PENDIENTE |
| Observaciones sobre limitaciones | PENDIENTE |

No iniciar una ejecución reproducible si la unidad, el escenario, el corte o el contenido del paquete no están definidos. Conservar timestamps originales, offsets, zona IANA cuando esté disponible, fuente y precisión. No completar datos ausentes mediante suposiciones.

## 2.1 Paquete sintético congelable

El paquete de entradas sintéticas para T01–T19 está en [t01-t19-synthetic-evidence.json](../../tests/fixtures/methodology/intensity-horizons/t01-t19-synthetic-evidence.json). Su identificador es `SINAYXA-IH-T01-T19-SYNTHETIC-001`. Todos los nombres, acontecimientos, registros y marcas temporales son ficticios y sirven exclusivamente para probar la aplicación de las reglas.

El paquete contiene 19 casos ordenados, unidades, escenarios, cortes, elementos de evidencia y resultados esperados. Los resultados esperados son oráculos de prueba, no resultados obtenidos. En particular, el material de T16 solo describe el requisito de dos evaluadores reales; no simula sus respuestas ni satisface la validación interevaluador.

Validador estructural compatible con Windows PowerShell 5.1: `scripts/validation/validate_intensity_horizon_fixture.ps1`. Desde la raíz del repositorio:

```powershell
.\scripts\validation\validate_intensity_horizon_fixture.ps1
```

El validador comprueba la identidad del paquete, los 19 IDs únicos y ordenados, campos obligatorios y el bloqueo de T16. También ejecuta comprobaciones deterministas de los vectores temporales T11, T12, T13, T14, T15, T18 y T19: aritmética de duraciones, límites de horizonte, conservación de fecha sin hora, separación de hitos e intervalos que cruzan fronteras. También imprime el SHA-256 del archivo local. Para registrar una ejecución reproducible, copiar ese hash a la ficha de ejecución junto con el commit exacto del repositorio; no modificar el fixture después de congelarlo. Cualquier cambio debe crear una nueva versión del paquete y un nuevo hash.

**Límite histórico de la versión inicial:** validar la estructura del fixture no ejecuta la batería metodológica ni convierte ningún caso a PASS. La referencia histórica a T16 como BLOCKED fue sustituida por el protocolo de evaluador único de la sección 6 y el fixture v1.2.0 de la sección 9. La matriz vigente de la sección 4 mantiene todos los casos en NOT_EXECUTED.

**Alcance ampliado del validador (commit `49db0a0cbe8f534eeeb8855e82279a4055bfda2d`):** además de la estructura, el script comprueba aritméticamente los vectores temporales de T11/T12, el tratamiento date-only de T13, los cuatro hitos de T14, el intervalo de frontera de T15, las 24 horas reales de T18 y el intervalo contradictorio de T19. Estas comprobaciones son deterministas sobre los datos sintéticos. No evalúan semánticamente intensidad/dirección de T01–T10/T16/T17, ni constituyen una ejecución integral de la batería. La ejecución local de esta versión ampliada en Windows PowerShell 5.1 quedó verificada y se registra en la sección 2.3. El resultado acredita únicamente las comprobaciones deterministas descritas; no constituye una ejecución integral de la batería metodológica.

### 2.2 Registro verificado de integridad del paquete

**Comprobación local comunicada por el propietario:**

| Campo | Resultado |
| --- | --- |
| Commit local | `6dcc3228578be7cd1a4d0421e51d62d823bca8d3` |
| Resultado del validador estructural | PASS |
| Identificador | `SINAYXA-IH-T01-T19-SYNTHETIC-001` |
| Casos detectados | 19 |
| T16 | BLOCKED (bloqueo conservado correctamente) |
| SHA-256 del fixture | `467F5B5236481C0EFDCAFF562DA3D4DFF27EF71C1FCB9D486E19072ABA902D22` |
| Markdown lint de los dos documentos | PASS; 0 issues |
| `git status --short` | Sin cambios pendientes |

El hash anterior corresponde al archivo local en la ruta `tests/fixtures/methodology/intensity-horizons/t01-t19-synthetic-evidence.json`. El propietario confirmó que el comando terminó con `Fixture validation: PASS` y que el árbol de trabajo estaba limpio.

**Alcance exacto de esta verificación:** acredita que el fixture local coincide con las comprobaciones estructurales implementadas y que los dos documentos Markdown pasan lint. No constituye ejecución de los resultados metodológicos T01–T19, no cambia sus estados y no valida acuerdo interevaluador. La matriz de la sección 4 permanece sin cambios.

### 2.3 Registro verificado de la ejecución ampliada del validador

**Ejecución local comunicada por el propietario y reproducida en Windows PowerShell 5.1:**

| Campo | Resultado |
| --- | --- |
| Commit ejecutado | `5e5dcb69663fd8e34b22825c9374bd0c949747b5` |
| Comando | `.scripts\validation\validate_intensity_horizon_fixture.ps1` |
| Validación estructural del fixture | PASS |
| Paquete | `SINAYXA-IH-T01-T19-SYNTHETIC-001` |
| Casos detectados | 19 |
| Comprobaciones temporales deterministas | PASS: T11, T12, T13, T14, T15, T18 y T19 |
| T16 | BLOCKED (bloqueo conservado correctamente) |
| SHA-256 | `467F5B5236481C0EFDCAFF562DA3D4DFF27EF71C1FCB9D486E19072ABA902D22` |
| Ruta del fixture | `tests/fixtures/methodology/intensity-horizons/t01-t19-synthetic-evidence.json` |
| `git status --short` | Sin cambios pendientes |

La salida observada fue: `Fixture structure validation: PASS`, `Temporal fixture checks: PASS (T11,T12,T13,T14,T15,T18,T19)` y `T16: BLOCKED (correctly preserved)`. El hash impreso coincide con el hash registrado para el paquete congelado.

**Alcance:** este resultado verifica la estructura del fixture y los cálculos/reglas temporales deterministas implementados para los siete casos indicados. No demuestra que la clasificación semántica de intensidad/dirección de T01–T10 y T17 sea correcta, no ejecuta una evaluación integral de T01–T19, no valida acuerdo interevaluador y no satisface T16. Por tanto, los estados de la matriz de la sección 4 permanecen sin cambios: T01–T15 y T17–T19 siguen NOT_EXECUTED; T16 sigue BLOCKED. El PASS aquí registrado corresponde exclusivamente al validador de fixture y sus comprobaciones temporales.

## 3. Estados permitidos

- **NOT_EXECUTED:** no existe ejecución registrada.
- **IN_PROGRESS:** ejecución iniciada, todavía sin resultado revisado.
- **PASS:** resultado obtenido coincide con el esperado y existe evidencia suficiente del procedimiento.
- **FAIL:** resultado obtenido contradice el esperado o revela una regla ambigua/inconsistente.
- **BLOCKED:** no puede ejecutarse por una dependencia o condición no satisfecha.
- **NOT_APPLICABLE:** solo con justificación explícita; no utilizar para ocultar un caso difícil.

Un caso solo puede marcarse PASS o FAIL cuando se registren entradas, procedimiento, resultado obtenido, evidencia y responsable. Una comprobación de escritorio o una simulación no cuenta como ejecución independiente.

## 4. Matriz de seguimiento

Los resultados esperados se resumen aquí para facilitar el control. La descripción íntegra del escenario y el error que debe detectar cada caso permanecen en la propuesta vinculada.

| ID | Resultado esperado resumido | Estado inicial | Resultado obtenido | Evidencia/registro |
| --- | --- | --- | --- | --- |
| T01 | I0; dirección NEUTRAL solo si está respaldada independientemente | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T02 | I1; sustituto solo atenúa si disponibilidad, capacidad y acceso están demostrados | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T03 | I2; separar efecto observado de efecto potencial restante | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T04 | I3; demostrar exposición amplia/central y separar efecto observado/potencial | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T05 | I4; amenaza concreta a función esencial o viabilidad demostrada | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T06 | INDETERMINADA; exposición amplia no compensa mecanismo especulativo | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T07 | I4 para escenario condicional sustentado; condición pendiente separada, sin probabilidad inventada | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T08 | Separación por segmentos; MIXTA agregada solo con unidad agregada explícita y respaldada | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T09 | Contradicción preservada; INDETERMINADA para alcance controvertido | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T10 | Mitigación no verificada no reduce intensidad | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T11 | 24 h → INMEDIATO; 7 × 24 h → CORTO; 90 × 24 h → MEDIO | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T12 | Instante posterior a cada frontera → categoría siguiente | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T13 | Fecha sin hora/zona: no inventar timestamp ni categoría exacta | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T14 | Anuncio, aprobación, entrada en vigor e implementación con hitos/relojes separados | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T15 | Intervalo que cruza categorías: conservar intervalo; categoría única INDETERMINADO | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T16 | Evaluación primaria de un humano + crítica IA separada; diferencias documentadas sin promediar ni afirmar acuerdo | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T17 | INDETERMINADA, no I0, cuando no se puede confirmar ni descartar mecanismo material | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T18 | Exactamente 24 h reales durante cambio horario → INMEDIATO | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T19 | Conservar fuentes e intervalo 23 h 50 min–24 h 10 min; categoría única INDETERMINADO | NOT_EXECUTED | PENDIENTE | PENDIENTE |

## 5. Ficha obligatoria por caso

Duplicar esta ficha para cada ejecución de T01–T19. No sustituir un registro anterior: las reevaluaciones deben crear una nueva ejecución vinculada a la anterior.

### Caso TXX

| Campo | Registro |
| --- | --- |
| Estado | NOT_EXECUTED |
| Versión/commit de la propuesta | PENDIENTE |
| Hash del paquete de evidencia | PENDIENTE |
| Fecha/hora de corte | PENDIENTE |
| Unidad y escenario | PENDIENTE |
| Evaluador | PENDIENTE |
| ¿Evaluación independiente? | PENDIENTE |
| Entradas efectivamente utilizadas | PENDIENTE |
| Procedimiento aplicado | PENDIENTE |
| Resultado esperado | PENDIENTE |
| Resultado obtenido | PENDIENTE |
| Evidencia que respalda el resultado | PENDIENTE |
| Discrepancias/contradicciones | PENDIENTE |
| Regla o anclaje cuestionado | PENDIENTE |
| Justificación del estado | PENDIENTE |
| Fecha/hora de registro | PENDIENTE |

## 6. Requisitos adicionales para T16 — protocolo de evaluador único

T16 deja de estar bloqueado por la ausencia de una segunda persona. En SINAYXA existe un único evaluador humano responsable: el propietario. La ejecución se realiza conforme a [single-human-ai-assisted-evaluation-protocol.md](../governance/single-human-ai-assisted-evaluation-protocol.md).

Secuencia obligatoria:

1. Congelar unidad, escenario, corte, propuesta, protocolo y paquete; registrar el SHA-256.
2. El propietario completa y sella la evaluación primaria humana antes de consultar la crítica de IA.
3. Una IA recibe el mismo paquete sin la conclusión humana, preferiblemente en un contexto aislado, y produce una crítica estructurada con referencias a IDs de evidencia.
4. Registrar producto/modelo/versión cuando estén disponibles, fecha/hora, prompt, hash del paquete, aislamiento y limitaciones. Los metadatos no disponibles se marcan `NOT_AVAILABLE`.
5. Comparar la crítica con la evaluación sellada; clasificar diferencias y documentar la decisión del propietario por cada hallazgo.
6. Si una diferencia revela una regla defectuosa, crear una versión metodológica nueva y repetir los casos afectados. Nunca sobrescribir la evaluación previa.

**Límite:** la IA no es un segundo evaluador humano, no tiene voto y no demuestra independencia estadística. T16 no mide acuerdo interevaluador, consenso humano ni fiabilidad interevaluador. Si la crítica de IA no se ejecuta, T16 permanece NOT_EXECUTED; la falta de un segundo humano no es motivo para BLOCKED.

## 7. Cierre de una ejecución

Una ejecución de la batería solo puede considerarse completa cuando:

1. T01–T19 tienen estado terminal justificado (PASS, FAIL, BLOCKED o NOT_APPLICABLE); los BLOCKED deben explicar la dependencia pendiente.
2. Cada PASS/FAIL contiene entradas, procedimiento, resultado obtenido y evidencia rastreable.
3. Las discrepancias han sido documentadas y no ocultadas mediante promedios o cambios retrospectivos.
4. T16 se ha ejecutado conforme al protocolo de evaluador único o permanece NOT_EXECUTED; nunca afirmar validación interevaluador ni consenso humano.
5. Se conserva el paquete congelado y los hashes que permiten reproducir la evaluación.
6. Cualquier modificación de la propuesta crea una nueva versión y exige identificar qué casos deben repetirse.

**Regla de integridad:** nunca cambiar NOT_EXECUTED/BLOCKED a PASS por inferencia, revisión de escritorio o porque el resultado esperado parezca obvio.

## 8. Ejecución local del fixture sintético v1.1.0

### Identificación del artefacto

| Campo | Valor |
| --- | --- |
| Paquete | `SINAYXA-IH-T01-T19-SYNTHETIC-002` |
| Versión | `1.1.0` |
| Commit local confirmado | `3e28232fa7c6a0e261a6fb9b9b5097ef8569a200` |
| SHA-256 | `E685D6BB4459F5A580ABFAC11979D4FCABF385EE7856EC28C16541C2AD05948C` |
| Casos detectados | 19 |
| Estado T16 | BLOCKED |

### Evidencia de ejecución comunicada por el propietario

Entorno: Windows PowerShell 5.1, raíz `C:\Proyecto\SINAYXA`.

Comandos ejecutados:

- `git pull --ff-only`
- `git rev-parse HEAD`
- `validate_intensity_horizon_fixture.ps1 -FixturePath <fixture v1.1.0>`
- `Get-FileHash -LiteralPath $fixture -Algorithm SHA256`
- `git status --short`

Resultado real informado:

- `Fixture structure validation: PASS`
- Paquete: `SINAYXA-IH-T01-T19-SYNTHETIC-002 v1.1.0`
- `Cases: 19`
- `Temporal fixture checks: PASS (T11,T12,T13,T14,T15,T18,T19)`
- `T16: BLOCKED (correctly preserved)`
- SHA-256 del validador y de `Get-FileHash` coincidentes: `E685D6BB4459F5A580ABFAC11979D4FCABF385EE7856EC28C16541C2AD05948C`
- `git status --short`: vacío.

**Alcance del PASS:** integridad estructural del fixture v1.1.0 y comprobaciones temporales deterministas. No acredita la corrección semántica de las clasificaciones esperadas de T01–T19, ni ejecución formal de esos casos, ni acuerdo entre evaluadores. La matriz de ejecución permanece sin cambios: T01–T15 y T17–T19 NOT_EXECUTED; T16 BLOCKED.

## 9. Fixture sintético v1.2.0 — adaptación de T16 al proyecto de un único humano

### Identificación

| Campo | Valor |
| --- | --- |
| Paquete | `SINAYXA-IH-T01-T19-SYNTHETIC-003` |
| Versión | `1.2.0` |
| Archivo | `tests/fixtures/methodology/intensity-horizons/t01-t19-synthetic-evidence-v1.2.0.json` |
| Paquete anterior | `SINAYXA-IH-T01-T19-SYNTHETIC-002` v1.1.0 |
| SHA-256 del paquete anterior | `E685D6BB4459F5A580ABFAC11979D4FCABF385EE7856EC28C16541C2AD05948C` |
| Estado de ejecución T16 | NOT_EXECUTED |

### Cambio de T16

La versión 1.2.0 conserva los 19 casos y los datos históricos de T01–T15 y T17–T19. T16 se redefine para comprobar un flujo viable con un solo evaluador humano:

- el propietario registra y sella la evaluación primaria;
- después, una IA realiza una crítica estructurada del mismo paquete sin recibir la conclusión humana;
- se registra la procedencia de la IA y cualquier limitación de aislamiento;
- el propietario resuelve y documenta los hallazgos;
- no se promedian resultados ni se afirma acuerdo interevaluador.

La versión 1.1.0 y su hash permanecen inmutables. La nueva versión no contiene respuestas humanas o de IA simuladas: solo define el proceso esperado.

### Validador

`validate_intensity_horizon_fixture.ps1` admite las versiones 1.0.0, 1.1.0 y 1.2.0. Para 1.2.0 comprueba el linaje del paquete y los campos de contrato de T16. El resultado del validador solo acreditará estructura y presencia de salvaguardas; no acreditará que el propietario haya realizado la evaluación ni que la crítica de IA se haya ejecutado.

### Estado y límites

T16 pasa de BLOCKED por una dependencia humana imposible a NOT_EXECUTED: el proceso ya es ejecutable por el único propietario, pero todavía no se ha realizado. Los estados de los otros casos no cambian. No se afirma acuerdo entre evaluadores humanos, fiabilidad interevaluador, consenso ni validez empírica.


## 10. Ejecución local del fixture sintético v1.2.0

### Identificación y entorno

| Campo | Valor |
| --- | --- |
| Paquete | `SINAYXA-IH-T01-T19-SYNTHETIC-003` |
| Versión | `1.2.0` |
| Commit local ejecutado | `bae7ae515ac64d64edf3676250a6cdde32889783` |
| Entorno | Windows PowerShell 5.1 |
| Casos detectados | 19 |
| SHA-256 | `5E02420E11FF6F9A1E456F6AFC227EB983B85F61C0AB2624F15D71484957F5BB` |

### Resultado comunicado por el propietario

- `Fixture structure validation: PASS`
- `Temporal fixture checks: PASS (T11,T12,T13,T14,T15,T18,T19)`
- `T16: SINGLE-HUMAN PROTOCOL DEFINED (not an execution result)`
- `Get-FileHash` devolvió el mismo SHA-256 que el validador.
- `git status --short`: vacío.

**Alcance:** queda verificada la estructura del fixture v1.2.0, el linaje comprobado por el validador y los vectores temporales deterministas indicados. La salida de T16 confirma que el protocolo de un único humano está definido; no acredita que se haya realizado la evaluación primaria ni la crítica de IA. T01–T15 y T17–T19 siguen NOT_EXECUTED; T16 sigue NOT_EXECUTED. No se declara acuerdo interevaluador humano, consenso ni validez empírica.

### Resultado de Markdown lint comunicado por el propietario

El comando solicitado para cuatro documentos produjo `312 issues in 2 files`. La configuración `.markdownlint-cli2.jsonc` incluye el patrón global `**/*.md`, por lo que la ejecución también alcanzó `docs/news-and-events/catalyst-taxonomy-test-cases.md`, un documento ajeno a este cambio. El registro de intensidad mostró incidencias de formato propias, que se corrigen en esta revisión. No se interpreta el resultado global como fallo de los cuatro documentos seleccionados ni se modifica aquí el documento de taxonomía ajeno al alcance.

Para una comprobación estrictamente limitada a los cuatro archivos, ejecutar markdownlint-cli2 con `--no-globs` y las cuatro rutas explícitas. El resultado de esa ejecución queda pendiente; no se declara PASS.
