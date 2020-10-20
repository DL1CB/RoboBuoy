import utime
from machine import Pin, I2C
from struct import pack,unpack
from math import atan2, degrees

i2c = I2C(scl=Pin(14), sda=Pin(12), freq=100000)

# Directly access the magnetomoeter via I2C BYPASS mode
i2c.writeto_mem(0x68, 0x6B, b'\x80') #PWR_MGMT_1 = H_RESET # Rest the MPU6050
i2c.writeto_mem(0x68, 0x6A, b'\x00') #USER_CTRL_AD = I2C_MST = 0x00 disable i2c master
i2c.writeto_mem(0x68, 0x37, b'\x02') #INT_PIN_CFG = BYPASS[1]

# Read the Factory set Magntometer Sesetivity Adjustments
i2c.writeto_mem(0x0C, 0x0A, b'\x1F') #CNTL1 Fuse ROM mode
utime.sleep_ms(100) # Settle Time
asax, asay, asaz = unpack('<bbb',i2c.readfrom_mem(0x0C, 0x10, 3)) 

# Calculate the Magntometer Sesetivity Adjustments
asax = (((asax-128)*0.5)/128)+1
asay = (((asay-128)*0.5)/128)+1
asaz = (((asaz-128)*0.5)/128)+1

#CNTL1 = 16-bit output, Continuous measurement mode 100Hz
i2c.writeto_mem(0x0C, 0x0A, b'\x16') 


def gyro():
    pass

def mag( calibration=(0,0,0,1,1,1,1,1,1) ):
    
    DRDY = i2c.readfrom_mem(0x0C, 0x02, 1)[0] & 0x01
    
    # two’s complement and Little Endian format. 
    # -32760 ~ 32760 in 16-bit output.
    x,y,z = unpack('<hhh',i2c.readfrom_mem(0x0C, 0x03, 6))  
    
    HOFL = i2c.readfrom_mem(0x0C, 0x09, 1)[0] & 0x08

    # apply the Factory Magentometer Sensetivity adjustment
    x,y,z = x * asax, y * asay ,z * asaz

    # apply calibration
    x,y,z = x - calibration[0], y - calibration[1], z - calibration[2]

    # apply normalisation
    x,y,z = x / calibration[3], y / calibration[4], z / calibration[5]

    # apply scale
    #x,y,z = x * calibration[6], y * calibration[7], z * calibration[8]

    return x,y,z

def calibrate( count=200, delay=50 ):

    minx = 0
    maxx = 0
    miny = 0
    maxy = 0
    minz = 0
    maxz = 0

    while count :

        count = count - 1

        x,y,z = mag()  

        minx = min(x,minx)
        maxx = max(x,maxx)
        miny = min(y,miny)
        maxy = max(y,maxy)
        minz = min(z,minz)
        maxz = max(z,maxz)
        
        utime.sleep_ms(delay)

    cx = (maxx + minx) / 2
    cy = (maxy + miny) / 2  
    cz = (maxz + minz) / 2  

    nx = abs(maxx - cx)
    ny = abs(maxy - cy)
    nz = abs(maxz - cz)

    # Soft iron correction
    avg_delta_x = (maxx - minx) / 2
    avg_delta_y = (maxy - miny) / 2
    avg_delta_z = (maxz - minz) / 2

    avg_delta = (avg_delta_x + avg_delta_y + avg_delta_z) / 3
    
    sx = avg_delta / avg_delta_x
    sy = avg_delta / avg_delta_y
    sz = avg_delta / avg_delta_z

    print("offset",cx,cy,cz)
    print("normalisation",nx,ny,nz)
    print("scale",sx,sy,sz)

    return cx, cy, cz ,nx, ny, nz, sx, sy, sz

def heading(x,y,z):
    return degrees(atan2(y,x))

def show(c):
    while True:
        print(heading(*mag(c)))
        utime.sleep_ms(100)

