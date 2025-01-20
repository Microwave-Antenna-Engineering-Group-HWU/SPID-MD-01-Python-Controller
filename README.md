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
   git clone https://github.com/yourusername/spid-md01-multimode-python.git
   cd spid-md01-multimode-python
