call ../env.bat
esptool.py --port %AMPY_PORT% --baud 115200 write_flash -fm dio -fs 4MB 0x0000 .\esp8266-20200911-v1.13.bin
