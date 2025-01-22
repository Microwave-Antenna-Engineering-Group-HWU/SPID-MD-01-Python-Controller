# Example from the provided code
def provided_example():
    PH = 10  # Pulses per degree, 0A in hex
    PV = 10  # Pulses per degree, 0A in hex
    taz = 0  # Example azimuth value
    tel = 0  # Example elevation value

    H = str(int(PH * (360 + taz)))
    H1 = "3" + H[0]
    H2 = "3" + H[1]
    H3 = "3" + H[2]
    H4 = "3" + H[3]
    V = str(int(PV * (360 + tel)))
    V1 = "3" + V[0]
    V2 = "3" + V[1]
    V3 = "3" + V[2]
    V4 = "3" + V[3]
    msg = bytes.fromhex("57" + H1 + H2 + H3 + H4 + "0A" + V1 + V2 + V3 + V4 + "0AF920")
    print("Provided example bytes:", msg)
    return msg

# Your example
def your_example():
    cmd = ['\x57', '\x33', '\x36', '\x30', '\x30', '\x0A', '\x33', '\x36', '\x30', '\x30', '\x0A', '\xF9', '\x20']
    packet = "".join(cmd)
    packet_bytes = packet.encode('latin1')  # Use 'latin1' to ensure correct byte values
    print("Your example bytes:", packet_bytes)
    return packet_bytes

if __name__ == "__main__":
    provided_bytes = provided_example()
    your_bytes = your_example()
    print("Bytes match:", provided_bytes == your_bytes)