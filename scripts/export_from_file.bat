@echo off
setlocal enabledelayedexpansion

set "file=modified.txt"

echo %%~fa | isra component clean --force


for /f "tokens=*" %%a in (%file%) do (
    echo %%a
    isra component load --file %%~fa
    isra standards expand
    isra component save --format yaml
    isra component batch
)

endlocal