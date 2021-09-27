@echo off
call ../../env.bat

echo generating fonts to src/ui/fonts
py .\font_to_py.py -x .\sources\SiemensSans-Black.ttf 18 ..\..\src\ui\fonts\Sans18.py
py .\font_to_py.py -x .\sources\SiemensSans-Black.ttf 24 ..\..\src\ui\fonts\Sans24.py
py .\font_to_py.py -x .\sources\SiemensSans-Black.ttf 30 ..\..\src\ui\fonts\Sans30.py
py .\font_to_py.py -x .\sources\SiemensSans-Black.ttf 40 ..\..\src\ui\fonts\Sans40.py

echo uploading fonts from src/ui/fonts to device
ampy rmdir /ui/fonts
ampy put ..\..\src\ui\fonts /ui/fonts
ampy ls /ui/fonts



