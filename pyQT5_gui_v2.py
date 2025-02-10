'''
File: 	pyQT5_gui.py
Author: Jaiden Ferraccioli and Spyros Daskalakis
Brief: 	This file contains the GUI for controlling the SPID Elektronik rot2proG antenna rotor controller.
'''

from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import serial.tools.list_ports
from rot2proG_serial_v4 import Rot2proG
import threading

class GuiApp(QtWidgets.QWidget):
	def __init__(self, rot2prog):
		super().__init__()
		self.rot2prog = rot2prog
		self.update_interval = 2  # Default update interval in seconds
		self.initUI()
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.update_status)
		self.connected = False
		self.mutex = QtCore.QMutex()  # Mutex for thread safety

	def initUI(self):
		self.setWindowTitle('Positioner Control 1')
		
		# Make window responsive
		self.setMinimumSize(500, 1000)
		self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		
		# Get screen resolution and set initial window size to half the screen
		screen = QtWidgets.QApplication.primaryScreen()
		screen_size = screen.size()
		print(f"Screen resolution: {screen_size.width()}x{screen_size.height()}")
		width = screen_size.width() * 0.5  # 50% of screen width
		height = screen_size.height() * 0.5  # 50% of screen height
		self.resize(width, height)
		
		layout = QtWidgets.QVBoxLayout()

		# Add logo
		logo_label = QtWidgets.QLabel(self)
		logo_pixmap = QtGui.QPixmap('Heriot-Watt_University_logo.svg')
		logo_label.setPixmap(logo_pixmap.scaled(200, 100, QtCore.Qt.KeepAspectRatio))
		logo_label.setAlignment(QtCore.Qt.AlignCenter)
		layout.addWidget(logo_label)

		# Add title
		title_label = QtWidgets.QLabel('Positioner 1', self)
		title_label.setAlignment(QtCore.Qt.AlignLeft)
		title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
		layout.addWidget(title_label)

		# Add COM port and baud rate inputs
		connection_group = QtWidgets.QGroupBox("Connection")
		connection_group.setStyleSheet("QGroupBox { font-weight: bold; color: red; }")
		connection_layout = QtWidgets.QFormLayout()
		self.com_port_input = QtWidgets.QComboBox(self)
		self.com_port_input.addItems(self.get_available_com_ports())
		self.com_port_input.setEditable(True)
		self.com_port_input.setCurrentText('COM17')
		connection_layout.addRow('COM Port:', self.com_port_input)

		self.baud_rate_input = QtWidgets.QComboBox(self)
		self.baud_rate_input.addItems(['300', '1200', '2400', '4800', '9600', '19200', '38400', '57600', '115200', '230400', '460800'])
		self.baud_rate_input.setEditable(True)
		self.baud_rate_input.setCurrentText('460800')
		connection_layout.addRow('Baud Rate:', self.baud_rate_input)

		self.connect_button = QtWidgets.QPushButton('Connect', self)
		self.connect_button.clicked.connect(self.toggle_connection)
		connection_layout.addRow(self.connect_button)

		connection_group.setLayout(connection_layout)
		layout.addWidget(connection_group)

		# Add update interval input
		interval_group = QtWidgets.QGroupBox("Update Interval")
		interval_group.setStyleSheet("QGroupBox { font-weight: bold; color: red; }")
		interval_layout = QtWidgets.QFormLayout()
		self.update_interval_input = QtWidgets.QLineEdit(self)
		self.update_interval_input.setText(str(self.update_interval))
		interval_layout.addRow('Update Interval (seconds):', self.update_interval_input)

		self.set_update_interval_button = QtWidgets.QPushButton('Set Interval', self)
		self.set_update_interval_button.clicked.connect(self.set_update_interval)
		interval_layout.addRow(self.set_update_interval_button)

		interval_group.setLayout(interval_layout)
		layout.addWidget(interval_group)

		# Add azimuth and elevation inputs
		position_group = QtWidgets.QGroupBox("Set Position")
		position_group.setStyleSheet("QGroupBox { font-weight: bold; color: red; }")
		position_layout = QtWidgets.QFormLayout()
		self.azimuth_input = QtWidgets.QLineEdit(self)
		position_layout.addRow('Azimuth (degrees):', self.azimuth_input)

		self.elevation_input = QtWidgets.QLineEdit(self)
		position_layout.addRow('Elevation (degrees):', self.elevation_input)

		self.set_button = QtWidgets.QPushButton('Set', self)
		self.set_button.clicked.connect(self.set_values)
		position_layout.addRow(self.set_button)

		position_group.setLayout(position_layout)
		layout.addWidget(position_group)

		# Add manual control
		manual_group = QtWidgets.QGroupBox("Manual Control")
		manual_group.setStyleSheet("QGroupBox { font-weight: bold; color: red; }")
		manual_layout = QtWidgets.QVBoxLayout()
		step_layout = QtWidgets.QFormLayout()
		self.step_input = QtWidgets.QLineEdit(self)
		self.step_input.setText('1.0')
		step_layout.addRow('Step (degrees):', self.step_input)
		manual_layout.addLayout(step_layout)

		button_layout = QtWidgets.QGridLayout()
		self.up_button = QtWidgets.QPushButton('Up', self)
		self.up_button.clicked.connect(self.move_up)
		button_layout.addWidget(self.up_button, 0, 1)

		self.left_button = QtWidgets.QPushButton('Left', self)
		self.left_button.clicked.connect(self.move_left)
		button_layout.addWidget(self.left_button, 1, 0)

		self.right_button = QtWidgets.QPushButton('Right', self)
		self.right_button.clicked.connect(self.move_right)
		button_layout.addWidget(self.right_button, 1, 2)

		self.down_button = QtWidgets.QPushButton('Down', self)
		self.down_button.clicked.connect(self.move_down)
		button_layout.addWidget(self.down_button, 2, 1)

		manual_layout.addLayout(button_layout)
		manual_group.setLayout(manual_layout)
		layout.addWidget(manual_group)

		# Add emergency stop button
		emergency_group = QtWidgets.QGroupBox("Emergency Stop")
		emergency_group.setStyleSheet("QGroupBox { font-weight: bold; color: red; }")
		emergency_layout = QtWidgets.QVBoxLayout()
		self.emergency_button = QtWidgets.QPushButton('Emergency Stop', self)
		self.emergency_button.setStyleSheet("background-color: red; color: white; font-size: 16px;")
		self.emergency_button.clicked.connect(self.stop)
		emergency_layout.addWidget(self.emergency_button)
		emergency_group.setLayout(emergency_layout)
		layout.addWidget(emergency_group)

		# Add status labels
		status_group = QtWidgets.QGroupBox("Status")
		status_group.setStyleSheet("QGroupBox { font-weight: bold; color: red; }")
		status_layout = QtWidgets.QVBoxLayout()
		self.azimuth_label = QtWidgets.QLabel('Azimuth: 0.0', self)
		self.azimuth_label.setAlignment(QtCore.Qt.AlignCenter)
		self.azimuth_label.setStyleSheet("font-size: 14px;")
		status_layout.addWidget(self.azimuth_label)

		self.elevation_label = QtWidgets.QLabel('Elevation: 0.0', self)
		self.elevation_label.setAlignment(QtCore.Qt.AlignCenter)
		self.elevation_label.setStyleSheet("font-size: 14px;")
		status_layout.addWidget(self.elevation_label)

		self.resolution_label = QtWidgets.QLabel('Resolution: 0.0 pulses/degree', self)
		self.resolution_label.setAlignment(QtCore.Qt.AlignCenter)
		self.resolution_label.setStyleSheet("font-size: 14px;")
		status_layout.addWidget(self.resolution_label)

		status_group.setLayout(status_layout)
		layout.addWidget(status_group)

		# Add messages box
		messages_group = QtWidgets.QGroupBox("Messages")
		messages_group.setStyleSheet("QGroupBox { font-weight: bold; color: red; }")
		messages_layout = QtWidgets.QVBoxLayout()
		self.messages_text = QtWidgets.QTextEdit(self)
		self.messages_text.setReadOnly(True)
		messages_layout.addWidget(self.messages_text)
		messages_group.setLayout(messages_layout)
		layout.addWidget(messages_group)

		# Add creator label
		self.creator_label = QtWidgets.QLabel('<a href="https://daskalakispiros.com/">daskalakispiros.com</a>', self)
		self.creator_label.setAlignment(QtCore.Qt.AlignCenter)
		self.creator_label.setOpenExternalLinks(True)
		self.creator_label.setStyleSheet("font-size: 10px;")
		layout.addWidget(self.creator_label)

		# Add group link
		self.group_label = QtWidgets.QLabel('<a href="https://microwaves.site.hw.ac.uk/">Microwaves & Antenna Engineering Group</a>', self)
		self.group_label.setAlignment(QtCore.Qt.AlignCenter)
		self.group_label.setOpenExternalLinks(True)
		self.group_label.setStyleSheet("font-size: 20px;")
		layout.addWidget(self.group_label)

		self.setLayout(layout)
		self.show()  # Show the window

	def get_available_com_ports(self):
		# Get list of available COM ports
		ports = serial.tools.list_ports.comports()
		return [port.device for port in ports]

	def toggle_connection(self):
		# Toggle connection state
		if self.connected:
			self.disconnect()
		else:
			threading.Thread(target=self.connect).start()

	def connect(self):
		# Connect to the device
		com_port = self.com_port_input.currentText()
		baud_rate = self.baud_rate_input.currentText()
		self.append_message(f"Connecting to {com_port} at {baud_rate} baud")
		try:
			self.mutex.lock()
			self.rot2prog = Rot2proG(com_port, debugging=True)
			self.rot2prog.ser.baudrate = int(baud_rate)
			self.timer.start(self.update_interval * 1000)
			self.connect_button.setText('Disconnect')
			self.connected = True
			self.append_message("Connected successfully")
			self.update_status()  # Run status command after connecting
		except Exception as e:
			self.append_message(f"Failed to connect: {e}")
		finally:
			self.mutex.unlock()

	def disconnect(self):
		# Disconnect from the device
		self.append_message("Disconnecting")
		self.mutex.lock()
		try:
			self.timer.stop()
			self.rot2prog.__del__()
			self.connect_button.setText('Connect')
			self.connected = False
			self.append_message("Disconnected successfully")
		finally:
			self.mutex.unlock()

	def update_status(self):
		# Update status labels
		self.mutex.lock()
		try:
			status = self.rot2prog.status()
			self.azimuth_label.setText(f'Azimuth: {status[0]}')
			self.elevation_label.setText(f'Elevation: {status[1]}')
			self.resolution_label.setText(f'Resolution: {status[2]} pulses/degree')
		except Exception as e:
			self.append_message(f"Failed to update status: {e}")
		finally:
			self.mutex.unlock()

	def set_update_interval(self):
		# Set the update interval for status updates
		if not self.connected:
			self.append_message("Error: Not connected")
			return
		try:
			interval = float(self.update_interval_input.text())
			if 0 < interval <= 60:
				self.update_interval = interval
				self.timer.setInterval(int(self.update_interval * 1000))
				self.append_message(f"Update interval set to {self.update_interval} seconds")
			else:
				self.append_message("Update interval must be between 0 and 60 seconds")
		except ValueError:
			self.append_message("Invalid update interval")

	def set_values(self):
		# Set azimuth and elevation values
		if not self.connected:
			self.append_message("Error: Not connected")
			return
		self.mutex.lock()
		try:
			azimuth = float(self.azimuth_input.text())
			elevation = float(self.elevation_input.text())
			if not (-180 <= azimuth <= 540):
				self.append_message(f"Error: Azimuth value {azimuth} out of limits. Must be between -180 and 540.")
				return
			if not (-21 <= elevation <= 180):
				self.append_message(f"Error: Elevation value {elevation} out of limits. Must be between -21 and 180.")
				return
			self.rot2prog.set(azimuth, elevation)
			self.append_message(f"Set values: Azimuth = {azimuth}, Elevation = {elevation}")
		except ValueError:
			self.append_message("Invalid azimuth or elevation value")
		finally:
			self.mutex.unlock()

	def move_up(self):
		# Move up by step value
		if not self.connected:
			self.append_message("Error: Not connected")
			return
		self.mutex.lock()
		try:
			step = float(self.step_input.text())
			if step > 0:
				current_elevation = float(self.elevation_label.text().split(': ')[1])
				new_elevation = current_elevation + step
				if new_elevation > 180:
					self.append_message(f"Error: Elevation value {new_elevation} out of limits. Must be between -21 and 180.")
					return
				self.rot2prog.set(float(self.azimuth_label.text().split(': ')[1]), new_elevation)
				self.append_message(f"Moved up by {step} degrees")
			else:
				self.append_message("Step must be a positive value")
		except ValueError:
			self.append_message("Invalid step value")
		finally:
			self.mutex.unlock()

	def move_down(self):
		# Move down by step value
		if not self.connected:
			self.append_message("Error: Not connected")
			return
		self.mutex.lock()
		try:
			step = float(self.step_input.text())
			if step > 0:
				current_elevation = float(self.elevation_label.text().split(': ')[1])
				new_elevation = current_elevation - step
				if new_elevation < -21:
					self.append_message(f"Error: Elevation value {new_elevation} out of limits. Must be between -21 and 180.")
					return
				self.rot2prog.set(float(self.azimuth_label.text().split(': ')[1]), new_elevation)
				self.append_message(f"Moved down by {step} degrees")
			else:
				self.append_message("Step must be a positive value")
		except ValueError:
			self.append_message("Invalid step value")
		finally:
			self.mutex.unlock()

	def move_left(self):
		# Move left by step value
		if not self.connected:
			self.append_message("Error: Not connected")
			return
		self.mutex.lock()
		try:
			step = float(self.step_input.text())
			if step > 0:
				current_azimuth = float(self.azimuth_label.text().split(': ')[1])
				new_azimuth = current_azimuth - step
				if new_azimuth < -180:
					self.append_message(f"Error: Azimuth value {new_azimuth} out of limits. Must be between -180 and 540.")
					return
				self.rot2prog.set(new_azimuth, float(self.elevation_label.text().split(': ')[1]))
				self.append_message(f"Moved left by {step} degrees")
			else:
				self.append_message("Step must be a positive value")
		except ValueError:
			self.append_message("Invalid step value")
		finally:
			self.mutex.unlock()

	def move_right(self):
		# Move right by step value
		if not self.connected:
			self.append_message("Error: Not connected")
			return
		self.mutex.lock()
		try:
			step = float(self.step_input.text())
			if step > 0:
				current_azimuth = float(self.azimuth_label.text().split(': ')[1])
				new_azimuth = current_azimuth + step
				if new_azimuth > 540:
					self.append_message(f"Error: Azimuth value {new_azimuth} out of limits. Must be between -180 and 540.")
					return
				self.rot2prog.set(new_azimuth, float(self.elevation_label.text().split(': ')[1]))
				self.append_message(f"Moved right by {step} degrees")
			else:
				self.append_message("Step must be a positive value")
		except ValueError:
			self.append_message("Invalid step value")
		finally:
			self.mutex.unlock()

	def stop(self):
		# Emergency stop
		if self.connected:
			self.mutex.lock()
			try:
				self.append_message("Emergency stop activated")
				self.rot2prog.stop()
			finally:
				self.mutex.unlock()
		else:
			self.append_message("Error: Not connected")

	def append_message(self, message):
		# Append message to the messages box
		self.messages_text.append(message)
		self.messages_text.verticalScrollBar().setValue(self.messages_text.verticalScrollBar().maximum())

	def closeEvent(self, event):
		# Handle window close event
		if self.connected:
			self.disconnect()
		event.accept()

def run_gui():
	# Run the GUI application
	app = QtWidgets.QApplication(sys.argv)
	gui = GuiApp(None)
	sys.exit(app.exec_())

if __name__ == "__main__":
	run_gui()
