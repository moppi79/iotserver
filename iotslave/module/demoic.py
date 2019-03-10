import os, time, sys, json, random

class demoic:	
	def install(self,config):
		
		return_var = {}#you kan name here all your comparison data. ram is stored in iotclient demon
		ram = {}
		ram['1'] = 1 #name your ic pins 
		ram['data'] = config['data']
		ram['count'] = 0
		iss = {} # name your iot Devices 
		iss['1'] = {'name':'onoff_Demo','value':'0', 'typ':'on_off','usable':'1','id':'1'}
		iss['2'] = {'name':'Demo_dimmer','value':'1', 'typ':'on_off','usable':'1','id':'2'}
		
		#triggern von Plugins wenn output nur von einem Plugin kommen kann (sollte schon in der konfig vorhanden sein)
		#return_var['plugin_trigger'][1] = {'name':'onoff_Demo','value':0, 'typ':'on_off','usable':1,'id':1}

		return (ram,iss)
	
	def comparison (self,ram,iss,logging): #ram (own ram), iss (iss['random'])
		ram['count'] = ram['count'] + 1
		

		iss_update = {}
		#logging.error(json.dumps(iss[x]))
		if iss != '':
			ram[str(iss['data']['id'])] = iss['data']['value']# beispiel abfrage
			t = 1
			ram['datass'] = "inser"
		
		else:
			zufall = random.randrange(1,10)
			if (zufall == 15): ## sends data 
				print ("erzeugt")
				iss_update['22'] = {} 
				iss_update['22']['id'] = '1'
				iss_update['22']['value'] = 33
				iss_update['22']['zufall'] = zufall
				iss_update['22']['count'] = ram['count']
				iss_update['22']['FAKE_DATA'] = 'it was in'
				iss_update['21'] = {} 
				iss_update['21']['id'] = '2'
				iss_update['21']['value'] = ram['1']
				ram['a'] = "a"
				ram['id'] = 3
			else:
				ram[zufall] = zufall 

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
		
		print(iss_update)	
		return([ram,iss_update])