import socket, json, time, sys

HOST = 'localhost'    # The remote host
PORT = 8007              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

with open('install_qeue.json', 'r') as json_file:
	json_data = json.load(json_file)
json_file.close()

while True:
	s.sendall(str(json_data))
	response = ''
	while True:
		try:
			response += s.recv(1024)
			if '"end": 1}' in response:
				print response
				break
		except socket.timeout, e:
			if err == 'timed out':
            	time.sleep(1)
            	print 'recv timed out, retry later'
            	continue
            else:
            	print e
            	sys.exit(1)
        except socket.error, e:
        	# Something else happened, handle error, exit, etc.
        	print e
        	sys.exit(1)
        else:
        	if len(msg) == 0:
        		print 'orderly shutdown on server end'
        		sys.exit(0)

	if 'PENDING' not in response:
		print "Everythis was done!"
		break
	else:
		time.sleep(5)
s.close()