""" 
A Singleton Instance of the I2C 
all drivers should use this Instance
"""
from machine import I2C, Pin
i2c = I2C(1,scl=Pin(22), sda=Pin(21), freq=400000)  


