from multiprocessing import Process, Queue
import os, time, random, datetime, json

class basic2:
	
	def install(self,logger): #install im ram 
		#logger.debug('install theard')
		print ('###################### BASIC2 ###########################')
		ret = {}
		
		ret['name'] = 'basic'
		
		ret['iss'] = {}
		ret['iss'][1] = {}
		ret['iss'][1]['id'] = 'lampe'
		ret['iss'][1]['typ'] = 'on_off'
		ret['iss'][1]['value'] = '0'
			
		return(ret)
		
	def work (self,data_work):
		print ('############################ RUN ################################')
		ret = {}
		
		if data_work != '':
			
			
			
			now = datetime.datetime.now()
			ttt = now.second
			if 'time' in self.ram:
				
				if ttt != self.ram['time']:
					self.ram['time'] = ttt
					print (self.ram)
					logger.error('new time {}'.format(ttt))
					#if self.ram['gir']['']
				
			else:
				self.ram['time'] = ttt
			
			'''
				array = {}
				array[1] = {}
				array[1]['data'] = {}
				array[1]['update'] = {}
				
			#ram['gir'][data_work['host']][data_work['zone']][data_work['system']][data_work['id']]['value']
			
				array[1]['update']['new'] = 0
				array[1]['data']['id'] = 'lampe'
				array[1]['data']['value'] = data_work['data']['value']
				'''
		else:
				
	
			x = 2
		
		return (ret)
		
	def time (self,data):
		if data == 'get':
				
			now = datetime.datetime.now()
				
			return (str(now.day)+':'+str(now.hour)+':'+str(now.minute)+':'+str(now.second))
			
		else:
			now = datetime.datetime.now()
				
			d,h,m,s = data.split(':')
			
			nowstamp = ((now.day*86400)+(now.hour*3600)+(now.minute*60)+(now.second))
				
			laststamp = ((int(d)*86400)+(int(h)*3600)+(int(m)*60)+(int(s)))
		
			return (nowstamp - laststamp)
				