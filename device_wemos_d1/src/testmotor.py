import d1motor
from machine import I2C, Pin
i2c = I2C(-1,Pin(5), Pin(4), freq=100000)
m0 = d1motor.Motor(0, i2c)
m1 = d1motor.Motor(1, i2c)
m0.speed(5000)  
m1.speed(-5000)  