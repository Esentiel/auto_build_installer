import paramiko
import time
from subprocess import call
from instance import Instance
import re
import sys
import os
# List of the future changes:
# 1 use OOP 


transaction_id = sys.argv[1]
instance_name = sys.argv[2]
order_num = sys.argv[3]
cc = sys.argv[4]
patch = sys.argv[5]

try:
	os.remove('servers/{folder}/installer.log'.format(folder = instance_name))
except:
	pass

with open('servers/{instnc}/{instnc}.lock'.format(instnc = instance_name),'a') as log_file:
	log_file.write('{trans_id},{ord_num},IN PROGRESS\n'.format(trans_id = transaction_id,ord_num = order_num))
log_file.close()

call(["robocopy", "\\\\vm-bee.netcracker.com\config",".", "config.json"])

with open(r"\\vm-bee.netcracker.com\config\cc_list.txt", 'r') as cc_file:
    domain_id = str([line.replace('{cc}:'.format(cc = cc), '') for line in cc_file.readlines() if cc in line][0]).strip()
cc_file.close()



instance = Instance(instance_name)
db_user = instance.db_user.upper()
app_host = str(instance.app_host)
db_host = instance.db_host
db_sid = instance.db_sid
db_port = instance.db_port
if '_13' in db_user:
	db_slave_user = str(instance_name + domain_id).upper()
else:
	db_slave_user = db_user
ssh_user = 'netcrk'
ssh_port = int(instance.ssh_port)
m = re.match('.*_(.*)_.*', instance_name)
server_id = m.group(1)
if app_host == 'qaapp051.netcracker.com':
	ssh_key = paramiko.RSAKey.from_private_key_file("keys/key_{server}".format(server = server_id))

with open('templates/dbschememanager.xml', 'r') as xml_file:
	xml_data = str(xml_file.read()).format(db_host = db_host, db_port = db_port, db_sid = db_sid, db_slave_user = db_slave_user, cc = cc)
xml_file.close()

with open('servers/{instnc}/dbschememanager.xml'.format(instnc = instance_name), 'w') as xml_file:
	xml_file.write(xml_data)
xml_file.close()

m = re.search('(.*)/(.*)', patch)
patch_SMB = str(m.group(1)).replace('ftp.netcracker.com/ftp/','')
patch_name =  str(m.group(2))

client_ftp = paramiko.SSHClient()
client_ftp.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client_ftp.connect(hostname='ftp.netcracker.com', username='dhl_ro', password = 'XXqiI3nY', port=22)
sftp_ftp = client_ftp.open_sftp()

sftp_ftp.get(patch_SMB+'/'+patch_name, 'servers/{server}/{patch}'.format(server = instance_name, patch = patch_name))
client_ftp.close()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
if app_host == 'qaapp051.netcracker.com':
	client.connect(hostname=app_host, username=ssh_user, pkey=ssh_key, port=ssh_port)
elif app_host == 'devapp088.netcracker.com':
	client.connect(hostname=app_host, username=ssh_user, password='crknet', port=ssh_port)

sftp = client.open_sftp()
sftp.put("servers/{inst}/{p_name}".format(inst = instance_name,p_name = patch_name), \
	'/netcracker/config/{inctnc}/{file}'.format(inctnc = instance_name, file = patch_name))
sftp.put('servers/{instnc}/dbschememanager.xml'.format(instnc = instance_name), \
	'/netcracker/config/{inctnc}/AutoInstaller/dbschememanager.xml'.format(inctnc = instance_name))

command = 'cd /netcracker/config/{instnc}; unzip -oq {pch}; ./install.sh > /dev/null 2>&1 &'.format(instnc = instance_name,pch = patch_name)
client.exec_command(command)
time.sleep(20)
command = 'tail -65 /netcracker/config/{instnc}/installer_logs/installer.log'.format(instnc = instance_name)
in_progress = False
while True:
	stdin, stdout, stderr = client.exec_command(command)
	data = stdout.read() + stderr.read()

	with open("servers/{inst}/installer.log".format(inst = instance_name), 'w') as thelog:
		thelog.write(data)
	thelog.close

	if '\nBUILD SUCCESSFUL\n' in data:
		with open('servers/{instnc}/{instnc}.lock'.format(instnc = instance_name),'a') as log_file:
			log_file.write('{trans_id},{ord_num},SUCCESSFUL\n'.format(trans_id = transaction_id,ord_num = order_num))
		log_file.close()
		break
	elif '\nBUILD FAILED\n' in data:
		with open('servers/{instnc}/{instnc}.lock'.format(instnc = instance_name),'a') as log_file:
			log_file.write('{trans_id},{ord_num},FAILED\n'.format(trans_id = transaction_id,ord_num = order_num))
		log_file.close()
		break
	else:
		if not in_progress:
			with open('servers/{instnc}/{instnc}.lock'.format(instnc = instance_name),'a') as log_file:
				log_file.write('{trans_id},{ord_num},IN PROGRESS\n'.format(trans_id = transaction_id,ord_num = order_num))
			log_file.close()
			in_progress = True
		time.sleep(10)

client.close()

os.remove('servers/{instnc}/{patch}'.format(instnc = instance_name, patch = patch_name))
# os.remove("servers/{inst}/installer.log".format(inst = instance_name))
