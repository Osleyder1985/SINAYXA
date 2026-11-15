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
| Comando | `.\scripts\validation\validate_intensity_horizon_fixture.ps1` |
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
| T01 | I0; dirección NEUTRAL solo si está respaldada independientemente | NOT_EXECUTED | I0; INDETERMINADA (decisión humana posterior a recomendación IA; desviación de secuencia) | Sección 11; ejecución conforme al protocolo pendiente |
| T02 | I1; sustituto solo atenúa si disponibilidad, capacidad y acceso están demostrados | NOT_EXECUTED | I1; INDETERMINADA (decisión humana posterior a recomendación IA; desviación de secuencia) | Sección 12; ejecución conforme al protocolo pendiente |
| T03 | I2; separar efecto observado de efecto potencial restante | NOT_EXECUTED | I2; NEGATIVA para el segmento institucional afectado (decisión humana posterior a recomendación IA; desviación de secuencia) | Sección 13; ejecución conforme al protocolo pendiente |
| T04 | I3; demostrar exposición amplia/central y separar efecto observado/potencial | NOT_EXECUTED | I3; NEGATIVA para el ecosistema DELTA definido (decisión humana posterior a recomendación IA; desviación de secuencia) | Sección 14; ejecución conforme al protocolo pendiente |
| T05 | I4; amenaza concreta a función esencial o viabilidad demostrada | NOT_EXECUTED | I4; NEGATIVA para el servicio de autorización de retiros EPSILON (decisión humana posterior a recomendación IA; desviación de secuencia) | Sección 15; ejecución conforme al protocolo pendiente |
| T06 | INDETERMINADA; exposición amplia no compensa mecanismo especulativo | NOT_EXECUTED | INDETERMINADA; dirección INDETERMINADA (decisión humana posterior a recomendación IA; desviación de secuencia) | Sección 16; ejecución conforme al protocolo pendiente |
| T07 | I4 para escenario condicional sustentado; condición pendiente separada, sin probabilidad inventada | NOT_EXECUTED | I4; NEGATIVA para el escenario condicional (decisión humana asistida por IA; desviación de secuencia); condición PENDING / NOT CONFIRMED; probabilidad NOT_ASSIGNED | Sección 17; ejecución conforme al protocolo pendiente |
| T08 | Separación por segmentos; MIXTA agregada solo con unidad agregada explícita y respaldada | NOT_EXECUTED | Segmento A: I2 / NEGATIVA; segmento B: I2 / POSITIVA; THETA agregado: sin clasificación (decisión humana asistida por IA; desviación de secuencia) | Sección 18; ejecución conforme al protocolo pendiente |
| T09 | Contradicción preservada; INDETERMINADA para alcance controvertido | NOT_EXECUTED | INDETERMINADA; dirección INDETERMINADA (decisión humana asistida por IA; desviación de secuencia) | Sección 19; ejecución conforme al protocolo pendiente |
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
| Justificación del estado | PENDIENTE || Fecha/hora de registro | PENDIENTE |

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


## 11. Registro de decisión asistida — T01

### 11.1 Identificación del caso

| Campo | Registro |
| --- | --- |
| Caso | T01 |
| Paquete | `SINAYXA-IH-T01-T19-SYNTHETIC-003` |
| Versión del paquete | `1.2.0` |
| SHA-256 del paquete | `5E02420E11FF6F9A1E456F6AFC227EB983B85F61C0AB2624F15D71484957F5BB` |
| Unidad | Funciones técnicas y operativas del protocolo ficticio ALPHA; excluye valoración del token, reputación, atención y demanda |
| Corte | `2026-01-10T12:00:00Z` |
| Evidencias examinadas | T01-E1, T01-E2 y T01-E3 |
| Decisión humana comunicada | I0; dirección INDETERMINADA |
| Estado de ejecución formal | NOT_EXECUTED |

### 11.2 Razonamiento y decisión adoptada

El propietario aceptó la recomendación metodológica de asignar **I0** para la unidad técnica y operativa delimitada. La evidencia sintética establece que:
- el inventario revisado no identifica dependencias técnicas u operativas respecto del sitio web renombrado (T01-E1);
- el alcance del inventario se declara completo para la unidad y el anuncio evaluados al corte (T01-E2);
- los registros de despliegue, configuración, acceso, estado de servicios e incidentes no muestran cambios operativos atribuibles al anuncio (T01-E3).

La dirección se registra como **INDETERMINADA**, no NEUTRAL: la evidencia permite descartar un mecanismo material dentro de la unidad técnica/operativa declarada, pero no establece una dirección para dimensiones excluidas ni aporta evidencia independiente que justifique NEUTRAL.

La clasificación no se extrapola al valor de mercado del token, reputación, atención ni demanda.

### 11.3 Desviación del protocolo y límites de validez

La recomendación de IA se presentó antes de que el propietario comunicara su decisión. Por tanto, esta interacción **no cumple la secuencia de la sección 3 del protocolo de evaluación con un único responsable humano**: no hubo una evaluación primaria humana sellada antes de la revisión de IA, ni una crítica posterior realizada sin conocer la conclusión humana.

La aceptación del propietario se conserva como una **decisión humana asistida por IA**, con exposición previa a la recomendación. No se etiqueta como evaluación ciega, independiente ni como ejecución conforme al protocolo. No se afirma acuerdo interevaluador, consenso, validez empírica ni ejecución integral de T01.

Para completar una ejecución formal conforme al protocolo, será necesario realizar una nueva evaluación en la secuencia correcta, con el paquete congelado y la evaluación humana sellada antes de entregar el paquete a la IA. Esa nueva ejecución deberá conservarse como un registro separado; no sobrescribirá esta decisión.

### 11.4 Resultado de auditoría

La decisión I0 / INDETERMINADA queda documentada como decisión humana asistida. **T01 permanece NOT_EXECUTED en la matriz formal** hasta completar una ejecución que respete el protocolo y documente sus artefactos. La coincidencia con el resultado esperado del fixture no se considera prueba de validez metodológica.


## 12. Registro de decisión asistida — T02

### 12.1 Identificación del caso

| Campo | Registro |
| --- | --- |
| Caso | T02 |
| Paquete | `SINAYXA-IH-T01-T19-SYNTHETIC-003` |
| Versión del paquete | `1.2.0` |
| SHA-256 del paquete | `5E02420E11FF6F9A1E456F6AFC227EB983B85F61C0AB2624F15D71484957F5BB` |
| Unidad | Servicio de atención de la plataforma ficticia BETA |
| Corte | `2026-01-10T12:00:00Z` |
| Evidencias examinadas | T02-E1, T02-E2 y T02-E3 |
| Decisión humana comunicada | I1; dirección INDETERMINADA |
| Estado de ejecución formal | NOT_EXECUTED |

### 12.2 Razonamiento y decisión adoptada

El propietario aceptó la recomendación metodológica de asignar **I1 (BAJA)** para la unidad de servicio de atención definida.

- T02-E1 documenta una interrupción efectiva y localizada en un único endpoint de soporte. También indica que trading, custodia, depósitos, retiros y liquidación continúan operativos.
- T02-E2 documenta que el canal alternativo acepta la misma clase de solicitudes bajo la carga de prueba medida.
- T02-E3 documenta que la población afectada puede autenticarse y acceder al canal alternativo.

La alternativa no se considera eficaz por el mero hecho de haber sido anunciada: el fixture aporta evidencia sintética específica de capacidad y acceso. El efecto queda acotado al servicio de soporte y no se acredita una alteración apreciable más amplia que justifique I2, ni exposición amplia/central para I3, ni amenaza a una función esencial para I4.

La dirección se registra como **INDETERMINADA**. La existencia de una interrupción no demuestra por sí sola la dirección neta de sus consecuencias dentro de la unidad, y la mitigación disponible no constituye evidencia de un efecto positivo o neutral.

### 12.3 Desviación del protocolo y límites de validez

La recomendación de IA se presentó antes de que el propietario comunicara su decisión. Por tanto, esta interacción no cumple la secuencia de evaluación primaria sellada antes de la crítica de IA establecida en el protocolo de evaluador único.

La aceptación se conserva como **decisión humana asistida por IA**, con exposición previa a la recomendación. No se etiqueta como evaluación ciega, independiente ni como ejecución conforme al protocolo. No se afirma acuerdo interevaluador, consenso, validez empírica ni ejecución integral de T02.

Para completar una ejecución formal conforme al protocolo, será necesaria una nueva evaluación con el paquete congelado: primero se registra y sella la evaluación humana sin conocer la salida de IA y, después, se realiza la crítica auxiliar separada. La nueva ejecución se conservará como un registro distinto, sin sobrescribir esta decisión.

### 12.4 Resultado de auditoría

La decisión **I1 / INDETERMINADA** queda documentada como decisión humana asistida. **T02 permanece NOT_EXECUTED en la matriz formal** hasta completar una ejecución que respete el protocolo y documente sus artefactos. La coincidencia con el resultado esperado del fixture no se considera prueba de validez metodológica.


## 13. Registro de decisión asistida — T03

### 13.1 Identificación del caso

| Campo | Registro |
| --- | --- |
| Caso | T03 |
| Paquete | `SINAYXA-IH-T01-T19-SYNTHETIC-003` |
| Versión del paquete | `1.2.0` |
| SHA-256 del paquete | `5E02420E11FF6F9A1E456F6AFC227EB983B85F61C0AB2624F15D71484957F5BB` |
| Unidad | Segmento institucional afectado del exchange ficticio GAMMA |
| Corte | `2026-01-10T12:00:00Z` |
| Evidencias examinadas | T03-E1, T03-E2, T03-E3 y T03-E4 |
| Decisión humana comunicada | I2; dirección NEGATIVA para el segmento institucional afectado |
| Estado de ejecución formal | NOT_EXECUTED |

### 13.2 Razonamiento y decisión adoptada

El propietario aceptó la recomendación metodológica de asignar **I2** y dirección **NEGATIVA** para el segmento institucional afectado.

- T03-E1 delimita el componente de procesamiento al segmento institucional identificado; no establece dependencia de otros segmentos.
- T03-E2 documenta 27 solicitudes de depósito pertenecientes a 11 cuentas institucionales que permanecen sin acreditar cuatro horas después del plazo de procesamiento documentado.
- T03-E3 acredita la consecuencia funcional: mientras los depósitos sigan pendientes, las cuentas afectadas no pueden utilizar esos fondos para trading ni como colateral. Los retiros de saldos ya acreditados y otras funciones del exchange permanecen disponibles.
- T03-E4 limita el alcance acreditado al segmento institucional y advierte que no se ha demostrado que ese segmento o esa ruta de depósitos sean centrales para el exchange en su conjunto.

El efecto observado se separa del potencial: el efecto observado es la falta de acreditación y la indisponibilidad funcional de los fondos al corte; el efecto potencial es que la restricción continúe mientras el componente permanezca indisponible. La duración futura no está establecida.

La dirección NEGATIVA se refiere exclusivamente a la restricción de capacidad operativa del segmento afectado. No implica una conclusión sobre el precio del token, el mercado general ni el exchange completo. Los recuentos y la duración son hechos ficticios del caso, no umbrales universales de intensidad.

### 13.3 Desviación del protocolo y límites de validez

La recomendación de IA se presentó antes de que el propietario comunicara su decisión. Por tanto, esta interacción no cumple la secuencia de evaluación primaria humana sellada antes de la crítica de IA establecida en el protocolo de evaluador único.

La aceptación se conserva como **decisión humana asistida por IA**, con exposición previa a la recomendación. No se etiqueta como evaluación ciega, independiente ni como ejecución conforme al protocolo. No se afirma acuerdo interevaluador, consenso, validez empírica ni ejecución integral de T03.

Para completar una ejecución formal conforme al protocolo, será necesaria una nueva evaluación con el paquete congelado: primero se registra y sella la evaluación humana sin conocer la salida de IA y, después, se realiza la crítica auxiliar separada. La nueva ejecución se conservará como un registro distinto, sin sobrescribir esta decisión.

### 13.4 Resultado de auditoría

La decisión **I2 / NEGATIVA para el segmento institucional afectado** queda documentada como decisión humana asistida. **T03 permanece NOT_EXECUTED en la matriz formal** hasta completar una ejecución que respete el protocolo y documente sus artefactos. La coincidencia con el resultado esperado del fixture no se considera prueba de validez metodológica.


## 14. Registro de decisión asistida — T04

### 14.1 Identificación del caso

| Campo | Registro |
| --- | --- |
| Caso | T04 |
| Paquete | `SINAYXA-IH-T01-T19-SYNTHETIC-003` |
| Versión del paquete | `1.2.0` |
| SHA-256 del paquete | `5E02420E11FF6F9A1E456F6AFC227EB983B85F61C0AB2624F15D71484957F5BB` |
| Unidad | Ecosistema ficticio de aplicaciones dependientes de oráculos del protocolo DELTA |
| Corte | `2026-01-10T12:00:00Z` |
| Evidencias examinadas | T04-E1, T04-E2, T04-E3, T04-E4 y T04-E5 |
| Decisión humana comunicada | I3; dirección NEGATIVA para el ecosistema DELTA definido |
| Estado de ejecución formal | NOT_EXECUTED |

### 14.2 Razonamiento y decisión adoptada

El propietario aceptó la recomendación metodológica de asignar **I3** y dirección **NEGATIVA** para el ecosistema DELTA definido.

- T04-E1 establece el denominador completo de cinco aplicaciones dentro de la unidad y acredita que cuatro dependen de la misma ruta de publicación del oráculo.
- T04-E2 registra que las actualizaciones del feed incumplen durante 38 minutos consecutivos la condición documentada de frescura, y que las cuatro aplicaciones dependientes registran el incumplimiento.
- T04-E3 confirma mediante registros de aplicación la suspensión de nuevas operaciones de lending y borrowing en las cuatro aplicaciones. Se trata de una alteración observada de una capacidad operativa material.
- T04-E4 documenta límites de continuidad: las posiciones existentes siguen siendo consultables, el feed secundario mantiene los controles de seguridad de esas posiciones y los retiros y el acceso de usuarios permanecen disponibles. No se acredita compromiso de custodia, liquidación, acceso esencial, viabilidad del protocolo ni interrupción general del sistema.
- T04-E5 confirma que el inventario de cinco aplicaciones está completo para la unidad definida y que las cuatro aplicaciones afectadas son componentes centrales de ese ecosistema. No se extrapola el resultado a aplicaciones externas a esa unidad.

La clasificación I3 se fundamenta en la exposición amplia y central dentro del ecosistema delimitado y en el cambio operativo material efectivamente observado. I2 no representa adecuadamente ese alcance. I4 no está respaldado porque las evidencias describen mecanismos de continuidad activos y no acreditan amenaza a la viabilidad, solvencia, custodia, liquidación o acceso esencial.

El efecto observado es la suspensión de nuevas operaciones de lending y borrowing en cuatro de las cinco aplicaciones al corte. El efecto potencial es que la suspensión continúe mientras se incumpla la condición de frescura del oráculo; no se establece duración posterior a los 38 minutos observados.

La dirección NEGATIVA se refiere exclusivamente a la condición operativa del ecosistema definido. No constituye una predicción del precio de un activo ni una conclusión sobre todo el mercado DeFi.

### 14.3 Desviación del protocolo y límites de validez

La recomendación de IA se presentó antes de que el propietario comunicara su decisión. Por tanto, esta interacción no cumple la secuencia de evaluación primaria humana sellada antes de la crítica de IA establecida en el protocolo de evaluador único.

La aceptación se conserva como **decisión humana asistida por IA**, con exposición previa a la recomendación. No se etiqueta como evaluación ciega, independiente ni como ejecución conforme al protocolo. No se afirma acuerdo interevaluador, consenso, validez empírica ni ejecución integral de T04.

Para completar una ejecución formal conforme al protocolo, será necesaria una nueva evaluación con el paquete congelado: primero se registra y sella la evaluación humana sin conocer la salida de IA y, después, se realiza la crítica auxiliar separada. La nueva ejecución se conservará como un registro distinto, sin sobrescribir esta decisión.

### 14.4 Resultado de auditoría

La decisión **I3 / NEGATIVA para el ecosistema DELTA definido** queda documentada como decisión humana asistida. **T04 permanece NOT_EXECUTED en la matriz formal** hasta completar una ejecución que respete el protocolo y documente sus artefactos. La coincidencia con el resultado esperado del fixture no se considera prueba de validez metodológica.


## 15. Registro de decisión asistida — T05
### 15.1 Identificación del caso

| Campo | Registro |
| --- | --- |
| Caso | T05 |
| Paquete | `SINAYXA-IH-T01-T19-SYNTHETIC-003` |
| Versión del paquete | `1.2.0` |
| SHA-256 del paquete | `5E02420E11FF6F9A1E456F6AFC227EB983B85F61C0AB2624F15D71484957F5BB` |
| Unidad | Servicio de autorización de retiros de la red ficticia de custodia EPSILON |
| Corte | `2026-01-10T12:00:00Z` |
| Evidencias examinadas | T05-E1, T05-E2 y T05-E3 |
| Decisión humana comunicada | I4; dirección NEGATIVA para el servicio de autorización de retiros EPSILON |
| Estado de ejecución formal | NOT_EXECUTED |

### 15.2 Razonamiento y decisión adoptada

El propietario aceptó la recomendación metodológica de asignar **I4** y dirección **NEGATIVA** para el servicio de autorización de retiros EPSILON.

- T05-E1 aporta un informe forense que confirma el compromiso del único servicio de autorización.
- T05-E2 establece que no existe una ruta independiente de autorización para la unidad de custodia declarada.
- T05-E3 documenta que el servicio comprometido es necesario para ejecutar retiros y que existe una amenaza al acceso esencial de los clientes a sus activos.

La combinación de compromiso confirmado, dependencia exclusiva y amenaza documentada a una función esencial respalda I4. No se trata solamente de una degradación de una capacidad secundaria ni de una interrupción acotada con alternativa demostrada.

La dirección NEGATIVA se refiere a la seguridad y al acceso esencial a los activos dentro de la unidad declarada. El registro no afirma que los activos hayan sido sustraídos, que exista una pérdida de fondos, que se haya producido insolvencia ni que el daño se haya materializado. Esas conclusiones no están respaldadas por las evidencias T05 disponibles.

### 15.3 Desviación del protocolo y límites de validez

La recomendación de IA se presentó antes de que el propietario comunicara su decisión. Por tanto, esta interacción no cumple la secuencia de evaluación primaria humana sellada antes de la crítica de IA establecida en el protocolo de evaluador único.

La aceptación se conserva como **decisión humana asistida por IA**, con exposición previa a la recomendación. No se etiqueta como evaluación ciega, independiente ni como ejecución conforme al protocolo. No se afirma acuerdo interevaluador, consenso, validez empírica ni ejecución integral de T05.

Para completar una ejecución formal conforme al protocolo, será necesaria una nueva evaluación con el paquete congelado: primero se registra y sella la evaluación humana sin conocer la salida de IA y, después, se realiza la crítica auxiliar separada. La nueva ejecución se conservará como un registro distinto, sin sobrescribir esta decisión.

### 15.4 Resultado de auditoría

La decisión **I4 / NEGATIVA para el servicio de autorización de retiros EPSILON** queda documentada como decisión humana asistida. **T05 permanece NOT_EXECUTED en la matriz formal** hasta completar una ejecución que respete el protocolo y documente sus artefactos. La coincidencia con el resultado esperado del fixture no se considera prueba de validez metodológica.


## 16. Registro de decisión asistida — T06

### 16.1 Identificación del caso

| Campo | Registro |
| --- | --- |
| Caso | T06 |
| Paquete | `SINAYXA-IH-T01-T19-SYNTHETIC-003` |
| Versión del paquete | `1.2.0` |
| SHA-256 del paquete | `5E02420E11FF6F9A1E456F6AFC227EB983B85F61C0AB2624F15D71484957F5BB` |
| Unidad | Segmento ficticio de mercado de criptoactivos ZETA |
| Corte | `2026-01-10T12:00:00Z` |
| Evidencias examinadas | T06-E1 y T06-E2 |
| Decisión humana comunicada | Intensidad INDETERMINADA; dirección INDETERMINADA |
| Estado de ejecución formal | NOT_EXECUTED |

### 16.2 Razonamiento y decisión adoptada

El propietario aceptó la recomendación metodológica de mantener la intensidad y la dirección como **INDETERMINADAS**.

- T06-E1 contiene únicamente una publicación anónima que afirma que un proveedor podría interrumpir su apoyo al segmento.
- T06-E2 establece que no existe inventario de dependencias verificado, declaración del proveedor ni evidencia operativa que conecte al proveedor con la unidad analizada.

La magnitud potencial de una eventual retirada no sustituye la evidencia necesaria para demostrar un mecanismo de exposición. Por tanto, no se asigna I1, I2, I3 o I4.

Tampoco se asigna I0: la falta de evidencia de dependencia no demuestra que el mecanismo de impacto material haya sido descartado. El caso no permite distinguir entre ausencia de dependencia y dependencia todavía no investigada o documentada.

La dirección permanece INDETERMINADA porque no se ha establecido una consecuencia atribuible sobre la unidad analizada.

El rumor puede justificar vigilancia y recopilación posterior de evidencias, pero no debe registrarse como catalizador confirmado ni como impacto demostrado. Una futura declaración oficial, inventario verificable o evidencia operativa deberá evaluarse con un nuevo corte y conservarse como una reevaluación, sin reescribir este registro.

### 16.3 Desviación del protocolo y límites de validez

La recomendación de IA se presentó antes de que el propietario comunicara su decisión. Por tanto, esta interacción no cumple la secuencia de evaluación primaria humana sellada antes de la crítica de IA establecida en el protocolo de evaluador único.

La aceptación se conserva como **decisión humana asistida por IA**, con exposición previa a la recomendación. No se etiqueta como evaluación ciega, independiente ni como ejecución conforme al protocolo. No se afirma acuerdo interevaluador, consenso, validez empírica ni ejecución integral de T06.

Para completar una ejecución formal conforme al protocolo, será necesaria una nueva evaluación con el paquete congelado: primero se registra y sella la evaluación humana sin conocer la salida de IA y, después, se realiza la crítica auxiliar separada. La nueva ejecución se conservará como un registro distinto, sin sobrescribir esta decisión.

### 16.4 Resultado de auditoría

La decisión **INDETERMINADA / INDETERMINADA** queda documentada como decisión humana asistida. **T06 permanece NOT_EXECUTED en la matriz formal** hasta completar una ejecución que respete el protocolo y documente sus artefactos. La coincidencia con el resultado esperado del fixture no se considera prueba de validez metodológica.



## 17. Registro de decisión asistida — T07

### 17.1 Identificación del caso

| Campo | Registro |
| --- | --- |
| Caso | T07 |
| Paquete | `SINAYXA-IH-T01-T19-SYNTHETIC-003` |
| Versión del paquete | `1.2.0` |
| SHA-256 del paquete | `5E02420E11FF6F9A1E456F6AFC227EB983B85F61C0AB2624F15D71484957F5BB` |
| Unidad | Función de retiro del puente ficticio ETA |
| Corte | `2026-01-10T12:00:00Z` |
| Evidencias examinadas | T07-E1, T07-E2 y T07-E3 |
| Decisión humana comunicada | I4 para el escenario condicional; dirección NEGATIVA para ese escenario |
| Estado de la condición desencadenante | PENDING / NOT CONFIRMED |
| Probabilidad | NOT_ASSIGNED |
| Estado de ejecución formal | NOT_EXECUTED |

### 17.2 Razonamiento y decisión adoptada

El propietario aceptó la recomendación de asignar **I4** al escenario condicional en el que se active la condición técnica de emergencia y se suspenda la única función de retiro.

- T07-E1 establece que el puente dispone de una única función de retiro y que no existe una ruta alternativa para la unidad evaluada.
- T07-E2 documenta en el plan de contingencia que la condición técnica de emergencia activa una pausa de los retiros.
- T07-E3 indica que la condición desencadenante no está confirmada en el corte evaluado.

La intensidad I4 se refiere exclusivamente a la gravedad del escenario condicional sustentado: la suspensión de la única función de retiro comprometería el acceso esencial a los activos dentro de la unidad definida. La ausencia de una ruta alternativa respalda la severidad de ese escenario.

Esta clasificación **no afirma que los retiros estén actualmente suspendidos**, que el desencadenante haya ocurrido ni que la suspensión sea inminente. La condición permanece PENDING / NOT CONFIRMED. No se asigna probabilidad porque las evidencias no proporcionan una base cuantitativa o cualitativa calibrada para hacerlo.

La dirección NEGATIVA se refiere al efecto que tendría la activación del escenario sobre la disponibilidad de retiros y el acceso a los activos. No describe un efecto actualmente observado ni predice el precio de un criptoactivo.

### 17.3 Desviación del protocolo y límites de validez

La recomendación de IA se presentó antes de que el propietario comunicara su decisión. Por tanto, esta interacción no cumple la secuencia de evaluación primaria humana sellada antes de la crítica de IA establecida en el protocolo de evaluador único.

La aceptación se conserva como **decisión humana asistida por IA**, con exposición previa a la recomendación. No se etiqueta como evaluación ciega, independiente ni como ejecución conforme al protocolo. No se afirma acuerdo interevaluador, consenso, validez empírica ni ejecución integral de T07.

Para completar una ejecución formal conforme al protocolo, será necesaria una nueva evaluación con el paquete congelado: primero se registra y sella la evaluación humana sin conocer la salida de IA y, después, se realiza la crítica auxiliar separada. La nueva ejecución se conservará como un registro distinto, sin sobrescribir esta decisión.

### 17.4 Resultado de auditoría

La decisión **I4 / NEGATIVA para el escenario condicional de suspensión de retiros** queda documentada como decisión humana asistida. La condición desencadenante permanece **PENDING / NOT CONFIRMED** y la probabilidad **NOT_ASSIGNED**. **T07 permanece NOT_EXECUTED en la matriz formal** hasta completar una ejecución que respete el protocolo y documente sus artefactos. La coincidencia con el resultado esperado del fixture no se considera prueba de validez metodológica.


## 18. Registro de decisión asistida — T08

### 18.1 Identificación del caso

| Campo | Registro |
| --- | --- |
| Caso | T08 |
| Paquete | `SINAYXA-IH-T01-T19-SYNTHETIC-003` |
| Versión del paquete | `1.2.0` |
| SHA-256 del paquete | `5E02420E11FF6F9A1E456F6AFC227EB983B85F61C0AB2624F15D71484957F5BB` |
| Unidad | Activo ficticio THETA, con segmentos de usuarios A y B definidos por flujos de trabajo separados |
| Corte | `2026-01-10T12:00:00Z` |
| Evidencias examinadas | T08-E1, T08-E2, T08-E3, T08-E4 y T08-E5 |
| Decisión humana comunicada | Segmento A: I2 / NEGATIVA; segmento B: I2 / POSITIVA; agregado: sin clasificación |
| Estado de ejecución formal | NOT_EXECUTED |

### 18.2 Razonamiento y decisión adoptada

El propietario aceptó mantener clasificaciones independientes para los dos segmentos y no asignar una clasificación agregada al activo THETA.

**Segmento A — I2 / NEGATIVA**

- T08-E1 establece que el flujo de liquidación declarado depende de la integración R como única ruta soportada, según el inventario de flujos y los registros previos de transacciones exitosas.
- T08-E2 documenta que, después del evento, R rechaza las solicitudes del flujo de Segmento A y que las transacciones afectadas no pueden completar la liquidación; no hay ruta alternativa disponible al corte.

La pérdida de la única ruta soportada constituye una restricción funcional directa y material, acotada al flujo de liquidación de ese segmento. No se acredita amenaza a acceso esencial o viabilidad que justifique I4, ni exposición amplia/central fuera de la unidad delimitada que justifique I3.

**Segmento B — I2 / POSITIVA**

- T08-E3 establece que, antes del evento, el flujo de ejecución de mercado declarado no disponía de una ruta soportada hacia el venue identificado.
- T08-E4 documenta que la integración R pasa a estar disponible y que los registros de transacciones exitosas confirman la ejecución del flujo antes no disponible.

La nueva capacidad funcional es directa y está observada, pero permanece acotada al flujo declarado. La evidencia no justifica elevar la intensidad a I3 o I4.

**Activo THETA en conjunto — sin clasificación agregada**

T08-E5 confirma que A y B son segmentos definidos por dependencias y poblaciones de evidencia diferentes, pero no proporciona una unidad agregada de mercado ni un denominador común para combinarlos. Por ello, no se asigna intensidad ni dirección agregada. No se utiliza el beneficio de B para cancelar el perjuicio de A, ni viceversa.

La categoría MIXTA podría considerarse únicamente en una reevaluación agregada posterior, si se define explícitamente una unidad agregada defendible y se conservan por separado las clasificaciones y evidencias de ambos segmentos. No se promedian ni compensan sus efectos.

Las direcciones NEGATIVA y POSITIVA describen las consecuencias funcionales observadas en cada segmento. No constituyen una predicción de precio ni una conclusión global sobre el mercado del activo THETA.

### 18.3 Desviación del protocolo y límites de validez

La recomendación de IA se presentó antes de que el propietario comunicara su decisión. Por tanto, esta interacción no cumple la secuencia de evaluación primaria humana sellada antes de la crítica de IA establecida en el protocolo de evaluador único.

La aceptación se conserva como **decisión humana asistida por IA**, con exposición previa a la recomendación. No se etiqueta como evaluación ciega, independiente ni como ejecución conforme al protocolo. No se afirma acuerdo interevaluador, consenso, validez empírica ni ejecución integral de T08.

Para completar una ejecución formal conforme al protocolo, será necesaria una nueva evaluación con el paquete congelado: primero se registra y sella la evaluación humana sin conocer la salida de IA y, después, se realiza la crítica auxiliar separada. La nueva ejecución se conservará como un registro distinto, sin sobrescribir esta decisión.

### 18.4 Resultado de auditoría

Las decisiones **I2 / NEGATIVA para el segmento A** e **I2 / POSITIVA para el segmento B**, sin clasificación agregada para THETA, quedan documentadas como decisión humana asistida. **T08 permanece NOT_EXECUTED en la matriz formal** hasta completar una ejecución que respete el protocolo y documente sus artefactos. La coincidencia con el resultado esperado del fixture no se considera prueba de validez metodológica.



## 19. Registro de decisión asistida — T09

### 19.1 Identificación del caso

| Campo | Registro |
| --- | --- |
| Caso | T09 |
| Paquete | `SINAYXA-IH-T01-T19-SYNTHETIC-003` |
| Versión del paquete | `1.2.0` |
| SHA-256 del paquete | `5E02420E11FF6F9A1E456F6AFC227EB983B85F61C0AB2624F15D71484957F5BB` |
| Unidad | Población de validadores del protocolo ficticio IOTA |
| Corte | `2026-01-10T12:00:00Z` |
| Evidencias examinadas | T09-E1, T09-E2 y T09-E3 |
| Decisión humana comunicada | Intensidad INDETERMINADA; dirección INDETERMINADA |
| Estado de ejecución formal | NOT_EXECUTED |

### 19.2 Razonamiento y decisión adoptada

El propietario aceptó mantener la intensidad y la dirección como **INDETERMINADAS** ante la contradicción no resuelta sobre el alcance de la exposición.

- T09-E1 contiene un informe que afirma que la exposición de validadores es amplia, pero no revela el denominador utilizado para sustentar esa afirmación.
- T09-E2 aporta registros contrarios y cuestiona que la exposición sea amplia.
- T09-E3 establece que no existe una regla metodológica aprobada de credibilidad de fuentes que permita resolver el conflicto.

No se selecciona uno de los informes por autoridad, mayoría, apariencia de precisión ni preferencia del evaluador. Tampoco se combinan sus afirmaciones como si fueran compatibles. La contradicción se conserva explícitamente y el alcance controvertido no se considera establecido.

No se asigna I0: la falta de demostración de exposición amplia no equivale a evidencia suficiente para descartar un mecanismo material dentro de la unidad evaluada. Tampoco se asigna I1, I2, I3 o I4, porque el alcance y la exposición material no pueden establecerse con la evidencia disponible y una regla de resolución aprobada.

La dirección permanece INDETERMINADA porque no se ha demostrado una consecuencia atribuible con dirección determinada. La evaluación no debe convertir la incertidumbre sobre el alcance en una conclusión sobre el precio del activo ni sobre el protocolo en su conjunto.

La reevaluación requerirá evidencia verificable que permita delimitar la población y/o una regla de credibilidad aprobada y aplicable. Cualquier nueva evaluación deberá conservar las fuentes originales, el conflicto, el nuevo corte y la justificación de los cambios; no deberá sobrescribir este registro.

### 19.3 Desviación del protocolo y límites de validez

La recomendación de IA se presentó antes de que el propietario comunicara su decisión. Por tanto, esta interacción no cumple la secuencia de evaluación primaria humana sellada antes de la crítica de IA establecida en el protocolo de evaluador único.

La aceptación se conserva como **decisión humana asistida por IA**, con exposición previa a la recomendación. No se etiqueta como evaluación ciega, independiente ni como ejecución conforme al protocolo. No se afirma acuerdo interevaluador, consenso, validez empírica ni ejecución integral de T09.

Para completar una ejecución formal conforme al protocolo, será necesaria una nueva evaluación con el paquete congelado: primero se registra y sella la evaluación humana sin conocer la salida de IA y, después, se realiza la crítica auxiliar separada. La nueva ejecución se conservará como un registro distinto, sin sobrescribir esta decisión.

### 19.4 Resultado de auditoría

La decisión **INDETERMINADA / INDETERMINADA** queda documentada como decisión humana asistida. La contradicción entre T09-E1 y T09-E2 permanece abierta; no se ha establecido un criterio aprobado para resolverla. **T09 permanece NOT_EXECUTED en la matriz formal** hasta completar una ejecución que respete el protocolo y documente sus artefactos. La coincidencia con el resultado esperado del fixture no se considera prueba de validez metodológica.
