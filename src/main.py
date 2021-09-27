#from ui.router import transition
#import networking.blue

import uasyncio as asyncio
from drivers.i2c import i2c
from drivers.ahrs import AHRS
from store.ahrs import magbias
print("RoboBuoy V0.0 Dev")

ahrs = AHRS(i2c=i2c)

#ahrs.dofusion()

async def main():
    asyncio.create_task(ahrs.fusionTask())
    
    await asyncio.sleep_ms(20000)

asyncio.run(main())