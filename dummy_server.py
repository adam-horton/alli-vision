#!/usr/bin/env python3

# Dummy server to report all messages sent by 
# alli's vision for debugging purposes only

import socket

HOST = socket.gethostbyname(socket.gethostname()) # "127.0.0.1" 
PORT = 65432 

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f'Socket server listening on {HOST}:{PORT}')
    conn, addr = s.accept()
    with conn:
        print(f'Connected by {addr}')
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(data.decode())
            conn.sendall(b'Hello from the server')