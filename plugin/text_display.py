import os, time, sys, logging, datetime, random

class text_display:
	
	def install(self):
		return_data = {}
		
		
		return_data['name'] = 'text_display' 
		return_data['display_typ'] = 'text' 
		return_data['next'] = 10 #delay time to the next update seconds
		
		return (return_data);