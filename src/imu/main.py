from mpu9250 import mag
import utime
while True:
    print("{},{},{}".format(*mag()))
    utime.sleep_ms(50)