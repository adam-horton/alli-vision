import socket

HOST = '100.65.29.50' # "127.0.0.1"
PORT = 65432  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'Hello World!')
    data = s.recv(1024)

print(data.decode())