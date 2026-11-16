# Issue #93 — Laboratorio de validación sintética

Esta primera etapa del laboratorio se limita al sistema de archivos local. Utiliza registros sintéticos generados y un directorio temporal. No establece conexiones de red, no inicia servicios, no instala paquetes, no accede a credenciales ni modifica datos de producción.

## Requisitos

- PowerShell 7.6.6.
- No requiere módulos de PowerShell ni dependencias externas.

## Ejecución

Desde la raíz del repositorio:

```powershell
pwsh -NoLogo -NoProfile -File .\\scripts\\validation\\Invoke-SyntheticValidationLab.ps1
```

Para conservar el directorio temporal con las evidencias:

```powershell
pwsh -NoLogo -NoProfile -File .\\scripts\\validation\\Invoke-SyntheticValidationLab.ps1 -KeepArtifacts
```

Para reproducir el mismo contenido de los registros sintéticos:

```powershell
pwsh -NoLogo -NoProfile -File .\\scripts\\validation\\Invoke-SyntheticValidationLab.ps1 -Seed 20261116
```

El comando emite un único informe JSON compacto y devuelve un código de salida distinto de cero si ocurre un fallo.

## Comprobaciones

- Generación determinista del conjunto de datos sintéticos.
- Manifiesto SHA-256 y tamaños en bytes.
- Integridad de la exportación y de la restauración.
- Detección de una modificación intencional del contenido.
- Reconciliación de la eliminación en el conjunto de datos, la exportación y el contenido restaurado.

## Evidencia y limitaciones

Un resultado PASS demuestra únicamente el flujo del sistema de archivos dentro del directorio temporal aislado. No demuestra las operaciones de copia de seguridad y restauración de PostgreSQL, WORM/Object Lock físico, borrado seguro de medios, eliminación de copias de seguridad en proveedores externos, snapshots externos ni migraciones de producción. Esas capacidades requieren validaciones independientes en entornos específicos.

De forma predeterminada, el directorio temporal se elimina después de generar el informe. Utiliza -KeepArtifacts únicamente cuando sea necesario inspeccionar los artefactos sintéticos.
