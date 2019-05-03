import os, time, sys, logging, datetime, random

class text_display:
	
	def install(self,logger):
		print ('############################ install text_display ################################')
		return_data = {}
		
		return_data ['name'] = 'text_display'
		
		return_data['iss'] = {}
		return_data['iss'][1] = {}
		return_data['iss'][1]['id'] = 'display_tisch'
		return_data['iss'][1]['typ'] = 'text'
		return_data['iss'][1]['value'] = ''
		
		
		#return_data['name'] = 'text_display' 
		#return_data['display_typ'] = 'text' 
		#return_data['next'] = 10 #delay time to the next update seconds
		
		return (return_data);
		
	def work (self,data_work,gir,ownram,logger):
		#print ('############################ RUN text_display ################################')
		x = 1
		return(['',ownram])