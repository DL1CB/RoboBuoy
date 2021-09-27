from drivers.ili9341 import img,textBox,brightness
from drivers.button  import btnA, btnC
from ui.fonts        import Sans18, Sans30

def render():
    brightness(100)
    img(60, 20, "bitmaps/qrcode.jpg")
    textBox(100,  10, "Scan to Register", Sans18)

