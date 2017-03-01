#! /usr/bin/env python
import subprocess
import os

log_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cleanchrome.log')

def etime_2_sec(etime):
	print etime
	days = etime.split('-')
	if len(days) == 2:
		days = int(days[0])
		dtime = etime.split('-')[1].split(':')
	elif len(days) == 1:
		days = 0
		dtime = etime.split('-')[0].split(':')
	else:
		with open(log_path, 'a') as f:
                        f.write('\n error day'+ etime)
			return 0

	day_sec = days * 24* 3600
	h, m, s = 0, 0, 0
	if len(dtime)== 3:
		h = int(dtime[0])*3600
		m = int(dtime[1])*60
		s = int(dtime[2])
	elif len(dtime)== 2:
		m = int(dtime[0])*60
                s = int(dtime[1])
	else: 
		with open(log_path, 'a') as f:
			f.write('\n error ptime'+ etime)
	
	sec = h + m + s	
	return sec + day_sec

def kill_proc():
	p_name = 'chrome'
	cmd = "ps -eo pid,etime,command| grep -i '%s' "%p_name
	print cmd
	chrome_procs = subprocess.check_output( cmd , shell = True).strip().splitlines()

	for cp in chrome_procs:
		print '--' , cp
		tk = cp.split()
		if not len(tk) >=3:
			continue
		pid, etime, pname = tk[0], tk[1], tk[2]
		print pid, etime, pname
		sec= etime_2_sec(etime)
		print sec, etime
		if sec > 900: #more than 15 min
			os.system('kill -9 %s'%pid)
		
	

#print chrome_procs
#print etime_2_sec('21-18:26:30')
#print etime_2_sec('15:28:37')
#print etime_2_sec('48:14')
#print etime_2_sec('00:01')
kill_proc()
