import daemon, os, time, sys, signal, lockfile, socket, socketserver, json, logging, random,datetime, threading, configparser
from collections import defaultdict
from multiprocessing import Process, Queue

config = configparser.ConfigParser()
config.read('../config.py')

HOST, PORT = config['SERVER']['Adress'], int(config['SERVER']['Port']) ##adresse und port vom server-server

clients_max = int(config['SERVER']['clients_max']) 

global logger
logger = logging.getLogger()
logger.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh = logging.FileHandler(config['GLOBAL']['workingpath']+'/'+config['SERVER']['logname'])
fh.setFormatter(formatter)
logger.addHandler(fh)

global ram
ram = defaultdict(object)
ram = {}

global timeschlitz
timeschlitz = defaultdict(object)
timeschlitz = {}

global variable
variable = defaultdict(object)
variable = {}

global sensor_ram 
sensor_ram = defaultdict(object)
sensor_ram = {}
'''
#data from client_Server to webclient
global iot_ram
iot_ram = defaultdict(object)
iot_ram = {}

#data from webclient to server_client
global iot_cache
iot_cache = defaultdict(object)
iot_cache = {}
'''

#auth token, web and server_client
global iot_token
iot_token = defaultdict(object)
iot_token = {}

global iss_stack
iss_stack = defaultdict(object)
iss_stack = {}
iss_stack['time'] = {} #value for delete timer ['time'][token] = time-hash

global iss_install
iss_install = defaultdict(object)
iss_install = {}

global gir
gir = defaultdict(object)
gir = {}

################
# dummy server #
################

iot_token['testserver1'] = {}

iot_token['testserver1']['host'] = 'zero'
iot_token['testserver1']['zone'] = 'darkzone'
iot_token['testserver1']['typ'] = 'server'
iot_token['testserver1']['time'] = ''

iss_install['testbaustein'] = {}

iss_install['testbaustein']['sender'] = {}
iss_install['testbaustein']['update'] = {}

iss_install['testbaustein']['update']['new'] = 1

iss_install['testbaustein']['data'] = {}
iss_install['testbaustein']['data']['id'] = 'xx'
iss_install['testbaustein']['data']['value'] = '1'
iss_install['testbaustein']['data']['new'] = 1


iss_install['testbaustein']['sender']['host'] = 'zero'
iss_install['testbaustein']['sender']['zone'] = 'darkzone'
iss_install['testbaustein']['sender']['name'] = 'testic'
iss_install['testbaustein']['sender']['system'] = 'i2c'

variable['zero'] = {}
variable['zero']['darkzone'] = {}
 
variable['zero']['darkzone']['stop'] = '0'
variable['zero']['darkzone']['kill'] = '0'
variable['zero']['darkzone']['sensor'] = '0'

variable['zero']['darkzone']['update'] = '0'
variable['zero']['darkzone']['webupdate'] = '0'

###############



'''
inhalt variable {
host { (Laufende maschine)
name (server-client){
"update": 1, gab es ein update
"timeslot": 1, welcher time slot
"stop": 1, stop signal an den server das er keine anfragen mehr an den bus stellen soll
"switch": 1, welcher time slot er hat
"lasttime": 1510398777, letztes mal gemeldet
"webupdate": 0, gab es ein update von einem webclient 
"sensor" : 0, # abfrage von sensoren 

"tsupdate": 0, # es gab ein update fuer den Timeslot
"number"{ iclist
"numer"{ config data


'''

class iot():

	def all_in(self,data): #need key iotfunk --> funklist
		logging.error('all-in')
		#input filter
		funklist = {'array':'array',
					'update':'update',
					'push':'push',
					'new_slot':'new_slot',
					'iss':'iss',
					'Clean_iss_stack':'Clean_iss_stack',
					'web_new':'web_new',
					'web_exist':'web_exist',
					'web_array':'web_array',
					'web_get':'web_get',
					'web_set':'web_set'
					}
		checker = 0
			#Old web clients delete
		for x in iot_token:
			if iot_token[x]['typ'] == 'webclient':

				if self.time(iot_token[x]['time']) > 300:
					
					del iot_token[x]
					logging.error(json.dumps('token gelöscht'))
					

			#do functio
		print (data['iotfunk'])
		if data['iotfunk'] in funklist:
			
			ausgabe = getattr(self,funklist[data['iotfunk']])(data)
		else:
			logging.error('fehlerhafter befehl vom HTML client')
			ausgabe = 'error in data '
			
		return (ausgabe)

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
			
	
	def new_slot(self,data):#returns a new token for web client/ client_server, reserves a new space on ram. need ['count'] 
		
		count = int(data['count'])
		loop = 1
		ret = {}
		while loop <= count:
			token = sensor.new('',20)
			iss_stack[token] = {}
			iss_stack['time'][token] = self.time('get') 
			ret[loop] = token
			loop = loop + 1
		
		return(ret)
		
	def Clean_iss_stack(self,data): #delete old key´s and data
		looper = iss_stack['time'].copy()
		#logging.error('ausführunfg')
		for x in looper:
			#logging.error('delete key: {} date: {}'.format(x,self.time(iss_stack['time'][x])))
			
			if self.time(iss_stack['time'][x]) > 10:
				del iss_stack['time'][x]
				del iss_stack[x]
				logging.error('delete key:{}'.format(x))
			
	def iss (self,data): #need data['messages']['token'](token was comes from new_slot) and data['token'] (server/webclient token) returns new massages
		logging.error('iss install')
		shadow = data['messages'].copy()
		logging.error(json.dumps(data))
		logging.error(json.dumps(iss_stack))
		for x in shadow: #all submitet ISS-Messages from Client (to store in iss_stack)
			logging.error('x:{}'.format(x))
			for y in iot_token: #client list 
				logging.error('y:{}'.format(y))
				
				if 'target' in data['messages']: #when data is targeted a single client
					logging.error('target')
					if iot_token[y]['host'] == data['messages'][x]['host'] and iot_token[y]['zone'] == data['messages'][x]['zone']:
						iss_stack[x][y] = {}
						iss_stack[x][y] = data['messages'][x]
				else: #to all clients
					logging.error('else')
					if data['messages'][x]['update']['new'] == 1: #when iss messages installes a new service
						logging.error('update new data')
						iss_stack[x][y] = {}
						iss_stack[x][y] = data['messages'][x]
						iss_install[x] = {}
						iss_install[x] = data['messages'][x]
					else: ## standart ISS Update message
						logging.error('update')
						#logging.error(json.dumps(data))
						#logging.error(json.dumps(iss_install))
						iss_stack[x][y] = {}
						iss_stack[x][y] = data['messages'][x]
						
						logging.error(json.dumps(iss_stack))
						iss_shadow = iss_install.copy()
						for z in iss_shadow: #data override in install massesages with actual data
							#logging.error('z:{}'.format(z))
							#logging.error('y:{}'.format(y))
							#logging.error('x:{}'.format(x))
							#logging.error(json.dumps(data['messages'][x]))
							#logging.error(json.dumps(iss_shadow[z]))
							if iss_shadow[z]['sender']['host'] == data['messages'][x]['sender']['host'] and iss_shadow[z]['sender']['zone'] == data['messages'][x]['sender']['zone'] and iss_shadow[z]['sender']['name'] == data['messages'][x]['sender']['name'] and iss_shadow[z]['data']['id'] == data['messages'][x]['data']['id']:
								logging.error(json.dumps('vorhandxen'))
								iss_install[z]['data']['value'] = data['messages'][x]['data']['value']

			logging.error(json.dumps(iss_stack))
			del iss_stack[x][data['token']]
		
		'''
			ich muss beide noch einfügen damit dann der server dann geziehlt daten abruft. nicht 20 mal die sekunde 
			variable['zero']['darkzone']['update'] = '0'
			variable['zero']['darkzone']['webupdate'] = '0'
		
		'''
		
		logging.error('done while')
		ret = {}
		iss_shadow = iss_stack.copy()
		for x in iss_shadow: #return all data to client, and delete
			if data['token'] in iss_stack[x]:
				ret[x] = {}
				ret[x] = iss_stack[x][data['token']]
				del iss_stack[x][data['token']]
		
		logging.error(json.dumps(ret))
		logging.error('iss ende')
		return (ret)


	def web_exist (self,data): # Looks web id is Exist
		ret = {}
		ret['return'] = iot_token.get(data['token'], 'not exist')
		
		if ret['return'] != 'not exist':
			ret['return'] = 'ok'
		
		return(ret)
		
		
	def web_new (self,data): # sets new web_clients (usable for Client-server Plugins)
		logging.error('webnew')
		token = sensor.new('',20)
		iot_token[token] = {}
		iot_token[token]['host'] = token
		iot_token[token]['typ'] = 'webclient'
		iot_token[token]['time'] = self.time('get')
		
		logging.error(json.dumps('iot_token'))
		logging.error(json.dumps(iot_token))
		ret = {}
		ret['session_id'] = token
		
		return(ret)

	def web_array (self,data): #push the entire iot_config 
		logging.error('webarray')
		#ret = {}
		'''
		for x in iot_token: #abfrage aller daten
			
			if iot_token[x]['typ'] == "server": #den inhalt von server daten abrufen
				ret[iot_token[x]['host']] = {}
				ret[iot_token[x]['host']][iot_token[x]['zone']] = {}
				
				ret[iot_token[x]['host']][iot_token[x]['zone']] = iot_config[iot_token[x]['host']][iot_token[x]['zone']]
		
		'''
		ret = 'test'
		
		
		logging.error(json.dumps('iot_token'))
		logging.error(json.dumps(iot_token))
		return (ret)

	

	
class sensor():#sensorabfrage classe

	def eingang(self,data):#erste stelle wo daten reinkommen
		logging.error('eingang')
		if data['sensor'] == 'new':
			
			newkey = self.new(10)
			logging.debug(newkey)
			sensor_ram[newkey] = {}
			sensor_ram[newkey]['all_client'] = 0
			#logging.error(json.dumps(sensor_ram))
			for x in variable: #x ist name vom client
				logging.debug('for')
				sensor_ram[newkey] = {} #container erstellen
				for y in variable[x]:
					sensor_ram[newkey][x] = {} #container erstellen
					if ram[x][y]['sensor'] == 1: #suche ob client Sensoren hat
						sensor_ram[newkey][x][y] = {} #container erstellen
						variable[x][y]['sensor'] = newkey
						variable[x][y]['update'] = 1
						variable[x][y]['stop'] = 1
						sensor_ram[newkey][x][y]['abgeholt'] = 0
						ram[newkey] = 0
					
			logging.error(json.dumps(variable))
			return (newkey)
		
		if data['sensor'] == 'start': #Client muss antworten mir sensort:start, target_key:xxxxxxxx, name:client_name
			'''
			Client muss antworten mir sensor:start, target_key:xxxxxxxx, name:client_name, host:name
			antworten sind, "go" "wait"
			'''
			retuerner = 'fail'

			if sensor_ram[data['target_key']][data['host']][data['zone']]['abgeholt'] == 0:
				sensor_ram[data['target_key']][data['host']][data['zone']]['abgeholt'] = 1 #auf abgeholt setzen
				variable[data['host']][data['zone']]['sensor'] = 0 #wieder auf 0 setzen 
				logging.error('if abfrage')
			
			checker = {0:0, 1:0, 2:0, 3:0}#variable vorerstellen 0 noch kein target key, 1 key erhalten (wartet), 2(key erhalten ermittelt sensor daten), 3 Daten geliefert)
			
			for x in sensor_ram[data['target_key']][data['host']]:
				checker[sensor_ram[data['target_key']][data['host']][x]['abgeholt']] = checker[sensor_ram[data['target_key']][data['host']][x]['abgeholt']] + 1

			if checker[2] == 0:
				
				sensor_ram[data['target_key']][data['host']][data['zone']]['abgeholt'] = 2 #holt nun date
				retuerner = 'go'
				logging.debug('go signal ')
			else:
				logging.debug('wait signal')
				retuerner ='wait'
				
			return (retuerner) 
		
		if data['sensor'] == 'deliver':	#sensordaten empfangen
			'''
			Client muss antworten mir sensor:deliver, target_key:xxxxxxxx, name:client_name, host:hostname, werte:{}
			antwort ist immer 'ok'
			'''
			
			sensor_ram[data['target_key']][data['host']][data['zone']] = data['werte']
			sensor_ram[data['target_key']][data['host']][data['zone']]['abgeholt'] = 3 #auf geliefert gesetzt
			variable[data['host']][data['zone']]['stop'] = 1
			variable[data['host']][data['zone']]['update'] = 1
			ifabgeholtgleich3 = 0
			vergleich = 0
			for x in sensor_ram[data['target_key']]: #ueberpruefen ob alle Clients sensor daten gesendet hat 
				for y in sensor_ram[data['target_key']][x]:
					vergleich += 1
					if sensor_ram[data['target_key']][x][y]['abgeholt'] == 3:
						ifabgeholtgleich3 += 1
					
						
				
			if ifabgeholtgleich3 == vergleich: #wenn alle daten uebermittelet wurden. clients wieder auf normal stellung setzen
				ram[data['target_key']] = 1
				for x in variable: #x ist name vom client
					logging.debug('for')
					
					for y in variable[x]:
						
						if ram[x][y]['sensor'] == 1: #suche ob client Sensoren hat
							
							variable[x][y]['sensor'] = 0 #standart wert zurück setzen
							variable[x][y]['update'] = 1
							variable[x][y]['stop'] = 0  #stop aufheben
				
			logging.error(json.dumps(sensor_ram))
			logging.error(json.dumps(variable))
		
			return ('ok') 
		
		if data['sensor'] == 'return': #server antwort an anfrager, mit zwei aussagen, alle sensor daten ODER er solle weiter warten
			if ram[data['target_key']] == 1:
				return (sensor_ram[data['target_key']]) 
			else:
				return('wait')
			
			
		
	def new(self,data=10):#erstellen von schlüssel für sensor
		logging.error('new_rand')
		ausgabe = ''
		for x in range(1,data):
			#print (x)
			zufall = random.randrange(1,4)
			
			if (zufall == 1):
				ausgabe = ausgabe + str(random.randrange(0,10)) # zahlen
			if (zufall == 2):
				ausgabe = ausgabe + chr(random.randrange(65,91)) #Grossbuchstaben
			if (zufall == 3):
				ausgabe = ausgabe + chr(random.randrange(97,123)) # kleine buchstaben
		logging.error(ausgabe)
		
		return(ausgabe)
				
class check():#standart abfrage von server-Clients
	
	def eingang(self,data): #über mittelt was der client nun zutun hat.
		#logging.error(json.dumps(variable))
		#logging.error(json.dumps(ram))
		#logging.error(json.dumps(timeschlitz))
		#logging.error('check anfrage')
		if data['zone'] in variable[data['host']]:
		
			if variable[data['host']][data['zone']]['update'] == 1:
				logging.error('new update call')
				returner = {} #container erstellen
				returner['stop'] = variable[data['host']][data['zone']]['stop'] #stop signal
				returner['kill'] = variable[data['host']][data['zone']]['kill'] #stop signal
				returner['webupdate'] = variable[data['host']][data['zone']]['webupdate'] #ansage das Webupdate da ist (zusätzlicher Trigger)
				returner['sensor'] = variable[data['host']][data['zone']]['sensor'] #ansage, das er nun sensor daten liefern soll(geparrt mit STOP)
				returner['tsupdate'] = variable[data['host']][data['zone']]['tsupdate'] #wenn client sich neuen Time slot abhoilen soll
				variable[data['host']][data['zone']]['update'] = 0 #general update signal für update, eher wichtig für den server
				logging.error(json.dumps(returner))
			else:
				returner = 'ok' # standart antwort wenn es nichts neues gibt 
				#logging.error('check')
		else:
			logging.error('not exist anymore'+data['zone'])
			returner = 'ok'
			
		return (returner)
		
	def delete(self, name, host): #client aus speicher entfernen
		logging.error(name)
		logging.error('check::delete')
		#logging.error(json.dumps(timeschlitz))
		#logging.error(json.dumps(variable))
		logging.error(json.dumps(iot_token))
		#logging.error(json.dumps(iot_config))
		
		if variable[host][name]['switch'] == 1: #wenn Client mit einem Multiplexer ausgestatet ist 
			#logging.error('timeslot delete')
			#logging.error(json.dumps(timeschlitz[host][variable[host][name]['timeslot']]))
			del timeschlitz[host][variable[host][name]['timeslot']] #löschen variable
			
		#logging.debug(json.dumps(variable))
		del variable[host][name] #löschen variable
		
		#logging.error('1')
		#logging.error(ram[host][name]['sesession_id'])
		
		del iot_token[ram[host][name]['sesession_id']]
		#logging.error('2')
		#del iot_config[host][name] 
		#logging.error('3')
		
		#logging.debug(json.dumps(ram))
		del ram[host][name] #löschen variable
		
		#logging.error(json.dumps(timeschlitz))
		#logging.error(json.dumps(variable))
		#logging.error(json.dumps(ram))
		shadow_copy = iss_install.copy()
		
		for x in shadow_copy: #delete install data
			if shadow_copy[x]['sender']['host'] == host:
				logging.error(json.dumps(shadow_copy[x]))
				del iss_install[x]
		logging.error(host)
		logging.error(json.dumps(shadow_copy))	
		returner = {'shutdown':'ok'}
		logging.error('aaa')
		logging.error(returner)
		logging.error('bbbb')
		return (returner)

class server(): # server standart Classe
	
	def new_data (self,umwandel):

		if umwandel['funktion'] == 'add':#neuen client in ram einfügen
			insertnew = 1
			if umwandel['host'] in ram:#abfrage ob shon angemeldet
				if umwandel['zone'] in ram[umwandel['host']]:
					logging.error('why!')
					checker = check()
					checker.delete(umwandel['zone'],umwandel['host'])
					insertnew = 1
					 
				else:
					insertnew = 1
			else:
				ram[umwandel['host']] = {}
				insertnew = 1
				
			if insertnew == 1:##wenn user nicht angelegt ist
				logging.error('new')
				ram[umwandel['host']][umwandel['zone']] = umwandel #in speicher einfügen
				#returner = json.dumps('ok') #ok senden
				addnew = timer_san()
				sesession_id = sensor.new('',20)
				logging.error(sesession_id)
				iot_token[sesession_id] = {}
				ret = {}
				logging.error(json.dumps(umwandel))
				ret['sesession_id'] = sesession_id
				ram[umwandel['host']][umwandel['zone']]['sesession_id'] = sesession_id
				#in refernz datenbank ablegen (durchsuchbar)
				iot_token[sesession_id]['host'] = umwandel['host']
				iot_token[sesession_id]['zone'] = umwandel['zone']
				iot_token[sesession_id]['typ'] = 'server'
				iot_token[sesession_id]['time'] = iot.time('','get')
				#ablegen der IoT konfig data 
				#iot_config[umwandel['host']] = {}
				#iot_config[umwandel['host']][umwandel['zone']]  = {}
				#iot_config[umwandel['host']][umwandel['zone']] = umwandel['iot']
				
				logging.error(json.dumps('iot_token'))
				logging.error(json.dumps(iot_token))
				#logging.error(json.dumps('iot_config'))
				#logging.error(json.dumps(iot_config))
				
				
				addnew.new_client(umwandel['zone'], umwandel['host']) #erzeuge Timeslice 
				#addnew.timeslicer()
				
				###Copy iss_install into iss stack
				################## HIER WEITER MACZHEN !!!!!!! ###########################
				shadow_copy = iss_install.copy()
				for x in shadow_copy:
					iss_stack[x] = {}
					iss_stack[x][sesession_id] = {}
					iss_stack[x][sesession_id] = iss_install[x]

				################## HIER WEITER MACZHEN !!!!!!! ###########################
				logging.error(json.dumps(iss_stack))
				logging.error('install komplete')
				logging.error(json.dumps(ret))
				return (ret)
				
		elif umwandel['funktion'] == 'iot': #die standart abrfragen, ob es änderungen giebt
			logging.error('iot aufruf')
			v1 = iot()
			return v1.all_in(umwandel)
			
		elif umwandel['funktion'] == 'all_data_print': ## Print all Varibles in Error log
			logging.error('ram')
			logging.error(json.dumps(ram))
			logging.error('timeschlitz')
			logging.error(json.dumps(timeschlitz))
			logging.error('variable')
			logging.error(json.dumps(variable))
			logging.error('sensor_ram')
			logging.error(json.dumps(sensor_ram))
			logging.error('iot_token')
			logging.error(json.dumps(iot_token))
			logging.error('iss_stack')
			logging.error(json.dumps(iss_stack))
			logging.error('iss_install')
			logging.error(json.dumps(iss_install))
			logging.error('gir')
			logging.error(json.dumps(gir))
			
		elif umwandel['funktion'] == 'check': #die standart abrfragen, ob es änderungen giebt 
			logging.debug('check aufruf')
			checker = check()
			return (checker.eingang(umwandel))
		
		elif umwandel['funktion'] == 'sensor': ##wenn sensort aktiv ist. 
			logging.error('sensor aufruf')
			senso = sensor()
			return senso.eingang(umwandel)
		
		elif umwandel['funktion'] == 'update': ## wenn sich etwas am Server-client ändert (damit inhalt variable geändert wird)
			
			return ram
		
		elif umwandel['funktion'] == 'stop': ## wenn sich etwas am Server-client ändert (damit inhalt variable geändert wird)
			
			logging.error('stop '+umwandel['zone'])
			returner = json.dumps('nope')
			if variable[umwandel['host']][umwandel['zone']]['stop'] == 0:
				logging.error('stop varibale setzen '+umwandel['zone'])
				variable[umwandel['host']][umwandel['zone']]['stop'] = 1
				variable[umwandel['host']][umwandel['zone']]['update'] = 1
				if 'kill' in umwandel:
					
					variable[umwandel['host']][umwandel['zone']]['kill'] = 1
					logging.error('kill -- variable: {}'.format(variable))
				returner = 'ok'
			else:
				#logging.error('else '+variable)
				if variable[umwandel['host']][umwandel['zone']]['update'] == 1:
					logging.error('warten '+umwandel['zone'])
					returner = 'wait'
				else:
					logging.error('absetzen delete '+umwandel['zone'])
					logging.error('delete')
					deleter = check()
					ausgabe = deleter.delete(umwandel['zone'],umwandel['host'])
					returner = 'kill'
					if len(variable[umwandel['host']]) != 0:
						logging.error('delete-create new time slice')
						create = timer_san()
						create.timeslicer(umwandel['host'])
					else:
						logging.error('delete kein neuer time sclice')
			
			return returner
			
		
		elif umwandel['funktion'] == 'delete': #wenn ein client nicht mehr benötigt wird 
			logging.error('delete')
			deleter = check()
			ausgabe = deleter.delete(umwandel['zone'],umwandel['host'])
			if len(variable[umwandel['host']]) != 0:
				logging.debug('delete-create new time slice')
				create = timer_san()
				create.timeslicer(umwandel['host'])
			else:
				logging.debug('delete kein neuer time sclice')
			return ausgabe
		
		elif umwandel['funktion'] == 'timeslice': #rückgabe neuer Timeslot 
			logging.error('timeslicer_funk')
			logging.error(json.dumps(timeschlitz[umwandel['host']][int(variable[umwandel['host']][umwandel['zone']]['timeslot'])]))
			variable[umwandel['host']][umwandel['zone']]['tsupdate'] = 0
			return timeschlitz[umwandel['host']][int(variable[umwandel['host']][umwandel['zone']]['timeslot'])]
		else:
			logging.error('unbekannter befehl')
			
			return {'error': 'unbekannter befehl'}

class timer_san():
	def timeslicer(self,host):
		logging.error('timeslicer')
		counter = 1
		
		for key in variable[host]:#zuweisen der zeitschlitze
			if variable[host][key]['switch'] == 1:
				variable[host][key]['timeslot'] = counter
				variable[host][key]['update'] = 1 
				variable[host][key]['tsupdate'] = 1
				variable[host][key]['stop'] = 0
				counter +=1
		
		anzahl_schlitze = 6 #abfrage zeiten innerhalb einer sekunde
		anzahl_clientes = len(variable) #angemeldete Clients
		schlitze = int(1000000 / anzahl_schlitze) #durschnitt aus microsekunden rechnen
		schlitzzeit = int(schlitze / anzahl_clientes) #durchschnitt für cliets
		schlitzzeitplus = 0
		#timeschlitz['schlitzzeit'] = schlitzzeit 
		if host in timeschlitz:#
			voidvar = 1
		else:
			timeschlitz[host] = {} #leerer container
			
		for nummer22 in range(1, anzahl_clientes+1):#forschleife für IC´s
			timeschlitz[host][nummer22] = {}#leere container erstellen
			
		for schlitzer in range(1,anzahl_schlitze+1):
			for user in range(1,anzahl_clientes+1):
				timeschlitz[host][user]['schlitzzeit'] = schlitzzeit 
				timeschlitz[host][user][schlitzer] = schlitzzeitplus
				schlitzzeitplus = schlitzzeitplus + schlitzzeit
		logging.error(json.dumps(timeschlitz))
	
	
	def new_client(self, name, host):
		logging.error('durchlauf new_client')
		logging.error(ram)
		if host in variable:#
			voidvar = 1
			logging.error('gefunden')
		else:
			variable[host] = {} #leerer container
			logging.error('nicht gefunden')
			
			
		
		variable[host][name] = {} #leerer container
		ts = int(time.time())
		variable[host][name]['lasttime'] = ts #timestamp
		variable[host][name]['webupdate'] = 0 #wenn es zu einem aktor chanche kam
		variable[host][name]['timeslot'] = 0 #zugewiesener Timesolt vom timeslicer
		variable[host][name]['stop'] = 0
		variable[host][name]['update'] = 1
		variable[host][name]['sensor'] = 0
		variable[host][name]['tsupdate'] = 0
		variable[host][name]['kill'] = 0
		variable[host][name]['aktor'] = {} #leerer container
		if ram[host][name]['switch'] == 1:
			variable[host][name]['switch'] = 1
			self.timeslicer(host)
		else:
			variable[host][name]['switch'] = 0
		#logging.error(str(ram[host][name]['num']))
		'''
		for y in ram[host][name]['iot']:
			#logging.error('Fehler bei install daten in Master Server-'+str(ram[host][name][str(y)]['num']+1))
			variable[host][name][y] = {}
			for x in ram[host][name]['iot'][y]:
				
				#logging.error('Fehler bei install daten in Master Serverhhhh')
				variable[host][name][y][x] = {}
				variable[host][name][y][x] = ram[host][name]['iot'][y][x]
				variable[host][name][y][x]['update'] = 0
		'''
				
		 ##kann nachher gelöscht werden
		#logging.error(json.dumps(variable))
		
#################################################	
#												#
#				   TCP-Deamon					#
#												#
#################################################

class data_server(): #Server Thread
	
	def io():
		
		in_data = {}
		
		while True: #main while 
				
			sleepi = True
			while sleepi: ##Standby while
				time.sleep(0.02)
				
				if Server_cron_queue.empty() != True:#cron data
					sleepi = False
				
				if TCP2Server_queue_stack['aktive'].empty() != True:
					sleepi = False
			
				
			io = datahelper()
			in_data = io.transmit('',0)## check on new data
			ret = ''
			
			
			#logging.error('test')
			in_data_copy = in_data.copy()
			server_io = server()
			if Server_cron_queue.empty() != True:#cron data
				crondata = Server_cron_queue.get()
				server_io.new_data(json.loads(crondata)) #no return data
					
				
			for x in in_data_copy: #JSON catch
				try:
					umwandel = json.loads(in_data_copy[x])
    		
				except ValueError as err:
					logging.error('JSON fehlerhaft')
					umwandel = {'server_control':'Error data'}
					logging.error('Fehlerhafte JSON data')
					logging.error(err)
				
				if ret == '': #when more than one entry selektor
					ret = {}
				
				if 'server_control' in umwandel: ## abfangen von server deamon befehle 
					demon_queue_data['close'].put('1')
					ret[x] = json.dumps({'data':'end'})
					# here Logon system Later !!!
				else:
					try:
						ret[x] = json.dumps(server_io.new_data(umwandel)) ###Doing server call
						logging.debug('thread: {}, data: {}'.format(x,json.dumps(in_data[x])))
					except ValueError as err:
						logging.error('Fehlerhafte JSON data ')
						logging.error(err)
						ret[x] = {'error':'Error data'}
					except KeyError as err:
						logging.error('Fehlerhafte JSON data')
						logging.error(err)
						logging.error('thread: {}, data: {}'.format(x,json.dumps(in_data[x])))
						ret[x] = {'error':'Error data'}
				
				del in_data[x]
			
			if ret != '': #whend data must be submittet
				logging.debug('Return data from server: {}'.format(json.dumps(ret)))
				in_data = io.transmit(ret,0)
			
			time.sleep(0.06)
			


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler): #In comeing TCP data

	def handle(self):
		# self.request is the TCP socket connected to the client
		cur_thread = threading.current_thread()
		loop_count = 0
		anwser = 0 
		exit = 0 
		loop_control = True
		logging.error('data neu')
        ###########to become a free Data Slot #################
		while loop_control: 
			if TCP2Server_queue_stack['aktive'].empty() == True:
				TCP2Server_queue_stack['aktive'].put('1') #wake up system 
				logging.debug('thread start: {}'.format(cur_thread.name))
			if anwser == 0:
				loop_count = random.randrange(1,TCP2Server_queue_stack['max_client'])

			if TCP2Server_queue_stack[loop_count]['lock'].empty() == True:
				logging.debug('Obtain slot: {}, thread: {}'.format(loop_count,cur_thread.name))
				TCP2Server_queue_stack[loop_count]['lock'].put(cur_thread.name)
				TCP2Server_queue_stack[loop_count]['ready'].put(cur_thread.name)
				print (loop_count)
				print (cur_thread.name)
				own_slot = loop_count
				anwser == 1
				exit = 1

			if exit == 1:
				loop_control = False
				break
		
		logging.error('hab token')
        ######### Put data in the slot ##############
		count = self.request.recv(10).strip() #### handle dynamic byte count
		lenght = int(count.decode('utf8'))
		self.request.sendall('ok'.encode('utf8'))
		logging.error(lenght)
		logging.error('habe daten')
		
		data = self.request.recv(lenght).strip() #### handle data
		rawdata = data.decode('utf8')
		logging.error(rawdata)
		
		TCP2Server_queue_stack[own_slot]['data'].put(rawdata)
		TCP2Server_queue_stack[own_slot]['ready'].put(own_slot)
        
        #########
		trigger = True
		loop = 0
		while trigger: #waiting server task done
			if TCP2Server_queue_stack[own_slot]['ready_return'].empty() != True:
				dataout = TCP2Server_queue_stack[own_slot]['data'].get()
				trigger = False

			time.sleep(0.2)
			loop = loop + 1
			print (loop)
			logging.error(loop)
			if loop > 20: #when server takes over 2 seconds to progess the data. force to close
				dataout='Server error'
				logging.error('TCP servre error, thread: {}'.format(cur_thread.name))
				trigger = False
				if TCP2Server_queue_stack[own_slot]['ready'].empty() != True:
					garbage = TCP2Server_queue_stack[own_slot]['ready'].get()
				if TCP2Server_queue_stack[own_slot]['ready_return'].empty() != True:
					garbage = TCP2Server_queue_stack[own_slot]['ready'].get()
				if TCP2Server_queue_stack[own_slot]['data'].empty() != True:
					garbage = TCP2Server_queue_stack[own_slot]['data'].get()
        		
				garbage = TCP2Server_queue_stack[own_slot]['lock'].get()
		
		
		logging.error('sende daten')
		#return data to client
		TCP2Server_queue_stack[own_slot]['ready'].put(own_slot)
		length = len(dataout)
		string = str(length)
		logging.error(string.zfill(30))
		self.request.sendall(bytes(string.zfill(30), 'utf8'))
		response = str(self.request.recv(10), 'utf8')
		
		self.request.sendall(dataout.encode('utf8'))
		logging.error('close')
		self.close()
		#self.request.finish()
		
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class datahelper (): #data transver helper TCP Multiplexer <--> Server Thread
	
	def transmit(self,in_data,typ):
		if typ == 1:
			target, me = 'server', 'client'
		else:
			target, me = 'client', 'server'
		
		loop_control = True
		loopnum = 1
		ret = {}
		one = 0
		two = 0
		count = 1
		while loop_control:
			#print ('one {} : two {}, loopnum:{},typ:{},me:{},target:{} ### datain : {} #####'.format(one,two,loopnum,typ,me,target,in_data))
			if Io_stack[loopnum]['lock'].empty() == True:
				Io_stack[loopnum]['lock'].put('data')
				
				if Io_stack[loopnum]['data_to_'+target+''].empty() != True:
					ret = Io_stack[loopnum]['data_to_'+target+''].get()
					print (ret)
					
				if type (in_data) == dict:
					
					Io_stack[loopnum]['data_to_'+me+''].put(in_data)
					in_data = ''

				garbage = Io_stack[loopnum]['lock'].get()

			if loopnum == 1:
				one = 1
				loopnum = 2
			else:
				loopnum = 1
				two = 1
			#loop_control = False
			count = count + 1	
			#time.sleep(0.05)
			if count == 10:
				loop_control = False
			
			if one == 1 and two == 1:
				loop_control = False
	
		return (ret)

class data_handle_TCP2Server (): ##### TCP Multiplex Service (threaded)
	
	def start():
		
		loop_count = 0
		TCP_handler_stack = {}

		while loop_count < TCP2Server_queue_stack['max_client']: #### generate data stack
			loop_count = loop_count + 1
			TCP_handler_stack[loop_count] = {}
			TCP_handler_stack[loop_count]['name'] = ''
			TCP_handler_stack[loop_count]['stage'] = 0
			TCP_handler_stack[loop_count]['data'] = ''

		datasend = {}
		stage_one_helper = 0	
		loop_count = 0
		sleep_loop_delay = 0
		while True: #### main while
			sleepi = True
			while sleepi: ### Sleep loop when non aktive TCP connection
				time.sleep(0.01)
				if TCP2Server_queue_stack['aktive'].empty() != True:
					print ('aktive verbindung')
					sleepi = False
					
			sleeper = 0	
			while loop_count < TCP2Server_queue_stack['max_client']: #stageing system 0 to 4
				loop_count = loop_count + 1
				
				
				if TCP_handler_stack[loop_count]['stage'] == 0: ### TCP new Slot #####
					
					
					if TCP2Server_queue_stack[loop_count]['lock'].empty() != True:
						sleeper = 1 #checker for aktive connecktion
						name = TCP2Server_queue_stack[loop_count]['ready'].get()
						TCP_handler_stack[loop_count]['name'] = name
						TCP_handler_stack[loop_count]['stage'] = 1
						logging.debug('multiplex slot: {}, thread: {},stage: {}'.format(loop_count,TCP_handler_stack[loop_count]['name'],TCP_handler_stack[loop_count]['stage']))
				
				elif TCP_handler_stack[loop_count]['stage'] == 1: ### Get Data from TCP stack #####
					sleeper = 1 #checker for aktive connecktion
					
					if TCP2Server_queue_stack[loop_count]['ready'].empty() != True: ## when data has been written
						datasend[TCP_handler_stack[loop_count]['name']] = TCP2Server_queue_stack[loop_count]['data'].get()
						carbage = TCP2Server_queue_stack[loop_count]['ready'].get()
						TCP_handler_stack[loop_count]['stage'] = 2
						stage_one_helper = 1
						logging.debug('multiplex slot: {}, thread: {},stage: {}'.format(loop_count,TCP_handler_stack[loop_count]['name'],TCP_handler_stack[loop_count]['stage']))
						
				elif TCP_handler_stack[loop_count]['stage'] == 2: #### Return data to TCP stack
					sleeper = 1 #checker for aktive connecktion
					
					if TCP_handler_stack[loop_count]['data'] != '':
						TCP2Server_queue_stack[loop_count]['data'].put(TCP_handler_stack[loop_count]['data']) ###
						TCP2Server_queue_stack[loop_count]['ready_return'].put('1')
						TCP_handler_stack[loop_count]['stage'] = 3
						logging.debug('multiplex slot: {}, thread: {},stage: {}'.format(loop_count,TCP_handler_stack[loop_count]['name'],TCP_handler_stack[loop_count]['stage']))
					
				elif TCP_handler_stack[loop_count]['stage'] == 3: #### freeing space Handle space
					
					sleeper = 1 #checker for aktive connecktion
					if TCP2Server_queue_stack[loop_count]['ready'].empty() != True:
						TCP_handler_stack[loop_count]['stage'] = 0
						TCP_handler_stack[loop_count]['name'] = ''
						TCP_handler_stack[loop_count]['data'] = ''
						garbage = TCP2Server_queue_stack[loop_count]['ready'].get()
						garbage = TCP2Server_queue_stack[loop_count]['ready_return'].get()
						garbage = TCP2Server_queue_stack[loop_count]['lock'].get()
				else:
					logging.error('multiplex slot Massive error')
			################ Ende WHILE ####################################					
			
			if stage_one_helper == 1:
				stage_one_helper = 0
			else:
				datasend = ''

			io = datahelper()
			in_data = io.transmit(datasend,1)## daten an server übermittelen 
			datasend = {}
			print (in_data)
			for x in in_data: 

				for y in TCP_handler_stack:

					if TCP_handler_stack[y]['name'] == x:
						TCP_handler_stack[y]['data'] = in_data[x]
						logging.debug(json.dumps('data from server, Thread: {}, data: {}'.format(x,in_data[x])))

			if sleeper == 0: ###sleep delay
				sleep_loop_delay = sleep_loop_delay + 1
			else:
				sleep_loop_delay = 0
				
			if sleep_loop_delay == 3: #sets server in Standby
				logging.debug('multiplex sleep')
				sleep_loop_delay = 0
				garbage = TCP2Server_queue_stack['aktive'].get()
			loop_count = 0
			datasend = {}
			time.sleep(0.09)
			

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


def Demon_start(): #### main Thread
	logging.error(json.dumps('Server Start'))
	while True:

		# Start a thread with the server -- that thread will then start one
		# more thread for each request
		
		global TCP2Server_queue_stack
		global Io_stack
		global demon_queue_data
		global Server_cron_queue
		
		demon_queue_data = {}
		demon_queue_data['close'] = Queue()
		
		Server_cron_queue = Queue()
		
		TCP2Server_queue_stack = {}
		TCP2Server_queue_stack['max_client'] = clients_max
		TCP2Server_queue_stack['aktive'] = Queue() ## income TCP aktive
		loop_count = 0
		
		#TCP stack data
		while loop_count < TCP2Server_queue_stack['max_client']: #data stac for TCP Multiplexer
			loop_count = loop_count + 1
			TCP2Server_queue_stack[loop_count] = {}
			TCP2Server_queue_stack[loop_count]['lock'] = Queue() 
			TCP2Server_queue_stack[loop_count]['ready'] = Queue() 
			TCP2Server_queue_stack[loop_count]['ready_return'] = Queue() 
			TCP2Server_queue_stack[loop_count]['data'] = Queue() 

		
		#intern Stack to server data
		Io_stack = {} 
		
		Io_stack[1] = {}
		Io_stack[1]['data_to_server'] = Queue()
		Io_stack[1]['data_to_client'] = Queue()
		Io_stack[1]['lock'] = Queue()
		
		Io_stack[2] = {}
		Io_stack[2]['data_to_client'] = Queue()
		Io_stack[2]['data_to_server'] = Queue()
		Io_stack[2]['lock'] = Queue()
		#############
		
		data_server_prozess = Process(target=data_server.io) #start server thread
		data_server_prozess.start()
		
		tcp2server_prozess = Process(target=data_handle_TCP2Server.start) #Start TCP demultiplexer
		tcp2server_prozess.start()
		
		#######################
		server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler) #define TCP
		ip, port = server.server_address
		server_thread = threading.Thread(target=server.serve_forever) #Start Main TCP servive
		server_thread.daemon = False
		server_thread.start()
		testcount = 0
		
		############  Debugger run #########
		stopper = 0
		logging.error('ms_time ')
		now_minute = ms_time(2) #set demon timer 
		logging.error('ms_time {}'.format(now_minute))
		
		while True: #basic run
			
			if data_server_prozess.is_alive() != True:
				logging.error(json.dumps('server Thread non aktive'))
				stopper = 1
			if tcp2server_prozess.is_alive() != True:
				logging.error(json.dumps('TCP Multiplexer non aktive'))
				stopper = 1
			if server_thread.is_alive() != True:
				logging.error(json.dumps('TCP thread non active'))
				stopper = 1
		
			if demon_queue_data['close'].empty() != True: ### close signal
				time.sleep(1)
				stopper = 1
				
			testcount = testcount + 1 
			print ('haupt prozess {}'.format(testcount))
			#print (server_thread.enumerate())
			time.sleep(1) 
			'''
			if testcount == 10:
				stopper = 1
			'''#### debug mode 
			if now_minute != ms_time(2): #demon run 
				now_minute = ms_time(2)
				logging.error('cron start')
				Server_cron_queue.put(json.dumps({'funktion':'iot','iotfunk':'Clean_iss_stack'}))
			
			if stopper == 1:
				break
		############  Debugger run #########		
		
		if stopper == 1: #### server shutdown
			Server_cron_queue.put(json.dumps({'funktion':'all_data_print'}))
			time.sleep(0.3)
			loop_count = 0
			
			if data_server_prozess.is_alive() == True:
				data_server_prozess.terminate()	
			if tcp2server_prozess.is_alive() == True:
				tcp2server_prozess.terminate()
			if server_thread.is_alive() == True:
				server.shutdown()
				server.server_close()

			while loop_count < TCP2Server_queue_stack['max_client']:
				loop_count = loop_count + 1
				TCP2Server_queue_stack[loop_count]['lock'].close()
				TCP2Server_queue_stack[loop_count]['ready'].close()
				TCP2Server_queue_stack[loop_count]['ready_return'].close()
				TCP2Server_queue_stack[loop_count]['data'].close()
			
			Io_stack[1]['data_to_server'].close()
			Io_stack[2]['data_to_client'].close()
			Io_stack[1]['data_to_server'].close()
			Io_stack[2]['data_to_client'].close()
			Io_stack[1]['lock'].close()
			Io_stack[2]['lock'].close()
			
			Server_cron_queue.close()
			demon_queue_data['close'].close()
			logging.error(json.dumps('Server Shutdown'))
			break


context = daemon.DaemonContext( #daemon konfig
	working_directory='/net/html/iotserver/iotserver',
   	umask=0o002,
   	files_preserve = [
   		fh.stream,
    ],

)

#Demon_start()
if len(sys.argv) == 2:
	if 'start' == sys.argv[1]:
		
		loop = 0;
		loopcount = 1;
		# Create the server, binding to localhost on port 9999
		while loop == 0:
			if loopcount > 10:
				loop = 1
			try:
				testverbindung = socketserver.TCPServer((HOST, PORT), ThreadedTCPRequestHandler)
				
			except OSError as err:
				print('port noch in nutzung ***warte***', err)
				time.sleep(1)
				loopcount = loopcount +1
			else:
				loop = 1
		
		try:	
			testverbindung.server_close()
		except AttributeError:
			print('Port ist dauerhaft in nutzung')
		except NameError:
			print('Unbekannter fehler')
		else:	
			print("wird gestartet ...")
			logging.error('server start')
			with context:
				Demon_start()
				
	elif 'stop' == sys.argv[1]:
		def client(ip, port, message): ### This can be used as simple client 
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
				sock.connect((ip, port))
				#### SEND DATA #####
				length = len(message)
				sock.sendall(bytes(str(length), 'utf8'))
				response = str(sock.recv(10), 'utf8')
				sock.sendall(bytes(message, 'utf8'))
				#### SEND DATA #####
       
				 ###Bekome data #####
				count = str(sock.recv(10).strip(), 'utf8')
				sock.sendall(bytes('ok', 'utf8'))
				response = str(sock.recv(int(count)), 'utf8')
				print("Received count: {}".format(response))
				###Bekome data #####
				sock.close()
		print ('sending Close signal')       
		client(HOST, PORT, json.dumps({'server_control':'close','data':'hier client:'}))
		print ('server stopped.....')
		logging.error('server stop')
	elif 'restart' == sys.argv[1]:
		print ("lala") ##noch nichts geplant
	elif 'help' == sys.argv[1]:
		print ('start|stop|add|get|end')
	else:
		print ("Unknown command")
		sys.exit(2)
		
else:
   	print ("usage: %s start|stop|restart") 
sys.exit(2)