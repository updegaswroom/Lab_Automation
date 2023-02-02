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

    def __init__(self, pro800ID, port, slot, silent=True, sleepfunc=None):
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
                             dsrdtr = True)
        slot_init = ":SLOT " + str(slot)
        self.ser.write(slot_init.encode())

    def _send_cmd(self, command, argument, expect_response = False, retry = False):
        
        assert command[-1] != '?'

        if self._port is None:
            return

        if argument is None:
            argument = ''

        done = False
        while not done:
                if expect_response:
                    self.ser.reset_input_buffer() #Flush input buffer, discarding all its contents.

                self.ser.reset_output_buffer() #Clear output buffer, aborting the current output and discarding all that is in the buffer
                tosend = str(command) + str(argument) + '\r\n'
                self.ser.write(tosend.encode()) #Write the bytes data to the port, Unicode strings must be encoded 
                

                self.ser.flush() #Flush of file like objects. In this case, wait until all data is written.
                done = True
                print(self.ser.read())
                prefix = 1
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
         self._send_cmd(self, ':TEC ON', '', True, False)
    
    def TEC_off(self): #Switches the TEC output OFF
         self._send_cmd(self, ':TEC OFF', '', expect_response = True, retry = False)

    def TEC_status(self): #":TEC?" Reads the TEC output status:
         self._send_cmd(self, ':TEC', '?', expect_response = True, retry = False)

    def get_Temp_min(self): #Reads the minimum allowed set temperature
         self._send_cmd(self, 'TEMP:MIN', '?', expect_response = True, retry = False)

    def get_Temp_max(self):  #Reads the maximum allowed set temperature
         self._send_cmd(self, 'TEMP:MAX', '?', expect_response = True, retry = False)

    def __del__(self):
        print('Closing connection to PRO8000 on %s'%(self._port))
#%%
if __name__ == '__main__':

    def _readline(serialdev):
        """
        Returns a line, that is reads until \r\n.
        OK, so you are probably wondering why I wrote this. Why not just use
        self.ser.readline()?
        I am glad you asked.
        With python < 2.6, pySerial uses serial.FileLike, that provides a readline
        that accepts the max number of chars to read, and the end of line
        character.
        With python >= 2.6, pySerial uses io.RawIOBase, whose readline only
        accepts the max number of chars to read. io.RawIOBase does support the
        idea of a end of line character, but it is an attribute on the instance,
        which makes sense... except pySerial doesn't pass the newline= keyword
        argument along to the underlying class, and so you can't actually change
        it.
        """
        done = False
        line = str()
        # print 'reading line',
        while not done:
            c = serialdev.read()
            c = c.decode('ascii')
            # ignore \r since it is part of the line terminator
            if len(c) == 0:
                raise Exception("no response")
            elif c == '\r':
                time.sleep(0.1)
                continue
            elif c == '\n':
                time.sleep(0.1)
                done = True
            elif ord(c) > 32 and ord(c) < 127:
                time.sleep(0.1)
                line += c
            #else:
            #    raise Exception(c)

        return line

    _port = "COM3"
    ser = serial.Serial(port=_port,
                             baudrate=19200,
                             bytesize=8,
                             stopbits=1,
                             timeout=1,
                             parity='N',
                             xonxoff = False,
                             rtscts = False,
                             dsrdtr = True)
    ser.flushOutput()
    """slot_init = ":SLOT 1?\n"
    print(slot_init.encode())
    ser.write(slot_init.encode())"""

    ID = "*IDN?\n"
    print(ID.encode())
    ser.write(ID.encode())
    print(_readline(ser))
    SelfTest ="*TST?\n"
    print(SelfTest.encode())
    ser.write(SelfTest.encode())
    print(_readline(ser))

    T_read = ":TEMP:ACT?\n"
    print(T_read.encode())
    ser.write(T_read.encode())
    print(_readline(ser))

    T_set = ":TEMP:SET 10\n"
    print(T_set.encode())
    ser.write(T_set.encode())

    TEC_on = ":TEC ON\n"
    print(TEC_on.encode())
    ser.write(TEC_on.encode())

    time.sleep(10)
    print(T_read.encode())
    ser.write(T_read.encode())
    print(_readline(ser))
    ser.close()

#%%
#TEC8000
"""
":TYPE:SUB?"Queries the module's sub-type: [:TYPE:SUB <NR1><LF>]where the <NR1> value stands for: 0 = Standard TED8000, 1 = TED8000-PT,2 = TED8000-KRYO
"""


# %%
