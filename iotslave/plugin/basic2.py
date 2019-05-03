from multiprocessing import Process, Queue
import os, time, random, datetime, json
#### zum Virtuellen Aktor umbauen
class gir_check:
	
	def __init__(self):
		self.loop = 0
		self.max_value = 0
		self.return_value = True

	def check(self,target,values): #prüft ob inhalt vorhanden, gibt true oder false aus
		self.loop = -1
		self.return_value = True
		self.max_value = 0
		
		for k in values:
			self.max_value = self.max_value + 1

		self.rekursiv(target,values)
		
		return(self.return_value)

	def rekursiv (self,target,value):
		self.loop = self.loop + 1
		if value[self.loop] in target:
			if type (target[value[self.loop]]) == dict:
				if (self.loop + 1) != self.max_value:
					self.rekursiv(target[value[self.loop]],value)
				
		else:
			self.return_value = False

class basic2:
	
	def install(self,logger): #install im ram 
		#logger.debug('install theard')
		#print ('###################### BASIC2 ###########################')
		ret = {}
		
		ret['name'] = 'basic2'
		
		ret['iss'] = {}
		ret['iss'][1] = {}
		ret['iss'][1]['id'] = 'lampe'
		ret['iss'][1]['typ'] = 'on_off'
		ret['iss'][1]['value'] = '0'
			
		return(ret)
		
	def work (self,data_work,gir,ownram,logger):
		ret = {}
		check_verzeichniss = gir_check()
		if data_work != '':

			now = datetime.datetime.now()
			ttt = now.second
			if 'time' in self.ram:
				
				if ttt != self.ram['time']:
					self.ram['time'] = ttt
					##print (self.ram)
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
			array = {}
			array[1] = {}
			array[1]['target'] = {}
			array[1]['data'] = {}
			array[1]['target']['host'] = 'raspi2'
			array[1]['target']['name'] = 'demoic'
			array[1]['target']['zone'] = 'balkon'
			array[1]['target']['system'] = 'i2c'
			array[1]['data']['id'] = '1'
			ownram[1] = 1111
			#print ('in thread data')
			#print (gir)
			#print ('in thread data')
			if check_verzeichniss.check(gir,['raspi2','balkon','i2c','demoic','1']) == True:
				#print ('###########---################')
				#print (gir['raspi2']['balkon']['i2c']['demoic']['1']['value'])
				if gir['raspi2']['balkon']['i2c']['demoic']['1']['value'] == '1':
					array[1]['data']['value'] = 0
					#print ('########### HIER DIE 0 ###############')
				else:
					array[1]['data']['value'] = 1
					#print ('########### HIER DIE 1 ###############')
		
		return (['',ownram])
		##return ([array,ownram])
		
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
				