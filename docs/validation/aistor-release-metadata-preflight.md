# Preflight de metadata oficial AIStor

## Objetivo

Capturar y preservar la respuesta JSON de la API oficial de releases AIStor para resolver, con evidencia fechada, el release estable de Server/Client. Este preflight no descarga ni ejecuta software.

## Fuente

- API oficial: `https://dl.min.io/api/releases/aistor/latest`.

## Ejecución

El workflow `aistor-release-metadata-preflight.yml` ejecuta `scripts/validation/Get-AIStorReleaseMetadata.sh` en un runner efímero de GitHub Actions.

El script:

1. Recupera únicamente la respuesta JSON del endpoint oficial.
2. Comprueba que la respuesta sea un objeto JSON.
3. Preserva el contenido original como artefacto.
4. Registra SHA-256, tamaño, claves de primer nivel, timestamp UTC, commit y workflow run.
5. Marca el resultado como `CAPTURED` o `BLOCKED`; no clasifica por sí mismo ningún release como GA.

## Controles explícitos

- No descarga imágenes ni binarios.
- No ejecuta `docker pull`.
- No instala software.
- No solicita ni activa licencias.
- No crea buckets, volúmenes ni recursos externos.
- No activa Object Lock.
- No inventa versión, digest, firma, SBOM o condiciones de licencia.

## Criterio de interpretación

Una captura `CAPTURED` solo demuestra que la respuesta JSON oficial fue preservada íntegramente y con hash. No equivale a aprobar el release. La revisión posterior debe identificar Server y Client, comprobar el canal GA y contrastar la versión con release notes y mecanismos oficiales de integridad/licencia.

Si el endpoint no responde, el JSON es inválido o su estructura no permite distinguir releases, el resultado permanece `BLOCKED`. No se utiliza una versión antigua como sustituto implícito.

Refs #100, #91, #89. Este preflight no cierra ninguna de las áreas A–E de #88.
