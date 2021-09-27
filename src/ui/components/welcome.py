from drivers.ili9341 import img,textBox,brightness
from drivers.button  import btnA, btnB
from ui.fonts        import Sans18, Sans24, Sans40

def render(  ):
    brightness(100)
    img(0, 0, "bitmaps/welcome.jpg")




