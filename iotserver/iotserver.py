import daemon, os, time, sys, signal, lockfile, socket, socketserver, json, logging, random,datetime, threading, configparser
from collections import defaultdict
from multiprocessing import Process, Queue

from iss_helper import iss_create

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

global timeschlitz #veraltet
timeschlitz = defaultdict(object)
timeschlitz = {}

global variable #veraltet
variable = defaultdict(object)
variable = {}

global sensor_ram #veraltet
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
'''
iot_token
20xn <-- Client token 
[20xn][host]
[20xn][zone]

'''

global iot_token
iot_token = defaultdict(object)
iot_token = {}

'''
iss_stack 
iss_stack[Iss_token][client_token] = {iss}

'''
global iss_stack
iss_stack = defaultdict(object)
iss_stack = {}
iss_stack['time'] = {} #value for delete timer ['time'][token] = time-hash

'''
iss_install
iss_stack[client_token] = {iss [update]['new']=1}

'''

global iss_install
iss_install = defaultdict(object)
iss_install = {}

global gir #veraltet, ging in den Client über
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

class iot():#alle Iot abfragen werden abgehandelt. 

	def all_in(self,data): #need key iotfunk --> funklist
		logging.error('all-in')
		#input filter
		funklist = {'array':'array',
					'update':'update',
					'push':'push',
					'new_slot':'new_slot',
					'Kill_client':'Kill_client',
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
		trash = iot_token.copy()
		for x in trash:####!!!!das hier sollte später Demon !!!!!###### Web cliebnt Delete
			if iot_token[x]['typ'] == 'webclient':

				if self.time(iot_token[x]['time']) > 300:
					
					del iot_token[x]
					logging.error(json.dumps('token gelöscht'))
					

			#do functio
		#print (data['iotfunk'])
		if data['iotfunk'] in funklist:#funktion ausführen
			 
			ausgabe = getattr(self,funklist[data['iotfunk']])(data)

		else:
			logging.error('fehlerhafter befehl vom HTML client')
			ausgabe = 'error in data '
			
		return (ausgabe)#gebe daten zurück an Server.iot()

	def time (self,data):#time stamp erzeugen für Token
		if data == 'get':#sgibt zeit stempelt zurück
			now = datetime.datetime.now()
			return (str(now.day)+':'+str(now.hour)+':'+str(now.minute)+':'+str(now.second))
		
		else:#gibt vergangene zeit zückt wenn alter zeit stempel angeben ist 
			now = datetime.datetime.now()
			
			d,h,m,s = data.split(':')
			
			nowstamp = ((now.day*86400)+(now.hour*3600)+(now.minute*60)+(now.second))
			
			laststamp = ((int(d)*86400)+(int(h)*3600)+(int(m)*60)+(int(s)))
	
			return (nowstamp - laststamp)
			
	
	def Kill_client(self,data):# erzeugt ein iss packet zum shutdown eines clients
		#erwarte CLient,ERzeige massege zum kill
		#via Message System
		#cha.target('client','none','run','system') VAR KILL 
		
		logging.error('Sende Kill data')
	
	def new_slot(self,data):#returns a new token for web client/ client_server, reserves a new space on ram. need ['count'] 
		
		count = int(data['count'])
		loop = 1
		ret = {}
		while loop <= count:
			token = sensor.new('',20)#erzeugt zufalls code
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
		logging.error(json.dumps(data))
		if data['messages'] != '' and data['token'] in iot_token:
			shadow = data['messages'].copy()
			logging.error(json.dumps(data))
			logging.error(json.dumps(iss_stack))
			for x in shadow: #all submitet ISS-Messages from Client (to store in iss_stack)
				logging.error('x:{}'.format(x))
				for y in iot_token: #client list 
					logging.error('y:{}'.format(y))
					
					if 'target' in data['messages'][x]: #when data is targeted a single client
						logging.error('target')
						if iot_token[y]['host'] == data['messages'][x]['target']['host'] and iot_token[y]['zone'] == data['messages'][x]['target']['zone']:
							iss_stack[x][y] = {}
							iss_stack[x][y] = data['messages'][x]
							#logging.error('target data Set')
							#logging.error(json.dumps(iss_stack))
							#logging.error('Message')
							#logging.error(json.dumps(data))
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
								logging.error('z:{}'.format(z))
								logging.error('y:{}'.format(y))
								logging.error('x:{}'.format(x))
								logging.error(json.dumps(data['messages'][x]))
								logging.error(json.dumps(iss_shadow[z]))
								if iss_shadow[z]['sender']['host'] == data['messages'][x]['sender']['host'] and iss_shadow[z]['sender']['zone'] == data['messages'][x]['sender']['zone'] and iss_shadow[z]['sender']['name'] == data['messages'][x]['sender']['name'] and iss_shadow[z]['data']['id'] == data['messages'][x]['data']['id']:
									logging.error(json.dumps('vorhandxen'))
									if data['messages'][x]['sender']['name'] == 'sensor':
										iss_install[z]['data'] = data['messages'][x]['data']
									else:
										iss_install[z]['data']['value'] = data['messages'][x]['data']['value']
	
						#logging.error(json.dumps(iss_stack))
						#del iss_stack[x][data['token']]
			
			'''
				ich muss beide noch einfügen damit dann der server dann geziehlt daten abruft. nicht 20 mal die sekunde 
				variable['zero']['darkzone']['update'] = '0'
				variable['zero']['darkzone']['webupdate'] = '0'
			
			'''
		
		logging.error('done while')
		ret = {}
		logging.error(json.dumps(iss_stack))
		logging.error(json.dumps(iot_token))
		logging.error(json.dumps(data['token']))
		iss_shadow = iss_stack.copy()
		logging.error('asdaasdsa')
		if data['token'] in iot_token:
	
			for x in iss_shadow: #return all data to client, and delete
				logging.error(x)
				#logging.error('Token')
				#logging.error(data['token'])
				if data['token'] in iss_stack[x]:
					logging.error('Daten zur übermittlung gefunden')
					#logging.error(json.dumps(iss_stack[x]))
					#logging.error('Token')
					#logging.error(data['token'])
					
					
					ret[x] = {}
					ret[x] = iss_stack[x][data['token']]
					del iss_stack[x][data['token']]
	
			
			logging.error(json.dumps(ret))
			logging.error('iss ende')
		else:
			logging.error('unbekannter Token')
			ausgabe = 'unbekannter token'
		
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
		ret['iss_install'] = {}
		ret['iss_install'] = iss_install
		
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

	

	
class sensor():#veraltet und nciht mehr geraucht, aber es wegen new noch vorhanden. 

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

				
class check():
	'''
	dieser part ist veraltet und sollte auf dauer gelöscht werden. da nun alles über iss bearbeitet wird
	Delete sollte in eine andere class verschobwen werden. 
	da es weiterhin die funktion hat alle Variablen zu säubern
	'''
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
		logging.error(json.dumps(variable))
		logging.error(json.dumps(iot_token))
		logging.error(json.dumps(ram))
		#logging.error(json.dumps(iot_config))
		'''
		if variable[host][name]['switch'] == 1: #wenn Client mit einem Multiplexer ausgestatet ist 
			#logging.error('timeslot delete')
			#logging.error(json.dumps(timeschlitz[host][variable[host][name]['timeslot']]))
			del timeschlitz[host][variable[host][name]['timeslot']] #löschen variable
		'''	
		#logging.debug(json.dumps(variable))
		#del variable[host][name] #löschen variable
		
		#logging.error('-1-')
		#logging.error(ram[host][name]['sesession_id'])
		
		del iot_token[ram[host][name]['sesession_id']]
		#logging.error('2')
		#del iot_config[host][name] 
		#logging.error('-3-')
		
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
	'''
	das hier ist die haupt funktion
	alle andfragen werdern hier als erstes rein geschoben 
	und dann zu geordentet 
	'''
	
	def time_slot(self):#erstellt timeslots für muliplexer
		coun_clint = {} # count total of clients
		new_ts = {} # timeslots counts
		slot_count = 6 #slots per second
		#logging.error(json.dumps('first'))
		for x in iot_token: #count clients 
			if iot_token[x]['host'] not in coun_clint:
				coun_clint[iot_token[x]['host']] = 1
				new_ts[iot_token[x]['host']] = {}
				new_ts[iot_token[x]['host']][iot_token[x]['zone']] = {}
				new_ts[iot_token[x]['host']][iot_token[x]['zone']]['count'] = 1
				new_ts[iot_token[x]['host']][iot_token[x]['zone']]['token'] = x
			else:
				coun_clint[iot_token[x]['host']] = coun_clint[iot_token[x]['host']]  + 1
				new_ts[iot_token[x]['host']][iot_token[x]['zone']]['count'] = coun_clint[iot_token[x]['host']]
				new_ts[iot_token[x]['host']][iot_token[x]['zone']]['token'] = x
	
		ts_slots = {} #time-slots
		#logging.error(json.dumps('second'))
		for x in coun_clint: #create Time slots
			slot_counter = coun_clint[x] * slot_count #max slots for client
			slot_length = int (1000 / slot_counter) #slot time
			count = 0 #while steering 
			client_count = 1 #zone conter
			ts_slot_counter = 1
			
			ts_slots[x] = {} 
			while count < slot_counter: 
	
				if client_count not in ts_slots[x]: #first create
					ts_slots[x][client_count] = {}
					ts_slots[x][client_count]['lenght'] = slot_length
					
				ts_slots[x][client_count][ts_slot_counter] = count * slot_length
				
				client_count = client_count + 1
				
				if client_count > coun_clint[x]: # next slot
					client_count = 1
					ts_slot_counter = ts_slot_counter + 1
				
				
				count = count + 1
		#logging.error(json.dumps('thrid'))
		
		#logging.error(json.dumps(ts_slots))
		#logging.error(json.dumps(new_ts))
		#logging.error(json.dumps(coun_clint))
		
		io_con = iot()
		for x in new_ts:
			logging.error (x)
			print (new_ts[x])
			for y in new_ts[x]:
				logging.error(y)
				#print (new_ts[x][y])
				slot = io_con.new_slot({'count':'1'})
				#logging.error(json.dumps(slot))
				#logging.error(json.dumps('hier'))
				cha = iss_create()
				#logging.error(json.dumps('hier1'))
				cha.sender(config['SERVER']['Name'],'none','time_slot','system')#hier server name
				#logging.error(json.dumps('hier2'))
				cha.target(x,y,'Timeslot','system')
				#logging.error(json.dumps('hier3'))
				#logging.error(json.dumps(cha.install_data('Time_slot',ts_slots[x][new_ts[x][y]],'data')))
				token_temp = new_ts[x][y]['token']
				iss_stack[slot[1]][token_temp] = cha.install_data('Time_slot',ts_slots[x][new_ts[x][y]['count']],'data')
				
	
	def new_data (self,umwandel):
		
		if umwandel['funktion'] == 'test':#sollte mal gelöscht werden
			logging.error(json.dumps('funktion:test'))
			raa = 'aaaa'
			return (raa)

		if umwandel['funktion'] == 'add':#erzeugt Client Token, und erstelle Speicher-konstruckt
			insertnew = 1
			if umwandel['host'] in ram:#abfrage ob shon angemeldet
				if umwandel['zone'] in ram[umwandel['host']]:#check ob Client vorhanden, wenbn ja löschen (wenn client unsauber beendet wurde )
					logging.error('why!')
					checker = check()##!!!!!!!hier muss die class umgezogen werden
					checker.delete(umwandel['zone'],umwandel['host'])
					insertnew = 1
					 
				else:
					insertnew = 1
			else:
				ram[umwandel['host']] = {}
				insertnew = 1
				
			if insertnew == 1:##Dies if muss weg wie auch alle insert New !!!!!!! 
				logging.error('new')
				ram[umwandel['host']][umwandel['zone']] = umwandel #in speicher einfügen
				#returner = json.dumps('ok') #ok senden

				
				sesession_id = sensor.new('',20)
				logging.error(sesession_id)
				iot_token[sesession_id] = {}#insert token in Session ID 
				ret = {}
				logging.error(json.dumps(umwandel))
				ret['sesession_id'] = sesession_id
				ram[umwandel['host']][umwandel['zone']]['sesession_id'] = sesession_id #veraltet
				#in refernz datenbank ablegen (durchsuchbar)
				iot_token[sesession_id]['host'] = umwandel['host']
				iot_token[sesession_id]['zone'] = umwandel['zone']
				iot_token[sesession_id]['typ'] = 'server'
				iot_token[sesession_id]['time'] = iot.time('','get')
				
				self.time_slot()

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
			##graue werte sind vars die es mal gab
			logging.error('ram')
			logging.error(json.dumps(ram))
			#logging.error('timeschlitz')
			#logging.error(json.dumps(timeschlitz))
			#logging.error('variable')
			#logging.error(json.dumps(variable))
			#logging.error('sensor_ram')
			#logging.error(json.dumps(sensor_ram))
			logging.error('iot_token')
			logging.error(json.dumps(iot_token))
			logging.error('iss_stack')
			logging.error(json.dumps(iss_stack))
			logging.error('iss_install')
			logging.error(json.dumps(iss_install))
			#logging.error('gir')
			#logging.error(json.dumps(gir))
			
		elif umwandel['funktion'] == 'check': #Veraltet
			logging.debug('check aufruf')
			checker = check()
			#return (checker.eingang(umwandel))
			return ('veraltet')
		
		elif umwandel['funktion'] == 'sensor': ##veraltet
			#logging.error('sensor aufruf')
			#senso = sensor()
			#return senso.eingang(umwandel)
			return senso.eingang('veraltet')
		
		elif umwandel['funktion'] == 'update': #veraltet
			
			#return ram
			return('veraltet')
		
		
		elif umwandel['funktion'] == 'stop': ##veraltet
			'''
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
			'''
			return('veraltet')
			
		
		elif umwandel['funktion'] == 'delete': #wenn ein client nicht mehr benötigt wird 
			logging.error('delete')
			deleter = check()
			ausgabe = deleter.delete(umwandel['zone'],umwandel['host'])
			'''
			if len(variable[umwandel['host']]) != 0:
				logging.debug('delete-create new time slice')
				create = timer_san()
				create.timeslicer(umwandel['host'])
			else:
				logging.debug('delete kein neuer time sclice')
			'''	
			return ausgabe




'''
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
		'#'#'
		for y in ram[host][name]['iot']:
			#logging.error('Fehler bei install daten in Master Server-'+str(ram[host][name][str(y)]['num']+1))
			variable[host][name][y] = {}
			for x in ram[host][name]['iot'][y]:
				
				#logging.error('Fehler bei install daten in Master Serverhhhh')
				variable[host][name][y][x] = {}
				variable[host][name][y][x] = ram[host][name]['iot'][y][x]
				variable[host][name][y][x]['update'] = 0
		'#'#'
				
		 ##kann nachher gelöscht werden
		#logging.error(json.dumps(variable))
'''		
		
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
				lalal = server_io.new_data(json.loads(crondata))
				#logging.error(json.dumps(lalal))
				cron_Server_queue.put(lalal) #Retrun Data to Deamon
					
				
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
		global cron_Server_queue
		
		demon_queue_data = {}
		demon_queue_data['close'] = Queue()
		
		Server_cron_queue = Queue()
		cron_Server_queue = Queue()
		
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
		
		server_name = config['SERVER']['Name']
		######## Install server in Server ###### 
		
		def server_return(): ### Waiter ####
			while True:
				if cron_Server_queue.empty() != True:#cron data
					ret = cron_Server_queue.get()
					logging.error('get data')
					logging.error(json.dumps(ret))
					return(ret)
					break
		
		Server_cron_queue.put(json.dumps({'funktion':'add','host':server_name,'zone':'none','switch':'0'}))
		
		ser = server_return()
		sesession_id = ser['sesession_id']
		
		Server_cron_queue.put(json.dumps({'funktion':'iot','iotfunk':'iss','messages':'','token':sesession_id}))
		ser = server_return()
		
		Server_cron_queue.put(json.dumps({'funktion':'iot','iotfunk':'new_slot','count':'1'}))
		ser = server_return()
		
		cha = iss_create()
		cha.sender(server_name,'none','freq','system')
		cha.update(server_name,'none','freq','system',1)
		mess = {}
		mess[ser[1]] = cha.install_data('freq','25','int')
		#logging.error('aaa')
		#logging.error(json.dumps(mess))
		
		Server_cron_queue.put(json.dumps({'funktion':'iot','iotfunk':'iss','messages':mess,'token':sesession_id}))
		ser = server_return()
		###Basic Data Set into Server
		#logging.error(json.dumps(ser))
		#logging.error('new send 1')


		while True: #basic run
			'''
			#must be AKTIVE wenn Server goes Produktive !!!!!
			Server_cron_queue.put(json.dumps({'funktion':'iot','iotfunk':'iss','messages':'','token':sesession_id}))
			ser = server_return()
			if ser != {}:
				logging.error('es ist zeug vorhanden')
				
				for x in ser :
					if ser[x]['target']['host'] == server_name and ser[x]['sender']['host'] != server_name: ## Echo system, later a need real Timing System
						logging.error('es ist für mich')
						logging.error(json.dumps(ser[x]['data']['id']))
						if ser[x]['data']['id'] == 'freq':
							a = 1
							
							Server_cron_queue.put(json.dumps({'funktion':'iot','iotfunk':'new_slot','count':'1'}))
							ser1 = server_return()
							cha.delete()
							cha.sender(server_name,'none','freq','system')
							cha.update(server_name,'none','freq','system',0)
							mess = {}
							mess[ser1[1]] = cha.install_data('freq',ser[x]['data']['value'],'int')
							Server_cron_queue.put(json.dumps({'funktion':'iot','iotfunk':'iss','messages':mess,'token':sesession_id}))
			'''
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