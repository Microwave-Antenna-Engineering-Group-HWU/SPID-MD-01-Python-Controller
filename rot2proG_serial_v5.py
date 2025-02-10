'''
File: 	rot2proG_serial_v4_gui.py
Author: Jaiden Ferraccioli and Spyros Daskalakis
Brief: 	This class is a control interface for the SPID Elektronik rot2proG antenna rotor controller.
	This software was designed as an open source interface between the rotor controller and
	other systems. This can be paired with an orbit propagator in order to extend usability and
	range of communication between an earth station and satellites or a communication station
	and a moving target. 
'''

import serial
import time

class Rot2proG:

	pulse = 0
	debug = False
	max_az = float(540)  # Maximum azimuth. Defaults to 540.
	min_az = float(-180)  # Minimum azimuth. Defaults to -180.
	max_el = float(180)  # Maximum elevation. Defaults to 180.
	min_el = float(-21)  # Minimum elevation. Defaults to -21.
	dev_path = ""

	'''
	This sets up the serial connection and pulse value.
	When set to true, the debugging parameter allows for information such as
	azimuth, elevation and pulse to be printed out when functions are called.
	Debugging defaults to False.
	'''
	def __init__(self, dev_path, debugging=False):
		#self.ser = serial.Serial(port='/dev/ttyUSB0',baudrate=600, bytesize=8, parity='N', stopbits=1, timeout=None)
		self.dev_path = dev_path
		self.ser = serial.Serial(port=self.dev_path, baudrate=460800, bytesize=8, parity='N', stopbits=1, timeout=None)
		print(str(self.ser.name))
		self.status()
		self.debug = debugging
		if(self.debug):
			print(self.ser.name)
			print("Pulse: " + str(self.pulse) + "\n")

	'''
	This makes sure that the serial connection is closed when the class is deleted 
	or the program terminates.
	'''
	def __del__(self):
		self.ser.close()

	def set_dev_path(self, path):
		print("Old Device Path: " + self.dev_path)
		old_path = self.dev_path
		try:
			self.ser.close()
			self.ser = serial.Serial(port=str(path), baudrate=460800, bytesize=8, parity='N', stopbits=1, timeout=None)
			self.dev_path = str(path)

		except AttributeError:
			self.ser = serial.Serial(port=str(old_path), baudrate=460800, bytesize=8, parity='N', stopbits=1, timeout=None)
			self.dev_path = self.ser.name
			print("Invalid Device path: " + path)
			print("Please Use a Valid Device Path: " + self.dev_path)
			pass
		print("New Device Path: " + self.dev_path)
		print("Serial: " + str(self.ser.name) + "\n")

	'''
	Send a STATUS command to the controller, which requests the current azimuth
	and elevation of the rotor. The azimuth, elevation and pulse are then computed,
	the pulse is set and the azimuth, elevation and pulse are returned as a list (first
	element being azimuth, the second being elevation, and the third being pulse).
	'''
	def status(self):
		cmd = [0x57, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1f, 0x20]
		packet = bytes(cmd)
		
		self.ser.write(packet)
		self.ser.flush()

		rec_packet = self.ser.read(12)
		az = (rec_packet[1] * 100) + (rec_packet[2] * 10) + rec_packet[3] + (rec_packet[4] / 10) - 360.0
		el = (rec_packet[6] * 100) + (rec_packet[7] * 10) + rec_packet[8] + (rec_packet[9] / 10) - 360.0
		ph = rec_packet[5]
		pv = rec_packet[10]

		ret = [az, el, ph]

		assert(ph == pv)
		self.pulse = ph

		if(self.debug):
			print("STATUS COMMAND SENT")
			print("Azimuth:   " + str(az))
			print("Elevation: " + str(el))
			print("PH: " + str(ph))
			print("PV: " + str(pv) + "\n")

		return ret

	'''
	Send a STOP command to the controller, which causes the rotor to stop moving and
	return the current azimuth, elevation and pulse of the rotor where it stopped. The
	azimuth, elevation and pulse are then computed, the pulse is set and the azimuth,
	elevation and pulse are returned as a list (first element being azimuth, second
	being elevation and the third being pulse).
	'''
	def stop(self):
		cmd = [0x57, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0f, 0x20]
		packet = bytes(cmd)

		self.ser.write(packet)
		self.ser.flush()

		rec_packet = self.ser.read(12)

		az = (rec_packet[1] * 100) + (rec_packet[2] * 10) + rec_packet[3] + (rec_packet[4] / 10) - 360.0
		el = (rec_packet[6] * 100) + (rec_packet[7] * 10) + rec_packet[8] + (rec_packet[9] / 10) - 360.0
		ph = rec_packet[5]
		pv = rec_packet[10]

		ret = [az, el, ph]

		assert(ph == pv)
		self.pulse = ph

		if(self.debug):
			print("STOP COMMAND SENT")
			print("Azimuth:   " + str(az))
			print("Elevation: " + str(el))
			print("PH: " + str(ph))
			print("PV: " + str(pv) + "\n")

		return ret

	'''
	Send a SET command to the controller, which causes the rotor to adjust its position
	to the azimuth and elevation specified by the azi and eli parameters respectively.
	The azi and eli parameters are floating point values that specify the desired position.
	There is no response to the SET command, thus nothing to return.
	'''
	def set(self, azi, eli):
		# Ensure azimuth and elevation are within valid ranges
		if not (self.min_az <= float(azi) <= self.max_az):
			print(f"Error: Azimuth value {azi} out of limits. Must be between {self.min_az} and {self.max_az}.")
			return
		if not (self.min_el <= float(eli) <= self.max_el):
			print(f"Error: Elevation value {eli} out of limits. Must be between {self.min_el} and {self.max_el}.")
			return

		# Calculate H and V based on pulses and +360 degree offset
		H = int(self.pulse * (360 + float(azi)))
		V = int(self.pulse * (360 + float(eli)))

		# Encode H and V as ASCII (0x30-0x39, i.e., '0'-'9')
		# convert to ascii characters
		H_str = "0000" + str(H)
		V_str = "0000" + str(V)

		# Create command packet
		cmd = [
			0x57,  # Start byte
			int(H_str[-4]) + 0x30, int(H_str[-3]) + 0x30, int(H_str[-2]) + 0x30, int(H_str[-1]) + 0x30,  # H1-H4
			self.pulse,  # PH
			int(V_str[-4]) + 0x30, int(V_str[-3]) + 0x30, int(V_str[-2]) + 0x30, int(V_str[-1]) + 0x30,  # V1-V4
			self.pulse,  # PV
			0x2f,  # K
			0x20   # END
		]
		packet = bytes(cmd)

		# Send command packet to the controller
		self.ser.write(packet)
		self.ser.flush()

		if self.debug:
			print("SET COMMAND SENT")
			print(f"Sent: {packet}")
			print(f"Set Azimuth: {azi} ({H_str})")
			print(f"Set Elevation: {eli} ({V_str})")
			print(f"Pulse: {self.pulse}\n")

		time.sleep(1)

	'''
	Calls the STATUS, STOP and SET functions multiple times
	in order to test the rot2proG class functionality.
	'''
	def test(self):
		self.status()
		self.stop()
		self.set(90, 90)
		a=True
		while(a):
			time.sleep(2)
			val = self.status()
			print(val)
			if(90 == val[0] and 90 == val[1]):
				a = False
			print("Az="+str(val[0]))
			print("El="+str(val[1]))
		self.set(0, 0)
		a=True
		while(a):
			time.sleep(2)
			val = self.status()
			if(0 == val[0] and 0 == val[1]):
				a = False
			print("Az="+str(val[0]))
			print("El="+str(val[1]))
		self.stop()

	def test_spiros(self):
		self.status()
		self.stop()
		self.set(90, 90)
	

if __name__ == "__main__":
	rot = Rot2proG('COM17', debugging=True)
	rot.test()
	del rot
	print("Done")
