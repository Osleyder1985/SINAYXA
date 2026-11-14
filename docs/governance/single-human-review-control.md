# Revisión documental con un único participante humano

**Estado:** política propuesta para revisión mediante PR  
**Ámbito:** documentos de especificación, taxonomías y contratos de pruebas de SINAYXA mantenidos por un único participante humano.  
**No constituye:** certificación ISO, auditoría externa ni declaración de dos revisores humanos independientes.

## 1. Propósito

Establecer un control de calidad honesto y verificable cuando SINAYXA tiene un único participante humano. La ausencia de una segunda persona no debe provocar ni una declaración ficticia de independencia ni una renuncia a revisar críticamente los documentos.

El modelo separa tres actividades que no son intercambiables:

1. **Revisión humana:** juicio y decisión del propietario, que debe leer y evaluar el artefacto.
2. **Revisión asistida:** análisis adversarial realizado con ayuda de IA. Puede descubrir defectos, pero no es una segunda persona ni una revisión independiente.
3. **Validación automatizada:** comprobaciones deterministas ejecutadas por herramientas versionadas. Demuestran únicamente las propiedades que efectivamente comprueban.

## 2. Fundamento normativo y límites

### 2.1 ISO 9001

La edición vigente es **ISO 9001:2026**, publicada el 16 de septiembre de 2026. La información pública de ISO describe un sistema de gestión de calidad aplicable a organizaciones de distintos tamaños y sectores, y trata, entre otros temas, la información documentada, la evaluación del desempeño y la mejora continua.

La página pública consultada no expone el texto íntegro de las cláusulas de ISO 9001:2026. Por ello, este documento **no atribuye a esa edición una cláusula concreta ni afirma que prohíba o exija dos revisores humanos**. Tampoco declara que SINAYXA esté certificado o sea conforme con ISO 9001.

Fuente oficial: [ISO 9001:2026](https://www.iso.org/standard/9001).

La guía oficial de ISO sobre información documentada de ISO 9001:2015 explica que la cantidad y el nivel de detalle de la documentación pueden adaptarse, entre otros factores, al tamaño de la organización, la complejidad de sus procesos y la competencia de las personas. Esa guía corresponde a la edición 2015 y se cita solo como antecedente explicativo, no como sustituto de los requisitos de 2026.

Fuente oficial: [Guidance on the requirements for Documented Information of ISO 9001:2015](https://www.iso.org/files/live/sites/isoorg/files/standards/docs/en/iso_9001_2015_guidance_documented_information.pdf).

### 2.2 ISO 31000

ISO identifica **ISO 31000:2018** como la edición publicada y confirmada en 2023. Proporciona principios y directrices para identificar, analizar, evaluar, tratar, supervisar y comunicar riesgos. ISO aclara que es una guía no certificable y que puede utilizarse como orientación para programas de auditoría internos o externos.

Fuente oficial: [ISO 31000:2018](https://www.iso.org/standard/31000).

### 2.3 Conclusión de aplicabilidad

En las fuentes oficiales públicas examinadas no se ha encontrado una regla universal que obligue a que cada documento de pruebas de software o taxonomía tenga dos revisores humanos independientes. Esto **no demuestra que no exista** una obligación aplicable en una regulación sectorial, contrato, política de un cliente o norma especializada.

Antes de utilizar este procedimiento en un contexto regulado o contractual, deben identificarse y comprobarse los requisitos externos aplicables y, cuando corresponda, consultarse el texto normativo íntegro.

La exigencia de dos revisores humanos independientes del Issue #29 fue un criterio de aceptación interno añadido al Issue. No debe confundirse con un requisito ISO demostrado.

## 3. Modelo de control de participante único

El estado de control se denomina:

**SINGLE-HUMAN REVIEW WITH COMPENSATING CONTROLS**

Este estado nunca se abrevia ni se interpreta como «dos revisiones humanas independientes».

### 3.1 Control H-OWNER — revisión humana del propietario

El propietario debe revisar el artefacto completo y registrar, como mínimo:

- identidad GitHub del revisor;
- fecha y commit/blob SHA exactos revisados;
- alcance e IDs examinados;
- decisión por cada ID: aceptar, corregir o indeterminado;
- regla aplicada y evidencia que fundamenta la decisión;
- defectos detectados, correcciones y resolución;
- cuestiones no resueltas y riesgo residual;
- declaración explícita de que la revisión fue realizada por el único participante humano.

No se permite completar el registro por inferencia ni atribuir al propietario decisiones que no haya tomado. Una revisión asistida no sustituye esta actividad.

### 3.2 Control AI-ADVERSARIAL — revisión asistida no independiente

Una segunda pasada adversarial asistida debe buscar de forma explícita:

- falsos positivos y falsos negativos;
- confusión entre publicación, afirmación, acontecimiento e hito;
- cambios de fase presentados como hechos consumados;
- conclusiones basadas únicamente en ausencia de evidencia;
- inferencias no justificadas de causalidad, impacto, venta, pérdida, explotación, adopción o reacción;
- contradicciones entre escenario, resultado, clasificación y evidencia;
- defectos de trazabilidad y campos desconocidos completados implícitamente.

El registro debe identificar herramienta/modelo cuando esté disponible, fecha, commit revisado, instrucciones o checklist, hallazgos y límites. El resultado se etiqueta **ASSISTED — NOT INDEPENDENT**.

### 3.3 Control AUTO-VALIDATION — validación determinista

Las propiedades estructurales deben comprobarse con scripts o herramientas versionadas en el repositorio, no únicamente mediante una explicación manual. El registro de cada ejecución debe incluir:

- commit y versión del script;
- entorno/versión del intérprete cuando sea relevante;
- comando exacto;
- resultado PASS/FAIL por comprobación;
- salida íntegra o artefacto de resultados;
- limitaciones conocidas.

Para una matriz de casos, las comprobaciones mínimas incluyen unicidad y cobertura de IDs, correspondencia con la matriz normativa, presencia de campos obligatorios, consistencia de tablas, enlaces locales y detección de contradicciones estructurales verificables.

Una validación estructural no demuestra corrección semántica, verdad factual ni calidad predictiva. No se debe declarar que un Markdown linter, CI o una suite automatizada se ejecutó si no hay evidencia de ejecución.

### 3.4 Control ADVERSARIAL-TEST — pruebas de sensibilidad a defectos

Cuando sea técnicamente viable, el conjunto de validaciones debe probarse contra copias temporales o fixtures con defectos deliberados, por ejemplo:

- ID duplicado o ausente;
- resultado esperado incompatible con el contrato;
- campo obligatorio eliminado;
- enlace local roto;
- etiqueta transversal omitida;
- caso negativo sin exclusión explícita.

El control solo se considera demostrado si la herramienta detecta los defectos introducidos. Las mutaciones se ejecutan sobre fixtures o copias temporales, nunca sobre el artefacto aprobado ni sobre `main`.

Si una mutación no puede detectarse automáticamente, se registra como limitación y se cubre mediante revisión manual explícita; no se afirma cobertura inexistente.

### 3.5 Control RISK-REGISTER — incertidumbre y riesgo residual

Cada defecto o incertidumbre debe registrar ID afectado, descripción, evidencia, consecuencia potencial, decisión, tratamiento, responsable y estado. No se fuerza consenso ni se convierte un dato desconocido en una conclusión negativa.

## 4. Revisión externa independiente

La revisión externa no es un requisito automático para todo documento. Se determina por el uso, impacto y obligaciones aplicables.

Debe tratarse como **OBLIGATORIA** antes de aprobar o utilizar el artefacto cuando:

- una ley, regulación, contrato, cliente o norma sectorial aplicable la exija;
- el artefacto controle una función crítica de seguridad o una decisión de cumplimiento para la que se requiera independencia;
- el análisis de riesgos aprobado identifique la independencia externa como control necesario para reducir un riesgo no aceptable.

Debe tratarse como **RECOMENDADA** antes de un uso productivo de alto impacto, distribución a terceros o utilización como base de decisiones financieras automatizadas, especialmente cuando las limitaciones del control de participante único puedan afectar a terceros.

Puede tratarse como **NO REQUERIDA PARA EL ALCANCE DOCUMENTAL ACTUAL** cuando el artefacto es una especificación interna/sintética, no existe requisito externo identificado y los controles compensatorios están completos. Esta clasificación no autoriza a presentarlo como validado externamente.

Si la revisión externa es obligatoria y no hay revisor disponible, el artefacto queda bloqueado para el uso que exige esa revisión. No se sustituye silenciosamente por una revisión asistida.

## 5. Estados de conformidad

| Estado | Significado | Uso permitido |
|---|---|---|
| `PASS — SINGLE-HUMAN COMPENSATING CONTROLS` | Revisión H-OWNER, revisión asistida, validaciones deterministas y controles adversariales exigidos completados; evidencia preservada; sin defectos bloqueantes. | Uso dentro del alcance interno aprobado, sujeto al riesgo residual documentado. |
| `PASS WITH LIMITATION — EXTERNAL REVIEW PENDING` | Controles compensatorios completados, pero una revisión externa recomendada está pendiente. | Solo uso interno limitado; no afirmar validación externa. |
| `NOT CONFORMANT` | Falta un control obligatorio, hay defectos bloqueantes o el riesgo residual no está aceptado. | No aprobar ni promover el artefacto. |
| `INDEPENDENT HUMAN REVIEW VERIFIED` | Dos personas humanas distintas completaron y registraron revisiones independientes conforme al protocolo aplicable. | Solo cuando existan evidencias verificables de ambas personas. |

Los estados son mutuamente distinguibles. Nunca se elevará un estado por la mera existencia de dos pasadas del mismo asistente.

## 6. Aplicación al Issue #29

Para los 36 escenarios principales y 10 casos BND del Issue #29:

1. Las revisiones A y B ya registradas permanecen como revisiones asistidas del mismo asistente; no se reinterpretan retroactivamente.
2. El propietario debe completar H-OWNER para los 46 casos, con decisiones por ID y evidencia.
3. La revisión adversarial asistida puede conservarse como AI-ADVERSARIAL, identificada como no independiente.
4. Las 12 comprobaciones programáticas puntuales ya registradas siguen siendo evidencia histórica de esa ejecución, pero no son una suite versionada y no se convierten retroactivamente en ella.
5. Antes de declarar conformidad compensatoria, las validaciones estructurales deben ser reproducibles desde herramientas/scripts conservados en el repositorio y las pruebas adversariales deben demostrar qué defectos detectan.
6. El documento debe registrar limitaciones y riesgos residuales, y usar el estado de conformidad exacto definido en esta política.
7. La revisión externa se decidirá según los criterios de la sección 4. Para este conjunto documental sintético, no se ha identificado hasta ahora un requisito externo que la haga obligatoria; esa conclusión deberá revisarse si cambia el uso o el contexto regulatorio.

Esta política no cierra el Issue #29 ni declara sus controles completados. El Issue #29 debe actualizarse mediante un cambio trazable, una vez aprobada esta política.

## 7. Registro de cambios

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0-proposal | 2026-11-14 | Primera propuesta para revisión mediante PR vinculada al Issue #30. |

## 8. Referencias

- [Issue #30 — Definir revisión documental para un proyecto con un único participante humano](https://github.com/Osleyder1985/SINAYXA/issues/30)
- [Issue #29 — Completar pruebas positivas y negativas de la taxonomía](https://github.com/Osleyder1985/SINAYXA/issues/29)
- [ISO 9001:2026 — página oficial](https://www.iso.org/standard/9001)
- [ISO 31000:2018 — página oficial](https://www.iso.org/standard/31000)
- [ISO guidance on documented information for ISO 9001:2015 — antecedente, no norma vigente](https://www.iso.org/files/live/sites/isoorg/files/standards/docs/en/iso_9001_2015_guidance_documented_information.pdf)
