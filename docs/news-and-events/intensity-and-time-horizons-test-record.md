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

## 2.1 Paquetes sintéticos congelados y linaje de versiones

El paquete original v1.0.0, [t01-t19-synthetic-evidence.json](../../tests/fixtures/methodology/intensity-horizons/t01-t19-synthetic-evidence.json), conserva el diseño histórico `SINAYXA-IH-T01-T19-SYNTHETIC-001`. Sus 19 casos, unidades, escenarios, cortes, evidencias y resultados esperados son ficticios. La versión inicial de T16 contenía un requisito de dos evaluadores humanos que fue posteriormente sustituido; por tanto, v1.0.0 es una referencia histórica inmutable, no el paquete vigente para el protocolo actual.

El paquete vigente de la batería es v1.2.0, [t01-t19-synthetic-evidence-v1.2.0.json](../../tests/fixtures/methodology/intensity-horizons/t01-t19-synthetic-evidence-v1.2.0.json), identificado como `SINAYXA-IH-T01-T19-SYNTHETIC-003`. Conserva los 19 casos, adapta T16 a un único evaluador humano con crítica auxiliar de IA y declara el linaje de v1.1.0. Las versiones anteriores v1.0.0 y v1.1.0 no se modifican.

Validador estructural compatible con Windows PowerShell 5.1: `scripts/validation/validate_intensity_horizon_fixture.ps1`. Para validar explícitamente el paquete vigente desde la raíz del repositorio:

```powershell
.\scripts\validation\validate_intensity_horizon_fixture.ps1 -FixturePath .\tests\fixtures\methodology\intensity-horizons\t01-t19-synthetic-evidence-v1.2.0.json
```

Si se omite `-FixturePath`, el validador utiliza deliberadamente el fixture original v1.0.0 para conservar compatibilidad histórica. El validador comprueba identidad y versión, 19 IDs únicos y ordenados, campos obligatorios, linaje declarado y contrato de T16; también ejecuta comprobaciones deterministas de los vectores temporales T11, T12, T13, T14, T15, T18 y T19. Imprime el SHA-256 del archivo local. Estas comprobaciones acreditan estructura y aritmética de los vectores, no la ejecución semántica de T01–T19 ni validez empírica.

Para registrar una ejecución reproducible, conservar el hash, el commit exacto y la versión del paquete congelado. No modificar un fixture después de congelarlo; cualquier cambio debe crear una nueva versión, identificador y hash. Los estados de ejecución vigentes se resumen en la sección 1 y la matriz de la sección 4: T01–T19 permanecen NOT_EXECUTED hasta completar el procedimiento correspondiente.
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
| T10 | Mitigación no verificada no reduce intensidad | NOT_EXECUTED | Intensidad base: NOT_ASSESSED; mitigación: UNVERIFIED; no reduce la evaluación base (decisión humana asistida por IA; desviación de secuencia) | Sección 20; ejecución conforme al protocolo pendiente |
| T11 | 24 h → INMEDIATO; 7 × 24 h → CORTO; 90 × 24 h → MEDIO | NOT_EXECUTED | Fronteras inclusivas aceptadas: ≤24 h INMEDIATO; >24 h–≤7×24 h CORTO; >7×24 h–≤90×24 h MEDIO; >90×24 h LARGO (decisión humana asistida por IA; desviación de secuencia) | Sección 21; ejecución conforme al protocolo pendiente |
| T12 | Un segundo después de cada frontera → horizonte siguiente | NOT_EXECUTED | 24 h + 1 s → CORTO; 7×24 h + 1 s → MEDIO; 90×24 h + 1 s → LARGO (decisión humana asistida por IA; desviación de secuencia) | Sección 22; ejecución conforme al protocolo pendiente |
| T13 | Fecha sin hora/zona: no inventar timestamp ni categoría exacta; horizonte INDETERMINADO | NOT_EXECUTED | DATE_ONLY_PRESERVED; horizonte INDETERMINADO; conservar precisión original (decisión humana asistida por IA; desviación de secuencia) | Sección 23; ejecución conforme al protocolo pendiente |
| T14 | Anuncio, aprobación, entrada en vigor e implementación son cuatro hitos/relojes separados | NOT_EXECUTED | Cuatro hitos independientes; timestamps, fuentes, zona horaria y verificación por separado; ausencias no inferidas (decisión humana asistida por IA; desviación de secuencia) | Sección 24; ejecución conforme al protocolo pendiente |
| T15 | Intervalo cruza frontera 24 h: conservar intervalo; horizonte único INDETERMINADO; compatibles INMEDIATO y CORTO | NOT_EXECUTED | Conservar límites 23 h 50 min–24 h 10 min; horizonte único INDETERMINADO; compatibles INMEDIATO y CORTO (decisión humana asistida por IA; desviación de secuencia) | Sección 25; ejecución conforme al protocolo pendiente |
| T16 | Evaluación primaria de un humano + crítica IA separada; diferencias documentadas sin promediar ni afirmar acuerdo | NOT_EXECUTED | PENDIENTE | PENDIENTE |
| T17 | Evidencia insuficiente para confirmar o descartar mecanismo material: INDETERMINADA | NOT_EXECUTED | Intensidad INDETERMINADA; no asignar I0 ni I1–I4; documentar brechas y permitir vigilancia sin confirmar catalizador (decisión humana asistida por IA; desviación de secuencia) | Sección 27; ejecución conforme al protocolo pendiente |
| T18 | Cambio horario Europe/Madrid: comparar instantes absolutos; 24 h reales → INMEDIATO | NOT_EXECUTED | Usar instantes comparables/UTC y zona Europe/Madrid; duración real exacta de 24 h → INMEDIATO; no usar diferencia ingenua de reloj local (decisión humana asistida por IA; desviación de secuencia) | Sección 28; ejecución conforme al protocolo pendiente |
| T19 | Fuentes discrepan a ambos lados de 24 h: intervalo 23 h 50 min–24 h 10 min | NOT_EXECUTED | Conservar ambas fuentes y el intervalo; categoría única INDETERMINADO; horizontes compatibles INMEDIATO y CORTO; no promediar ni elegir arbitrariamente (decisión humana asistida por IA; desviación de secuencia) | Sección 29; ejecución conforme al protocolo pendiente |

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

**Alcance del PASS:** integridad estructural del fixture v1.1.0 y comprobaciones temporales deterministas. No acredita la corrección semántica de las clasificaciones esperadas de T01–T19, ni ejecución formal de esos casos, ni acuerdo entre evaluadores. **Estado histórico de ese snapshot v1.1.0:** T01–T15 y T17–T19 NOT_EXECUTED; T16 BLOCKED por el requisito de dos evaluadores humanos que entonces contenía el protocolo. Ese bloqueo fue sustituido en v1.2.0; el estado vigente de T16 es NOT_EXECUTED bajo el protocolo de un único evaluador humano con crítica auxiliar de IA (secciones 1 y 9).

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



## 20. Registro de decisión asistida — T10

### 20.1 Identificación del caso

| Campo | Registro |
| --- | --- |
| Caso | T10 |
| Paquete | `SINAYXA-IH-T01-T19-SYNTHETIC-003` |
| Versión del paquete | `1.2.0` |
| SHA-256 del paquete | `5E02420E11FF6F9A1E456F6AFC227EB983B85F61C0AB2624F15D71484957F5BB` |
| Unidad | Cola de retiros del exchange ficticio KAPPA |
| Evidencias examinadas | T10-E1, T10-E2 y T10-E3 |
| Decisión humana comunicada | Intensidad base: NOT_ASSESSED; mitigación: UNVERIFIED; no reducir la evaluación base |
| Estado de ejecución formal | NOT_EXECUTED |

### 20.2 Razonamiento y decisión adoptada

El propietario aceptó que el anuncio de una ruta de recuperación no reduzca ni modifique la evaluación de la restricción original mientras no se demuestren su despliegue, capacidad y acceso efectivo.

- T10-E1 documenta que el exchange anuncia que está preparando una ruta de recuperación.
- T10-E2 no aporta registros de despliegue, pruebas de capacidad ni evidencia de que los usuarios puedan acceder a esa ruta.
- T10-E3 confirma que la restricción original de retiros continúa documentada.

Por tanto, la mitigación se registra como **UNVERIFIED**. Su disponibilidad, capacidad y acceso no están demostrados al corte. No se le atribuye efecto atenuante.

Este caso no proporciona una evaluación completa de la intensidad base de la restricción original. En consecuencia, la intensidad base permanece **NOT_ASSESSED** en este registro. No se inventa una clasificación ni se utiliza T10 para inferir la intensidad de la restricción a partir del anuncio de recuperación.

Una reevaluación de la mitigación requerirá evidencia verificable y fechada de despliegue, pruebas de capacidad pertinentes para la población y el flujo afectados, y acceso efectivo para los usuarios de esa unidad. La evidencia de uno de estos elementos no sustituye automáticamente a los otros. Cualquier cambio posterior deberá conservar el estado anterior, el nuevo corte y la evidencia que justifique la modificación.

### 20.3 Desviación del protocolo y límites de validez

La recomendación de IA se presentó antes de que el propietario comunicara su decisión. Por tanto, esta interacción no cumple la secuencia de evaluación primaria humana sellada antes de la crítica de IA establecida en el protocolo de evaluador único.

La aceptación se conserva como **decisión humana asistida por IA**, con exposición previa a la recomendación. No se etiqueta como evaluación ciega, independiente ni como ejecución conforme al protocolo. No se afirma acuerdo interevaluador, consenso, validez empírica ni ejecución integral de T10.

Para completar una ejecución formal conforme al protocolo, será necesaria una nueva evaluación con el paquete congelado: primero se registra y sella la evaluación humana sin conocer la salida de IA y, después, se realiza la crítica auxiliar separada. La nueva ejecución se conservará como un registro distinto, sin sobrescribir esta decisión.

### 20.4 Resultado de auditoría

La decisión **intensidad base NOT_ASSESSED / mitigación UNVERIFIED / sin reducción de la evaluación base** queda documentada como decisión humana asistida. La ruta de recuperación no se considera disponible, capaz ni accesible con las evidencias aportadas. **T10 permanece NOT_EXECUTED en la matriz formal** hasta completar una ejecución que respete el protocolo y documente sus artefactos. La coincidencia con el resultado esperado del fixture no se considera prueba de validez metodológica.



## 21. Registro de decisión asistida — T11

### 21.1 Identificación del caso

| Campo | Registro |
| --- | --- |
| Caso | T11 |
| Paquete | `SINAYXA-IH-T01-T19-SYNTHETIC-003` |
| Versión del paquete | `1.2.0` |
| SHA-256 del paquete | `5E02420E11FF6F9A1E456F6AFC227EB983B85F61C0AB2624F15D71484957F5BB` |
| Unidad | Clasificación de horizontes por duración transcurrida |
| Evidencias examinadas | T11: duraciones sintéticas exactas de 24 h, 7 × 24 h y 90 × 24 h |
| Decisión humana comunicada | Aceptación de las fronteras inclusivas y de las tres asignaciones del caso |
| Estado de ejecución formal | NOT_EXECUTED |

### 21.2 Regla temporal aceptada

El propietario aceptó que las fronteras sean inclusivas en el extremo superior de cada horizonte, con la siguiente partición continua:

| Duración transcurrida | Horizonte |
| --- | --- |
| (0 < d leq 24) horas | INMEDIATO |
| (24 < d leq 7 	imes 24) horas | CORTO |
| (7 	imes 24 < d leq 90 	imes 24) horas | MEDIO |
| (d > 90 	imes 24) horas | LARGO |

Para las duraciones exactas incluidas en T11:

- 24 horas se clasifica como INMEDIATO.
- 7 × 24 horas se clasifica como CORTO.
- 90 × 24 horas se clasifica como MEDIO.

La regla se refiere a duración transcurrida, no a diferencias entre fechas de calendario ni a etiquetas informales como «hoy» o «esta semana». Los extremos compartidos se asignan una sola vez: 24 horas pertenece a INMEDIATO; 7 × 24 horas pertenece a CORTO; 90 × 24 horas pertenece a MEDIO. Los intervalos contiguos no dejan huecos ni solapamientos.

La duración debe calcularse a partir de instantes comparables y de precisión suficiente. Cuando falte hora, zona, precisión o información necesaria para establecer la duración exacta, no se debe inventar el instante ni forzar una categoría. Los casos de información temporal incompleta se tratarán conforme a los casos específicos del fixture y a la regla de incertidumbre temporal.

### 21.3 Desviación del protocolo y límites de validez

La recomendación de IA se presentó antes de que el propietario comunicara su decisión. Por tanto, esta interacción no cumple la secuencia de evaluación primaria humana sellada antes de la crítica de IA establecida en el protocolo de evaluador único.

La aceptación se conserva como **decisión humana asistida por IA**, con exposición previa a la recomendación. No se etiqueta como evaluación ciega, independiente ni como ejecución conforme al protocolo. No se afirma acuerdo interevaluador, consenso, validez empírica ni ejecución integral de T11.

Para completar una ejecución formal conforme al protocolo, será necesaria una nueva evaluación con el paquete congelado: primero se registra y sella la evaluación humana sin conocer la salida de IA y, después, se realiza la crítica auxiliar separada. La nueva ejecución se conservará como un registro distinto, sin sobrescribir esta decisión.

### 21.4 Resultado de auditoría

La regla de fronteras inclusivas y las asignaciones de T11 quedan documentadas como decisión humana asistida. Este registro expresa una decisión metodológica sobre el tratamiento de duraciones exactas; no demuestra por sí mismo que una implementación de software la aplique correctamente. **T11 permanece NOT_EXECUTED en la matriz formal** hasta completar una ejecución que respete el protocolo y documente sus artefactos. La coincidencia con el resultado esperado del fixture no se considera prueba de validez metodológica.



## 22. Registro de decisión asistida — T12

### 22.1 Identificación del caso

| Campo | Registro |
| --- | --- |
| Caso | T12 |
| Paquete | `SINAYXA-IH-T01-T19-SYNTHETIC-003` |
| Versión del paquete | `1.2.0` |
| SHA-256 del paquete | `5E02420E11FF6F9A1E456F6AFC227EB983B85F61C0AB2624F15D71484957F5BB` |
| Unidad | Clasificación de horizontes por duración transcurrida |
| Evidencias examinadas | T12: duraciones sintéticas de un segundo después de 24 h, 7 × 24 h y 90 × 24 h |
| Decisión humana comunicada | Aceptación de las tres asignaciones al horizonte siguiente |
| Estado de ejecución formal | NOT_EXECUTED |

### 22.2 Regla temporal y decisión adoptada

El propietario aceptó que una duración situada exactamente un segundo después de cada frontera pase al siguiente horizonte:

| Duración transcurrida | Horizonte |
| --- | --- |
| 24 horas + 1 segundo | CORTO |
| 7 × 24 horas + 1 segundo | MEDIO |
| 90 × 24 horas + 1 segundo | LARGO |

Estas asignaciones son coherentes con la partición inclusiva aceptada en T11:

- (0 < d leq 24) horas: INMEDIATO.
- (24 < d leq 7 	imes 24) horas: CORTO.
- (7 	imes 24 < d leq 90 	imes 24) horas: MEDIO.
- (d > 90 	imes 24) horas: LARGO.

El segundo adicional debe formar parte de la duración transcurrida calculada entre instantes comparables. No se redondeará la duración antes de clasificarla, pues ese redondeo podría volver a colocar el instante dentro del horizonte anterior. La precisión disponible debe ser suficiente para distinguir el segundo adicional; si no lo es, se conservará la incertidumbre y no se forzará la categoría.

### 22.3 Desviación del protocolo y límites de validez

La recomendación de IA se presentó antes de que el propietario comunicara su decisión. Por tanto, esta interacción no cumple la secuencia de evaluación primaria humana sellada antes de la crítica de IA establecida en el protocolo de evaluador único.

La aceptación se conserva como **decisión humana asistida por IA**, con exposición previa a la recomendación. No se etiqueta como evaluación ciega, independiente ni como ejecución conforme al protocolo. No se afirma acuerdo interevaluador, consenso, validez empírica ni ejecución integral de T12.

Para completar una ejecución formal conforme al protocolo, será necesaria una nueva evaluación con el paquete congelado: primero se registra y sella la evaluación humana sin conocer la salida de IA y, después, se realiza la crítica auxiliar separada. La nueva ejecución se conservará como un registro distinto, sin sobrescribir esta decisión.

### 22.4 Resultado de auditoría

Las tres asignaciones de T12 quedan documentadas como decisión humana asistida y son consistentes con la regla temporal aprobada en T11. Este registro no demuestra por sí mismo que una implementación de software calcule duraciones sin redondeos prematuros ni aplique correctamente los límites. **T12 permanece NOT_EXECUTED en la matriz formal** hasta completar una ejecución que respete el protocolo y documente sus artefactos. La coincidencia con el resultado esperado del fixture no se considera prueba de validez metodológica.



## 23. Registro de decisión asistida — T13

### 23.1 Identificación del caso

| Campo | Registro |
| --- | --- |
| Caso | T13 |
| Paquete | `SINAYXA-IH-T01-T19-SYNTHETIC-003` |
| Versión del paquete | `1.2.0` |
| SHA-256 del paquete | `5E02420E11FF6F9A1E456F6AFC227EB983B85F61C0AB2624F15D71484957F5BB` |
| Unidad | Determinación del horizonte temporal de un evento con fecha incompleta |
| Evidencia examinada | T13: fecha de calendario sin hora ni zona horaria |
| Decisión humana comunicada | DATE_ONLY_PRESERVED; horizonte INDETERMINADO |
| Estado de ejecución formal | NOT_EXECUTED |

### 23.2 Decisión y tratamiento de la precisión temporal

El propietario aceptó conservar la fecha recibida sin completar los componentes temporales ausentes y no asignar un horizonte exacto.

- Estado temporal: **DATE_ONLY_PRESERVED**.
- Horizonte: **INDETERMINADO**.
- Hora: no proporcionada; no se infiere.
- Zona horaria: no proporcionada; no se infiere.
- Timestamp: no se fabrica ni se normaliza a una hora arbitraria.

Una fecha de calendario identifica un día, no un instante único. Sin hora y referencia de zona horaria suficientes no se puede determinar rigurosamente el tiempo transcurrido hasta o desde otro instante, ni decidir de forma fiable si una frontera de horizonte ha sido cruzada.

La fecha original debe preservarse con su precisión de origen. Si posteriormente se obtiene una hora, zona horaria o intervalo verificable, la evaluación podrá revisarse con un nuevo corte y trazabilidad de la evidencia añadida. La nueva información no debe sobrescribir el dato original ni ocultar que la evaluación inicial se realizó con precisión limitada.

### 23.3 Desviación del protocolo y límites de validez

La recomendación de IA se presentó antes de que el propietario comunicara su decisión. Por tanto, esta interacción no cumple la secuencia de evaluación primaria humana sellada antes de la crítica de IA establecida en el protocolo de evaluador único.

La aceptación se conserva como **decisión humana asistida por IA**, con exposición previa a la recomendación. No se etiqueta como evaluación ciega, independiente ni como ejecución conforme al protocolo. No se afirma acuerdo interevaluador, consenso, validez empírica ni ejecución integral de T13.

Para completar una ejecución formal conforme al protocolo, será necesaria una nueva evaluación con el paquete congelado: primero se registra y sella la evaluación humana sin conocer la salida de IA y, después, se realiza la crítica auxiliar separada. La nueva ejecución se conservará como un registro distinto, sin sobrescribir esta decisión.

### 23.4 Resultado de auditoría

La decisión **DATE_ONLY_PRESERVED / horizonte INDETERMINADO** queda documentada como decisión humana asistida. No se inventaron hora, zona horaria ni timestamp, y no se asignó una categoría temporal exacta que la evidencia no permite sostener. **T13 permanece NOT_EXECUTED en la matriz formal** hasta completar una ejecución que respete el protocolo y documente sus artefactos. La coincidencia con el resultado esperado del fixture no se considera prueba de validez metodológica.



## 24. Registro de decisión asistida — T14

### 24.1 Identificación del caso

| Campo | Registro |
| --- | --- |
| Caso | T14 |
| Paquete | `SINAYXA-IH-T01-T19-SYNTHETIC-003` |
| Versión del paquete | `1.2.0` |
| SHA-256 del paquete | `5E02420E11FF6F9A1E456F6AFC227EB983B85F61C0AB2624F15D71484957F5BB` |
| Unidad | Separación de hitos temporales de un acontecimiento |
| Evidencia examinada | T14: anuncio, aprobación, entrada en vigor e implementación |
| Decisión humana comunicada | Tratar los cuatro hitos como relojes independientes y registrar cada uno por separado |
| Estado de ejecución formal | NOT_EXECUTED |

### 24.2 Decisión y registro de los cuatro relojes

El propietario aceptó que los siguientes hitos no son intercambiables y deben conservarse como eventos temporales separados:

1. **Anuncio:** momento en que la información se comunica públicamente.
2. **Aprobación:** momento en que la autoridad o entidad competente adopta formalmente la decisión.
3. **Entrada en vigor:** momento desde el cual la medida o decisión produce efectos formales.
4. **Implementación:** momento en que la medida se ejecuta efectivamente en los sistemas, procesos o actividades afectados.

Para cada hito se debe registrar, cuando esté disponible:

- Timestamp original y precisión declarada.
- Zona horaria o referencia temporal explícita.
- Fuente documental y localizador de evidencia.
- Estado de verificación.
- Unidad, alcance y población a la que corresponde.
- Relación con los otros hitos, sin presumir que ocurren simultáneamente.

No se debe asumir que el anuncio equivale a aprobación, que la aprobación equivale a entrada en vigor ni que la entrada en vigor demuestra implementación. Tampoco se debe inferir que la implementación comenzó en la fecha anunciada.

Cuando un hito no esté documentado, debe conservarse como desconocido o no verificado según corresponda. No se debe completar con una fecha inferida, copiar el timestamp de otro hito ni convertir una fecha de calendario sin hora y zona en un instante artificial. Si las fuentes discrepan, se preservará la discrepancia y se documentará su alcance.

La cronología resultante debe permitir que los análisis posteriores distingan entre anticipación informativa, decisión formal, efecto jurídico u operativo y ejecución efectiva. La mera proximidad temporal entre cualquiera de estos hitos y un movimiento de mercado no demuestra causalidad.

### 24.3 Desviación del protocolo y límites de validez

La recomendación de IA se presentó antes de que el propietario comunicara su decisión. Por tanto, esta interacción no cumple la secuencia de evaluación primaria humana sellada antes de la crítica de IA establecida en el protocolo de evaluador único.

La aceptación se conserva como **decisión humana asistida por IA**, con exposición previa a la recomendación. No se etiqueta como evaluación ciega, independiente ni como ejecución conforme al protocolo. No se afirma acuerdo interevaluador, consenso, validez empírica ni ejecución integral de T14.

Para completar una ejecución formal conforme al protocolo, será necesaria una nueva evaluación con el paquete congelado: primero se registra y sella la evaluación humana sin conocer la salida de IA y, después, se realiza la crítica auxiliar separada. La nueva ejecución se conservará como un registro distinto, sin sobrescribir esta decisión.

### 24.4 Resultado de auditoría

La separación de anuncio, aprobación, entrada en vigor e implementación queda documentada como decisión humana asistida. Los cuatro hitos deben conservar fuentes y metadatos temporales propios; la ausencia o discrepancia de uno no se resuelve copiando otro. **T14 permanece NOT_EXECUTED en la matriz formal** hasta completar una ejecución que respete el protocolo y documente sus artefactos. La coincidencia con el resultado esperado del fixture no se considera prueba de validez metodológica.



## 25. Registro de decisión asistida — T15

### 25.1 Identificación del caso

| Campo | Registro |
| --- | --- |
| Caso | T15 |
| Paquete | `SINAYXA-IH-T01-T19-SYNTHETIC-003` |
| Versión del paquete | `1.2.0` |
| SHA-256 del paquete | `5E02420E11FF6F9A1E456F6AFC227EB983B85F61C0AB2624F15D71484957F5BB` |
| Unidad | Clasificación de horizonte cuando el intervalo de duración cruza una frontera |
| Evidencia examinada | T15: intervalo de duración que cruza la frontera de 24 horas |
| Decisión humana comunicada | Conservar el intervalo; horizonte único INDETERMINADO; horizontes compatibles INMEDIATO y CORTO |
| Estado de ejecución formal | NOT_EXECUTED |

### 25.2 Decisión y tratamiento del intervalo

El propietario aceptó conservar el intervalo temporal completo cuando sus límites se sitúan a ambos lados de una frontera de horizonte. No se debe sustituir el intervalo por un punto estimado ni elegir una categoría única que los datos no permiten establecer.

Para el intervalo sintético de T15:

- Límite inferior: 23 horas y 50 minutos.
- Límite superior: 24 horas y 10 minutos.
- Horizonte único: **INDETERMINADO**.
- Horizontes compatibles con el intervalo: **INMEDIATO** y **CORTO**.

El límite inferior cae dentro de INMEDIATO y el superior dentro de CORTO, conforme a las fronteras inclusivas definidas en T11. Por ello, la evidencia no permite asignar un único horizonte con precisión suficiente. Los horizontes compatibles describen las categorías que el intervalo permite; no son dos clasificaciones simultáneas de un mismo valor conocido.

Se conservarán los límites originales, la unidad, la precisión y la procedencia del intervalo. No se utilizará el punto medio, el redondeo ni una estimación arbitraria para forzar una clasificación. Si evidencia posterior reduce el intervalo a un rango contenido íntegramente en un horizonte, podrá realizarse una nueva evaluación con un nuevo corte, preservando el registro anterior y explicando el cambio.

### 25.3 Desviación del protocolo y límites de validez

La recomendación de IA se presentó antes de que el propietario comunicara su decisión. Por tanto, esta interacción no cumple la secuencia de evaluación primaria humana sellada antes de la crítica de IA establecida en el protocolo de evaluador único.

La aceptación se conserva como **decisión humana asistida por IA**, con exposición previa a la recomendación. No se etiqueta como evaluación ciega, independiente ni como ejecución conforme al protocolo. No se afirma acuerdo interevaluador, consenso, validez empírica ni ejecución integral de T15.

Para completar una ejecución formal conforme al protocolo, será necesaria una nueva evaluación con el paquete congelado: primero se registra y sella la evaluación humana sin conocer la salida de IA y, después, se realiza la crítica auxiliar separada. La nueva ejecución se conservará como un registro distinto, sin sobrescribir esta decisión.

### 25.4 Resultado de auditoría

La decisión **intervalo conservado / horizonte único INDETERMINADO / horizontes compatibles INMEDIATO y CORTO** queda documentada como decisión humana asistida. No se ha forzado una categoría única a partir de un intervalo que cruza la frontera de 24 horas. **T15 permanece NOT_EXECUTED en la matriz formal** hasta completar una ejecución que respete el protocolo y documente sus artefactos. La coincidencia con el resultado esperado del fixture no se considera prueba de validez metodológica.



## 26. Registro de decisión asistida — T16

### 26.1 Identificación del caso

| Campo | Registro |
| --- | --- |
| Caso | T16 |
| Paquete | `SINAYXA-IH-T01-T19-SYNTHETIC-003` |
| Versión del paquete | `1.2.0` |
| SHA-256 del paquete | `5E02420E11FF6F9A1E456F6AFC227EB983B85F61C0AB2624F15D71484957F5BB` |
| Unidad | Gobernanza de la evaluación humana asistida por IA |
| Evidencia examinada | T16: secuencia de evaluación primaria humana sellada y crítica IA separada |
| Decisión humana comunicada | Aceptación del protocolo y de sus límites de interpretación |
| Estado de ejecución formal | NOT_EXECUTED |

### 26.2 Protocolo aceptado

El propietario aceptó el siguiente orden para futuras ejecuciones formales:

1. Congelar el paquete, su versión y hash, la unidad de evaluación, el escenario, el corte temporal y las fuentes disponibles.
2. El evaluador humano realiza la evaluación primaria sin conocer la salida de IA y registra/sella su resultado antes de solicitar o consultar esa salida.
3. La IA produce una crítica estructurada y separada, con sus evidencias, objeciones, incertidumbres y límites.
4. Se comparan ambos artefactos, preservando coincidencias y discrepancias.
5. El evaluador humano resuelve las discrepancias y registra la decisión final, sus razones y cualquier cambio respecto de la evaluación primaria.

La IA es una herramienta auxiliar de análisis y crítica; no constituye un segundo evaluador humano ni un voto adicional. No se deben promediar sus resultados con los humanos ni contar la coincidencia humano-IA como acuerdo interevaluador, consenso o evidencia de independencia estadística. Cualquier repetición realizada por la misma persona solo podrá describirse como consistencia intraevaluador, si el diseño y los registros permiten sostener esa descripción.

### 26.3 Desviación histórica y límites de validez

En los casos T01–T15 registrados en este ciclo, las recomendaciones de IA se presentaron antes de que el propietario comunicara sus decisiones. Esas decisiones se conservan como decisiones humanas asistidas con exposición previa a la recomendación; no son evaluaciones primarias aisladas, ciegas ni ejecuciones formales conformes a la secuencia establecida.

La aceptación de este protocolo en T16 no convierte retroactivamente los casos anteriores en ejecuciones conformes. Sus estados formales permanecen sin ejecución. Tampoco se afirma que el protocolo haya sido ejecutado en T16: este registro documenta la aceptación de la regla de gobernanza, no una prueba empírica de su eficacia.

Las futuras ejecuciones deberán conservar, como mínimo, los artefactos sellados de la evaluación humana primaria, la crítica IA separada, los metadatos de modelo y prompt, el contexto disponible para cada etapa, la comparación y la resolución humana. Si no puede garantizarse el aislamiento de la evaluación primaria respecto de la salida IA, la exposición deberá documentarse y la ejecución no podrá describirse como ciega o independiente.

### 26.4 Resultado de auditoría

Queda aceptado el protocolo de evaluación primaria humana sellada antes de la crítica IA separada, así como la prohibición de presentar la IA como segundo evaluador humano o de atribuir acuerdo interevaluador, consenso o independencia estadística. La desviación de secuencia en T01–T15 queda explícitamente preservada y no se corrige retroactivamente. **T16 permanece NOT_EXECUTED en la matriz formal**: la aceptación de un procedimiento no equivale a su ejecución ni demuestra su eficacia. La coincidencia con el resultado esperado del fixture no se considera prueba de validez metodológica.



## 27. Registro de decisión asistida — T17

### 27.1 Identificación del caso

| Campo | Registro |
| --- | --- |
| Caso | T17 |
| Paquete | `SINAYXA-IH-T01-T19-SYNTHETIC-003` |
| Versión del paquete | `1.2.0` |
| SHA-256 del paquete | `5E02420E11FF6F9A1E456F6AFC227EB983B85F61C0AB2624F15D71484957F5BB` |
| Unidad | Evaluación de un mecanismo material con evidencia incompleta |
| Evidencia examinada | T17: información insuficiente para confirmar o descartar el mecanismo |
| Decisión humana comunicada | Intensidad INDETERMINADA; no asignar I0 ni I1–I4 |
| Estado de ejecución formal | NOT_EXECUTED |

### 27.2 Decisión y razonamiento

El propietario aceptó clasificar la intensidad como **INDETERMINADA** cuando la evidencia disponible no permite confirmar ni descartar un mecanismo material.

No se asigna I0. Esa clasificación exige evidencia suficiente para descartar un mecanismo material dentro de la unidad, escenario y corte delimitados. La mera ausencia de registros, la falta de confirmación o una búsqueda incompleta no constituyen evidencia de ausencia.

Tampoco se asigna I1, I2, I3 o I4. Esas categorías requieren evidencia suficiente para establecer un mecanismo y evaluar su exposición, alcance y consecuencias conforme a las definiciones metodológicas. La incertidumbre no autoriza a elegir una intensidad por intuición, plausibilidad narrativa o presión de clasificación.

La evaluación debe identificar explícitamente:

- Qué mecanismo se plantea y qué evidencia verificable lo respaldaría.
- Qué evidencias existen y cuáles son sus límites.
- Qué datos, registros, denominadores, dependencias o verificaciones faltan.
- Qué fuentes podrían resolver las brechas y qué condiciones de acceso o fiabilidad deben comprobarse.
- Qué unidad, escenario y corte temporal están realmente cubiertos.

La incertidumbre puede justificar vigilancia, preservación de fuentes y recopilación adicional. No permite presentar un rumor, una hipótesis o una señal no verificada como catalizador confirmado. Una evaluación posterior deberá utilizar un nuevo corte, registrar la evidencia añadida y explicar cualquier cambio sin borrar esta conclusión inicial.

### 27.3 Desviación del protocolo y límites de validez

La recomendación de IA se presentó antes de que el propietario comunicara su decisión. Por tanto, esta interacción no cumple la secuencia de evaluación primaria humana sellada antes de la crítica de IA establecida en el protocolo de evaluador único.

La aceptación se conserva como **decisión humana asistida por IA**, con exposición previa a la recomendación. No se etiqueta como evaluación ciega, independiente ni como ejecución conforme al protocolo. No se afirma acuerdo interevaluador, consenso, validez empírica ni ejecución integral de T17.

Para completar una ejecución formal conforme al protocolo, será necesaria una nueva evaluación con el paquete congelado: primero se registra y sella la evaluación humana sin conocer la salida de IA y, después, se realiza la crítica auxiliar separada. La nueva ejecución se conservará como un registro distinto, sin sobrescribir esta decisión.

### 27.4 Resultado de auditoría

La decisión **INDETERMINADA** queda documentada porque la evidencia no permite confirmar ni descartar el mecanismo material. No se equipara ausencia de evidencia con evidencia de ausencia, ni se fuerza I0 o I1–I4. La vigilancia y la recopilación adicional pueden continuar sin elevar una hipótesis a catalizador confirmado. **T17 permanece NOT_EXECUTED en la matriz formal** hasta completar una ejecución que respete el protocolo y documente sus artefactos. La coincidencia con el resultado esperado del fixture no se considera prueba de validez metodológica.



## 28. Registro de decisión asistida — T18

### 28.1 Identificación del caso

| Campo | Registro |
| --- | --- |
| Caso | T18 |
| Paquete | `SINAYXA-IH-T01-T19-SYNTHETIC-003` |
| Versión del paquete | `1.2.0` |
| SHA-256 del paquete | `5E02420E11FF6F9A1E456F6AFC227EB983B85F61C0AB2624F15D71484957F5BB` |
| Unidad | Cálculo de duración durante un cambio horario en Europe/Madrid |
| Evidencia examinada | T18: timestamps en zona Europe/Madrid a ambos lados de un cambio horario |
| Decisión humana comunicada | Comparar instantes absolutos; una duración real de 24 horas se clasifica como INMEDIATO |
| Estado de ejecución formal | NOT_EXECUTED |

### 28.2 Decisión y regla de cálculo

El propietario aceptó que la duración se calcule entre instantes absolutos comparables, preservando la zona horaria de origen `Europe/Madrid` y evitando la resta ingenua de las representaciones locales del reloj.

- La zona IANA de origen debe conservarse como metadato: `Europe/Madrid`.
- Cada timestamp debe interpretarse con su offset y reglas de zona válidos para la fecha correspondiente.
- La duración se calcula entre los instantes equivalentes, por ejemplo después de convertirlos a UTC.
- Una duración real exactamente igual a 24 horas pertenece a **INMEDIATO**, conforme a la frontera inclusiva aceptada en T11.
- El salto del reloj local al entrar o salir del horario de verano no constituye por sí mismo tiempo transcurrido.

Durante una transición de horario, la diferencia aparente entre las horas locales puede ser distinta de la duración absoluta. Por tanto, no se deben restar horas de pared ni asumir que la diferencia entre las etiquetas locales representa el tiempo real. Si un timestamp local es ambiguo o inexistente y no incluye offset u otra información suficiente para resolverlo, se debe preservar esa ambigüedad y dejar la duración sin determinar; no se elegirá arbitrariamente uno de los instantes posibles.

La clasificación depende de la duración absoluta calculada con precisión suficiente. No se redondeará antes de aplicar las fronteras temporales. Este registro acepta la regla metodológica; no demuestra por sí mismo que el código de SINAYXA la implemente correctamente.

### 28.3 Desviación del protocolo y límites de validez

La recomendación de IA se presentó antes de que el propietario comunicara su decisión. Por tanto, esta interacción no cumple la secuencia de evaluación primaria humana sellada antes de la crítica de IA establecida en el protocolo de evaluador único.

La aceptación se conserva como **decisión humana asistida por IA**, con exposición previa a la recomendación. No se etiqueta como evaluación ciega, independiente ni como ejecución conforme al protocolo. No se afirma acuerdo interevaluador, consenso, validez empírica ni ejecución integral de T18.

Para completar una ejecución formal conforme al protocolo, será necesaria una nueva evaluación con el paquete congelado: primero se registra y sella la evaluación humana sin conocer la salida de IA y, después, se realiza la crítica auxiliar separada. La nueva ejecución se conservará como un registro distinto, sin sobrescribir esta decisión.

### 28.4 Resultado de auditoría

La decisión **instantes absolutos / zona Europe/Madrid preservada / 24 horas reales = INMEDIATO** queda documentada como decisión humana asistida. La aritmética ingenua de horas locales no se acepta como sustituto del cálculo de duración real; timestamps ambiguos o inexistentes sin offset suficiente no se resolverán por conjetura. **T18 permanece NOT_EXECUTED en la matriz formal** hasta completar una ejecución que respete el protocolo y documente sus artefactos. La coincidencia con el resultado esperado del fixture no se considera prueba de validez metodológica.



## 29. Registro de decisión asistida — T19

### 29.1 Identificación del caso

| Campo | Registro |
| --- | --- |
| Caso | T19 |
| Paquete | `SINAYXA-IH-T01-T19-SYNTHETIC-003` |
| Versión del paquete | `1.2.0` |
| SHA-256 del paquete | `5E02420E11FF6F9A1E456F6AFC227EB983B85F61C0AB2624F15D71484957F5BB` |
| Unidad | Determinación del horizonte ante timestamps discrepantes de dos fuentes |
| Evidencia examinada | T19: una fuente sitúa el evento a 23 h 50 min y otra a 24 h 10 min |
| Decisión humana comunicada | Conservar ambas fuentes y el intervalo; categoría única INDETERMINADO; horizontes compatibles INMEDIATO y CORTO |
| Estado de ejecución formal | NOT_EXECUTED |

### 29.2 Decisión y razonamiento

El propietario aceptó conservar ambas observaciones y representar la incertidumbre temporal mediante el intervalo **23 h 50 min–24 h 10 min**.

La frontera de 24 horas separa INMEDIATO de CORTO. Como el intervalo contiene duraciones a ambos lados de esa frontera, no existe base para asignar una categoría única con la evidencia disponible.

Por tanto:

- Horizonte único: **INDETERMINADO**.
- Horizontes compatibles: **INMEDIATO** y **CORTO**.
- Se conservan las dos fuentes, sus timestamps originales, sus zonas u offsets cuando estén disponibles y sus respectivos metadatos de procedencia.
- No se selecciona una fuente por conveniencia, autoridad no establecida o coincidencia con el resultado esperado.
- No se calcula un promedio para fabricar un timestamp representativo ni se redondea el intervalo para forzar una categoría.
- La discrepancia y sus consecuencias para la clasificación permanecen visibles para evaluaciones posteriores.

La incertidumbre solo podrá reducirse mediante evidencia adicional que permita justificar qué timestamp representa mejor el acontecimiento o acotar el intervalo sin cruzar la frontera. Si una fuente carece de zona horaria, precisión o metadatos necesarios, esa limitación debe conservarse; no se completará por inferencia.

### 29.3 Desviación del protocolo y límites de validez

La recomendación de IA se presentó antes de que el propietario comunicara su decisión. Por tanto, esta interacción no cumple la secuencia de evaluación primaria humana sellada antes de la crítica de IA establecida en el protocolo de evaluador único.

La aceptación se conserva como **decisión humana asistida por IA**, con exposición previa a la recomendación. No se etiqueta como evaluación ciega, independiente ni como ejecución conforme al protocolo. No se afirma acuerdo interevaluador, consenso, validez empírica ni ejecución integral de T19.

Para completar una ejecución formal conforme al protocolo, será necesaria una nueva evaluación con el paquete congelado: primero se registra y sella la evaluación humana sin conocer la salida de IA y, después, se realiza la crítica auxiliar separada. La nueva ejecución se conservará como un registro distinto, sin sobrescribir esta decisión.

### 29.4 Resultado de auditoría

La clasificación única **INDETERMINADO**, con horizontes compatibles **INMEDIATO** y **CORTO**, queda documentada porque el intervalo de evidencia cruza la frontera de 24 horas. Las observaciones originales permanecen preservadas; no se promedian ni se resuelve arbitrariamente la discrepancia. **T19 permanece NOT_EXECUTED en la matriz formal** hasta completar una ejecución que respete el protocolo y documente sus artefactos. La coincidencia con el resultado esperado del fixture no se considera prueba de validez metodológica.


## 30. Registro de revisión documental — aclaraciones I0 y tiempo de hitos pasados

**Tipo de actividad:** revisión metodológica documental; no es ejecución de T01–T19.

Se actualizó la propuesta asociada al Issue #14 para resolver dos ambigüedades detectadas en la revisión técnica:

1. **I0 y alcance de evidencia:** I0 exige una revisión de alcance delimitado que identifique unidad, población/segmento, escenario, fecha de corte, fuentes y áreas examinadas y limitaciones conocidas. La falta de búsqueda suficiente, fuentes esenciales no examinadas o lagunas que impidan descartar un mecanismo material conducen a INDETERMINADA. I0 no se extrapola a canales o poblaciones fuera del alcance revisado.
2. **Hitos pasados:** el tiempo entre un hito ocurrido y la fecha de corte se registra como tiempo transcurrido/antigüedad, no como horizonte futuro ni como latencia de transmisión. El horizonte de transmisión restante requiere un objetivo futuro y un mecanismo/latencia justificables; de lo contrario, es INDETERMINADO.

La batería existente mantiene sus identidades y estados. T01 ya delimita explícitamente su unidad a funciones técnicas/operativas y documenta el inventario revisado; su resultado esperado I0 se limita a ese alcance. T17 conserva el resultado INDETERMINADA cuando faltan inventario de dependencias y confirmación operativa. Estos casos son compatibles con la aclaración, pero su presencia no equivale a una nueva ejecución.

**Estado de ejecución tras esta revisión:** T01–T15 y T17–T19 continúan NOT_EXECUTED; T16 continúa NOT_EXECUTED conforme al protocolo de evaluador único y crítica auxiliar de IA. No se ha ejecutado PowerShell, no se ha recalculado el SHA-256 del fixture y no se declara PASS de la batería metodológica. La modificación documental requiere revisión local de formato y verificación de repositorio antes de integrar la PR.


## 31. Revisión integral de consistencia documental de la PR #40

**Tipo:** revisión estática de coherencia y trazabilidad sobre los archivos versionados de esta rama. No es ejecución de PowerShell, Markdown lint ni ejecución metodológica.

### Correcciones aplicadas

- Se alineó la definición principal I0, la regla general, la frontera I0/I1 y el marcador detallado: todos exigen revisión de alcance delimitado y prohíben extrapolar la conclusión fuera de la unidad/segmento/canales examinados. Las lagunas, fuentes esenciales no revisadas o búsquedas incompletas conducen a INDETERMINADA.
- Se precisó el reloj del acontecimiento: los hitos futuros se expresan como tiempo restante; los hitos pasados conservan antigüedad/tiempo transcurrido separado, que no se etiqueta como horizonte futuro ni como latencia de transmisión.
- Se marcó como histórico el estado T16 BLOCKED del paquete v1.1.0 y se distinguió del estado vigente NOT_EXECUTED bajo el protocolo v1.2.0.
- Se identificó v1.2.0 como paquete vigente y se documentó el comando PowerShell explícito para validarlo. Omitir FixturePath sigue seleccionando intencionadamente el fixture histórico v1.0.0.
- Se actualizó la revisión semántica histórica para registrar el seguimiento posterior de T01/T03/T04/T08/T10 y el cambio de gobernanza de T16, sin alterar los resultados ni estados originales de v1.0.0.

### Comprobaciones estáticas realizadas

- Los tres fixtures JSON v1.0.0, v1.1.0 y v1.2.0 se pudieron analizar; cada uno contiene 19 IDs únicos y secuenciales T01–T19.
- Se comprobaron los campos y resultados esperados de T01, T16 y T17 en v1.2.0. T01 limita I0 a las funciones técnicas/operativas declaradas; T17 conserva INDETERMINADA ante información esencial ausente; T16 define evaluación humana primaria y crítica auxiliar de IA sin atribuir acuerdo interevaluador.
- Se revisó estáticamente el validador PowerShell: conserva compatibilidad histórica, verifica el linaje y contrato de T16 en v1.2.0 y comprueba los vectores temporales T11/T12/T13/T14/T15/T18/T19. No se ejecutó el script.
- Se resolvieron los cuatro enlaces Markdown internos detectados en los documentos revisados; todos apuntan a archivos existentes en esta rama.
- La rama sigue basada en el HEAD actual de main observado durante la revisión; GitHub reporta la PR mergeable/clean, pero esto no sustituye la revisión ni las verificaciones locales.

### Verificaciones pendientes y límites

- Markdown lint aislado para los cuatro documentos: pendiente. El registro anterior informa 312 incidencias en una ejecución global que alcanzó dos archivos; no se dispone aquí de la salida detallada por regla y no se declara PASS del lint.
- Ejecución del validador en Windows PowerShell 5.1 sobre el HEAD actual: pendiente. Los PASS locales anteriores pertenecen a commits anteriores y no se extrapolan a estos cambios.
- Batería metodológica T01–T19: todos los casos siguen NOT_EXECUTED; T16 también NOT_EXECUTED bajo el protocolo v1.2.0.
- No hay ejecuciones de GitHub Actions/check-runs registradas para el HEAD revisado. No se encontró un directorio de workflows en el repositorio.
- Esta revisión no aprueba los niveles ni las ventanas, no autoriza implementación y no recomienda fusionar todavía la PR #40.
