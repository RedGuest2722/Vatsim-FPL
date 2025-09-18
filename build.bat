@echo off
if exist "D:\My Stuff\Coding Projects\Vatsim-FPL\Vatsim FPL Checker" (
    rmdir "D:\My Stuff\Coding Projects\Vatsim-FPL\Vatsim FPL Checker")

pyinstaller --clean --distpath "D:\My Stuff\Coding Projects\Vatsim-FPL\Vatsim FPL Checker\" main.spec
rmdir "D:\My Stuff\Coding Projects\Vatsim-FPL\build" /S /Q
echo Done.