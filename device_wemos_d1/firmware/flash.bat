echo Flashing target => WEMOS D1 Mini Pro 
esptool.py --port com4 --baud 115200 write_flash -fm dio -fs 4MB 0x0000 .\esp8266-20180511-v1.9.4.bin
