@echo off
call ../../env.bat

py sources_to_bitmaps.py

rem echo uploading bitmaps
rem ampy rmdir /bitmaps
ampy put ./bitmaps/qrcode.jpg /bitmaps/qrcode.jpg




