@echo off
call ./env.bat

echo uploading imu
rem ampy rmdir /imu
rem ampy put ./src/imu /imu

ampy put ./src/imu/mpu9250.py /main.py 

echo starting serial console
call ./console.bat



