import socket

HOST = '100.65.29.50' # "127.0.0.1"
PORT = 65432  # The port used by the server
inp = ''

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while not inp == 'Quit':
        inp = input('Data to send: ')
        s.sendall(inp.encode('utf-8'))
        data = s.recv(1024)
        print(data.decode())