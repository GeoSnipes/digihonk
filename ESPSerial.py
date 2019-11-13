import sys
from argparse import ArgumentParser
from os import walk

import serial
from time import sleep

class ESPConnect:
    def __init__(self, port, baudrate=115200):
        if sys.platform.startswith('linux'):
            self.port = self.get_device()
            print('[INFO] Linux operating system identified. Port to device: '+self.port)
        elif sys.platform.startswith('win'):
            self.port = port
            print('[INFO] Windows operating system identified. Port to device: '+self.port)
        else:
            print('[ERROR] Operating system could not be identified')
            self.port = None

        self.baudrate = baudrate
        self.espconn = self.estab_connect()
        
        if not self.check_serial_open():
            print('[INFO] Communication port to device could not be opened.')
            quit()
        
        self.flush_serial_inout()
        # print(espconn.get_settings())
        #espconn.setDTR(False)   # will cause reset on comm connection
        self.espconn.setRTS(False)   # will cause esp reset on comm disconnection
    
    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if self.check_serial_open():
            self.close_connect()

    def get_device(self, defL="/dev/"):
        """Automate finding arduino connecting port for linux
        
        param defL: linux, folder where mount points are found (default- /dev/)
        rtype: string
        """

        for _, _, files in walk(defL):
            for mnt_point in files:
                if 'ttyUSB' in mnt_point:
                    picon = defL + mnt_point

        try:
            picon
            return picon
        except NameError:
            return ''

    def estab_connect(self):
        """Establish serial connection with esp

        param port: port connection the device uses (default- linux, folder where mount points are found)
        rtype: Serial object or quit on failure
        """

        try:
            return serial.Serial(self.port, self.baudrate)
        except serial.serialutil.SerialException:
            print(f'[ERROR] SeriaException: could not open connection to ESP on "{self.port}"')
            quit()

    def close_connect(self):
        """Safely close serial connection with device

        rtype: None
        """
        self.espconn.close()

    def check_serial_open(self):
        """Check if serial connection was established and connected

        rtype: bool
        """
        return self.espconn.is_open      

    def flush_serial_inout(self):
        """Flush any input or output from IO buffer

        rtype: None
        """
        sleep(.5)
        self.espconn.flushInput()
        self.espconn.flushOutput()

    def update_beacon_ssid(self, message):
        """Send to serial new SSID device should use

        param message: new ssid to send to device
        rtype: None
        """
        self.espconn.write(message.encode())

    def read_from_esp(self, delay=.5, entire=False):
        """Read from device data received from Serial.print

        param delay: seconds to wait before trying to read
        rtype: str
        """
        if entire:
            delay = 4
        sleep(delay)
        try:
            if self.espconn.inWaiting()>0:
                if entire:
                    return self.espconn.read(self.espconn.inWaiting()).decode().strip()
                return(self.espconn.readline().decode().strip())

        except UnicodeDecodeError:
            print('[INFO] ESP RESET. Cannot Read')
            return None

commPort = "COM23"

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-n', dest='SSID', action='store', help='Get new SSID', default='0:newSSID')
    parser.add_argument('-p', dest='port', action='store', help='Supply port (WIN only)', default=commPort)
    results = parser.parse_args()
    
    results.SSID='1:'
    with ESPConnect(results.port) as serconn:
        if results.SSID.startswith('1:'):
            serconn.update_beacon_ssid(results.SSID)
            print(serconn.read_from_esp(.8, True))
        else: 
            serconn.update_beacon_ssid(results.SSID)
        # print(serconn.read_from_esp())

# with ESPConnect('COM23') as serconn:
#     serconn.update_beacon_ssid('1:00')
#     print(serconn.read_from_esp(entire=True).split('\n'))
    
