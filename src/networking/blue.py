import bluetooth
import ustruct as struct
import uasyncio as asyncio
from micropython import const

from store.ownerinfo import ownerinfo
from store.patroninfo import patroninfo

from drivers.rgb import rgb, off
from drivers.ili9341 import img, brightness, screenColor
from ui.colors.basic import WHITE 

from networking.bencode import encodeTransformer, decodeTransformer

# Bluetooth Configuration Registers
ADV_TYPE_FLAGS = const(0x01)
ADV_TYPE_NAME = const(0x09)
ADV_TYPE_UUID16_COMPLETE = const(0x3)
ADV_TYPE_UUID32_COMPLETE = const(0x5)
ADV_TYPE_UUID128_COMPLETE = const(0x7)
ADV_TYPE_APPEARANCE = const(0x19)

# Bluetooth Event Constants
CENTRAL_CONNECT = const(1)
CENTRAL_DISCONNECT = const(2)
GATTS_WRITE = const(3)

# Nordic UART Service (NUS)
# The Bluetooth LE GATT Nordic UART Service is a custom service that 
# receives and writes data and serves as a bridge to the UART interface.
SERVICE_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")

# Enable notifications for the TX Characteristic to receive data from the application. 
# The application transmits all data that is received over UART as notifications.
TX_Charactaristic = (
    bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY,
)

# Write data to the RX Characteristic to send it on to the UART interface.
RX_Charactaristic = (
    bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    bluetooth.FLAG_WRITE | bluetooth.FLAG_WRITE_NO_RESPONSE,
)

# Service Definition
SERVICE = (
    SERVICE_UUID,
    (TX_Charactaristic, RX_Charactaristic),
)

def advertisement(limited_disc=False, br_edr=False, name=None, services=None, appearance=0):
    """ 
    Generates the bluetooh advertisement payload
    """
    payload = bytearray()

    def _append(adv_type, value):
        nonlocal payload
        payload += struct.pack("BB", len(value) + 1, adv_type) + value

    _append(
        ADV_TYPE_FLAGS,
        struct.pack("B", (0x01 if limited_disc else 0x02) + (0x18 if br_edr else 0x04)),
    )

    if name:
        _append(ADV_TYPE_NAME, name)

    if services:
        for uuid in services:
            b = bytes(uuid)
            if len(b) == 2:
                _append(ADV_TYPE_UUID16_COMPLETE, b)
            elif len(b) == 4:
                _append(ADV_TYPE_UUID32_COMPLETE, b)
            elif len(b) == 16:
                _append(ADV_TYPE_UUID128_COMPLETE, b)

    # See org.bluetooth.characteristic.gap.appearance.xml
    if appearance:
        _append(ADV_TYPE_APPEARANCE, struct.pack("<h", appearance))

    return payload



def connectionHandler( newUserInfoHandler ):
    """
    I report new user info by calling newUserInfoHandler
    I return an eventHandler to be bound to the bluetooth Interrupt handler
    """
    decoder = None

    def eventHandler( event, data ):
        nonlocal decoder

        if event == CENTRAL_CONNECT:
            conn_handle, _, _ = data
            # create decodeTransforer to capture userInof over multiplt 20 byte packets
            decoder = decodeTransformer( newUserInfoHandler , conn_handle)
   
        elif event == CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            decoder = None
            ble.gap_advertise()
            
        elif event == GATTS_WRITE:
            conn_handle, value_handle = data
            if value_handle == rx_characteristic_ref and decoder:
                # handle a userinfo packet of 20 bytes
                decoder( ble.gatts_read( value_handle ) )

    return eventHandler

def newUserInfoHandler( userinfo, conn_handle ):
    print( userinfo )
    asyncio.run(sendOwnerInfo( conn_handle, ownerinfo ))
    asyncio.run(showSuccess()) 

async def sendOwnerInfo( conn_handle, ownerinfo ):
    for chunk in encodeTransformer( 20, ownerinfo ):
        await asyncio.sleep_ms(100)
        ble.gatts_notify(conn_handle, tx_charactaristic_ref, chunk)
   

async def showWelcome():
    brightness(100)
    rgb(0x0000FF)
    img(0, 0, "bitmaps/welcome.jpg")
    await asyncio.sleep(1)
    off()
    img(60, 20, "bitmaps/qrcode.jpg")   

async def showSuccess():
    await asyncio.sleep(1)
    brightness(100)
    rgb(0x00FF00)
    img(60, 20, "bitmaps/success.jpg")
    await asyncio.sleep(1)
    off()
    img(60, 20, "bitmaps/qrcode.jpg")

async def showFail():
    brightness(100)
    rgb(0xFF0000)
    img(60, 20, "bitmaps/fail.jpg")
    await asyncio.sleep(1)
    off()
    img(60, 20, "bitmaps/qrcode.jpg")   


# clear the screen
asyncio.run(showWelcome())

# create and activate bluetooth low enery instance
ble = bluetooth.BLE()
ble.active(True)

# register the service and get the characteristics handler id
((tx_charactaristic_ref, rx_characteristic_ref),) = ble.gatts_register_services((SERVICE,))

eventHandler = connectionHandler( newUserInfoHandler )
ble.irq(eventHandler)

payload = advertisement(name="DigiReg", services=[SERVICE_UUID]) 
ble.gap_advertise(100000, adv_data=payload)


