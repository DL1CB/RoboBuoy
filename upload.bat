@echo off
call ./env.bat

echo uploading imu
ampy rmdir /imu
ampy put ./src/imu /imu

echo starting serial console
call ./console.bat



