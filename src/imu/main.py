from imu.mpu9250 import mag
import utime
while True:
    print("{},{},{}".format(*mag(c)))
    utime.sleep_ms(50)