

import struct
import ubinascii
import bluetooth
from micropython import const

# bluetooth irq event code
_IRQ_SCAN_RESULT = const(5)

# bluetooth advertisement type code
_ADV_SCAN_IND = const(2) # scannable undirected advertising

def ble_irq_handler(event, data):
    """
    asyncronously binds to the bluetooth stack 
    receives events and data 
    https://docs.micropython.org/en/latest/library/ubluetooth.html
    """

    if event == _IRQ_SCAN_RESULT:

        # A single scan result.
        addr_type, addr, adv_type, rssi, adv_data = data

        # validate the exposure notification advertisement
        if addr_type != 1 : return 
        if adv_type != _ADV_SCAN_IND : return
        if len(adv_data) != 28 : return 
        if struct.unpack('H', adv_data[2:4] ) != (0xfd6f,) : return
        if struct.unpack('H', adv_data[6:8] ) != (0xfd6f,) : return

        print(adv_data)

        serviceUUID_lenght  = adv_data[0]
        serviceUUID_type    = adv_data[1]
        serviceUUID         = adv_data[2:4]

        serviceData_lenght  = adv_data[4]
        serviceData_type    = adv_data[5]
        serviceData_ens     = adv_data[6:8]
        serviceData_rpi     = adv_data[8:24] 
        serviceData_aemKey  = adv_data[24:28] 

        print( 'addr',               ubinascii.hexlify( addr ))
        print( 'rssi',               rssi )
        print( 'serviceData_ens',    ubinascii.hexlify( serviceData_ens ))
        print( 'serviceData_rpi', ubinascii.hexlify( serviceData_rpi ))
        print( 'serviceData_aemKey', ubinascii.hexlify( serviceData_aemKey ))

 



def start_advertising( rpi, ame ):
    """
    Start the bluetooth stack, bind the irqhandler, scan indefinitely
    Bytes: rpi - Rolling Proximity Identifier
    Bytes: aem - Associated Encrypted Metadata
    """

    assert type(rpi) is bytes , "expecting rpi of type bytes" 
    assert type(ame) is bytes , "expecting ame of type bytes" 
    assert len(rpi) == 16 , "expecting rpi lenght of 16"
    assert len(ame) == 4  , "expecting ame lenght of 16"

    # get a reference to the bluetooth singleton
    ble = bluetooth.BLE()

    # Activate ESP32's Bluetooth module
    while not ble.active():
        ble.active(True)

    adv_data = b'\x03\x03o\xfd\x17\x16o\xfd' + rpi + ame

    print('adv_data', adv_data)
    print('adv_data', ubinascii.hexlify( adv_data ))

    interval_us = 625 * 1000

    print( 'advertising every %i microseconds' % interval_us)

    ble.gap_advertise(interval_us, adv_data=adv_data)


def stop_advertising(y ):

    # get a reference tothe bluetooth singleton
    ble = bluetooth.BLE()
    # stop advertising
    ble.gap_advertise(None)



def start_listening():
    """
    Start the bluetooth stack, bind the irqhandler, scan indefinitely
    """
    ble = bluetooth.BLE()
    
    received = ble.irq(ble_irq_handler)
    print(received, "HERE I AM")
    
    # Activate ESP32's Bluetooth module
    while not ble.active():
        ble.active(True)
    
    # Scan continuously (at 100% duty cycle)
    ble.gap_scan(0, 30000, 30000)

    print('listening')

def stop_listening():
    """
    Stop the bluetooth stack, unbind the irqhandler
    """
    ble = bluetooth.BLE()
    ble.active(False)


