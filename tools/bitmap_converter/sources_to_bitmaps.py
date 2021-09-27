import os
from PIL import Image
from struct import pack



def bmptobitmap( sourcefilename ):
    img = Image.open("./sources/"+sourcefilename)
    width, height = img.size
    with open('./bitmaps/'+sourcefilename,'wb') as f:
        f.write( pack(">HH", width, height ))
        for pixel in img.getdata():
            f.write( pack(">H", (((pixel[0] & 0x00F8) << 8) | (( pixel[1] & 0x00FC) << 3) | ((pixel[2] & 0x00F8) >> 3)) ) )

sources = os.listdir('./sources')

for sourcefilename in os.listdir('./sources'):
    print("converting ", sourcefilename)
    bmptobitmap( sourcefilename )            
