# Preflight de metadata oficial AIStor

## Objetivo

Capturar y preservar la respuesta JSON de la API oficial de releases AIStor para resolver, con evidencia fechada, el release estable de Server/Client. Este preflight no descarga ni ejecuta software.

## Fuente

- API oficial Server: `https://dl.min.io/api/releases/aistor/latest`.
- Índice oficial de release notes/SBOM de AIStor Client (`mc`): `https://dl.min.io/aistor/mc/release/notes/`.

## Ejecución

El workflow `aistor-release-metadata-preflight.yml` ejecuta `scripts/validation/Get-AIStorReleaseMetadata.sh` en un runner efímero de GitHub Actions.

El script:

1. Recupera la respuesta JSON oficial de AIStor Server y el índice oficial de release notes de AIStor Client.
2. Comprueba que el JSON de Server sea válido y que el índice de Client contenga versiones de release.
3. Preserva ambos contenidos originales como artefactos.
4. Registra SHA-256, tamaño, versión, fecha de release, URLs de release notes/SBOM, timestamp UTC, commit y workflow run.
5. Marca el resultado como `CAPTURED`, `PARTIAL` o `BLOCKED`; diferencia el latest estable del endpoint Server y el latest publicado en el índice Client.

## Controles explícitos

- No descarga imágenes ni binarios.
- No ejecuta `docker pull`.
- No instala software.
- No solicita ni activa licencias.
- No crea buckets, volúmenes ni recursos externos.
- No activa Object Lock.
- No inventa versión, digest, firma, SBOM o condiciones de licencia.

## Criterio de interpretación

Una captura `CAPTURED` demuestra que los metadatos oficiales de Server y Client fueron preservados íntegramente y con hash. La API Server documenta el endpoint `/latest` como la consulta del último release estable. Client publica releases por separado; su índice de release notes/SBOM permite identificar el último release publicado, que debe contrastarse con la documentación de actualización estable y la fecha del Server. La captura no resuelve el digest OCI ni aprueba condiciones de licencia.

Si el endpoint no responde, el JSON es inválido o su estructura no permite distinguir releases, el resultado permanece `BLOCKED`. No se utiliza una versión antigua como sustituto implícito.

Refs #100, #91, #89. Este preflight no cierra ninguna de las áreas A–E de #88.
