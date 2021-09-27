import utime
from machine import Pin, I2C
from struct import pack, unpack
from math import atan2, degrees
# Author: Chris Bentley ... incase you forgot you wrote this LOL

i2c = I2C(scl=Pin(14), sda=Pin(12), freq=400000)

# Directly access the magnetomoeter via I2C BYPASS mode
try:
    i2c.writeto_mem(0x68, 0x6B, b'\x80') #PWR_MGMT_1 = H_RESET # Rest the MPU6050
    i2c.writeto_mem(0x68, 0x6A, b'\x00') #USER_CTRL_AD = I2C_MST = 0x00 disable i2c master
    i2c.writeto_mem(0x68, 0x37, b'\x02') #INT_PIN_CFG = BYPASS[1]
except OSError as e:
    print('please check imu wiring')

# Read the Factory set Magntometer Sesetivity Adjustments
i2c.writeto_mem(0x0C, 0x0A, b'\x1F') #CNTL1 Fuse ROM mode
utime.sleep_ms(100) # Settle Time

# Read factory calibrated sensitivity constants
asax, asay, asaz = unpack('<bbb',i2c.readfrom_mem(0x0C, 0x10, 3)) 

# Calculate the Magnetometer Sesetivity Adjustments
asax = (((asax-128)*0.5)/128)+1
asay = (((asay-128)*0.5)/128)+1
asaz = (((asaz-128)*0.5)/128)+1

# Set Register CNTL1 to 16-bit output, Continuous measurement mode 100Hz
i2c.writeto_mem(0x0C, 0x0A, b'\x16') 

# TODO is not accurate :-o
def temp():
    """
    return the temperature in degrees celcius
    """
    t = unpack('>H',i2c.readfrom_mem(0x68, 0x41, 2))[0]
    t = ((t-21) / 333.87) + 21
    return t


# Accelerometer 
# accelFS:  full-scale range of ±2g (accelFS = 0), ±4g (accelFS = 1), ±8g (accelFS = 2), and ±16g (accelFS = 3)
# accelSSF: sensitivity scale factor 16.384 (accelSSF = 0), 8.192 (accelSSF = 1), 4.096 (accelSSF = 2), 2.048 (accelSSF = 3) LSB/g
# accelLPF: 

 

def accelInit(accelFS = 0):
    accelfullScaleRange(accelFS)

    
def accelfullScaleRange( fullScaleRange=None ):
    """    
    Sets and reads the Gyro operating range and low pass filter frequencies
    fullScaleRange:
        0 is +-2g
        1 is +-4g
        2 is +-8g
        3 is +-16g
    """
    if fullScaleRange != None and fullScaleRange in [0,1,2,3]:
        i2c.writeto_mem(0x68, 0x1C, pack('b',
         (i2c.readfrom_mem(0x68, 0x1C, 1)[0] & ~24) | fullScaleRange << 3
        ))
    return (i2c.readfrom_mem(0x68, 0x1C, 1)[0] & 24) >> 3 


def accel():
    """
    return tuple of accelerations (x,y,z)
    """
    x,y,z = unpack('>hhh',i2c.readfrom_mem(0x68, 0x3B, 6)) 

    x = x / 16384
    y = y / 16384
    z = z / 16384

    return x,y,z

def accelMean(samples=10, delay=10):
    
    ox, oy, oz = 0.0, 0.0, 0.0
    n = float(samples)

    while samples:
        utime.sleep_ms(delay)
        gx, gy, gz = accel()
        ox += gx
        oy += gy
        oz += gz
        samples -= 1

    # mean gyro values
    ox,oy,oz = int(ox // n), int(oy // n), int(oz // n)

    return ox,oy,oz     

def accelOffset(offset=None):
    if offset and len(offset) == 3:
        i2c.writeto_mem(0x68, 0x77, pack('>HHH',*offset))
    return unpack('>hhh',i2c.readfrom_mem(0x68, 0x77, 6))  

def accelCalibrate(samples=256, delay=50):
    """
    calculates the gyro offset
    wites the gyro offset to the mpu9250
    the mpu9250 will subtract the offset internally
    """

    # clear the offset so it does not become part of the calibration
    accelOffset( (0,0,0) ) 

    # mean gyro values
    ox,oy,oz = accelMean( samples, delay )

    # negate and devide by 8 for the offset. not sure why is div 8
    ox,oy,oz = -ox//8, -oy//8 , -oz//8
    
    accelOffset( (ox,oy,oz) )

    return ox,oy,oz        

  
# Gyro 
# full-scale range of ±250 (gyroFS = 0), ±500 (gyroFS = 1), ±1000 (gyroFS = 2), and ±2000 (gyroFS = 3) °/sec (dps)
# sensitivity scale factor of 131 (gyroSSF = 0), 65.5 (gyroSSF = 1), 32.8 (gyroSSF = 2), 16.4 (gyroSSF = 3 ) LSB/(º/s)
# low-pass filter 

def gyroInit(gyroFS = 0, gyroLPF = 6):
    gyrofullScaleRange(gyroFS)
    gyroLowPassFilter(gyroLPF)
    #gyroMean()
    #return gyroCalibrate()

def gyro( calibration=(0,0,0) ):
    """
    return tuple of radians (x,y,z)
    """
    x,y,z = unpack('>hhh',i2c.readfrom_mem(0x68, 0x43, 6)) 

    x = x // 131
    y = y // 131
    z = z // 131

    # apply calibration
    x,y,z = x - calibration[0], y - calibration[1], z - calibration[2]

    return x,y,z

def gyroMean(samples=10, delay=10):
    ox, oy, oz = 0.0, 0.0, 0.0
    n = float(samples)

    while samples:
        utime.sleep_ms(delay)
        gx, gy, gz = gyro()
        ox += gx
        oy += gy
        oz += gz
        samples -= 1

    # mean gyro values
    ox,oy,oz = int(ox // n), int(oy // n), int(oz // n)

    return ox,oy,oz    

def gyroOffset(offset=None):
    """
    Sets and reads the Gyro Offset
    offset List [x,y,z]
    returns tuple ( X,Y,Z )
    """
    if offset and len(offset) == 3:
        i2c.writeto_mem(0x68, 0x13, pack('>HHH',*offset))
    return unpack('>hhh',i2c.readfrom_mem(0x68, 0x13, 6)) 

    
def gyroCalibrate(samples=256, delay=50):
    """
    calculates the gyro offset
    writes the gyro offset to the mpu9250
    the mpu9250 will add the offset internally
    """

    # clear the offset so it does not become part of the calibration
    gyroOffset( (0,0,0) ) 

    # mean gyro values
    ox,oy,oz = gyroMean( samples, delay )

    # negate and devide by 4 for the offset. not sure why its div 4
    ox,oy,oz = -ox//4, -oy//4 , -oz//4
    
    gyroOffset( (ox,oy,oz) )

    return ox,oy,oz

def gyrofullScaleRange( fullScaleRange=None ):
    """    
    Sets and reads the Gyro operating range and low pass filter frequencies
    fullScaleRange:
        0 is +-250  degrees/second
        1 is +-500  degrees/second 
        2 is +-1000 degrees/second 
        3 is +-2000 degrees/second  
    """
    if fullScaleRange != None and fullScaleRange in [0,1,2,3]:
        i2c.writeto_mem(0x68, 0x1B, pack('b',
         (i2c.readfrom_mem(0x68, 0x1B, 1)[0] & ~24) | fullScaleRange << 3
        ))
    return (i2c.readfrom_mem(0x68, 0x1B, 1)[0] & 24) >> 3 

def gyroLowPassFilter( bandwidth=None ):
    """    
    Sets and reads the Gyro operating range and low pass filter frequencies
    bandwidth:
        0 is 250Hz
        1 is 184Hz
        2 is  92Hz
        3 is  41Hz
        4 is  20Hz
        5 is  10Hz
        6 is  5Hz
        7 is  3600Hz
    """
    if bandwidth and bandwidth in [0,1,2,3,4,5,6,7]:
        i2c.writeto_mem(0x68, 0x1A, pack('b',
        (i2c.readfrom_mem(0x68, 0x1A, 1)[0] & ~7 ) | bandwidth
        ))
    return i2c.readfrom_mem(0x68, 0x1A, 1)[0] & 7
  
def mag( calibration=(0,0,0,1,1,1,1,1,1) ):
    
    DRDY = i2c.readfrom_mem(0x0C, 0x02, 1)[0] & 0x01
    
    # two’s complement and Little Endian format. 
    # -32760 ~ 32760 in 16-bit output.
    #x,y,z = unpack('<hhh',i2c.readfrom_mem(0x0C, 0x03, 6))  

    y,x,z = unpack('<hhh',i2c.readfrom_mem(0x0C, 0x03, 6))  
    
    z = -1 * z

    HOFL = i2c.readfrom_mem(0x0C, 0x09, 1)[0] & 0x08

    # apply the Factory Magentometer Sensetivity adjustment
    x,y,z = x * asax, y * asay , z * asaz

    # apply calibration
    x,y,z = x - calibration[0], y - calibration[1], z - calibration[2]

    # apply normalisation
    x,y,z = x / calibration[3], y / calibration[4], z / calibration[5]

    # apply scale
    x,y,z = x * calibration[6], y * calibration[7], z * calibration[8]

    return x,y,z

def magCalibrate( samples=200, delay=50 ):

    minx = 0
    maxx = 0
    miny = 0
    maxy = 0
    minz = 0
    maxz = 0

    while samples :

        samples = samples - 1

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

def magToHeading(x,y,z):
    """
    converts magentometer x and y cartesian coordinates to a Heading in degrees
    """
    return degrees(atan2(y,x))

def showHeading(c):
    """
    continously shows the magnetic heading in degrees
    """
    while True:
        print( magToHeading(*mag(c)))
        utime.sleep_ms(100)

def showGyro(c):
    """
    continously shows the Gyro cartesain coordinates
    """
    while True:
        print( gyro(c) )
        utime.sleep_ms(100)
