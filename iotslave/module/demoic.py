import os, time, sys

class demoic:	
	def install(self,config,number):
		
		return_var = {}#you kan name here all your comparison data. ram is stored in iotclient demon
	
		return_var['id_1'] = 1 #name your ic pins 
		
		
		
		return_var['iss'] = {} # name your iot Devices 
		return_var['iss'][1] = {'name':'onoff_Demo','value':0, 'typ':'on_off','usable':1,'id':1}
		
		#triggern von Plugins wenn output nur von einem Plugin kommen kann (sollte schon in der konfig vorhanden sein)
		#return_var['plugin_trigger'][1] = {'name':'onoff_Demo','value':0, 'typ':'on_off','usable':1,'id':1}
		
		
		return (return_var)
	
	def comparison (self,ram,iss): #ram (own ram), iss (iss['random'])
		t = 0
		for x in iss:
			ram['id_'+chr(iss[x]['id'])] = iss[x]['value']# beispiel abfrage
			t = 1
			
			#do write data in the hardware ic´s 
		'''
		Here you read out your IC 
		write date into und put data back in the ram
		you must wrote a iss update 
		ram[iss]  = {} <-- container create
		ram[iss][x]  = {} <-- random cars
		ram[iss][x]['id'] <-- id 
		ram[iss][x]['value'] <-- value 
		ram[iss][x]['data'] <-- optional data
		
		'''
		
		if t != 0:
			ram['iss'] = {}
			ram['iss']['22']  = {} 
			ram['iss']['22']['id'] = 'id_1'
			ram['iss']['22']['value'] = ram['id_1']
			
			 
		
		return(ram)