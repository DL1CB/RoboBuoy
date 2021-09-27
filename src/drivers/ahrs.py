
import utime
import uasyncio
from struct import pack, unpack
from math import atan2, asin, degrees, sqrt, radians
from store.ahrs import accelbias, magbias, save

class AHRS(object):
    '''
    Class provides 9-DOF sensor fusion for the MPU6050 allowing yaw, pitch and roll and quaternion to be extracted. 
    This uses the Madgwick algorithm.
    '''

    def __init__( self, i2c ):

        self.accelSSF = 16384
        self.gyroSSF = 131
        self.declination = 0   # Optional offset for true north. A +ve value adds to heading
        
        aelf.accelbias = accelbias()
        self.magbias = magbias()
        
        #self.magbias =  (45.9844, -21.3047, 43.5039, 57.375, 45.3516, 43.5039, 0.84956, 1.07479, 1.12044)

        GyroMeasError = radians(40)         # Original code indicates this leads to a 2 sec response time
        self.beta = sqrt(3.0 / 4.0) * GyroMeasError  # compute beta (see README)
        self.startTime = None

        self.q = [1.0, 0.0, 0.0, 0.0]       # vector to hold quaternion

        self.pitch = 0
        self.yaw = 0
        self.roll = 0

        self.accel = (0,0,0)
        self.gyro = (0,0,0)
        self.mag = (0,0,0)
        
        self.i2c = i2c 

        self.initMag()
        self.initAccel(fullScaleRange=0)
        self.gyrofullScaleRange(fullScaleRange = 0)
        self.gyroLowPassFilter(bandwidth = 6)


    def initMag( self ):
        # Directly access the magnetomoeter via I2C BYPASS mode
        try:
            self.i2c.writeto_mem(0x69, 0x6B, b'\x80') #PWR_MGMT_1 = H_RESET # Rest the MPU6050
            self.i2c.writeto_mem(0x69, 0x6A, b'\x00') #USER_CTRL_AD = I2C_MST = 0x00 disable i2c master
            self.i2c.writeto_mem(0x69, 0x37, b'\x02') #INT_PIN_CFG = BYPASS[1]
        except OSError as e:
            print('please check the MPU9250 I2C wiring ')

        # Read the Factory set Magntometer Sesetivity Adjustments
        self.i2c.writeto_mem(0x0C, 0x0A, b'\x1F') #CNTL1 Fuse ROM mode
        utime.sleep_ms(100) # Settle Time

        # Read factory calibrated sensitivity constants
        asax, asay, asaz = unpack('<bbb',self.i2c.readfrom_mem(0x0C, 0x10, 3)) 

        # Calculate the Magnetometer Sesetivity Adjustments
        self.asax = (((asax-128)*0.5)/128)+1
        self.asay = (((asay-128)*0.5)/128)+1
        self.asaz = (((asaz-128)*0.5)/128)+1

        # Set Register CNTL1 to 16-bit output, Continuous measurement mode 100Hz
        self.i2c.writeto_mem(0x0C, 0x0A, b'\x16') 

    def initAccel( self, fullScaleRange=0 ):
        '''
        Sets and reads the Accelerometers operating range and low pass filter frequencies
        fullScaleRange: 0,1,2,3 => +-2g,+-4g,+-8g,+-16g
        returns fullScaleRange
        ''' 
        if fullScaleRange != None and fullScaleRange in [0,1,2,3]:
            self.i2c.writeto_mem(0x69, 0x1C, pack('b',
            (self.i2c.readfrom_mem(0x69, 0x1C, 1)[0] & ~24) | fullScaleRange << 3
            ))

            # pick the accelerometer Sensitivity Scale Factor    
            self.accelSSF = 16834 #[16384,8192,4096,2048][fullScaleRange] 
    
        return (self.i2c.readfrom_mem(0x69, 0x1C, 1)[0] & 24) >> 3 

    def readAccel( self ):
        """
        return tuple of accelerations (x,y,z)
        """
        x,y,z = unpack('>hhh',self.i2c.readfrom_mem(0x69, 0x3B, 6)) 

        x = x / self.accelSSF
        y = y / self.accelSSF
        z = z / self.accelSSF

        return x,y,z


    def meanAccel( self, samples=10, delay=10):
        
        ox, oy, oz = 0.0, 0.0, 0.0
        n = float(samples)

        while samples:
            utime.sleep_ms(delay)
            gx, gy, gz = self.readAccel()
            ox += gx
            oy += gy
            oz += gz
            samples -= 1

        # mean accel values
        ox,oy,oz = ox / n, oy / n, oz / n

        return ox,oy,oz     

    def readGyro( self ):
        """
        return tuple of degrees per second (x,y,z)
        """
        x,y,z = unpack('>hhh',self.i2c.readfrom_mem(0x69, 0x43, 6)) 
        x = x / self.gyroSSF
        y = y / self.gyroSSF
        z = z / self.gyroSSF

        return x,y,z 

    def gyrofullScaleRange(self, fullScaleRange=None ):
        """    
        Sets and reads the Gyro full scal operting range
        fullScaleRange: 0,1,2,3 => +-250, +-500, +-1000, +-2000 degrees/second  
        """
        if fullScaleRange != None and fullScaleRange in [0,1,2,3]:
            self.i2c.writeto_mem(0x69, 0x1B, pack('b',
            (self.i2c.readfrom_mem(0x69, 0x1B, 1)[0] & ~24) | fullScaleRange << 3
            ))

            # pick the gyro Sensitivity Scale Factor    
            self.gyroSSF = 131 #[131,65.5,32.8,16.4][fullScaleRange] 

        return (self.i2c.readfrom_mem(0x69, 0x1B, 1)[0] & 24) >> 3 

    def gyroLowPassFilter(self, bandwidth=None ):
        """    
        Sets and reads the Gyro operating range and low pass filter frequencies
        bandwidth: 0,1,2,3,4,5,6,7 => 250Hz, 184Hz, 92Hz, 41Hz, 20Hz, 10Hz, 5Hz, 3600Hz
        """
        if bandwidth and bandwidth in [0,1,2,3,4,5,6,7]:
            self.i2c.writeto_mem(0x69, 0x1A, pack('b',
            (self.i2c.readfrom_mem(0x69, 0x1A, 1)[0] & ~7 ) | bandwidth
            ))

        return self.i2c.readfrom_mem(0x69, 0x1A, 1)[0] & 7   


    def readMag( self, bias=(0,0,0,1,1,1,1,1,1) ):
        
        DRDY = self.i2c.readfrom_mem(0x0C, 0x02, 1)[0] & 0x01
 
        if DRDY != 0x01 : # Data is ready
            raise Exception()

        # Correct the orentation of the magnetometer to align with the accelermeter and gyro
        y,x,z = unpack('<hhh',self.i2c.readfrom_mem(0x0C, 0x03, 6))  
        z = -1 * z

        HOFL = self.i2c.readfrom_mem(0x0C, 0x09, 1)[0] & 0x08

        # apply the Factory Magentometer Sensetivity adjustment
        x,y,z = x * self.asax, y * self.asay , z * self.asaz

        # calibrate
        x,y,z = x - bias[0], y - bias[1], z - bias[2]

        # normalize
        x,y,z = x / bias[3], y / bias[4], z / bias[5]

        # scale
        x,y,z = x * bias[6], y * bias[7], z * bias[8]

        return x,y,z





    def calibrateMag( self, samples=800, delay=10 ):
        '''
        Creates a tuple of magbias
        During the calibration rotate the gyro in all directions
        '''
        print("calibrate magnetmeter, by waving it around in a figure of 8")
        minx = 0
        maxx = 0
        miny = 0
        maxy = 0
        minz = 0
        maxz = 0

        while samples :

            samples = samples - 1
            try:
                x,y,z = self.readMag()  
                minx = min(x,minx)
                maxx = max(x,maxx)
                miny = min(y,miny)
                maxy = max(y,maxy)
                minz = min(z,minz)
                maxz = max(z,maxz)
            except Exception:
                pass
        
            print(x,y,z)
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


        self.magbias = (cx, cy, cz ,nx, ny, nz, sx, sy, sz)
        magbias(self.magbias)
        save()

        print("magbias saved")

        return cx, cy, cz ,nx, ny, nz, sx, sy, sz

    def deltat( self):
        '''
        Calculates for the differince in time between updates to the Madwicks algorythm
        it drives the Integration to produce the quaternian
        '''
        currentTime = utime.ticks_us()

        if self.startTime is None:
            self.startTime = currentTime
            return 0.0001  # 100μs notional delay. 1st reading is invalid in any case

        dt =  utime.ticks_diff(currentTime,self.startTime  )/1000000
        self.startTime = currentTime
        return dt

    def fusion(self, accel, gyro, mag ): # 3-tuples (x, y, z) for accel, gyro and mag data
        mx, my, mz = mag # Units irrelevant (normalised)
        ax, ay, az = accel # Units irrelevant (normalised)
        gx, gy, gz = (radians(x) for x in gyro)  # Units deg/s
        q1, q2, q3, q4 = (self.q[x] for x in range(4))   # short name local variable for readability
        # Auxiliary variables to avoid repeated arithmetic
        _2q1 = 2 * q1
        _2q2 = 2 * q2
        _2q3 = 2 * q3
        _2q4 = 2 * q4
        _2q1q3 = 2 * q1 * q3
        _2q3q4 = 2 * q3 * q4
        q1q1 = q1 * q1
        q1q2 = q1 * q2
        q1q3 = q1 * q3
        q1q4 = q1 * q4
        q2q2 = q2 * q2
        q2q3 = q2 * q3
        q2q4 = q2 * q4
        q3q3 = q3 * q3
        q3q4 = q3 * q4
        q4q4 = q4 * q4

        # Normalise accelerometer measurement
        norm = sqrt(ax * ax + ay * ay + az * az)
        if (norm == 0):
            return # handle NaN
        norm = 1 / norm                     # use reciprocal for division
        ax *= norm
        ay *= norm
        az *= norm

        # Normalise magnetometer measurement
        norm = sqrt(mx * mx + my * my + mz * mz)
        if (norm == 0):
            return                          # handle NaN
        norm = 1 / norm                     # use reciprocal for division
        mx *= norm
        my *= norm
        mz *= norm

        # Reference direction of Earth's magnetic field
        _2q1mx = 2 * q1 * mx
        _2q1my = 2 * q1 * my
        _2q1mz = 2 * q1 * mz
        _2q2mx = 2 * q2 * mx
        hx = mx * q1q1 - _2q1my * q4 + _2q1mz * q3 + mx * q2q2 + _2q2 * my * q3 + _2q2 * mz * q4 - mx * q3q3 - mx * q4q4
        hy = _2q1mx * q4 + my * q1q1 - _2q1mz * q2 + _2q2mx * q3 - my * q2q2 + my * q3q3 + _2q3 * mz * q4 - my * q4q4
        _2bx = sqrt(hx * hx + hy * hy)
        _2bz = -_2q1mx * q3 + _2q1my * q2 + mz * q1q1 + _2q2mx * q4 - mz * q2q2 + _2q3 * my * q4 - mz * q3q3 + mz * q4q4
        _4bx = 2 * _2bx
        _4bz = 2 * _2bz

        # Gradient descent algorithm corrective step
        s1 = (-_2q3 * (2 * q2q4 - _2q1q3 - ax) + _2q2 * (2 * q1q2 + _2q3q4 - ay) - _2bz * q3 * (_2bx * (0.5 - q3q3 - q4q4)
             + _2bz * (q2q4 - q1q3) - mx) + (-_2bx * q4 + _2bz * q2) * (_2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my)
             + _2bx * q3 * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz))

        s2 = (_2q4 * (2 * q2q4 - _2q1q3 - ax) + _2q1 * (2 * q1q2 + _2q3q4 - ay) - 4 * q2 * (1 - 2 * q2q2 - 2 * q3q3 - az)
             + _2bz * q4 * (_2bx * (0.5 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx) + (_2bx * q3 + _2bz * q1) * (_2bx * (q2q3 - q1q4)
             + _2bz * (q1q2 + q3q4) - my) + (_2bx * q4 - _4bz * q2) * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz))

        s3 = (-_2q1 * (2 * q2q4 - _2q1q3 - ax) + _2q4 * (2 * q1q2 + _2q3q4 - ay) - 4 * q3 * (1 - 2 * q2q2 - 2 * q3q3 - az)
             + (-_4bx * q3 - _2bz * q1) * (_2bx * (0.5 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx)
             + (_2bx * q2 + _2bz * q4) * (_2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my)
             + (_2bx * q1 - _4bz * q3) * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz))

        s4 = (_2q2 * (2 * q2q4 - _2q1q3 - ax) + _2q3 * (2 * q1q2 + _2q3q4 - ay) + (-_4bx * q4 + _2bz * q2) * (_2bx * (0.5 - q3q3 - q4q4)
              + _2bz * (q2q4 - q1q3) - mx) + (-_2bx * q1 + _2bz * q3) * (_2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my)
              + _2bx * q2 * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz))

        norm = 1 / sqrt(s1 * s1 + s2 * s2 + s3 * s3 + s4 * s4)    # normalise step magnitude
        s1 *= norm
        s2 *= norm
        s3 *= norm
        s4 *= norm

        # Compute rate of change of quaternion
        qDot1 = 0.5 * (-q2 * gx - q3 * gy - q4 * gz) - self.beta * s1
        qDot2 = 0.5 * ( q1 * gx + q3 * gz - q4 * gy) - self.beta * s2
        qDot3 = 0.5 * ( q1 * gy - q2 * gz + q4 * gx) - self.beta * s3
        qDot4 = 0.5 * ( q1 * gz + q2 * gy - q3 * gx) - self.beta * s4


        dt = self.deltat()
        # Integrate to yield quaternion
        q1 += qDot1 * dt
        q2 += qDot2 * dt
        q3 += qDot3 * dt
        q4 += qDot4 * dt

        # normalise quaternion
        norm = 1 / sqrt(q1 * q1 + q2 * q2 + q3 * q3 + q4 * q4)    
        self.q = q1 * norm, q2 * norm, q3 * norm, q4 * norm

        self.yaw = self.declination + degrees(atan2(2.0 * (self.q[1] * self.q[2] + self.q[0] * self.q[3]),
            self.q[0] * self.q[0] + self.q[1] * self.q[1] - self.q[2] * self.q[2] - self.q[3] * self.q[3]))

        self.pitch = degrees(-asin(2.0 * (self.q[1] * self.q[3] - self.q[0] * self.q[2])))

        self.roll = degrees(atan2(2.0 * (self.q[0] * self.q[1] + self.q[2] * self.q[3]),
            self.q[0] * self.q[0] - self.q[1] * self.q[1] - self.q[2] * self.q[2] + self.q[3] * self.q[3]))


    def dofusion( self ):
        while True:
            try:
                accel = self.readAccel()
                gyro = self.readGyro()
                mag = self.readMag(self.magbias)
                self.fusion( accel, gyro, mag )
                print("w{}wa{}ab{}bc{}c".format(self.q[0],self.q[1],self.q[2],self.q[3]))
            except Exception:
                pass
            
    # async tasks

    def heading( self ):
        while True:
            try:
                x,y,z = self.readMag(self.magbias)
                print( degrees(atan2(y, x)) )
            except Exception:
                pass
          
    async def fusionTask( self ):
        while True:
            try:
                self.mag = self.readMag(self.magbias)
                self.accel = self.readAccel()
                self.gyro = self.readGyro()
                self.fusion( self.accel, self.gyro, self.mag )
                print("w{}wa{}ab{}bc{}c".format(self.q[0],self.q[1],self.q[2],self.q[3]))
            except Exception:
                pass
            await uasyncio.sleep_ms(0)

