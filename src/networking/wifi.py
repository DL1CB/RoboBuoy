import network 
from store.wifi import ssid, password
# join a wifi access point
def joinwifi():
    """ join a wifi access point """
    station = network.WLAN(network.STA_IF) # initiate a station mode

    if not station.isconnected():
            print('connecting to network:', ssid())
            station.active(True)
            station.connect(ssid(), password())
         

            while not station.isconnected():
                pass

    # deactivating access point mode
    ap = network.WLAN(network.AP_IF)
    ap.active(False)

    ip = station.ifconfig()[0]
    print('connected as:', ip)

    return ip
