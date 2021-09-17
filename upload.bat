@echo off
call ./env.bat

echo uploading imu
rem ampy rmdir /imu
rem ampy put ./src/imu /imu

ampy put ./src/imu/mpu9250.py /mpu9250.py 
ampy put ./src/imu/deltat.py /deltat.py 
ampy put ./src/imu/fusion.py /fusion.py 
ampy put ./src/main.py /main.py 

echo starting serial console
call ./console.bat



