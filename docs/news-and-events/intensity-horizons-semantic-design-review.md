# Revisión de diseño semántico del fixture T01–T10 y T17

## 1. Propósito y límites

Este documento registra una **revisión de escritorio asistida por IA** del diseño de los casos semánticos T01–T10 y T17 del paquete sintético `SINAYXA-IH-T01-T19-SYNTHETIC-001`.

No es una ejecución de la batería metodológica, no es una evaluación humana independiente, no acredita validez empírica ni acuerdo interevaluador y no modifica el estado de ningún caso. Su finalidad es comprobar si las entradas congeladas contienen evidencia suficiente para justificar los resultados esperados conforme a las secciones 3.1–3.5 y 9.1 de la propuesta.

## 2. Identificación y reproducibilidad

| Campo | Valor |
| --- | --- |
| Rama revisada | `docs/issue-14-intensity-horizons` |
| Commit de referencia | `6debea98b5bd4e4a3370ed5bcd3d416023276648` |
| Propuesta | `docs/news-and-events/intensity-and-time-horizons-proposal.md` |
| Blob SHA de la propuesta | `f76cf86d80f378e69c6d188b2a22cbe25158ceb2` |
| Fixture | `tests/fixtures/methodology/intensity-horizons/t01-t19-synthetic-evidence.json` |
| Blob SHA del fixture | `a725f4625b52f989b4417b416fb3703610f3ffa2` |
| Paquete | `SINAYXA-IH-T01-T19-SYNTHETIC-001`, versión `1.0.0` |
| Naturaleza de la revisión | Escritorio, asistida por IA; no independiente |
| Fecha de corte de los casos | La definida individualmente en el fixture |

La revisión usa exclusivamente los contenidos versionados indicados. No se consultaron datos reales ni fuentes externas.

## 3. Criterio de lectura

Se distingue entre:

- **Coherencia del resultado esperado:** la regla metodológica y el resultado esperado no se contradicen.
- **Suficiencia de las entradas:** las evidencias incluidas permiten justificar ese resultado sin completar lagunas por inferencia.
- **Límite de alcance:** una entrada puede servir para probar una regla concreta sin ser suficiente para asignar una clasificación completa.

Una expectativa escrita en el campo `scenario` no se trata automáticamente como evidencia independiente que demuestre la expectativa del campo `expected`. Cuando el escenario declara que un efecto es «material», se comprueba si las evidencias aportan respaldo propio para esa materialidad.

## 4. Revisión por caso

| Caso | Resultado esperado | Evaluación del diseño | Hallazgo y tratamiento |
| --- | --- | --- | --- |
| T01 | I0; dirección independiente | **INSUFICIENCIA DE ALCANCE** | El inventario descarta dependencias técnicas/operativas enumeradas, pero la unidad incluye el token público y el anuncio es de marca. No se excluyen expresamente canales reputacionales, de confianza, atención o demanda. La evidencia podría descartar el canal técnico, pero no necesariamente todo mecanismo material hacia la unidad amplia declarada. Delimitar la unidad a funciones técnicas/operativas o incorporar evidencia suficiente sobre los canales restantes antes de usar I0. Dirección INDETERMINADA sigue siendo correcta sin evidencia direccional separada. |
| T02 | I1; dirección INDETERMINADA | **COHERENTE, CON ALCANCE ACOTADO** | El incidente está limitado a un endpoint no crítico; las funciones centrales permanecen operativas; el canal alternativo acepta la clase de solicitudes y la población puede acceder. Es consistente con I1 y con no asignar dirección. El fixture no cuantifica duración, pero no debe inventarse una duración ni exigirse un umbral numérico universal. |
| T03 | I2; NEGATIVA para el segmento si se confirma la restricción | **EVIDENCIA PARCIAL** | El mapa de componentes y el registro operativo respaldan un canal directo y una cola de depósitos limitada al segmento. No se describe cuánto se retrasa el procesamiento, si existe bloqueo efectivo, ni por qué el cambio es apreciable para ese segmento. El alcance acotado sí está respaldado. Para sostener I2 sin inferencias, añadir evidencia sintética del efecto operativo relevante (por ejemplo, indisponibilidad efectiva o retraso documentado y su consecuencia para el segmento). Mantener la dirección condicional a la confirmación de la restricción. |
| T04 | I3; NEGATIVA para el ecosistema | **EVIDENCIA PARCIAL** | La centralidad del oráculo está documentada y el reporte indica degradación que afecta a las aplicaciones listadas. Sin embargo, «degradación» no especifica qué condición material cambia ni su alcance operativo. Los controles de fallback y continuidad ayudan a descartar I4, pero no demuestran por sí solos materialidad I3. Añadir evidencia sintética del tipo y alcance de la degradación y de la condición material afectada, manteniendo documentado que no se compromete una función esencial. |
| T05 | I4; NEGATIVA | **COHERENTE** | El informe forense confirma compromiso de la única ruta de autorización; el inventario descarta una ruta independiente y la evaluación vincula el servicio con el acceso esencial a retiros. La cadena de compromiso de función esencial está explícita. |
| T06 | INDETERMINADA | **COHERENTE** | La publicación anónima no se conecta con la unidad mediante inventario, declaración del proveedor ni evidencia operativa. La amplitud potencial no compensa la falta del mecanismo. INDETERMINADA para intensidad y dirección es consistente. |
| T07 | I4 para escenario condicional; condición pendiente; probabilidad no asignada | **COHERENTE PARA EL ESCENARIO DEFINIDO** | La función de retiro es única, no hay ruta alternativa y el plan vincula la condición de emergencia con una pausa. Que la condición no esté confirmada no reduce la severidad dentro del escenario condicional ni autoriza asignar probabilidad. La ficha debe conservar explícitamente que I4 aplica solo al escenario «si se activa la condición». |
| T08 | Direcciones opuestas por segmento; intensidades evaluadas por separado | **EVIDENCIA PARCIAL** | La separación de poblaciones está definida y los registros describen pérdida/ganancia de acceso. No se aporta evidencia independiente de que la integración sea material para cada segmento; esa calificación aparece en el escenario, no en el contenido probatorio. Añadir evidencia sintética de la función de la integración y de la consecuencia concreta para cada población. No asignar una intensidad numérica a A o B con el paquete actual. MIXTA solo para una unidad agregada explícitamente definida. |
| T09 | INDETERMINADA para alcance controvertido; dirección indeterminada salvo soporte independiente | **COHERENTE** | Existe afirmación de amplitud sin denominador, evidencia contraria y ausencia de regla aprobada para resolver la discrepancia. Preservar ambas fuentes y no seleccionar una por autoridad o mayoría es consistente con la propuesta. |
| T10 | Mitigación UNVERIFIED; no reducir intensidad por ella | **COHERENTE COMO PRUEBA DE MITIGACIÓN; NO COMO CLASIFICACIÓN COMPLETA** | La promesa de recuperación no demuestra despliegue, capacidad ni acceso; la restricción original continúa documentada. El caso permite probar que la mitigación no puede atenuar una evaluación. No contiene una intensidad basal ni evidencia suficiente para reconstruirla, por lo que no debe producir por sí solo un nivel I0–I4. |
| T17 | INDETERMINADA para intensidad y dirección | **COHERENTE** | La propuesta omite contratos afectados, detalles de implementación e inventario de dependencias. La información no confirma ni descarta el mecanismo material; clasificar I0 sería incorrecto. |

## 5. Resultado de la revisión de diseño

- **Coherencia sin insuficiencia material detectada para el propósito limitado del caso:** T02, T05, T06, T07, T09 y T17.
- **Necesitan precisión o evidencia sintética adicional antes de usarse como oráculos semánticos concluyentes:** T01, T03, T04 y T08.
- **Prueba de regla limitada, sin clasificación basal completa:** T10.

Esta agrupación es un resultado de revisión de diseño, no el estado de ejecución de los casos.

## 6. Acciones recomendadas para una futura versión del paquete

1. Mantener inmutable el paquete v1.0.0 y su hash. No editar retrospectivamente las entradas congeladas.
2. Preparar una versión nueva del fixture con un nuevo identificador/versión y SHA-256, incorporando únicamente la evidencia sintética necesaria para T01, T03, T04 y T08.
3. Mantener T10 como prueba de mitigación no verificada y hacer explícito que no asigna intensidad basal; alternativamente, crear un caso separado con línea base probatoria completa.
4. Para T01, decidir si la unidad es exclusivamente técnica/operativa o si incluye canales de reputación, confianza, atención y demanda. No conservar I0 para una unidad amplia si esos canales no se han examinado.
5. Volver a revisar la nueva versión contra los mismos anclajes y registrar cualquier cambio en los resultados esperados, sin convertir esta revisión de escritorio en PASS.
6. Mantener los estados de ejecución T01–T10 y T17 en `NOT_EXECUTED`. T16 permanece `BLOCKED` hasta que dos evaluadores humanos independientes completen el protocolo.

## 7. Declaración de no ejecución

No se ejecutó una evaluación formal con un evaluador humano independiente; no se compararon respuestas independientes; no se calculó acuerdo; no se cambió ningún estado de la matriz del registro de ejecución. Este documento no aprueba la propuesta del Issue #14 ni autoriza su implementación.
