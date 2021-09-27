@echo off

call ./env.bat

echo This will erase and flash the firmware
pause
cd firmware
call erase.bat
call flash.bat
cd ..

call ./upload.bat