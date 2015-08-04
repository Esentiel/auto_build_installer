import socket

HOST = 'localhost'    # The remote host
PORT = 8007              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.sendall('{"server": "U96_Q51_6300", "order_num": 1, "path_to_patch": "ftp.netcracker.com/ftp/Projects/DHL/IM.GRE_CP/_Internal_Deliverables/8.2.1.DHL.CP.PH1.Migration.SmokeTest/_ci-builds", "patch_name": "96_8.2.1.DHL_CP.Migration.SmokeTest_rev2894_autoinstaller.zip", "end": 1}')
s.close()