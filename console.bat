@echo off
call ./env.bat
PuTTY.exe -serial %AMPY_PORT% -sercfg 115200,8,n,1,N
rem python -m serial.tools.miniterm --exit-char 24 --menu-char 25 --encoding Latin1 %AMPY_PORT% 115200