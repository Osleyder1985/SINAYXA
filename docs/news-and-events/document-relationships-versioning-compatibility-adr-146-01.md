# ADR-146-01 — Versionado y compatibilidad de relaciones documentales

- Issue: #146
- PR de diseño base: #147
- Estado: PROPUESTA PARA REVISIÓN; no aprobada ni implementada.
- Fecha: 2026-11-19
- Base examinada: commit `673955d754443ef3640079e9dc7f1b5b26e21c82` de la PR #85.
- Alcance: decisión de versionado, consumidores internos localizados y matriz de compatibilidad para una futura representación de relaciones documentales.

## 1. Contexto y evidencia

La inspección del contrato 0.2.1 propuesto en #85 encontró:

1. `schemas/source-evidence-contract-0.2.1.schema.json` fija `contract_version.const = "0.2.1"`, exige las colecciones raíz enumeradas en el esquema y usa `additionalProperties: false` en la raíz y en los objetos tipados.
2. El esquema contiene 27 definiciones; 21 definiciones de objeto tipado rechazan propiedades adicionales.
3. `scripts/validation/validate_source_evidence_contract_0_2_1.py` carga expresamente el esquema y fixture 0.2.1 y aplica validaciones semánticas adicionales.
4. `scripts/validation/contract_0_2_1_extensions.py` y `scripts/validation/test_contract_0_2_1_extensions.py` implementan y prueban invariantes del contrato 0.2.1.
5. `scripts/validation/migrate_source_evidence_contract_0_2_0_to_0_2_1.py` acepta exclusivamente la versión fuente 0.2.0 y genera 0.2.1. No es un migrador 0.2.1→0.2.2.
6. `scripts/validation/validate_source_evidence_contract.ps1` usa por defecto el fixture 0.2.0 y exige literalmente `contract_version = '0.2.0'`. `validate_source_evidence_contract_schema.py` también apunta al esquema y fixture 0.2.0.
7. Los workflows PowerShell y Security enumeran rutas de 0.2.1. El workflow PostgreSQL/event registry valida el contrato temporal y el registro de eventos, no demuestra por sí mismo que consuma paquetes source-evidence 0.2.1.

**Importante:** la comparación de árboles recursivos encontró 102 archivos en el HEAD de #85 y 88 en el `main` examinado. Los archivos de 0.2.1 citados estaban en el HEAD de #85 y no en ese `main`. Por ello, este ADR describe la propuesta en #85, no una versión ya integrada en `main`.

### 1.1 Inventario acotado de consumidores

| Componente | Papel observado | Compatibilidad con 0.2.2 |
| --- | --- | --- |
| JSON Schema 0.2.1 | Validador estructural estricto | No compatible; debe rechazar versión/campos nuevos |
| Validador Python 0.2.1 | Validador semántico específico | No compatible salvo evolución explícita y pruebas separadas |
| Extensiones/pruebas Python 0.2.1 | Invariantes y regresiones | No validan 0.2.2 |
| Migrador 0.2.0→0.2.1 | Productor de 0.2.1 | No migra a 0.2.2 |
| Validador PowerShell 0.2.0 | Consumidor heredado 0.2.0 | No compatible con 0.2.1/0.2.2 |
| Validador de esquema base 0.2.0 | Validador heredado 0.2.0 | No valida 0.2.2 |
| CI PowerShell/Security | Ejecuta controles sobre rutas explícitas | Requiere nuevos controles 0.2.2 |
| Registro de eventos | Subsistema temporal/event registry separado | No se ha demostrado que consuma source-evidence 0.2.1 |

Este inventario cubre únicamente los archivos y árboles inspeccionados del repositorio. No demuestra la inexistencia de consumidores externos, privados o fuera del repositorio. Esos consumidores quedan **NO INVENTARIADOS / NO VERIFICADOS**.

## 2. Decisión recomendada

Adoptar una versión lógica explícita **0.2.2**, aditiva y separada de 0.2.1, para incorporar la colección tipada de aserciones de relaciones documentales descrita en el documento de diseño de #147.

- No modificar el esquema, fixture, validador ni significado de 0.2.1.
- Mantener una ruta de validación 0.2.1 estricta y reproducible.
- Crear esquema y validador propios para 0.2.2.
- Un consumidor debe seleccionar la ruta por `contract_version` explícita. Una versión desconocida o no soportada produce rechazo explícito.
- Si el validador 0.2.2 admite paquetes 0.2.1, debe hacerlo mediante una ruta heredada explícita, no relajando el esquema 0.2.2 ni ignorando campos.
- No convertir texto libre, cronología o similitud en relaciones estructuradas automáticamente.
- No convertir `supersedes_source_version_id` ni `provenance_edges` en relaciones de corrección entre documentos.
- Preservar declaraciones contradictorias y ciclos como datos/anomalías revisables; no descartar evidencia ni aplicar transitividad automáticamente.

La numeración 0.2.2 es una recomendación condicionada a que el proyecto confirme su política de versionado. No constituye aprobación del contrato.

## 3. Matriz de compatibilidad propuesta

| Productor → consumidor | Resultado requerido | Regla |
| --- | --- | --- |
| 0.2.1 → consumidor 0.2.1 | Compatible | Validación con esquema y validador 0.2.1 exactos |
| 0.2.2 → consumidor 0.2.1 | No compatible; rechazo explícito | Prohibido ignorar propiedades o degradar silenciosamente |
| 0.2.1 → consumidor 0.2.2 | Lectura heredada explícita | Ruta 0.2.1 separada; no inferir relaciones ausentes |
| 0.2.2 → consumidor 0.2.2 | Compatible | Validación estructural y semántica 0.2.2 |
| 0.2.1 → conversión a 0.2.2 | Conversión controlada | Preservar snapshot/hash; no inventar relaciones; declarar que no estaban representadas |
| 0.2.2 → exportación 0.2.1 | Pérdida de información | Sólo exportación derivada con informe de pérdida explícito; conservar original 0.2.2 |

La ausencia de una relación en un paquete 0.2.1 significa únicamente que no está representada en ese paquete. No prueba que la relación no exista.

## 4. Requisitos de compatibilidad y migración

1. Validar la versión declarada antes de procesar el contenido.
2. Rechazar versiones desconocidas o no soportadas con un error identificable.
3. Mantener validadores independientes o rutas explícitas por versión.
4. En lectura heredada 0.2.1, no sintetizar relaciones documentales ni asignar estado “sin relaciones”.
5. En migración 0.2.1→0.2.2 (si se implementa), conservar snapshot de origen, hash de entrada/salida, versión de migrador, reglas aplicadas, errores y pérdidas.
6. No afirmar migración sin pérdida semántica si relaciones candidatas sólo aparecen en texto narrativo.
7. Exportar 0.2.2→0.2.1 sólo como derivado identificado, con inventario de campos y relaciones descartados.
8. Probar IDs, referencias, alcance, atribución, evidencia favorable/contraria, timestamps, estados de revisión e historial.
9. Probar import/export round-trip para 0.2.2 y demostrar igualdad semántica de todos los campos soportados.
10. Probar rechazo de referencias rotas, propiedades desconocidas, versiones incorrectas y pérdida silenciosa.
11. Preservar ciclos/contradicciones como anomalías; cualquier restricción específica por tipo debe demostrar que no elimina declaraciones originales.
12. No afirmar compatibilidad con consumidores externos hasta que se inventaríen y prueben.

## 5. Plan de implementación condicionado

1. Revisar y aprobar/corregir este ADR y el alcance del inventario.
2. Actualizar el documento de diseño de #147 para reflejar las decisiones semánticas acordadas: atribución documental sin `ANALYST_INFERENCE`, estado explícito del alcance y preservación de ciclos.
3. Definir esquema 0.2.2 y fixtures normativos, manteniendo los fixtures actuales como fixtures de diseño hasta entonces.
4. Implementar selector/version dispatch, validador estructural, validador semántico y migración sólo si se demuestra necesaria.
5. Añadir CI para 0.2.2, pruebas de compatibilidad y round-trip en el mismo cambio.
6. Revisar el diff y los resultados de CI sobre el mismo HEAD antes de solicitar aprobación.

## 6. No objetivos y límites

Este ADR no autoriza captura automática, crawling, scraping, monitorización, autenticación automática, clasificación automática de credibilidad, inferencia causal ni señales de trading. Tampoco aprueba el contrato 0.2.2, modifica 0.2.1/#15/#16, cierra #146 ni autoriza fusionar #147 a `main`.

## 7. Criterio de aceptación

La decisión sólo podrá considerarse aprobada cuando:

- el inventario interno esté revisado y los consumidores externos conocidos estén declarados;
- el versionado y la matriz estén aceptados;
- el diseño semántico de relaciones esté alineado con este ADR;
- las pruebas normativas y CI demuestren los comportamientos requeridos sobre el mismo commit.

Hasta entonces, compatibilidad externa, migración ejecutable y round-trip sin pérdida permanecen **NO VERIFICADOS**.
