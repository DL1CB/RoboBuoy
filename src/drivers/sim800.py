import utime 
from machine import UART

uart = None

def port():
	global uart 
	uart = uart or UART(1, tx=17, rx=16, baudrate=115200, timeout=5000)
	return uart
	
def convert_to_string(buf):
	try:
		tt =  buf.decode('utf-8').strip()
		return tt
	except UnicodeError:
		tmp = bytearray(buf)
		for i in range(len(tmp)):
			if tmp[i]>127:
				tmp[i] = ord('#')
		return bytes(tmp).decode('utf-8').strip()	
	
def cmd( command, read=True):
	result = None
	port().write( command+'\r\n' )
	if read:
		utime.sleep(1)
		buf = port().read()
		if buf:
			result = convert_to_string(buf)
	return result

def AT():
	port().write("AT\r\n")
	return port().read()	

def signalquality():
	"""
	Signal quality test, value range is 0-31 , 31 is the best
	"""
	return cmd( "AT+CSQ" )

def siminfo():
	"""
	Read SIM information to confirm whether the SIM is plugged
	return the IMEI of the SIM 
	"""
	return cmd( "AT+CCID" )

def registerednetwork():
	"""
	Check whether it has registered in the network
	"""
	return cmd( "AT+CREG?" )

def networkname():
	"""
	Checks the network name
	"""
	return cmd( "AT+COPS?" )	

def bearer(APN):
	AT()
	cmd("AT+SAPBR=0,1")
	AT()
	cmd('AT+SAPBR=3,1,"CONTYPE","GPRS"')
	cmd(('AT+SAPBR=3,1,"APN","{}"'.format(APN)))
	cmd("AT+SAPBR=1,1")
	try:
		IP = cmd( "AT+SAPBR=2,1").split()[4].split(",")[-1].replace('"','')
	except:
		IP = None
	return IP

