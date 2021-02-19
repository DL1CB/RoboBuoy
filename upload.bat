@echo off
call ./env.bat

WMIC PROCESS WHERE "NAME LIKE '%PUTTY.EXE%'" CALL TERMINATE

echo uploading imu
rem ampy rmdir /imu
rem ampy put ./src/imu /imu

ampy put ./src/imu/mpu9250.py /mpu9250.py 
ampy put ./src/pseudo.py /main.py 

echo starting serial console
call ./console.bat



