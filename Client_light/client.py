import socket, json

HOST = 'localhost'    # The remote host
PORT = 8007              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

with open('install_qeue.json', 'r') as json_file:
	json_data = json.load(json_file)
json_file.close()
s.sendall(str(json_data))
s.close()