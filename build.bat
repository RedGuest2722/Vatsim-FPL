@echo off
setlocal

set "BAT_DIR=%~dp0"
set "DIST_DIR=%BAT_DIR%/Vatsim FPL Checker"


echo Building with PyInstaller...
pyinstaller --clean --distpath "%DIST_DIR%" main.spec


echo Cleaning up build artifacts...
if exist "%BAT_DIR%/build" (
    rmdir /S /Q "%BAT_DIR%/build"
)

echo Done.
pause
