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
	max_az = float(360)
	min_az = float(-180)
	max_el = float(180)
	min_el = float(0)
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
		print("Calling set")
		assert(float(azi) <= self.max_az)
		assert(float(azi) >= self.min_az)
		assert(float(eli) <= self.max_el)
		assert(float(eli) >= self.min_el)

		az = "0" + str(int(self.pulse * (float(azi) + 360)))
		el = "0" + str(int(self.pulse * (float(eli) + 360)))

		cmd = [0x57, int(az[-4]), int(az[-3]), int(az[-2]), int(az[-1]), self.pulse, int(el[-4]), int(el[-3]), int(el[-2]), int(el[-1]), self.pulse, 0x2f, 0x20]
		packet = bytes(cmd)

		self.ser.write(packet)
		self.ser.flush()

		if(self.debug):
			print("SET COMMAND SENT")
			print("Sent: " + packet.decode('latin-1'))
			print("Set Azimuth:   " + str(azi) + " (" + str(az) + ")")
			print("Set Elevation: " + str(eli) + " (" + str(el) + ")")
			print("Pulse: " + chr(self.pulse) + "\n")

		time.sleep(1)

	