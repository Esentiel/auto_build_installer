host='localhost'
port=8008
log_port=8007
rez="1280x860"
serv_list=r'\\vm-bee.netcracker.com\config\list.txt'
cc_list=r'\\vm-bee.netcracker.com\config\cc_list.txt'
ftp_root=r'./Projects/DHL/IM.GRE_CP/_Internal_Deliverables'
ftp_root_extnd=r'ftp.netcracker.com/ftp/Projects/DHL/IM.GRE_CP/_Internal_Deliverables'
with open('config.cfg', 'r') as cfg:
	delivs=cfg.read().strip().split(';')
cfg.close()
delivs=['Migration.Core.1','PPS.1','PH1.Migration.SmokeTest','PPS.9','Migration.Master.1','RefData','data-duplicator']
title='Anime Auto bulk installer tool for DHL project and friends'