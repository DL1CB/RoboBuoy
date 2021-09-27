@echo off
call ../env.bat
esptool.py --chip esp32 --port %AMPY_PORT%  write_flash -z 0x1000 ./esp32-20210902-v1.17.bin