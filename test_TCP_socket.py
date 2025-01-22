import socket

def test_md01_connection(host, port):
    """Test the TCP socket connection to the MD-01 controller."""
    try:
        # Create a socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Connecting to {host}:{port}...")
        
        # Connect to the MD-01 controller
        sock.connect((host, port))
        print("Connection successful!")

        # Send a test command (replace 'TEST_COMMAND' with a valid command for the MD-01)
        test_command = "TEST_COMMAND\n"  # Example command
        sock.send(test_command.encode('utf-8'))
        print(f"Sent: {test_command.strip()}")

        # Wait for a response
        response = sock.recv(1024).decode('utf-8')
        print(f"Response: {response.strip()}")

        # Close the connection
        sock.close()
        print("Connection closed.")
    except socket.error as e:
        print(f"Socket error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Replace '192.168.0.10' and '23' with your MD-01's IP and port
    host = "192.168.0.10"
    port = 23

    test_md01_connection(host, port)