# coding=utf8
import daemon, os, time, sys, signal, lockfile, daemon.pidfile, socket, socketserver, json, logging, random,datetime
from collections import defaultdict

HOST, PORT = "localhost", 5050 ##adresse und port vom server-server

logger = logging.getLogger()
logger.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh = logging.FileHandler("/net/html/iotserver/server.log")
fh.setFormatter(formatter)
logger.addHandler(fh)


ram = defaultdict(object)
ram = {}

timeschlitz = defaultdict(object)
timeschlitz = {}	

variable = defaultdict(object)
variable = {}

sensor_ram = defaultdict(object)
sensor_ram = {}

#data from client_Server to webclient
iot_ram = defaultdict(object)
iot_ram = {}

#data from webclient to server_client
iot_cache = defaultdict(object)
iot_cache = {}

#auth token, web and server_client
iot_token = defaultdict(object)
iot_token = {}

#iot Config from server_client
iot_config = defaultdict(object)
iot_config = {}

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
					'server_client_get':'server_client_get',
					'server_client_set':'server_client_set',
					'web_new':'web_new',
					'web_exist':'web_exist',
					'web_array':'web_array',
					'web_get':'web_get',
					'web_set':'web_set'
					}
		checker = 0
		for funk in funklist:
			
			#Old web clients delete
			for x in iot_token:

				if iot_token[x]['typ'] == 'webclient':

					if self.time(iot_token[x]['time']) > 300:
						
						del iot_token[x]
						logging.error(json.dumps('token gelöscht'))
						

			#do function		
			if data['iotfunk'] == funk:
				
				
	
				ausgabe = getattr(self,funklist[data['iotfunk']])(data)
				checker = 1
			
			if checker == 0:
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
			
	
	def new_slot(self,data):#returns a new token for web client/ client_server, reserves a new space on ram.
	#erstellt einen token, in dem bereich wo es her kommt. und wo es hin geht. 
		
		token = sensor.new('',10)


	def server_client_get (self,data): #returns new data from web client 
		
		print('mumu')
		
	
	def server_client_set(self,data): #sets data from server_client in ram with notification to web_clients
		
		print('mumu')
			
	
	def web_exist (self,data): # Looks web id is Exist
		ret = {}
		ret['return'] = iot_token.get(data['session_id'], 'not exist')
		
		if ret['return'] != 'not exist':
			ret['return'] = 'ok'
		
		return(ret)
		
		
	def web_new (self,data): # sets new web_clients (usable for Client-server Plugins)
		
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
		ret = {}
		for x in iot_token: #abfrage aller daten
			
			if iot_token[x]['typ'] == "server": #den inhalt von server daten abrufen
				ret[iot_token[x]['host']] = {}
				ret[iot_token[x]['host']][iot_token[x]['zone']] = {}
				
				ret[iot_token[x]['host']][iot_token[x]['zone']] = iot_config[iot_token[x]['host']][iot_token[x]['zone']]
		
		
		logging.error(json.dumps('iot_token'))
		logging.error(json.dumps(iot_token))
		logging.error(json.dumps('iot_config'))
		logging.error(json.dumps(iot_config))
		return (ret)
		
		
	def web_get (self,data): #says the changes on client_server iot
		
		return (data)
		
	def web_set (self,data): #set data to client_server
		
		return (data)
	

	
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
			else:
				returner = "ok" # standart antwort wenn es nichts neues gibt 
				#logging.error('check')
		else:
			logging.error('not exist anymore'+data['zone'])
			returner = 'ok'
			
		return (returner)
		
	def delete(self, name, host): #client aus speicher entfernen
		#logging.error(name)
		#logging.error(json.dumps(timeschlitz))
		#logging.error(json.dumps(variable))
		logging.error(json.dumps(iot_token))
		logging.error(json.dumps(iot_config))
		
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
		del iot_config[host][name] 
		#logging.error('3')
		
		#logging.debug(json.dumps(ram))
		del ram[host][name] #löschen variable
		
		#logging.error(json.dumps(timeschlitz))
		#logging.error(json.dumps(variable))
		#logging.error(json.dumps(ram))
			
		returner = "ok"
		return (returner)

class server(): # server standart Classe
	
	def new_data (self,jsoncode):
		'''
		jede anfrage wird erst durch dieses Konstruck bearbeitet und dann in die passende unterklasse 
		weiter geleitet.
		'''
		try:
			umwandel = json.loads(jsoncode)
    		
		except ValueError as err:
			logging.error('JSON fehlerhaft')
			umwandel = {'funktion':'error'}
		
		if umwandel['funktion'] == 'add':#neuen client in ram einfügen
			insertnew = 1
			if umwandel['host'] in ram:#abfrage ob shon angemeldet
				if umwandel['zone'] in ram[umwandel['host']]:
					returner = json.dumps('why')
					return returner	
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
				iot_config[umwandel['host']] = {}
				iot_config[umwandel['host']][umwandel['zone']]  = {}
				iot_config[umwandel['host']][umwandel['zone']] = umwandel['iot']
				
				logging.error(json.dumps('iot_token'))
				logging.error(json.dumps(iot_token))
				logging.error(json.dumps('iot_config'))
				logging.error(json.dumps(iot_config))
				
				
				addnew.new_client(umwandel['zone'], umwandel['host']) #erzeuge Timeslice 
				#addnew.timeslicer()
				logging.error(ret)
				return json.dumps(ret)
				
		elif umwandel['funktion'] == 'iot': #die standart abrfragen, ob es änderungen giebt
			logging.error('iot aufruf')
			v1 = iot()
			returner = json.dumps(v1.all_in(umwandel))
			return returner
			
			
		elif umwandel['funktion'] == 'check': #die standart abrfragen, ob es änderungen giebt 
			logging.debug('check aufruf')
			checker = check()
			returner = json.dumps(checker.eingang(umwandel))
			return returner
		
		elif umwandel['funktion'] == 'sensor': ##wenn sensort aktiv ist. 
			logging.error('sensor aufruf')
			senso = sensor()
			returner = json.dumps(senso.eingang(umwandel))
			
			#returner = json.dumps(ram)
			return returner
		
		elif umwandel['funktion'] == 'update': ## wenn sich etwas am Server-client ändert (damit inhalt variable geändert wird)
			returner = json.dumps(ram)
			return returner
		
		elif umwandel['funktion'] == 'stop': ## wenn sich etwas am Server-client ändert (damit inhalt variable geändert wird)
			
			logging.error('stop '+umwandel['zone'])
			returner = json.dumps('nope')
			if variable[umwandel['host']][umwandel['zone']]['stop'] == 0:
				logging.error('stop varibale setzen '+umwandel['zone'])
				variable[umwandel['host']][umwandel['zone']]['stop'] = 1
				variable[umwandel['host']][umwandel['zone']]['update'] = 1
				if 'kill' in umwandel:
					variable[umwandel['host']][umwandel['zone']]['kill'] = 1
				returner = json.dumps('ok')
			else:
				#logging.error('else '+variable)
				if variable[umwandel['host']][umwandel['zone']]['update'] == 1:
					logging.error('warten '+umwandel['zone'])
					returner = json.dumps('wait')
				else:
					logging.error('absetzen delete '+umwandel['zone'])
					logging.error('delete')
					deleter = check()
					ausgabe = deleter.delete(umwandel['zone'],umwandel['host'])
					returner = json.dumps('kill')
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
			returner = json.dumps(ausgabe)
			if len(variable[umwandel['host']]) != 0:
				logging.debug('delete-create new time slice')
				create = timer_san()
				create.timeslicer(umwandel['host'])
			else:
				logging.debug('delete kein neuer time sclice')
			return returner
		
		elif umwandel['funktion'] == 'timeslice': #rückgabe neuer Timeslot 
			logging.error('timeslicer_funk')
			logging.error(json.dumps(timeschlitz[umwandel['host']][int(variable[umwandel['host']][umwandel['zone']]['timeslot'])]))
			variable[umwandel['host']][umwandel['zone']]['tsupdate'] = 0
			returner = json.dumps(timeschlitz[umwandel['host']][int(variable[umwandel['host']][umwandel['zone']]['timeslot'])])
			
			return returner
		else:
			logging.error('unbekannter befehl')
			returner = json.dumps('error: unbekannter befehl')
			return returner

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
		
		for y in ram[host][name]['iot']:
			#logging.error('Fehler bei install daten in Master Server-'+str(ram[host][name][str(y)]['num']+1))
			variable[host][name][y] = {}
			for x in ram[host][name]['iot'][y]:
				
				#logging.error('Fehler bei install daten in Master Serverhhhh')
				variable[host][name][y][x] = {}
				variable[host][name][y][x] = ram[host][name]['iot'][y][x]
				variable[host][name][y][x]['update'] = 0
				
		 ##kann nachher gelöscht werden
		#logging.error(json.dumps(variable))


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        data = self.request.recv(10024).strip()
        rawdata = data.decode('utf-8')
        
        call = server()
        
        dataout = call.new_data(rawdata)
        
        ausgabe = dataout.encode('utf8')
        self.request.sendall(ausgabe)

def do_something():
	while True:
		
		
		# Create the server, binding to localhost on port 9999
		server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
		# Activate the server; this will keep running until you
		# interrupt the program with Ctrl-C
		server.serve_forever()
		
		


context = daemon.DaemonContext( #daemon konfig
	working_directory='/net',
   	umask=0o002,
   	pidfile=daemon.pidfile.PIDLockFile('/net/schedule'),
   	files_preserve = [
   		fh.stream,
    ],

)


if len(sys.argv) == 2:
	if 'start' == sys.argv[1]:
		
		loop = 0;
		loopcount = 1;
		# Create the server, binding to localhost on port 9999
		while loop == 0:
			if loopcount > 10:
				loop = 1
			try:
				testverbindung = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
				
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
				do_something()
				
	elif 'stop' == sys.argv[1]:
		pidfile = open('/net/schedule', 'r') #pid File suchen
		line = pidfile.readline().strip()#daten lesen
		pidfile.close()
		#print(line); #nummer ausgabe
		pid = int(line) #zur int umwandelkn
		os.kill(pid, signal.SIGKILL) #PID kill
		os.remove('/net/schedule') #alte PID löschen
		print ('beendet.....')
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

#####Junk zum testen ######

'''


			#tester = json.dumps(ram)
			#file = open('/net/html/i2cclient/file.txt', 'w')
			#with open('file.txt', 'rb+') as file:
			#file.write(tester)
			#file.close()
			
'''