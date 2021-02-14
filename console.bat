@echo off
call ./env.bat
PuTTY.exe -serial %AMPY_PORT% -sercfg 115200,8,n,1,N