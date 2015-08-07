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
patch = sys.argv[4]

with open('servers/{instnc}/{instnc}.lock'.format(instnc = instance_name),'a') as log_file:
    log_file.write('{trans_id},{ord_num},IN PROGRESS\n'.format(trans_id = transaction_id,ord_num = order_num))
log_file.close()



call(["robocopy", "\\\\vm-bee.netcracker.com\config",".", "config.json"])


instance = Instance(instance_name)
db_user = str(instance_name.upper())
app_host = str(instance.app_host)
ssh_user = 'netcrk'
ssh_port = int(instance.ssh_port)
m = re.match('.*_(.*)_.*', instance_name)
server_id = m.group(1)
ssh_key = paramiko.RSAKey.from_private_key_file("keys/key_{server}".format(server = server_id))


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
client.connect(hostname=app_host, username=ssh_user, pkey=ssh_key, port=ssh_port)

sftp = client.open_sftp()
sftp.put("servers/{inst}/{p_name}".format(inst = instance_name,p_name = patch_name), \
    '/netcracker/config/{inctnc}/{file}'.format(inctnc = instance_name, file = patch_name))

command = 'cd /netcracker/config/{instnc}; unzip -oq {pch}; ./install.sh > /dev/null 2>&1 &'.format(instnc = instance_name,pch = patch_name)
client.exec_command(command)
time.sleep(5)
command = 'tail -100 /netcracker/config/{instnc}/installer_logs/installer.log'.format(instnc = instance_name)
in_progress = False
while True:
    stdin, stdout, stderr = client.exec_command(command)
    data = stdout.read() + stderr.read()
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
        time.sleep(30)

client.close()

os.remove('servers/{instnc}/{patch}'.format(instnc = instance_name, patch = patch_name))
# os.remove('config.json')
