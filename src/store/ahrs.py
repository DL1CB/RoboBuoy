
"""
This stores the AHRS state of the device
"""

ahrs = {
    "magbias":(20.03906, -23.30859, 17.7207, 48.9375, 54.10547, 36.19727, 0.9484222, 0.8578321, 1.282235),
    "accelbias":(0,0,1)
}

# mutations

def accelbias( *argv ):
    if len(argv):
        ahrs["accelbias"] = argv[0]
    return ahrs["accebias"]

def magbias( *argv ):
    if len(argv):
        ahrs["magbias"] = argv[0]
    return ahrs["magbias"]

def save( filename='ahrs.json' ):
    """write ahrs to flash"""
    import json
    with open(filename, 'w') as file:
        json.dump(ahrs, file)

def load( filename='ahrs.json' ):
    """load ahrs set from flash"""
    import json 
    try:
        with open(filename, 'r') as file:
            global ahrs
            ahrs = json.load(file)
    except Exception :
        pass

load() # the ahrs set from flash, when the library is first called