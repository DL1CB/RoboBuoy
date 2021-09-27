@echo off
call ../env.bat
esptool.py --port %AMPY_PORT% erase_flash
