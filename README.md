# SPID-MD-01-Python-Controller
This repository provides Python scripts and utilities to control the SPID MD-01 positioner using the SPID ROT2 protocol over three communication methods:
- **LAN (Ethernet)** via TCP/IP
- **USB** as a virtual COM port
- **RS232** serial interface

The MD-01 is a powerful rotor controller for antenna systems, supporting azimuth and elevation movement. This repository enables developers to interface with the controller using Python and the SPID ROT2 protocol for precise position control and status retrieval.

## Features
- **Multi-Mode Communication:**
  - **LAN:** Control the MD-01 over a TCP/IP connection on port 23.
  - **USB:** Communicate with the MD-01 via a virtual COM port.
  - **RS232:** Use a traditional serial connection with customizable baud rates.

- **Control Functions:**
  - Set and retrieve azimuth and elevation positions.
  - Start and stop movement commands.
  - Receive real-time position updates.

- **Protocol:** Fully implements the SPID ROT2 protocol for command and response handling.

## Requirements
- **Hardware:**
  - SPID MD-01 controller
  - Ethernet, USB, or RS232 interface

- **Software:**
  - Python 3.7 or higher
  - Required libraries (listed in `requirements.txt`)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/SPID-MD-01-Python-Controller.git
   cd SPID-MD-01-Python-Controller
   ```

## Python Files
- `rot2proG_serial_v2.py`: Control interface for the SPID Elektronik rot2proG antenna rotor controller.
- `rot2proG_serial_v3_gui.py`: Enhanced control interface with additional functionalities.
- `rot2proG_serial_v4.py`: Latest control interface with debugging capabilities.
- `pyQT5_gui.py`: PyQt5-based GUI for controlling the SPID Elektronik rot2proG antenna rotor controller.

## GUI Implementation
The GUI was implemented using PyQt5 and is based on the files `rot2proG_serial_v4.py` and `pyQT5_gui.py`. Below is a screenshot of the GUI:

<p align="center">
  < src="https://github.com/daskals/SPID-MD-01-Python-Controller/blob/main/gui.PNG">
</p>

## References
- For more information on the SPID Rot1Prog and Rot2Prog Protocol, visit [this blog post](https://ryeng.name/blog/3).
- This repository is inspired by and references the work done in [this repo](https://github.com/jaidenfe/rot2proG/tree/master).
