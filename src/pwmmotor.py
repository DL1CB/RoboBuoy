import machine

rightfwd = machine.PWM(machine.Pin(5), freq=1000)   #D1
rightrev = machine.PWM(machine.Pin(4), freq=1000)   #D2
leftrev = machine.PWM(machine.Pin(0), freq=1000)  #D3
leftfwd = machine.PWM(machine.Pin(2), freq=1000)  #D4

# stop
rightfwd.duty(1023)
rightrev.duty(1023)
leftfwd.duty(1023)
leftrev.duty(1023)
