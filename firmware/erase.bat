call ../env.bat
esptool.py --port %AMPY_PORT% --baud 460800 erase_flash