import serial.tools.list_ports
import sys
ports = serial.tools.list_ports.comports()
port=""
if(len(ports)>1):
    print("Too many ports...limit it to only one!!!")
    sys.exit()
elif(ports==[]):
    print("No device found!")
    sys.exit()
for port, desc, hwid in sorted(ports):
    portuse=port
