import daemon, os, time, sys, signal, lockfile, socket, logging, datetime, json, random, configparser, fileinput

from multiprocessing import Process, Queue
from collections import defaultdict

from i2c_thread import thread_i2c, i2c_abruf
from gpio_thread import thread_gpio, gpio_abruf

from TCP_Thread import TCP_run,server_coneckt

from iss_helper import iss_create

import RPi.GPIO as GPIO


config = configparser.ConfigParser()
config.read('../config.py')

ic_class = {}

sensor = {}

global ram			
ram = defaultdict(object)
ram = {}

ram['pluginhold'] = {}
ram['gpio'] = {}


iss = {} #IoT space system

gir = {} #Global IoT RAM

ic_chip = defaultdict(object)

sensordic = defaultdict(object)		

#plugin_class = {'basic2','text_display','io_basic'}
for x in config['module']:
	if config['module'][x] == "1":
		exec('from module.'+x+' import '+x+'') 
		exec("ic_class['"+x+"'] = "+x+"()")

for x in config['sensors']:
	if config['sensors'][x] == "1":
		exec('from sensors.'+x+' import '+x+'') 
		
plugin_class = {}	
for x in config['plugin']:
	if config['plugin'][x] == "1":
		plugin_class[x] = 1

#from plugin.basic import basic

############## load working classes ############
from thread import thread_class


############## load working classes ############

HOST, PORT = config['SERVER']['Adress'], int(config['SERVER']['Port']) ##adresse und port vom server-server

workingpath = config['GLOBAL']['workingpath']

logger = logging.getLogger()
logger.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh = logging.FileHandler(config['GLOBAL']['workingpath']+'/'+config['Slave_Basic']['logname'])
fh.setFormatter(formatter)
logger.addHandler(fh)

master_pfad = '/net'
master_pidfile = '/net/master' #pidfile verzeichniss/name

i2cswitch = {'adress':int(config['Slave_Basic']['switch_adress'],16),'port':int(config['Slave_Basic']['switch_port'])} #TI-PCA9548A
#i2cswitch = {'adress':0x70,'port':int(config['Slave_Basic']['switch_port'])} #TI-PCA9548A
ic_list = {'host':config['Slave_Basic']['Name'],'zone':config['Slave_Basic']['Zone'], 'switch':int(config['Slave_Basic']['switch'])} #anzahl I2C slaves mit adresse


linee = ''	
with fileinput.input(files=('../config_ic.py')) as f:
    for line in f:
        linee = linee + line 

exec(linee)

###########Prüfen ob iot_ram weg kann #######
iot_ram = defaultdict(object)
iot_ram = {}
iot_ram['data'] = {} #all iot interface data from modul or Plugin
iot_ram['get'] = {} #get data from IoT server
iot_ram['send'] = {} #send data to IoT server
###########Prüfen ob iot_ram weg kann #######

class gpio:
	
	def __init__(self):# intiate interface and install all ports in server
		
		ram['bus_stack'] = {}
		ram['start_param'] = {}
		for x in ic_chip:
			if ic_chip[x]['bus'] in ram['bus_stack']:
				ram['bus_stack'][ic_chip[x]['bus']][ic_chip[x]['icname']] = ic_chip[x]
			else: 
				ram['bus_stack'][ic_chip[x]['bus']]= {}
				ram['bus_stack'][ic_chip[x]['bus']][ic_chip[x]['icname']] = ic_chip[x]
		

		print (ram['bus_stack'])
		
		for x in ram['bus_stack']:#Regestrie alle Aktoren in den Bus
			for y in ram['bus_stack'][x]:
				ram['bus_'+x] = {}
				#ram['bus_'+x]['queue_in'] =
				#ram['bus_'+x]['queue_out'] =
				call = {}
				exec("call['"+ x +"'] = "+ x +"_abruf()")
				install_data = call[x].install(ram['bus_stack'][x][y])
				for z in install_data: #Verschiebe install daten von modul 
					if z == 'ram': #eigener ram vom Plugin 
						ram['bus_stack'][x][y]['ram'] = {}
						ram['bus_stack'][x][y]['ram'] = install_data['ram']
						
						
					else:
						self.data_to_iss(z,x,ram['bus_stack'][x][y]['icname'],install_data[z])

		
		data_iss = {}
		sensor_for = 0
		
		for x in sensor: #only runs on Sensor entrys
			
			if 'data_standart' not in ram['bus_stack'][sensor[x]['bus']]:
				ram['bus_stack'][sensor[x]['bus']]['data_standart'] = {}
				ram['bus_stack'][sensor[x]['bus']]['sensor_update'] = {}
				ram['bus_stack'][sensor[x]['bus']]['sensor'] = {}
				for g in config['sensors']:
				#print (config['sensors'][x])
					
					ram['bus_stack'][sensor[x]['bus']]['sensor_update'][g] = ''
					ram['bus_stack'][sensor[x]['bus']]['sensor_update'][g] = config['sensors'][g]
			ram['bus_stack'][sensor[x]['bus']]['sensor'][x] = sensor[x]
			b = sensor[x]
			call = {}
			exec("call['"+ sensor[x]['bus'] +"'] = "+ sensor[x]['bus'] +"_abruf()")
			a = call[sensor[x]['bus']].sensor_install(b)
			print ('#####SENSOR#########')
			print (sensor)
			print (a)
			
			
			for y in a[2]: #ISS Create
			
				self.data_to_iss(y,sensor[x]['bus'],"sensor",a[2][y])
			
			for y in a[1]: #Standart Konfig betanken
				
				ram['bus_stack'][sensor[x]['bus']]['data_standart'][y] = a[1][y]
				
		
		print ('#############SENSOR DATA##############') 
		#print (ram['bus_stack'][sensor[x]['bus']])
		self.Prepare_start()# starting all threads
		
		
	def data_to_iss(self,iss_id,system,name,data): #ISS generator 
		iss[iss_id] = {}
		iss[iss_id]['sender'] = {}
		iss[iss_id]['update'] = {}
		iss[iss_id]['data'] = {}
		
		iss[iss_id]['sender']['host'] = ic_list['host']
		iss[iss_id]['sender']['zone'] = ic_list['zone']
		iss[iss_id]['sender']['name'] = name
		iss[iss_id]['sender']['system'] = system
		
		iss[iss_id]['update'] = data['update']
		iss[iss_id]['data'] = data['data']
		
		iss[iss_id]['counter'] = ram['Massage_counter'] ######### Hier neu 
						
		ram['Massage_counter'] = ram['Massage_counter'] + 1 
		
		
	
	def skirmish(self, length): #zufallsgenerator
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
	
	def Prepare_start(self):#prepare system and start new treahd
		for x in ram['bus_stack']:
			self.start(x)


	def start(self,x): # Singele Start Thread
		print ("start")
		print (x)
		ram['gpio'][x] = {}
		ram['gpio'][x]['name'] = x		#thread_run = thread_class()
		
		#install = plugin_class[ram['gpio'][name]['name']]
		config = {} #config data übertragen
		config['host'] = ic_list['host']
		config['zone'] = ic_list['zone']
		config['name'] = ram['gpio'][x]['name']
		ram['gpio'][x]['queue_in'] = Queue() # Queue erstellen iput from Plugin
		ram['gpio'][x]['queue_out'] = Queue() # Queue erstellen send data to Plugin 
		
		if x == "i2c":
			ram['gpio'][x]['prozess'] = Process(target=thread_i2c.run, name=ram['gpio'][x]['name'], args=(config, ram['bus_stack'][x], ram['gpio'][x]['queue_out'], ram['gpio'][x]['queue_in'],logger)) #prozess vorbereiten
		
		if x == "gpio":
			ram['gpio'][x]['prozess'] = Process(target=thread_gpio.run, name=ram['gpio'][x]['name'], args=(config, ram['bus_stack'][x], ram['gpio'][x]['queue_out'], ram['gpio'][x]['queue_in'],logger)) #prozess vorbereiten

		ram['gpio'][x]['prozess'].start() # Prozzes starten

	
	def end (self):# kill all Threads and queue
		for x in ram['bus_stack']:
			logger.error('end Plugin:'+x)
			#ram['gpio'][x]['prozess'].join()
			ram['gpio'][x]['prozess'].terminate()
			ram['gpio'][x]['queue_in'].close
			ram['gpio'][x]['queue_out'].close
			


	def comparison(self): #Call Hardware
		
		shadow_copy = iss.copy()
		print('####abfrage#####')
		print (shadow_copy)
		for x in shadow_copy: #is data in ISS to send hardware
			new_data = ''
			print ("ja hier daten")
			print (shadow_copy[x])
			if 'target' in shadow_copy[x]:#Rufe alle verfügbaren Schnitstellen ab
				for y in ram['gpio']:
					
					#daten in thread hoch laden
					if (shadow_copy[x]['target']['host'] == ic_list['host']) and (shadow_copy[x]['target']['system'] == y):
						
						print ('###!!!!!!!#####!!!!!!#####!!!!!#####')
						ram['gpio'][y]['queue_out'].put(iss[x])
						del iss[x]
						
		
		for y in ram['gpio']: #is new data from hardware to send server/plugins
			new_data = {}
			while ram['gpio'][y]['queue_in'].qsize() != 0:
				vari = self.skirmish(5)
				new_data[vari] = {}
				new_data[vari] = ram['gpio'][y]['queue_in'].get()
			if new_data != {}:
				for o in new_data:
					for z in new_data[o]:
						print('§§§§§§§$%$%%%%!!!!!!!!!!!!! hier DATA VON IO')
						print(new_data[o])
						iss[z] = {}
						iss[z] = new_data[o][z]
						iss[z]['sender']['host'] = ic_list['host']
						iss[z]['sender']['zone'] = ic_list['zone']
						iss[z]['sender']['system'] = y



class iot:
	
	def __init__(self): 
		print ('init')
		self.submit_counter = 0

	def update(self):
		global iss
		sortiert = self.sorting_iss()#lese daten aus dem ISS 
		print ('!!!!!!!!!!!!!####sorter######!!!!!!!!!!!!!!!')
		print (sortiert)
		#server =  server_coneckt()
		logging.error('update')
		loop = 0
		for x in sortiert:
			self.submit_counter = self.submit_counter + 1
			ram['TCP-SERVER']['data_out'].put(sortiert[x]) 
			print('HIER HIER HIER')
			#iss = server.sock2({'funktion':'iot','iotfunk':'iss','messages':submit_data,'token':ram['sesession_id']})
		
		if ram['TCP-SERVER']['data_in'].empty() != True:
			while ram['TCP-SERVER']['data_in'].qsize() != 0:
				iss[thread.skirmish('',20)] = ram['TCP-SERVER']['data_in'].get()
				print ('data in')
			
		logging.error(json.dumps(iss))
		update_copy = iss.copy()
		for x in update_copy: #daten aus dem ISS löschen nach dem sie in Class Thread zum GIR hinzugefügt wurden
			if 'plugin' in update_copy[x]:
				#logging.error(json.dumps(iss[x]))
				print ('del')
				del iss[x]
				
			else:
				print ('kein plugin')


	def sorting_iss (self):#sorting double data and ignoring 
		#logging.error(json.dumps(iss))
		copy_iss = iss.copy()
		ret = {}
		for x in copy_iss:
			if copy_iss[x]['sender']['host'] == ic_list['host'] and copy_iss[x]['sender']['zone'] == ic_list['zone']:
				if 'update' in copy_iss[x]:
					print (copy_iss[x])
					if copy_iss[x]['update']['new'] == 0:
												
						if isinstance(copy_iss[x]['data']['id'],int):
							inttostr = str(copy_iss[x]['data']['id'])
						else:
							inttostr = copy_iss[x]['data']['id']
							
						name = ''+inttostr+''+copy_iss[x]['sender']['system']+''+copy_iss[x]['sender']['name']+''
						if name not in ret:
							ret[name] = {}
							ret[name] = copy_iss[x]
						
						if ret[name]['counter'] > copy_iss[x]['counter']:
							ret[name] = copy_iss[x]
					else:
						
						if isinstance(copy_iss[x]['data']['id'],int):
							inttostr = str(copy_iss[x]['data']['id'])
						else:
							inttostr = copy_iss[x]['data']['id']
							
						name = ''+inttostr+''+copy_iss[x]['sender']['system']+''+copy_iss[x]['sender']['name']+''
						ret[name] = {}
						ret[name] = copy_iss[x]
		
		logging.error('transfer DATA')			
		logging.error(json.dumps(ret))
		return(ret)
		
class thread: #ausführen von einzelen plugins im hintergrund0
	
	def __init__(self): #install im ram 
	
		
		for x in plugin_class: #abfrage von allen plugins
			
			thread_install_data = thread_class()

			ausgabe = thread_install_data.install_thread_data(x,logger)
			
			#ausgabe = install.install(logger)
			
			new_value = self.skirmish(5)
			ram['pluginhold'][new_value] = {} #erzeugen Container
			ram['pluginhold'][new_value]['name'] = x
			
			if 'iss' in ausgabe: ## wenn iot daten bei der install schon in den bus müssen 
				'''
				grounddata = {}	
				grounddata['sender'] = {}
				grounddata['sender']['host'] = ic_list['host']
				grounddata['sender']['zone'] = ic_list['zone']
				grounddata['sender']['name'] = ausgabe['name']
				grounddata['sender']['system'] = 'plugin'
				grounddata['update'] = {}
				grounddata['update']['new'] = 1
				'''	
				for a in ausgabe['iss']:
					dataskirmisch = self.skirmish(10)
					iss[dataskirmisch] = {}
					#iss[dataskirmisch].update(grounddata)
					
					iss[dataskirmisch]['sender'] = {}
					iss[dataskirmisch]['sender']['host'] = ic_list['host']
					iss[dataskirmisch]['sender']['zone'] = ic_list['zone']
					iss[dataskirmisch]['sender']['name'] = ausgabe['name']
					iss[dataskirmisch]['sender']['system'] = 'plugin'
					iss[dataskirmisch]['update'] = {}
					iss[dataskirmisch]['update']['new'] = 1
					
					iss[dataskirmisch]['counter'] = ram['Massage_counter'] 
					ram['Massage_counter'] = ram['Massage_counter'] + 1
					
					iss[dataskirmisch]['data'] = ausgabe['iss'][a]
				
			self.thread_start(new_value,'')
			
			
	def thread_start(self,name,girdata): #start thread 
		print ("start")
		thread_run = thread_class()

		#install = plugin_class[ram['pluginhold'][name]['name']]
		config = {} #config data übertragen
		config['host'] = ic_list['host']
		config['zone'] = ic_list['zone']
		config['name'] = ram['pluginhold'][name]['name']
		
		ram['pluginhold'][name]['queue_in'] = Queue() # Queue erstellen iput from Plugin
		ram['pluginhold'][name]['queue_out'] = Queue() # Queue erstellen send data to Plugin
		ram['pluginhold'][name]['prozess'] = Process(target=thread_run.run, name=ram['pluginhold'][name]['name'], args=(ram['pluginhold'][name]['queue_out'],ram['pluginhold'][name]['queue_in'],config,girdata,logger)) #prozess vorbereiten
		ram['pluginhold'][name]['prozess'].start() # Prozzes starten
	
	def comparison(self):
		for x in ram['pluginhold']:# check theard is alive or restart target prozess
			if ram['pluginhold'][x]['prozess'].is_alive() == True:
				#print ('ich lebe')
				kkkkkk = 1
			else:
				self.thread_start(x,gir)
				logger.error('Plugin death:'+ram['pluginhold'][x]['name'])
				print ('bin tot '+ram['pluginhold'][x]['name'])
		
		
		shadow_copy = iss.copy()

		#print (shadow_copy)
		
		for i in shadow_copy: #send data to Plugin
			if 'update' in shadow_copy[i]: #update global IoT data 
				
				if 'plugin' not in shadow_copy[i]: # wenn data schon übermittelt wurden
					new_gir = {}
					
					new_gir['gir'] = self.array_create(shadow_copy[i]) #transform Gir für die übermittlung 
					
					iss[i]['plugin'] = 1 #zur überprüfung damit daten nicht doppelt übermittelt werden
					#del iss[i]
					for x in ram['pluginhold']:
						#logger.error(json.dumps(new_gir))
						#print ('transmit data')
						#print (new_gir)
						#print ('transmit data')
						
						ram['pluginhold'][x]['queue_out'].put(new_gir)

			else: # check is target 
			
				if iss[i]['target']['system'] == 'plugin':
					for x in ram['pluginhold']: #Put data to Plugin this is target
						
						if iss[i]['target']['name'] == ram['pluginhold'][x]['name']:
							ram['pluginhold'][x]['queue_out'].put(iss[i])
							print ('del iss plugin')
							del iss[i]
							
						#ram['pluginhold'][x]['queue_out'].put(iss[i])
					#del iss[i]
		shadow_copy.clear()
		
				
		for x in ram['pluginhold']:
			##abfrage vom,thread
			
			z = 1
			ausgabe = {}
			if ram['pluginhold'][x]['queue_in'].empty() != True:
				
				
				while ram['pluginhold'][x]['queue_in'].qsize() != 0: #alle verfügabren daten abrufen 
						print('###########data call###############')
						data1 = ram['pluginhold'][x]['queue_in'].get()
						ausgabe[z] = data1
						z = z + 1
				
				if z != 1:
					for k in ausgabe:
						
						new_key = self.skirmish(10)
						iss[new_key] = ausgabe[k] #data , id , value, ['target']['host'] , etc,
						iss[new_key]['sender'] = {}
						iss[new_key]['sender']['host'] = ic_list['host']
						iss[new_key]['sender']['zone'] = ic_list['zone']
						iss[new_key]['sender']['name'] = ram['pluginhold'][x]['name']
						iss[new_key]['sender']['system'] = 'plugin'
						iss[new_key]['counter'] = ram['Massage_counter'] 
						ram['Massage_counter'] = ram['Massage_counter'] + 1
						print ('#########new data################')
						print (iss[new_key])
						#print ('new data')
					#print (array1)
				##übertragen von daten zum Thread
			#print (iss)
			
	def end(self): # clean up

		for x in ram['pluginhold']:
			logger.error('end Plugin:'+ram['pluginhold'][x]['name'])
			#ram['pluginhold'][x]['prozess'].join()
			ram['pluginhold'][x]['prozess'].terminate()
			ram['pluginhold'][x]['queue_in'].close
			ram['pluginhold'][x]['queue_out'].close
		
		del ram['pluginhold']
			
			

	def skirmish(self, length): #zufallsgenerator
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
		
	def array_create(self,data): ##update und retrn data satz
		#print ('array_create')
		#print (data)
		ret = {}
		
		if data['sender']['host'] in gir:
			ret[data['sender']['host']] = {}
			
		else:
			gir[data['sender']['host']] = {}
			ret[data['sender']['host']] = {}

		if data['sender']['zone'] in gir[data['sender']['host']]:
			ret[data['sender']['host']][data['sender']['zone']] = {}
		else:
			gir[data['sender']['host']][data['sender']['zone']] = {}
			ret[data['sender']['host']][data['sender']['zone']] = {}
			
		if data['sender']['system'] in gir[data['sender']['host']][data['sender']['zone']]:
			ret[data['sender']['host']][data['sender']['zone']][data['sender']['system']]  = {}
			
		else:
			gir[data['sender']['host']][data['sender']['zone']][data['sender']['system']]  = {}
			ret[data['sender']['host']][data['sender']['zone']][data['sender']['system']]  = {}
			
		if data['sender']['name'] in gir[data['sender']['host']][data['sender']['zone']][data['sender']['system']]:
			ret[data['sender']['host']][data['sender']['zone']][data['sender']['system']][data['sender']['name']] = {}
			
		else:
			
			gir[data['sender']['host']][data['sender']['zone']][data['sender']['system']][data['sender']['name']] = {}
			ret[data['sender']['host']][data['sender']['zone']][data['sender']['system']][data['sender']['name']] = {}

		if data['data']['id'] in gir[data['sender']['host']][data['sender']['zone']][data['sender']['system']][data['sender']['name']]:
			ret[data['sender']['host']][data['sender']['zone']][data['sender']['system']][data['sender']['name']][data['data']['id']] = {}
			
		else:
			
			gir[data['sender']['host']][data['sender']['zone']][data['sender']['system']][data['sender']['name']][data['data']['id']] = {}
			ret[data['sender']['host']][data['sender']['zone']][data['sender']['system']][data['sender']['name']][data['data']['id']] = {}

		
		for x in data['data']:
			if x != 'id':
				#print (x)
				gir[data['sender']['host']][data['sender']['zone']][data['sender']['system']][data['sender']['name']][data['data']['id']][x] = data['data'][x]
				ret[data['sender']['host']][data['sender']['zone']][data['sender']['system']][data['sender']['name']][data['data']['id']][x] = data['data'][x]
		
		
		'''
		gir[data['sender']['host']][data['sender']['zone']][data['sender']['system']][data['sender']['name']][data['data']['id']]['value'] = data['data']['value']
		if 'typ' in data['data']:
			gir[data['sender']['host']][data['sender']['zone']][data['sender']['system']][data['sender']['name']][data['data']['id']]['typ'] = data['data']['typ']
		else:
			gir[data['sender']['host']][data['sender']['zone']][data['sender']['system']][data['sender']['name']][data['data']['id']]['typ'] = gir[data['sender']['host']][data['sender']['zone']][data['sender']['system']][data['sender']['name']][data['data']['id']]['typ']

		ret[data['sender']['host']][data['sender']['zone']][data['sender']['system']][data['sender']['name']][data['data']['id']]['value'] = data['data']['value']
		if 'typ' in data['data']:
			ret[data['sender']['host']][data['sender']['zone']][data['sender']['system']][data['sender']['name']][data['data']['id']]['typ'] = data['data']['typ']
		else:
			ret[data['sender']['host']][data['sender']['zone']][data['sender']['system']][data['sender']['name']][data['data']['id']]['typ'] = gir[data['sender']['host']][data['sender']['zone']][data['sender']['system']][data['sender']['name']][data['data']['id']]['typ']
		'''

		return (ret)

class server_coneckt2alt:
	
	def __init__(self):
		
		if 'server_install' in ram:
			ram['server_install'] = ram['server_install']  #platzhalter
			
		else:
			ram['server_install'] = 1 #platzhalter
			transfer = defaultdict(object)
			transfer = {'funktion':'add'} #auszuführende Funktion im server
			transfer.update(ic_list) #funktions infos client
			#transfer['iot'] = {}
			#wichtig bei übermittluhng wird nur IoT verwendet. iot[ic_chip][aktor]
			'''
			for x in ic_chip:
				transfer['iot'][x] = ram[ic_chip[x]['icname']][x]['iot'] #aktorenliste
			'''
			#transfer['iot'] = iot_ram['data']
			
			ret = self.sock2(transfer)
			#print (ret)
			logger.error(json.dumps(ret))
			if 'sesession_id' in ret:
				
				ram['sesession_id'] = ret['sesession_id']
			else:
				logger.error('Fehler bei install daten in Master Server')	
			
			'''
			#ret = '"ok"'
			if ret != '"ok"':
				logger.error('Fehler bei install daten in Master Server')
				#print (ret)
			'''

	def check(self):
	
		verbindung = server_coneckt() #Client steuerung 
		#logger.error('check')
		data = {'funktion':'check','zone':ic_list['zone'], 'host':ic_list['host']}
		antwort = verbindung.sock2(data)
		if antwort != 'ok':
			logger.error('änderung check')
			ram['stop'] = antwort['stop']
			logger.error(json.dumps(antwort))
			ram['webupdate'] = antwort['webupdate']#!!!! muss eine ifabrfrage werden (aber auchg nur wichtig wenn KEIN Switch eingebaut ist !!!!!!!)
			ram['kill'] = antwort['kill']
			ram['sensor'] = antwort['sensor']
			
			if antwort['tsupdate'] == 1:
				logger.error('new Time')
				ram['timeslice'] = self.timeslice()
				
		return ('---') ### 
		
	def timeslice(self):
			transfer = defaultdict(object)
			transfer = {'funktion':'timeslice', 'zone':ic_list['zone'], 'host':ic_list['host']} #auszuführende Funktion im server
			transfer.update(ic_list) #funktions infos client
			#jsonstring = json.dumps(transfer)
			#ret = self.sock(jsonstring)
			
			#umwandel = json.loads(ret)
			umwandel = self.sock2(transfer)
			return (umwandel)
			
	def sock(self, data):#befehl an Server senden und Rückanwort empfangen
		
		server_address = ('localhost', 5050)#server adresse
		print('connecting to {} port {}'.format(*server_address))
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#art der verbingdung
		sock.connect(server_address)#verbindung herstellen
		sock.sendall(data.encode('utf8'))#befehl senden
		datain = sock.recv(1024).strip()#daten empfangen und leerzeichen entfernen
		sock.close()
		return datain.decode('utf-8') #return daten
	
	def sock2(self, data):#befehl an Server senden und Rückanwort empfangen
		
		if 'funktion' in data:
			json_string = json.dumps(data)
			print (json_string)
			if data['funktion'] != 'check':
				logger.error('send data to server: {}'.format(json_string))
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
				sock.connect((HOST, PORT))
				#### SEND DATA #####
				length = len(json_string)
				sock.sendall(bytes(str(length), 'utf8'))
				response = str(sock.recv(30), 'utf8')
				sock.sendall(bytes(json_string, 'utf8'))
				#### SEND DATA #####

				###Bekome data #####
				count = str(sock.recv(30).strip(), 'utf8')
				print("Received count: {}".format(count))
				sock.sendall(bytes('ok', 'utf8'))
        
				datain = str(sock.recv(int(count)).strip(), 'utf8')
				print("Received inhalt: {}".format(datain))
				###Bekome data #####
				sock.close()
			
			try:
				returner = json.loads(datain)
			except ValueError as error:
				logger.error('Fehlerhafte daten bekommen',datain)
			
			if returner != 'ok':
				logger.error('data from server: {}'.format(json.dumps(returner)))	
			return returner #return daten
		else:
			logger.error('keine funktion übermittelt')
			return 'error'

def time_get (data): #time stamp generator
		if data == 'get':
			
			now = datetime.datetime.now()
			
			return (str(now.day)+':'+str(now.hour)+':'+str(now.minute)+':'+str(now.second)+':'+str(now.microsecond))
		
		else: # 
			now = datetime.datetime.now()
			
			d,h,m,s,ms = data.split(':')
			
			nowstamp = ((now.day*86400)+(now.hour*3600)+(now.minute*60)+(now.second)+(now.microsecond))
			
			laststamp = ((int(d)*86400)+(int(h)*3600)+(int(m)*60)+(int(s))+(int(ms)))
	
			return (nowstamp - laststamp) 

def ms_time(select): #return 0 ms 1 Second 2 array with both
	now = datetime.datetime.now()
	if select == 0:
		return (now.microsecond)
	elif select == 1:
		return (now.second)
	elif select == 2:
		return (now.minute)
	elif select == 3:
		return (now.hour)
	else:
		return ({0:now.microsecond,1:now.second})

'''
hier fängt die deamon schleife an 
'''
class tcp_control:
	
	def __init__(self):

		ram['TCP-SERVER'] = {}
		ram['TCP-SERVER']['data_out'] = Queue() ### zum server 
		ram['TCP-SERVER']['data_in'] = Queue() ### Vom server
		ram['TCP-SERVER']['session_id'] = ic_list #erstmal mit standart server daten später dann nur noch Session ID 
		ram['TCP-SERVER']['thread'] = ''
		
		TCP_data = TCP_run.start(HOST, PORT,ic_list,logger)
		self.token = TCP_data
		print (TCP_data)
		print ('ja token')
		
	
	def kill (self):
		logger.error('end TCP Thread')
		print ('kill')
		ram['TCP-SERVER']['thread'].terminate()
		ram['TCP-SERVER']['data_out'].close
		ram['TCP-SERVER']['data_in'].close
	
	def start(self):
		#ram['TCP-SERVER']['thread'] 
		#TCP_run.run('',HOST, PORT,self.token,ram['TCP-SERVER']['data_in'],ram['TCP-SERVER']['data_out'],logger)
		
		ram['TCP-SERVER']['thread'] = Process(target=TCP_run.run, name='iot_tcp_provider', args=('',HOST, PORT,self.token,ram['TCP-SERVER']['data_in'],ram['TCP-SERVER']['data_out'],logger)) #prozess vorbereiten
		ram['TCP-SERVER']['thread'].start() # Prozzes starten
	
	

def main_loop():
	loopmaster = 0 #Counter wie oft Schleife gelaufen ist (für debug wichtig)
	ram['kill'] = 0
	ram['Massage_counter'] = 0 #Massage counter
	ram['iss_trasher'] = {} #Trasher variable
	run = 0 # variable für Gelaufne zeit

	freq = 20 #Aktuelle geschwindkeit
	loop_server_call = 0 # start parameter für interne Serverabfrage

	tcp = tcp_control()
	tcp.start()
	
	#time.sleep(5)
	#ram['TCP-SERVER']['data_out'].put('aaaaa')
	#ram['TCP-SERVER']['data_out'].put('bbbbb')
	
	
	
	
	##das hier kann weg
	#print('Server Initalisiern')
	#socket_call = server_coneckt()#Server verbindung starten
	#socket_call.check()
	#print('Server Initalisiern ende')
	#logger.error('server initalisiert')
	##/das hier kann weg ende
	
	
	print('thearad Initalisiern')
	plugin_obj = thread()
	print('thearad Initalisiern ende')
	logger.error('therad  initalisiert')

	print('GPIO Initalisiern')
	gpio_handler = gpio()
	logger.error('GPIO initalisiert')
	print('GPIO Initalisiern ende')
	
	iot_obj = iot()
	logger.error('iot  initalisiert')

	print('Starten While schleife ')
	'''
	iot_obj.update()
	
	time.sleep(5)
	iot_obj.update()
	time.sleep(2)
	plugin_obj.comparison()
	time.sleep(2)
	'''
	while True:
		iss_copy = iss.copy()
		for x in iss_copy:
			if 'target' in iss_copy[x]:
				if iss_copy[x]['target']['system'] == 'system':
					ram[iss[x]['data']['id']] = iss[x]['data']['value']
					del iss[x]
		'''		
		plugin_obj.end()
		gpio_handler.end()
		tcp.kill()
		print('#########RAM###########')
		print (ram)
		print('#########gir###########')
		print (gir)
		print('#########iss###########')
		print(iss)
		break
		'''
		########### Loop Time Management head #############
		start = ms_time(0)
		print (start)
		#print('start')

		########### Loop Time Management head END#############

		################### GPIO Call ###################
		for x in ram['gpio']: ##Alive Check
			if ram['gpio'][x]['prozess'].is_alive() != True:
				gpio_handler.start(x)
		
		gpio_handler.comparison()
		
		################### GPIO Call END ###################
		
		

		################### Plugin Call ###################
		
		plugin_obj.comparison()
		
		#logger.error(json.dumps(iss))
		################### Plugin Call END ###################
		
		################### Servercall ###################
		ministart = ms_time(0)
		if loop_server_call == 0 and ms_time(0) < 500000:
			logger.error('checker halb')
			loop_server_call = 1
			#socket_call.check()
			#print (ms_time(0) - ministart )
			
			
		if loop_server_call == 1 and ms_time(0) > 500000:
			logger.error('checker voll')
			loop_server_call = 0
			#socket_call.check()
			#print (ms_time(0) - ministart )
			
		
		################### ServerCall End ###################

		################### ISS Fragment Trasher ###################
		
		iss_trasher = iss.copy() ##Löscht Daten die nicht verwendet werden oder Fehlerhaft sind 
		for x in iss_trasher:
			if x in ram['iss_trasher']:
				if ram['iss_trasher'][x]['time'] != ms_time(1):
					if ram['iss_trasher'][x]['count'] <= 2:
						logger.error('ISS verworfen:')
						logging.error(json.dumps(iss[x]))
						del iss[x]
						del ram['iss_trasher'][x]
					else:
						ram['iss_trasher'][x]['count'] = ram['iss_trasher'][x]['count'] + 1 
						ram['iss_trasher'][x]['time'] = ms_time(1)
			else:
				ram['iss_trasher'][x]= {}
				ram['iss_trasher'][x]['time'] = ms_time(1)
				ram['iss_trasher'][x]['count'] = 0
				
		
		trasher = ram['iss_trasher'].copy()
		for x in trasher:
			if x not in iss:
				del ram['iss_trasher'][x]	
			
		################### ISS Fragment Trasher ###################
		
		

		################### prototypinm ###################	
		'''
		if 'proto' in ram:
			
			if ram['proto']['sec']  != ms_time(1):
				ram['proto']['sec'] = ms_time(1)
				
				ram['pcf8574'][2]['light'] = 0
				ram['pcf8574'][2]['write'] = 2
				
				ram['pcf8574'][2]['reset'] = 1
				ram['pcf8574'][2]['line1']['value'] = '{}:{}:{}'.format(str(ms_time(3)),str(ms_time(2)),str(ms_time(1)))
				ram['pcf8574'][2]['line2']['value'] = ''
				ram['pcf8574'][2]['line3']['value'] = ''
				ram['pcf8574'][2]['line4']['value'] = ''
			
		else:
			ram['proto'] = {}
			
			ram['proto']['sec'] = ms_time(1)
		'''	
		
		
		################### prototypinm END ###################	
		
		################### IoT transfer ###################	
		iot_obj.update()
		################### IoT Transfer ###################	
		
		########### Loop Time Management foot #############
		stop = ms_time(0)
		run = stop - start
		
		if run < 0: #start Stop Between zwo seconds 
			run2 = 1000000 - start
			run = run2 + stop
	
		waiter = round(1000000 / freq)# getting max time 

		wait = waiter - run 
		
		if wait < 0: #when time is out setting Sleep to 0 
			wait = 0
		
		speed = wait / 1000000 #ermittel Float
		print ('speed')
		print (speed)
		time.sleep(speed)
		
		########### Loop Time Management Foot #############
		
		if ram['kill'] == 1: ### Normal Programm end
			logger.error('kill signal')
			plugin_obj.end()
			gpio_handler.end()
			tcp.kill()
			logging.error('######## RAM #########')
			#logging.error(json.dumps(ram))
			logging.error('######## GIR #########')
			logging.error(json.dumps(gir))
			logging.error('######## ISS #########')
			logging.error(json.dumps(iss))
			
			
			logger.error('programm wurde beendet')
			time.sleep(1)
			break
			
		
		if 'loopcountdebug' == sys.argv[1]:
			loopmaster += 1
			if loopmaster > int(sys.argv[2]):
				print ('######## RAM #########')
				print(ram)
				print ('######## GIR #########')
				print(gir)
				print ('######## ISS #########')
				print(iss)
				plugin_obj.end()
				gpio_handler.end()
				tcp.kill()
				tcp = server_coneckt(HOST,PORT,logger)
				antwort = tcp.sock2({'funktion':'delete','zone':ic_list['zone'],'host':ic_list['host']})
				
				#print (ram['timeslice'])
				print ('programm ende')
				break #zum solo testen muss am schluss entfernt werden
			
			print (loopmaster)

		
		if 'singledebug' == sys.argv[1]:
			plugin_obj.end()
			gpio_handler.end()
			tcp.kill()
			tcp = server_coneckt(HOST,PORT,logger)
			antwort = tcp.sock2({'funktion':'delete','zone':ic_list['zone'],'host':ic_list['host']})
			print (antwort)
			print ('######## RAM #########')
			print(ram)
			print ('######## GIR #########')
			print(gir)
			print ('######## ISS #########')
			print(iss)
			break #muss zum ende entfernt werden


context = daemon.DaemonContext( #daemon konfig
	working_directory= workingpath ,
   	umask=0o002,
   	files_preserve = [
   		fh.stream,
    ],

)


if len(sys.argv) != 1:
	if 'start' == sys.argv[1]:
		print("wird gestartet ...")
		with context:
			main_loop()
	elif 'stop' == sys.argv[1]:
		print ("stopping Client")
		testersa = {'funktion':'stop','zone':ic_list['zone'] ,'host':ic_list['host'], 'kill':'1'}
			
		antwort = server_coneckt.sock2('',testersa)
		while True:
			testersa = {'funktion':'stop','zone':ic_list['zone'] ,'host':ic_list['host']}
			antwort = server_coneckt.sock2('',testersa)
			time.sleep(1)
			if antwort == 'kill':
				
				print('client stopped')
				break 
		'''	
		pidfile = open(workingpath+'/'+pidfilename, 'r') #pid File suchen
		line = pidfile.readline().strip()#daten lesen
		pidfile.close()
		#print(line); #nummer ausgabe
		pid = int(line) #zur int umwandelkn
		os.kill(pid, signal.SIGKILL) #PID kill
		os.remove(workingpath+'/'+pidfilename) #alte PID löschen
		print ('Client Closed')'''
	elif 'restart' == sys.argv[1]:
		print ("lala") ##noch nichts geplant
	elif 'singledebug' == sys.argv[1]:
		main_loop()	
	
	elif 'loopcountdebug' == sys.argv[1]:
		#print ("aa")
		if sys.argv[2] != '':
			
			main_loop()	
	
	elif 'help' == sys.argv[1]:
		print ('start|stop|add|get|end')
	else:
		print ("Unknown command")
		sys.exit(2)
		
else:
   	print ("usage: %s start|stop|restart|singledebug|loopcountdebug(anzahl)") 
sys.exit(2)

