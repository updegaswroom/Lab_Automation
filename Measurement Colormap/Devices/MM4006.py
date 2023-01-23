import time 
import serial
#import signal # For keyboard interrupt?
import threading
class NewportMM4006Error(Exception):
	
	def __init__(self, string):
		# check if error occured -- if not (TB@) do nothing, otherwise
		self.string = string
		#if len(str) >= 3
		#	self.axis = string[0]
		#else
		#	self.axis = None
			
	def __str__(self):
		return string
	
# make a decorator function that is handed over the esp controller and then calls the TB? command and raises an exception

#def Decorator(func)
#	def wrapper(func)
#	
#	
#	return wrapper


class NewportMM4006(object):
	def __init__(self, port):
		self.lock = threading.Lock()
		self.ser = serial.Serial(port=port,
                             baudrate=19200,
                             bytesize=8,
                             stopbits=1,
                             timeout=1,
                             parity='N',
                             xonxoff = False,
                             rtscts = False,
                             dsrdtr = False)
	def __del__(self):
		self.ser.close()
		
	def read(self,axis = None):
		reply = self.ser.readline().decode('ascii') 
		return reply[0:-1]    #toss last (two) strings away as they are \r\n
	
	def write(self,message = None, axis = None):
		if message != None:
			suffix = "\r\n"
			message = (str(axis) if axis != None else "") + message + suffix
			#check messega syntax via REGEX?
			self.ser.write(message.encode())
		else: 
			raise NewportMM4006Error("No Message was given")
			
			
	def query(self, message = None, axis = None, check_error = False):
		with self.lock:
			if check_error:
				self.write(message + "?", axis = axis)
				self.raise_error()
				#check for an error and raise exception --> wrong check for error first, send message check for error again, if check_eror ? true
			else:
				self.write(message + "?", axis = axis)
			return self.read()
	
	def read_error(self):
		return self.query('TB')
	def raise_error(self):
		err = self.read_error() 
		if err[0] != "0":
			raise NewportMM4006Error(err)
	def version(self):
		return self.query('VE')
	def abort(self):
		self.write('AB')
	#def axis(self):
		
	
		
class Axis(object):
	def __init__(self,controller,axis):
		self.ctrl = controller
		self.axis = axis
		self.read = self.ctrl.read
		self.waiting_time = 0.02
	
	
	def __del__(self):
		self.motor_off()
		
		
		
	def write(self, message):
		time.sleep(self.waiting_time)
		self.ctrl.write(message, self.axis)
			
	def query(self,message):
		self.write(message+"?")
		return self.read()
		
		
	def id(self):
		self.query('TS')
	def set_remote(self):
		self.write('MR')
	def set_local(self):
		self.write('ML')
	def motor_on(self):
		self.write('MO')
	def motor_off(self):
		self.write('MF')
	def set_home(self,pos):
		self.write('')
	def search_home(self,modus):
		self.write('OR')
	def ismoving(self):
		self.write('MS')  #remove first three elements in list and encode to ascii
		status = self.read()[3:]
		#print(status)
		A = [bin(ord(x))[2:].zfill(8) for x in status]
		B = A[0]
		#print(B[7])

		if (B[7] == "1"):
			return True
		else: 
			return False
			
	def move_abs(self, pos,checkmovement = True):
		self.write('PA'+str(pos))
		while checkmovement:
			time.sleep(self.waiting_time)
			checkmovement = self.ismoving()
	def move_rel(self, incr, checkmovement = True):
		self.write('PR'+str(incr))
		while checkmovement:
			time.sleep(self.waiting_time)
			checkmovement = self.ismoving()

	def abort(self):	
		self.write('AB')
	def stop(self):
		self.write('ST')
	def get_position(self):
		pos = self.query('TP')
		return pos[3:]
	def zero(self):
		self.write('ZP') # sets the new zeroed frame of reference to the current position of the axis
		
	def move_dir(self):
		self.write('')
	def unit(self):
		return print(self.query('SN'))
	def set_unit(self,unit):
		self.write('SN' + unit)
		#check if unit is a string
		
	@property
	def backlash(self):
		return float(self.query('BA'))
	@backlash.setter    #0 to distance equivalent to 10000 ecoder counts
	def backlash(self, value):
		self.wirte('BA'+str(value))
		
	@property
	def resolution(self):
		float(self.query('SU'))
	@resolution.setter	
	def resolution(self,value):
		self.motor_off()
		self.write('SU'+str(value))
		self.motor_on()
				
	@property
	def velocity(self):
		self.query('VA')
	@velocity.setter
	def velocity(self, speed):
		self.write('VA'+str(speed))
	
	def limits(self):
		self.query('')
		
	def wait(self):
	#"""This method will block until current motion is finished."""
		while self.ismoving:
			sleep(self.waiting_time)
	
	#UNIT = {0:"encoder count", 1:"motor step", 2:"mm", 3:"um", 4:"I", 5:"mI", 6:"uI", 7:"Dg", 8: "Gr", 9: "Rad", 10:"mRad", 11:"uRad"} #python way of defining sets

	#define a fixed initialization processthat is carried out at the setup of the controller?






#Test environment
def MotionTest():
	print("hello")
	CNTRL = NewportMM4006('COM3')
	
	
	print(CNTRL.version())
	print(CNTRL.query('4ZT')) 
	print(CNTRL.read_error())
		
	AXIS4 = Axis(CNTRL, 3)
	AXIS4.unit()
	AXIS4.motor_on()
	
	#get units, set units, get position, move_rel, move_abs, home, sethome, id
	time.sleep(2)
	print(AXIS4.id())
	AXIS4.move_rel(10)
	AXIS4.move_rel(-10)
	#adjust movement speed (very fast!!!)
	AXIS4.move_abs(0)
#	CNTRL.write('ML')
	print('Ende')
	del AXIS4
	del CNTRL
		

if __name__ == '__name__':     #allows for testing environment within the main file itself. If this file is imported in another file the name will become the import name and the methods test is capsuled!
	MotionTest()
