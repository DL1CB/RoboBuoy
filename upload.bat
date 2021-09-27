echo on

call ./env.bat

echo removing main.py
rem ampy rm /main.py
rem ampy rmdir /store
rem ampy rmdir /drivers
rem ampy rmdir /networking
rem ampy rmdir /ui

ampy mkdir /store
ampy mkdir /drivers



rem echo uploading ui
rem ampy put ./src/ui /ui

rem echo uploading bitmaps
rem ampy rmdir /bitmaps
rem ampy put ./src/bitmaps /bitmaps

echo uploading store
ampy put ./src/store/ahrs.py /store/ahrs.py

echo uploading drivers
ampy put ./src/drivers/ahrs.py /drivers/ahrs.py
ampy put ./src/drivers/i2c.py /drivers/i2c.py

rem echo uploading networking
rem ampy put ./src/networking /networking

echo uploading main 
ampy put ./src/main.py /main.py

echo starting serial console
call ./console.bat



