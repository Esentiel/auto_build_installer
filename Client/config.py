host='vm-bee.netcracker.com'
port=8008
log_port=8007
rez="1420x860"
serv_list=r'\\vm-bee.netcracker.com\config\list.txt'
cc_list=r'\\vm-bee.netcracker.com\config\cc_list.txt'
ftp_root=r'./Projects/DHL/IM.GRE_CP/_Internal_Deliverables'
ftp_root_extnd=r'ftp.netcracker.com/ftp/Projects/DHL/IM.GRE_CP/_Internal_Deliverables'
with open('config.cfg', 'r') as cfg:
	delivs=cfg.read().strip().split(';')
cfg.close()
title='Anime Auto bulk installer tool for DHL project and friends'
