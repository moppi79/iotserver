import os, time, sys

class demoic:	
	def install(self,config,number):
		
		return_var = {}
	
		return_var[1] = 0
		return_var['iot'] = {}
		return_var['iot'][1] = {'name':'onoff_Demo','value':0, 'typ':'on_off','usable':1,'id':1}
		
		#triggern von Plugins wenn output nur von einem Plugin kommen kann (sollte schon in der konfig vorhanden sein)
		#return_var['plugin_trigger'][1] = {'name':'onoff_Demo','value':0, 'typ':'on_off','usable':1,'id':1}
		
		
		return (return_var)
	
	def comparison (self,ram):
		
		
		return(ram)
