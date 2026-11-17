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
5. Preserva los sidecars oficiales SHA-256, OpenPGP `.asc` y Minisign `.minisig` para los binarios Windows amd64 de Server y Client, y calcula SHA-256 de cada sidecar capturado.
6. Marca el resultado como `CAPTURED`, `PARTIAL` o `BLOCKED`; diferencia el latest estable del endpoint Server y el latest publicado en el índice Client.

## Controles explícitos

- No descarga imágenes ni binarios.
- Los checksums y firmas detached son archivos auxiliares de metadata; su captura no verifica el binario ni la firma.
- No ejecuta `docker pull`.
- No instala software.
- No solicita ni activa licencias.
- No crea buckets, volúmenes ni recursos externos.
- No activa Object Lock.
- No inventa versión, digest, firma, SBOM o condiciones de licencia.

## Criterio de interpretación

Una captura `CAPTURED` demuestra que los metadatos oficiales de Server y Client fueron preservados íntegramente y con hash. La API Server documenta el endpoint `/latest` como la consulta del último release estable. Client publica releases por separado; su índice de release notes/SBOM permite identificar el último release publicado, que debe contrastarse con la documentación de actualización estable y la fecha del Server. La captura no resuelve por sí sola el digest OCI ni aprueba condiciones de licencia. El reporte 1.2.0 mantiene `signature_verification_performed=false` y `checksum_compared_to_binary=false`: los sidecars se preservan, pero no se descarga el ejecutable para recalcular su hash ni verificar criptográficamente la firma. `CAPTURED` significa que la captura de metadatos y sidecars está completa; `PARTIAL` indica que faltó alguno de los checksums/sidecars esperados.

Si el endpoint no responde, el JSON es inválido o su estructura no permite distinguir releases, el resultado permanece `BLOCKED`. No se utiliza una versión antigua como sustituto implícito.

Refs #100, #91, #89. Este preflight no cierra ninguna de las áreas A–E de #88.


## Sidecars oficiales Windows amd64 localizados

Para las versiones registradas en la captura actual, los directorios oficiales publican:

- Server `RELEASE.2026-09-19T17-05-25Z`: checksum publicado `29db67c14240d413ec00bae97338d46973c98a1df59e970938ac094bf675cce3`, más archivos `.asc` y `.minisig`.
- Client `RELEASE.2026-09-19T15-24-59Z`: checksum publicado `e3852ee80498034460bb9904e1c483d19172e8db10fa3a67141af131f9f1414b`, más archivos `.asc` y `.minisig`.

El preflight captura estos sidecars desde las rutas oficiales y conserva hashes de los propios sidecars. No afirma que esos hashes publicados hayan sido contrastados con los binarios. La verificación de firma requiere un artefacto binario y una clave pública/fingerprint confiable; queda fuera de esta captura metadata-only.
