# Registro de cambios del fixture T01–T19 v1.2.0

## 1. Identificación

| Campo | Valor |
| --- | --- |
| Paquete | `SINAYXA-IH-T01-T19-SYNTHETIC-003` |
| Versión | `1.2.0` |
| Archivo | `tests/fixtures/methodology/intensity-horizons/t01-t19-synthetic-evidence-v1.2.0.json` |
| Paquete anterior | `SINAYXA-IH-T01-T19-SYNTHETIC-002` / `1.1.0` |
| SHA-256 del paquete anterior | `E685D6BB4459F5A580ABFAC11979D4FCABF385EE7856EC28C16541C2AD05948C` |
| Propósito | Adaptar T16 a un proyecto con un único evaluador humano y asistencia auxiliar de IA |

## 2. Problema corregido

El fixture 1.1.0 mantenía T16 BLOCKED hasta contar con dos evaluadores humanos independientes. Esa condición es incompatible con la gobernanza declarada de SINAYXA: existe un único participante humano y no se incorporará una segunda persona artificialmente.

No corresponde contar una IA como persona, evaluador humano independiente ni sustituto estadístico de un segundo evaluador.

## 3. Cambio introducido en T16

La versión 1.2.0 sustituye el requisito imposible por un flujo de evaluación de un único humano:

1. El propietario congela el paquete, la unidad, el escenario y el corte.
2. El propietario realiza y sella la evaluación primaria antes de consultar a la IA.
3. La IA realiza una crítica adversarial del paquete congelado sin recibir la conclusión humana, preferiblemente en contexto aislado.
4. Se registran prompt, modelo/versión cuando estén disponibles, fecha, hash del paquete, salida y limitaciones.
5. El propietario clasifica las diferencias y decide, con justificación, qué hallazgos acepta.
6. Las reglas modificadas se versionan y los casos afectados se repiten.

La IA es auxiliar: no tiene voto, no es un segundo evaluador humano y no acredita acuerdo interevaluador, consenso ni fiabilidad interevaluador.

## 4. Inmutabilidad y linaje

- El fixture v1.0.0 no se modifica.
- El fixture v1.1.0 no se modifica.
- El fixture v1.2.0 es un artefacto nuevo que declara el SHA-256 de v1.1.0 como antecedente.
- Cualquier cambio futuro crea otra versión e identificador.

## 5. Validación automatizada

El validador se amplía para reconocer el paquete v1.2.0, verificar su linaje y comprobar que T16 contiene las salvaguardas de evaluación humana primaria, revisión IA auxiliar, procedencia y prohibición de declarar acuerdo interevaluador.

Estas comprobaciones son estructurales. No ejecutan el proceso humano ni la revisión de IA, no validan las clasificaciones semánticas y no acreditan validez empírica.

## 6. Estado de ejecución

T16 queda **NOT_EXECUTED**, no BLOCKED: el proceso ya no depende de una segunda persona, pero la evaluación y la crítica de IA aún deben realizarse realmente. Los estados de T01–T15 y T17–T19 no cambian. No se declara acuerdo interevaluador humano.
