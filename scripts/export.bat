@echo off
setlocal enabledelayedexpansion
set directory="C:\CS\Workspace\githubRepo\iriusrisk-ysc-components"

echo %%~fa | isra component clean --force

for /r "%directory%" %%a in (*.yaml) do (
    echo %%~fa | findstr /c:"to_review" > nul
    if errorlevel 1 (
        echo %%~fa
        isra component load --file %%~fa
        isra standards expand
        isra component save --format yaml
        isra component batch
    )
)
