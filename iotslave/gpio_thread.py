import daemon, os, time, sys, signal, lockfile, socket, logging, datetime, json, random, configparser, fileinput

from multiprocessing import Process, Queue
from collections import defaultdict

import RPi.GPIO as GPIO

glo_ram = {}
glo_ram['ram'] = {}
glo_ram['Massage_counter'] = 0

matching = {'in':{'typ_int':'in','funk_setup':'GPIO.IN'},
			'in_down':{'typ_int':'in','funk_setup':'GPIO.IN, pull_up_down=GPIO.PUD_DOWN'},
			'in_up':{'typ_int':'in','funk_setup':'GPIO.IN, pull_up_down=GPIO.PUD_UP'},
			'out':{'typ_int':'out','funk_setup':'GPIO.OUT'},
			'pwm':{'typ_int':'out','funk_setup':'GPIO.OUT'},
			}
			
class gpio_abruf:
	
	def sensor_install(self,ic):
		return('zero')
		
	def install(self,ic):
		#print (ic)
		ret = {}
		new_iss_number = skirmish(30)
		
		ret[new_iss_number] = {}
		ret[new_iss_number]['data'] = {}
		ret[new_iss_number]['data'] = ic['data']
		ret[new_iss_number]['data']['value'] = 0
		ret[new_iss_number]['update'] = {}
		ret[new_iss_number]['update']['new'] = 1
		
		
		return(ret)
	
	def setup (self,data):
		if 'mod' in data['data']:
			print ('###### MOD ####### MOD #########')
			matching[data['data']['typ']] = {}
			matching[data['data']['typ']]['typ_int'] = 'mod'
			matching[data['data']['typ']]['funk_setup'] = 'none'
		else:
			exec("GPIO.setup("+str(data['data']['id'])+", "+matching[data['data']['typ']]['funk_setup']+")")
		
		glo_ram['ram'][data['data']['id']] = {}
		glo_ram['ram'][data['data']['id']]['value'] = 0
		
		if matching[data['data']['typ']]['typ_int'] == 'out':
			
		
			if data['data']['typ'] == 'pwm':
				glo_ram['ram'][data['data']['id']]['pwm'] = GPIO.PWM(data['data']['id'],data['data']['hz'])
				glo_ram['ram'][data['data']['id']]['pwm'].ChangeDutyCycle(data['data']['value'])
				glo_ram['ram'][data['data']['id']]['value'] = data['data']['value']
			else:
				glo_ram['ram'][data['data']['id']]['value'] = data['data']['value']
				GPIO.output(data['data']['id'], data['data']['value'])
		
		
		
	def comparison(self,ram,data,logger):
		ret = {}
		#print ('aaaa')
		#print (ram)
		#print ('aaaa')
		if data != '':
			mod = 1
			ret_mod = {}
			if ram['data']['typ'] == 'pwm':
				
				glo_ram['ram'][data['data']['id']]['pwm'].ChangeDutyCycle(data['data']['value'])
				glo_ram['ram'][data['data']['id']]['pwm'].ChangeFrequency(data['data']['hz'])
				glo_ram['ram'][ram['data']['id']]['value'] = data['data']['value']
				#print ("PWM")
			elif ram['data']['typ'] == 'out':
				
				GPIO.output(int(data['data']['id']), int(data['data']['value']))
				glo_ram['ram'][ram['data']['id']]['value'] = data['data']['value']
				print ("out")
			
			else:
				#ist gedacht für infrarot module oder ähnliches was etwas rechpower brauch. 
				#es benötigt noch eine load funktion in der setup def und hier ein start und ende
				#wird später eingebaut 
				data['data']['value']
				#print('Datenübertragung zum MOD !!!!')
				ret_mod = {1:1,"krams":7777,'value':'la la la'}
				
			
			new_iss_number = skirmish(30)
			ret[new_iss_number] = {}
			ret[new_iss_number]['sender'] = {}
			ret[new_iss_number]['update'] = {}
			#ret[new_iss_number]['sender']['name'] = {}
			ret[new_iss_number]['sender']['name'] = ram['icname']
			
			ret[new_iss_number]['data'] = {}
			if ret_mod != {}:
				ret[new_iss_number]['data'] = ret_mod 
			else:
				ret[new_iss_number]['data']['value'] = glo_ram['ram'][ram['data']['id']]['value']
			ret[new_iss_number]['data']['id'] = ram['data']['id']
			ret[new_iss_number]['update']['new'] = 0
			
			ret[new_iss_number]['counter'] = glo_ram['Massage_counter'] 
			glo_ram['Massage_counter'] = glo_ram['Massage_counter'] + 1
			
		else: #wenn keine daten übermittelet wurden aber dennoch mod geprüft werden muss 
			
			if matching[ram['data']['typ']]['typ_int'] == 'mod':
				print ('hier daten schiebe')
				#muss noch erstellt werden.
		
			
		if matching[ram['data']['typ']]['typ_int'] == 'in':
			
			if GPIO.input(int(ram['data']['id'])) != glo_ram['ram'][ram['data']['id']]['value']:
				print ("ungleich")
				glo_ram['ram'][ram['data']['id']]['value'] = GPIO.input(ram['data']['id'])
			
			
				new_iss_number = skirmish(30)
				ret[new_iss_number] = {}
				ret[new_iss_number]['sender'] = {}
				ret[new_iss_number]['update'] = {}
				#ret[new_iss_number]['sender']['name'] = {}
				ret[new_iss_number]['sender']['name'] = ram['icname']
				
				ret[new_iss_number]['data'] = {}
				ret[new_iss_number]['data']['value'] = glo_ram['ram'][ram['data']['id']]['value']
				ret[new_iss_number]['data']['id'] = ram['data']['id']
				ret[new_iss_number]['update']['new'] = 0
				
				ret[new_iss_number]['counter'] = glo_ram['Massage_counter'] 
				glo_ram['Massage_counter'] = glo_ram['Massage_counter'] + 1
				
		
			
					
				
		#print (ret)
		return(ret)
		
def skirmish(length): #zufallsgenerator
	ausgabe = ''
	for x in range(0,length):
		#print (x)
		zufall = random.randrange(1,4)
	
		if (zufall == 1):
			ausgabe = ausgabe + str(random.randrange(0,10))
		if (zufall == 2):
			ausgabe = ausgabe + chr(random.randrange(65,91))
		if (zufall == 3):
			ausgabe = ausgabe + chr(random.randrange(97,123))
	return(ausgabe)			

class thread_gpio: #Thread 
	
	def run(system,chips,in_data,out_data,logger):
		
		#print (system)
		#print (chips)
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		#print ('########## TREAD START ########')
		call = gpio_abruf()
		count = 1
		chipname_list = {}
		for x in chips:
			call.setup(chips[x])
			chipname_list[x] = {}
		
		#print (chipname_list)

		
		glo_ram = chips
		while True:
		
			count = count + 1
			
			#print ('Loop Thread gpio'+ str(count))
			
			################### ISS Abfrage Vom Haupt Prozess ANFANG #####################
			
			glo_ram['loop'] = chipname_list
			new_data = ''
			while in_data.qsize() != 0: #new data from Server/plugin
				vardd = skirmish(10)
				
				new_data = {}
				new_data[vardd] = {}
				new_data[vardd] = in_data.get()
			
			new_var = ''
			if new_data != '': #send data to Hardware
				shadow_copy = new_data.copy()
				for x in shadow_copy:
					new_var = call.comparison(glo_ram[new_data[x]['target']['name']],new_data[x],logger)
					out_data.put(new_var)
					if new_data[x]['target']['name'] in glo_ram['loop']:
						del glo_ram['loop'][new_data[x]['target']['name']]
					#print('old delte')
					
			for x in glo_ram['loop']: #call Hardware to checkup
				
				new_var = call.comparison(glo_ram[x],'',logger)
				if new_var != {}:
					#print ('send data')
					#print (new_var)
					out_data.put(new_var)
			
			################### ISS Abfrage Vom Haupt Prozess ENDE #####################
			
			
			time.sleep(0.06)
			if count == 600:##Secure Debug Break (Delete after)
				break
		
		