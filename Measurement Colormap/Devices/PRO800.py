import serial
import time

class PRO800Error(Exception):
	def __init__(self, string):
		self.string = string		

	def __str__(self):
		return self.string

class PRO800(object):

    _port = None
    _smcID = None

    _silent = True

    _sleepfunc = time.sleep

    def __init__(self, pro800ID, port , slot, silent=True, sleepfunc=None):
        super(PRO800, self).__init__()
        
        assert port is not None
        assert pro800ID is not None
        if sleepfunc is not None:
            self._sleepfunc = sleepfunc
        self._silent = silent
        self._port = port
        self._last_sendcmd_time = 0
        self._pro800ID = str(pro800ID)
        print('Connecting to PRO8000 on %s'%(self._port))

        self.ser = serial.Serial(port=self._port,
                             baudrate=19200,
                             bytesize=8,
                             stopbits=1,
                             timeout=1,
                             parity='N',
                             xonxoff = False,
                             rtscts = False,
                             dsrdtr = False)
        slot_init = ":SLOT " + str(slot)
        self.ser.write(slot_init.encode())

    def __del__(self):
        print('Closing connection to PRO8000 on %s'%(self.port))

    def _send_cmd(self, command, argument, expect_response = False, retry = False):
        
        assert command[-1] != '?'

        if self._port is None:
            return

        if argument is None:
            argument = ''

        done = False
        while not done:
                if expect_response:
                    self.ser.flushInput()

                self.ser.flushOutput()
                tosend = str(command) + str(argument)
                self.ser.write(tosend)
                self.ser.write('\r\n')

                self.ser.flush()

                if expect_response:
                    try:
                        response = self._readline()
                        if response.startswith(prefix):
                            reply += (response[len(prefix):], )
                            done = True
                        else:
                            raise PRO800Error(command, response)
                    except Exception as ex:
                        if not retry or retry <= 0:
                            raise ex
                        else:
                            if type(retry) == int:
                                retry -= 1
                            continue
                else:
                    continue

    def _configure(self):
         self._send_cmd(self, ':TYPE:ID', '?', expect_response = True, retry = False) #Reads the module ID (here 223 for TED8000)
         self._send_cmd(self, '*RST', '', expect_response = False, retry = False) #Resets the PRO800 Series
         self._send_cmd(self, '*TST', '?', expect_response = True, retry = False) #Executes a self test and queries the result
    """
    *WAI
    Waiting until the last operation is completed
    *RST
    Resets the PRO8000 Series: All outputs of all modules are switched
    off, all macros are deactivated (not deleted), the unit stays in 'ready'
    status i.e. bit 0 (FIN) of the status byte register is set. All set parameters
    (current, power values etc. remain valid!)
    """


    def _readline(self):
        done = False
        line = str()
        # print 'reading line',
        while not done:
            c = self.ser.read()
            # ignore \r since it is part of the line terminator
            if len(c) == 0:
                raise PRO800Error('len = 0')
            elif c == '\r':
                continue
            elif c == '\n':
                done = True
            elif ord(c) > 32 and ord(c) < 127:
                line += c
            else:
                raise PRO800Error(c)

        return line

    def set_temp(self, value):  #":TEMP:SET <NR3>" Programs the set temperature
         self._send_cmd(self, ':TEMP:SET', ' '+ value, expect_response = True, retry = False)

    def meas_temp(self):  #":TEMP:MEAS <NR1>" Programs TEMP to be the measurement value for “ELCH1)” on position <NR1> (1...8) in the output string.
         self._send_cmd(self, ':TEMP:SET', ' 1', expect_response = True, retry = False)

    def get_temp_set(self): #Reads the set temperature
         self._send_cmd(self, ':TEMP:SET', '?', expect_response = True, retry = False)

    def get_temp_act(self): #Reads the actual temperature
         self._send_cmd(self, ':TEMP:ACT', '?', expect_response = True, retry = False)

    def TEC_on(self): #Switches the TEC output ON
         self._send_cmd(self, ':TEC ON', '', expect_response = True, retry = False)
    
    def TEC_off(self): #Switches the TEC output OFF
         self._send_cmd(self, ':TEC OFF', '', expect_response = True, retry = False)

    def TEC_status(self): #":TEC?" Reads the TEC output status:
         self._send_cmd(self, ':TEC', '?', expect_response = True, retry = False)

    def get_Temp_min(self): #Reads the minimum allowed set temperature
         self._send_cmd(self, 'TEMP:MIN', '?', expect_response = True, retry = False)

    def get_Temp_max(self):  #Reads the maximum allowed set temperature
         self._send_cmd(self, 'TEMP:MAX', '?', expect_response = True, retry = False)

if __name__ == '__main__':
    print('test')



#TEC8000
"""
":TYPE:SUB?"Queries the module's sub-type: [:TYPE:SUB <NR1><LF>]where the <NR1> value stands for: 0 = Standard TED8000, 1 = TED8000-PT,2 = TED8000-KRYO
"""

