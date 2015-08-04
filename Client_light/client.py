import socket, json

HOST = 'localhost'    # The remote host
PORT = 8007              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

json_data = json.load('install_qeue.json')
s.sendall(json_data)
s.close()