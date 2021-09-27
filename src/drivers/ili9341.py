import framebuf
import utime 
import ustruct
from machine import Pin, SPI, PWM
from micropython import const
from math import sqrt

RDDSDR     = const(0x0f) # Read Display Self-Diagnostic Result
SLPOUT     = const(0x11) # Sleep Out
INVON      = const(0x21) # Invert Display Colors ON
GAMSET     = const(0x26) # Gamma Set
DISPOFF    = const(0x28) # Display Off
DISPON     = const(0x29) # Display On
CASET      = const(0x2a) # Column Address Set
PASET      = const(0x2b) # Page Address Set
RAMWR      = const(0x2c) # Memory Write
RAMRD      = const(0x2e) # Memory Read
MADCTL     = const(0x36) # Memory Access Control
VSCRSADD   = const(0x37) # Vertical Scrolling Start Address
PIXSET     = const(0x3a) # Pixel Format Set
PWCTRLA    = const(0xcb) # Power Control A
PWCRTLB    = const(0xcf) # Power Control B
DTCTRLA    = const(0xe8) # Driver Timing Control A
DTCTRLB    = const(0xea) # Driver Timing Control B
PWRONCTRL  = const(0xed) # Power on Sequence Control
PRCTRL     = const(0xf7) # Pump Ratio Control
PWCTRL1    = const(0xc0) # Power Control 1
PWCTRL2    = const(0xc1) # Power Control 2
VMCTRL1    = const(0xc5) # VCOM Control 1
VMCTRL2    = const(0xc7) # VCOM Control 2
FRMCTR1    = const(0xb1) # Frame Rate Control 1
DISCTRL    = const(0xb6) # Display Function Control
ENA3G      = const(0xf2) # Enable 3G
PGAMCTRL   = const(0xe0) # Positive Gamma Control
NGAMCTRL   = const(0xe1) # Negative Gamma Control

COLUMN_SET  = const(0x2a)
PAGE_SET    = const(0x2b)
RAM_WRITE   = const(0x2c)
RAM_READ    = const(0x2e)

screenWidth  = 320
screenHeight = 240

backroundcolor  = 0xffffff

chunk = const(20) #maximum number of pixels per spi write
buf = bytearray(chunk * 2)

spi = SPI(2,baudrate=40000000, miso=Pin(19), mosi=Pin(23), sck=Pin(18))
cs  = Pin(14, Pin.OUT)
dc  = Pin(27, Pin.OUT)
rst = Pin(33, Pin.OUT)
led = PWM(Pin(32, Pin.OUT))


def color565(rgb):
    """ converts a rgb888 24 bit value to 16 bit rgb565 color value """
    #return 	((rgb >> 16 & 0x1f ) << 11) | ((rgb >> 8 & 0x3f ) << 5) | (rgb & 0x1f )
    return (((rgb >> 16 & 0x00F8) << 8) | (( rgb >> 8 & 0x00FC) << 3) | ((rgb & 0x00F8) >> 3)) 
     
def brightness(level=50):
    led.freq(500)
    led.duty( level * 1023 // 100  )

def reset():
    """ resets the ili9341 """
    cs.value(1)
    dc.value(0)
    rst.value(0)
    utime.sleep_ms(50)
    rst.value(1)
    utime.sleep_ms(50)    

def write(command=None, data=None):
    """ 
    writes a command, or a command and corresponding data to the ili9341
    """
    if command is not None:
        dc(0)
        cs(0)
        spi.write(bytearray([command]))
        cs(1)
    if data is not None:
        dc(1)
        cs(0)
        spi.write(data)
        cs(1)

def writeblock(x0, y0, x1, y1, data):
    write(COLUMN_SET, ustruct.pack(">HH", x0, x1))
    write(PAGE_SET, ustruct.pack(">HH", y0, y1))
    write(RAM_WRITE, data)    

def pixel(x, y, color):
    writeblock(x, y, x, y, ustruct.pack(">H", color565(color) ))

def hline(x, y, width, color=0x00000, weight=1):
    """Draw a horizontal line."""
    buf = bytes([ color565(color) >> 8, color565(color) & 0xFF ]) * width * weight
    writeblock( x, y, x+width-1, y+weight, buf )

def vline(x, y, height, color=0x00000, weight=1):
    """Draw a horizontal line."""
    buf = bytes([ color565(color) >> 8, color565(color) & 0xFF ]) * height * weight
    writeblock( x, y, x+weight-1, y+height, buf )     

def screenColor(color=0xebebeb):
    """Fill whole screen."""
    global backroundcolor
    backroundcolor = color    
    buf = ustruct.pack(">H", color565(color)) * screenWidth * screenHeight
    writeblock( 0, 0, screenWidth-1, screenHeight, buf ) 

def textBox( x, y, string, font, fgcolor=0x000000, bgcolor=0xFFFFFF ):
    text( x, y, string, font, fgcolor, bgcolor )

def text( x, y, string, font, fgcolor, bgcolor ):
    xpos = x
    for ch in string:
        xpos = char( xpos, y, ch, font, fgcolor, bgcolor )

def char( x, y, ch, font, fgcolor, bgcolor ):

    fg = color565(fgcolor)  
    bg = color565(bgcolor)

    glyph ,height, width = font.get_ch(ch)

    fb = framebuf.FrameBuffer(bytearray(glyph),width,height, framebuf.MONO_HLSB)      

    buf = bytearray(width*height*2)
    pointer = 0

    for h in range(height):
        for w in range(width):
            if fb.pixel(w,h):
                buf[pointer] = fg >> 8
                buf[pointer+1] = fg
                pointer += 2
            else:
                buf[pointer] = bg >> 8
                buf[pointer+1] = bg
                pointer += 2

    writeblock( x, y, x+width-1, y+height-1, buf)

    return x+width

def rect(x, y, width, height, fillcolor=None, bordercolor=None, borderweight=1):
    
    if fillcolor is not None:
        buf = bytes([ color565(fillcolor) >> 8, color565(fillcolor) & 0xFF ]) * width * height
        writeblock(x,y,x+width-1,y+height,buf)

    if bordercolor is not None:
        hline(x,y,width, bordercolor,borderweight)
        hline(x,        y+height-borderweight,   width, bordercolor,borderweight)
        vline(x,        y, height,  bordercolor,borderweight)
        vline(x+width-borderweight, y,           height, bordercolor,borderweight)

def circle( x0, y0, r, color ):
    from math import ceil
    color = ustruct.pack(">H", color565(color) )
    rsq = r*r 
    for x in range( r+1  ):

        if x == r:
            writeblock(x0+r, y0, x0+r, y0, color)
            writeblock(x0-r, y0, x0-r, y0, color)
        else:
            y = ceil(int(sqrt(rsq - x*x)))
            writeblock(x0+x, y0+y, x0+x, y0+y, color)
            writeblock(x0-x, y0+y, x0-x, y0+y, color)
            writeblock(x0+x, y0-y, x0+x, y0-y, color)
            writeblock(x0-x, y0-y, x0-x, y0-y, color)
    

def fillCircle( x, y, r, color, bgcolor=None ) :
    '''Draw a filled circle with given radius and color with aPos as center'''

    bgcolor = bgcolor or color

    x = min(screenWidth - 1, max(0, x))
    y = min(screenHeight - 1, max(0, y))

    rsq = r * r
    for i in range(r) :
        h = int(sqrt(rsq - i * i))
        y0 = y - h

        ey = y0 + h * 2
        ln = abs(ey - y0) + 1

        buf =  ustruct.pack(">H", color565(color) ) *2
        if i == r-1:
            buf +=  ustruct.pack(">H", color565(color) ) * (ln-4)
        else:
            buf +=  ustruct.pack(">H", color565(bgcolor) ) * (ln-4)
        buf +=  ustruct.pack(">H", color565(color) ) *2

        writeblock(x+i, y0, x+i , y0 + ln - 1, buf)
        writeblock(x-i, y0, x-i , y0 + ln - 1, buf)

       
def img(x, y, path ):
    """ images are prepared with the bitmapconvertertool """
    with open(path,"rb") as f:
        width, height = ustruct.unpack(">HH",f.read(4))
        writeblock(x, y, x+width-1, y+height-1, f.read())


#initilize
reset()
brightness(0)    
for command, data in (
    (RDDSDR,    b"\x03\x80\x02"),
    (PWCRTLB,   b"\x00\xc1\x30"),
    (PWRONCTRL, b"\x64\x03\x12\x81"),
    (DTCTRLA,   b"\x85\x00\x78"),
    (PWCTRLA,   b"\x39\x2c\x00\x34\x02"),
    (PRCTRL,    b"\x20"),
    (DTCTRLB,   b"\x00\x00"),
    (PWCTRL1,   b"\x23"),
    (PWCTRL2,   b"\x10"),
    (VMCTRL1,   b"\x3e\x08"),
    (VMCTRL2,   b"\x86"),
    (MADCTL,    b"\x08"),  
    (PIXSET,    b"\x55"),
    (FRMCTR1,   b"\x00\x18"),
    (DISCTRL,   b"\x08\x82\x27"),
    (ENA3G,     b"\x00"),
    (GAMSET,    b"\x01"),
    (PGAMCTRL,  b"\x0f\x31\x2b\x0c\x0e\x08\x4e\xf1\x37\x07\x10\x03\x0e\x09\x00"),
    (NGAMCTRL,  b"\x00\x0e\x14\x03\x11\x07\x31\xc1\x48\x08\x0f\x0c\x31\x36\x0f"),
    ( INVON, None ),
    ( SLPOUT, None )):
        write(command, data)
utime.sleep_ms( 120 )
write( DISPON )

