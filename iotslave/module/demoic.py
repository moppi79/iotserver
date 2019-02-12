import os, time, sys, json

class demoic:	
	def install(self,config):
		
		return_var = {}#you kan name here all your comparison data. ram is stored in iotclient demon
		ram = {}
		ram['1'] = 1 #name your ic pins 
		
		
		
		iss = {} # name your iot Devices 
		iss[1] = {'name':'onoff_Demo','value':'0', 'typ':'on_off','usable':'1','id':'1'}
		
		#triggern von Plugins wenn output nur von einem Plugin kommen kann (sollte schon in der konfig vorhanden sein)
		#return_var['plugin_trigger'][1] = {'name':'onoff_Demo','value':0, 'typ':'on_off','usable':1,'id':1}
		
		
		return ([ram,iss])
	
	def comparison (self,ram,iss,logging): #ram (own ram), iss (iss['random'])
		t = 0
		for x in iss:
			#print (iss)
			#logging.error(json.dumps(iss[x]))
			ram[str(iss[x]['data']['id'])] = iss[x]['data']['value']# beispiel abfrage
			t = 1
			#print (iss[x]['data']['value'])
			#do write data in the hardware ic´s 
		'''
		Here you read out your IC 
		write date into und put data back in the ram
		you must wrote a iss update 
		ram = {} <-- container create
		ram[x]  = {} <-- random chars
		ram[x]['id'] <-- id 
		ram[x]['value'] <-- value 
		ram[x]['data'] <-- optional data
		
		'''
		iss_update = ''
		if t != 0:
			iss_update = {}
			iss_update['22'] = {} 
			iss_update['22']['id'] = '1'
			iss_update['22']['value'] = ram['1']
			
		return([ram,iss_update])