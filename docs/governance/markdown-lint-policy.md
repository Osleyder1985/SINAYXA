# Política de calidad documental Markdown

**Issue:** [#35 — Definir política reproducible de Markdown lint](https://github.com/Osleyder1985/SINAYXA/issues/35)

**Estado:** política integrada en `main` mediante PR [#36](https://github.com/Osleyder1985/SINAYXA/pull/36). Su ejecución es un control procedimental local; no implica CI ni bloqueo automático de integraciones.

## 1. Objetivo

Establecer un control reproducible de calidad sintáctica y estructural para los documentos Markdown versionados de SINAYXA.

Markdown lint comprueba convenciones de formato y estructura. No valida la verdad factual, la calidad de las fuentes, la corrección normativa, la semántica de los requisitos ni la causalidad de las afirmaciones.

## 2. Obligatoriedad

La ejecución de Markdown lint es obligatoria antes de publicar cambios que incorporen, modifiquen, renombren o eliminen archivos Markdown.

El propietario debe comprobar y registrar el resultado sobre el SHA exacto que se propone integrar.

Esta obligación es un control procedimental local. Mientras no exista CI ni otro mecanismo de protección automatizado, GitHub no bloqueará técnicamente una publicación que omita la comprobación.

## 3. Herramienta y versiones

Se adopta `markdownlint-cli2` como interfaz de ejecución.

- Versión exacta: `0.24.1`.
- Runtime requerido: Node.js `>=22`.
- Entorno de referencia validado: Node.js `26.13.1` y npm `11.20.0`.
- Dependencia de desarrollo npm, fijada sin rangos semver.
- Dependencias transitivas fijadas mediante `package-lock.json`.
- Instalación reproducible: `npm ci`.
- Comando canónico: `npm run lint:markdown`.

No se utilizarán instalaciones globales ni versiones flotantes como evidencia de conformidad.

La actualización de la herramienta o de sus dependencias requiere revisar el cambio del lockfile y repetir la validación.

## 4. Alcance

Se incluyen todos los archivos Markdown del repositorio:

- README y documentación general.
- Documentos de gobernanza y políticas.
- Especificaciones y taxonomías.
- Matrices y casos de prueba.
- Documentación técnica futura.

La configuración utiliza el patrón `**/*.md`. Los archivos excluidos por `.gitignore`, como los contenidos de `node_modules`, no forman parte de la ejecución.

No se excluyen directorios de documentación por conveniencia ni se omiten documentos extensos.

## 5. Reglas y excepciones

Se mantienen activas las reglas predeterminadas de markdownlint.

La única excepción global inicial es:

- **MD013:** desactivada por la existencia de tablas técnicas, matrices de evidencia, referencias y URLs cuya longitud no debe alterarse mediante cortes artificiales.

No se desactivan globalmente reglas de encabezados, listas, bloques de código, enlaces o espacios.

Toda excepción adicional debe:

1. Identificar la regla afectada.
2. Justificar por qué no puede cumplirse en el fragmento.
3. Limitarse al menor ámbito posible.
4. Quedar visible en el documento o en la configuración versionada.

No se permite desactivar reglas globalmente para ocultar defectos encontrados.

## 6. Procedimiento local

Desde la raíz del repositorio, en Windows/PowerShell:

```powershell
node --version
npm --version
npm ci
npm run lint:markdown
```

La instalación debe respetar `package-lock.json`. No se debe sustituir `npm ci` por una instalación global de la herramienta.

El comando canónico no utiliza `--fix`. Las correcciones automáticas solo podrán aplicarse después de revisar los cambios que producirían.

## 7. Evidencia requerida

El registro de cada ejecución debe incluir:

- SHA exacto del commit examinado.
- Versión de Node.js.
- Versión de npm.
- Versión instalada de markdownlint-cli2.
- Comando ejecutado.
- Código de salida.
- Resultado íntegro o evidencia conservada de PASS/FAIL.
- Hallazgos y excepciones pendientes, si existen.

Una ejecución sobre un SHA no acredita automáticamente otro commit posterior.

## 8. Separación de controles

Markdown lint no sustituye:

- Revisión humana H-OWNER.
- Revisión asistida AI-ADVERSARIAL.
- Pruebas unitarias.
- Validadores de contratos y trazabilidad.
- Revisión de fuentes y evidencia factual.

No se declara revisión independiente por ejecutar una herramienta automática.

## 9. Límites de esta política

Esta política no autoriza:

- Crear workflows de GitHub Actions.
- Incorporar CI.
- Introducir Git hooks.
- Modificar el alcance de PR #32 o Issue #29.
- Alterar automáticamente documentos normativos.
- Afirmar conformidad o certificación ISO.

Cualquier automatización adicional requerirá un Issue independiente y una decisión explícita.
