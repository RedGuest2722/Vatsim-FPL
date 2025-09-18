@echo off
if exist "D:\My Stuff\Coding Projects\Vatsim-FPL\Vatsim FPL Checker Windows" (
    rmdir "D:\My Stuff\Coding Projects\Vatsim-FPL\Vatsim FPL Checker Windows")

pyinstaller --clean --distpath "D:\My Stuff\Coding Projects\Vatsim-FPL\Vatsim FPL Checker Windows\" build.spec
rmdir "D:\My Stuff\Coding Projects\Vatsim-FPL\build" /S /Q
echo Done.