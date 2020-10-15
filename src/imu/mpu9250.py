


#https://github.com/Intelligent-Vehicle-Perception/MPU-9250-Sensors-Data-Collect
#https://github.com/simondlevy/USFS/tree/master/extras/python
#https://github.com/anders-p/MPU9250-sensorfusion


from machine import Pin, I2C
from struct import pack,unpack

i2c = I2C(scl=Pin(14), sda=Pin(12), freq=100000)

def init():
    # Rest the MPU6050
    i2c.writeto_mem(0x68, 0x6B, b'\x80') #PWR_MGMT_1 = H_RESET

    # Directly access the magnetomoeter via MU9250 enable BYPASS mode
    i2c.writeto_mem(0x68, 0x37, b'\x02') #INT_PIN_CFG = BYPASS[1]
    i2c.writeto_mem(0x0C, 0x0A, b'\x16') #CNTL1 = 16-bit output, Continuous measurement mode 100Hz

def temp():
    return unpack('>H',i2c.readfrom_mem(0x68, 0x41, 2))[0] 

def accel():
    """
    return tuple of accelerations (x,y,z)
    """
    return unpack('>hhh',i2c.readfrom_mem(0x68, 0x3B, 6)) 

def accel_offset():
    return unpack('>hhh',i2c.readfrom_mem(0x68, 0x77, 6))      

def accel_selftest():
    """ 
    self test output generated during manufacturing tests
    return tuple (x,y,z) 
    """
    return unpack('>BBB',i2c.readfrom_mem(0x68, 0x0D, 3))        

def gyro():
    """
    return tuple of radians (x,y,z)
    """
    return unpack('>hhh',i2c.readfrom_mem(0x68, 0x43, 6)) 

def gyro_offset(offset=None):
    """
    offset List [x,y,z]
    returns tuple ( X,Y,Z )
    """
    if offset and len(offset) == 3:
        i2c.writeto_mem(0x68, 0x13, pack('>HHH',*offset))
    return unpack('>hhh',i2c.readfrom_mem(0x68, 0x13, 6)) 

def gyro_selftest():
    """ 
    self test output generated during manufacturing tests
    return tuple (x,y,z) 
    """
    return unpack('>BBB',i2c.readfrom_mem(0x68, 0x00, 3))         


def mag():
    """
    return tuple of radians (x,y,z)
    """
    return unpack('<hhh',i2c.readfrom_mem(0x0C, 0x00, 6))  #two’s complement and Little Endian format.