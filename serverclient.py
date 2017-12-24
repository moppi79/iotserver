import daemon, os, time, sys, signal, lockfile, daemon.pidfile, socket, logging, datetime, json, random

from multiprocessing import Process, Queue
from collections import defaultdict
from module.i2c_driver import i2c_treiber
#from i2ccall import i2c_abruf

from sensors.demosensor import demo_sensor
from sensors.bh1750 import bh1750
from sensors.htu21d import htu21d
from module.mcp23017 import mcp23017
from module.pcf8574 import pcf8574

pidfilename = 'clientpid'
workingpath = '/net/html/iotserver'


logger = logging.getLogger()
logger.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh = logging.FileHandler(workingpath+"/client.log")
fh.setFormatter(formatter)
logger.addHandler(fh)


master_pfad = '/net'
master_pidfile = '/net/master' #pidfile verzeichniss/name


'''
Aktoren rechen nach pin
pin		1		2		3		4		5		6		7		8
dezimal	1		2		4		8		16		32		64		128
hex		0x01 	0x02	0x04	0x08	0x10	0x20	0x40	0x80

ic_list und ic_chip
sind nur zum festlegen der START optionen
im laufenden betrieb sind alle werte im ram Bindend vorallem wenn sich ein IC neu starten sollte
werden alle daten aus dem ram gezogen 

'''
i2cswitch = {'adress':0x70,'port':1} #TI-PCA9548A
ic_list = {'host':'raspi2','name':'balkon', 'switch':1, 'sensor':1, 'num':1, 1:0x20} #anzahl I2C slaves mit adresse
'''
ic_list {
'host':'name',# name vom gerät
'name':'balkon', #name des client-server
'switch':1, ## ist ein switch angeschlossen TI-PCA9548A
'sensor':1, (hat dieser server-Client sensor daten zum auslesen 1. oder nur aktoren 0)
'num':1, # anzahl Ic´s 

1:0x20 ## laufende nummer mit hex werten für IC´s 
'''

ic_chip = defaultdict(object)

ic_chip[1] ={'icname':'mcp23017',
			'adresse':0x20,
			'num':7,#anzahl ports
			'bank':2,#anzahl banken
			100:[0x00,0x00,0x12], #adresse der bank, start wert, export register MCP23017
			101:[0x01,0xff,0x13], #adresse der bank, start wert, export register MCP23017 1 in 0 out
			#1:[0x12,0x01,'aktor','beschreibung',1,[ziel bei schalter]], #register,startwert,typ,beschreibung,'fürwebseite Schaltbar' ("0"nein, "1"ja)optionaler wert für schalter
			'pins':{
			1:[0x12,0x01,'out','aktor','Aussen beleuchtung','1'],#IRLZ-relay. aussenbeläuchtung
			2:[0x13,0x01,'in','on_off','Schalter draussen','0',[0x12,0x01]], #Schalter für aussenbleuchtung draussen
			3:[0x12,0x02,'out','aktor','LED','0'],#LED signal lampe draussen
			4:[0x13,0x02,'in','regen','Regensensor','0',[0x12,0x04]],#erkennung Regensensor
			5:[0x12,0x04,'out','heizung','Heizung','0'],#IRLZ schalter - heizung für regensensor
			6:[0x12,0x08,'out','Heartbeat','led','0'],#LED heartbeat
			7:[0x12,0x40,'in','on_off','Schalter draussen','0',[0x12,0x01]],
			}}


ic_chip[2] ={'icname':'pcf8574',
			'display_name':'schreibisch',
			'display_typ':'text', 
			'adress':0x27,
			'lines':4,
			'symbol':20,
			'lineadress':{1:0x80,
						2:0xC0,
						3:0x94,
						4:0xD4}}

sensordic = defaultdict(object)		
			
sensordic = {1:[0x23,'options',bh1750(),'licht'],
			2:[0x40,'options',htu21d(),'temperatur_feuchtigkeit']
}
			
ram = defaultdict(object)
ram = {}

ic_class = {'mcp23017':mcp23017(),'pcf8574':pcf8574()}

class i2c_abruf:
	
	def __init__(self):
		if 'firstrun' in ram:
			ram['firstrun'] = 1 #platzhalter
		else:
			ram['firstrun'] = 1
			
			for x in ic_chip: ##Declare all ic Dic
				ram[ic_chip[x]['icname']] = {}
			
			for x in ic_chip:
				classcall = ic_class[ic_chip[x]['icname']]
				
				ram[ic_chip[x]['icname']][x] = {}
				ram[ic_chip[x]['icname']][x].update(classcall.install(ic_chip[x], x))
				
				
	def icinit(self):
		for x in ic_chip: ##Declare all ic Dic
			ram[ic_chip[x]['icname']] = {}

		for x in ic_chip:
			classcall = ic_class[ic_chip[x]['icname']]
				
			ram[ic_chip[x]['icname']][x] = {}
			ram[ic_chip[x]['icname']][x].update(classcall.install(ic_chip[x]))
	
	def comparison(self):
		
		for x in ic_chip:
			classcall = ic_class[ic_chip[x]['icname']]
			print (classcall.comparison(ram[ic_chip[x]['icname']][x]))
			
			
	def switch(self): ##switch schalten
		
		switch = i2c_treiber(i2cswitch['adress']) 
		zustand = switch.readswitch()
		
		if zustand[1] == 99: #wenn switch nicht mehr erreichbar ist, programm termination
			logging.error('Switch nicht erreichbar')
			
		
		if zustand[1] != i2cswitch['port']: #hier muss drin ste
			switch.write(0x00,i2cswitch['port'])
		switch.close()

class server_coneckt:
	
	def __init__(self):
		
		if 'server_install' in ram:
			ram['server_install'] = ram['server_install']  #platzhalter
			print('nanan')
		else:
			ram['server_install'] = 1 #platzhalter
			transfer = defaultdict(object)
			transfer = {'funktion':'add'} #auszuführende Funktion im server
			transfer.update(ic_list) #funktions infos client
			transfer['iot'] = {}
			#wichtig bei übermittluhng wird nur IoT verwendet. iot[ic_chip][aktor]
			for x in ic_chip:
				transfer['iot'][x] = ram[ic_chip[x]['icname']][x]['iot'] #aktorenliste
			
			
			print (transfer)
			ret = self.sock2(transfer)
			
			#ret = '"ok"'
			if ret != '"ok"':
				logger.error('Fehler bei install daten in Master Server')
				#print (ret)

	def check(self):
	
		verbindung = server_coneckt()
		
		data = {'funktion':'check','name':ic_list['name'], 'host':ic_list['host']}
		#jsonstring = json.dumps(data)
		#antwort = json.loads(verbindung.sock(json.dumps(data))) #daten senden und holen
		antwort = verbindung.sock2(data)
		#antwort = json.loads(verbindung.sock(jsonstring))
		if antwort != 'ok':
			logger.error('änderung check')
			ram['stop'] = antwort['stop']
			
			ram['webupdate'] = antwort['webupdate']#!!!! muss eine ifabrfrage werden (aber auchg nur wichtig wenn KEIN Switch eingebaut ist !!!!!!!)
			
			ram['sensor'] = antwort['sensor']
			
			if antwort['tsupdate'] == 1:
				logger.error('new Time')
				ram['timeslice'] = self.timeslice()
				
		return ('---') ### 
		
	def timeslice(self):
			transfer = defaultdict(object)
			transfer = {'funktion':'timeslice', 'name':ic_list['name'], 'host':ic_list['host']} #auszuführende Funktion im server
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
			
			
			server_address = ('localhost', 5050)#server adresse
			print('connecting to {} port {}'.format(*server_address))
			#print (data)
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#art der verbingdung
			sock.connect(server_address)#verbindung herstellen
			sock.sendall(json_string.encode('utf8'))#befehl senden
			datain = sock.recv(1024).strip()#daten empfangen und leerzeichen entfernen
			sock.close()
			try:
				returner = json.loads(datain.decode('utf-8'))
			except ValueError as error:
				logger.error('Fehlerhafte daten bekommen',datain)
				
			return returner #return daten
		else:
			logger.error('keine funktion übermittelt')
			return 'error'
			
class thread: #ausführen von einzelen plugins im hintergrund0
	
	def __init__(self): #install im ram 
	
		ram['pluginhold'] = {}
	
		
	def new_thread(self,ziel): # start a new thread
		
		new_value = self.skirmish(5)
		ram['pluginhold'][new_value] = {} #erzeugen Container
		ram['pluginhold'][new_value]['queue'] = Queue() # Queue erstellen
		ram['pluginhold'][new_value]['prozess'] = Process(target=ziel, args=('bob',ram['pluginhold'][new_value]['queue'])) #prozess vorbereiten
		ram['pluginhold'][new_value]['prozess'].start() # Prozzes starten
		
		
	def comparison(self): # Abfragen ob Thread daten hat
		checker = 0
		delter = {} # gesammlete keys
		for x in ram['pluginhold']: #abfragen aller aktiven hintergrund prozesse
			checker = 1
			if ram['pluginhold'][x]['queue'].empty() != True: 
				delter[x] = x
				print (ram['pluginhold'][x]['queue'].get())
				
		if checker == 1: #nur aktiv wenn es einen aktiven prozess giebt
			for x in delter:
				self.end_thread(x)

			
	def end_thread(self,thread): # clean up
		ram['pluginhold'][thread]['prozess'].join()
		ram['pluginhold'][thread]['queue'].close
		ram['pluginhold'][thread]['prozess'].terminate()
		ram['pluginhold'].pop(thread)
		print('del')
		
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
		
def main_loop():
	loopmaster = 0
	secondloop = 70
	loopspeed = 1
	loopcounter = 1
	
	run = 0
	
	abfragen_sec = 10
	
	now = datetime.datetime.now()
	calc = {now.microsecond}
	
	loop_server_call = 0
	
	i2ccall = i2c_abruf()#umgebung starten 
	print('hier')
	print(ram)
	
	socket_call = server_coneckt()#Server verbindung starten
	socket_call.check()
	
	while True:
		#break
		########### Loop Time Management head #############
		start = ms_time(0)
		print (start)
		print('start')
		sleeptime_i2c_wait = 0
		'''
		if secondloop != ms_time(1): #every new second
			secondloop = ms_time(1)
			print ('loopcounter {} / loopspeed{} = {}'.format(loopcounter,loopspeed,(int(loopspeed/loopcounter))))
			speed = (int(1000000 - (int(loopspeed/loopcounter))*10)/10)/1000000
			loopspeed = 0
			loopcounter = 0
			if speed < 0: 
				speed = 0.1 #when speed negativ
				print ('negativ speed!!!!')
				
		'''
		
		
		
		########### Loop Time Management head END#############

		################### Multiplex system install ###################
		if ram['server_install'] == 1 and ic_list['switch'] == 1:
			ram['server_install'] = 0
			ram['timeslice_runtime'] = {}
			count = 0
			print('Multiplex system install')
			for x in ram['timeslice']: #Timeslice for
				
				if x != 'schlitzzeit': #schlitzzeit filter
					count += 1	
					
					calc = ms_time(0)
					maxtime =  ram['timeslice'][x] + ram['timeslice']['schlitzzeit'] #max runtime in timeslot
					if ram['timeslice'][x] < calc and maxtime > calc: #time korridor
						if str(int(x)+1) in ram['timeslice']:
							wait = (ram['timeslice'][str(int(x)+1)] - calc) /1000000 #wait time to next time slot
							ram['timeslice_runtime']['timeslice'] = int(x)+1
						else:
							wait = ((1000000 - calc) + (ram['timeslice']['1'])) /1000000 # if the max slice arrived go to first time slot
							ram['timeslice_runtime']['timeslice'] = 1
					
					maxtime = ram['timeslice'][x] - ram['timeslice']['schlitzzeit'] #when time another time slot. wait to the next slot 
					if ram['timeslice'][x] > calc and maxtime < calc:
						if str(int(x)+1) in ram['timeslice']:
							wait = (ram['timeslice'][str(int(x)+1)] - calc) /1000000
							ram['timeslice_runtime']['timeslice'] = int(x)+1
						else:
							wait = ((1000000 - calc) + (ram['timeslice']['1'])) /1000000 # if the max slice arrived go to first time slot
							ram['timeslice_runtime']['timeslice'] = 1
							
			ram['timeslice_runtime']['max'] = count 
			ram['timeslice_runtime']['second_now'] = ms_time(1)
			print('hier wait')
			print(wait)
			time.sleep(wait)
			
			i2ccall.switch() # Multiplex config
		
		#break
		################### Multiplex system install ###################
		#print(ram['timeslice'])
		################### I²C Call ###################
		if ram['stop'] == 0:
			if ic_list['switch'] == 1:
				now_timer = ms_time(0) 
				maxruntime = ram['timeslice'][str(ram['timeslice_runtime']['timeslice'])] + ram['timeslice']['schlitzzeit']

				if ram['timeslice'][str(ram['timeslice_runtime']['timeslice'])] < now_timer and maxruntime > now_timer: #abfrage ob zeit in zeitschlictz liegt 
					#print ('now timeslice')
					#print (ram['timeslice'][str((ram['timeslice_runtime']['timeslice'])+1)])
					
					zahl = now_timer - ram['timeslice'][str(ram['timeslice_runtime']['timeslice'])]
					prozentzahl = int((zahl / ram['timeslice']['schlitzzeit']) * 100) #prozentualer anteil im zeitschlitz
					#print ( 'ergebniss {}. now: {}'.format(zahl, ram['timeslice']['schlitzzeit']))
					print ( 'hier die zahl {} %'.format(prozentzahl))

					i2ccall.switch()# wenn Multiplexer vorhanden dann nun multiplexer einstellen
					i2ccall.comparison() #ausführen
					
					if prozentzahl > 50: #wenn die zeit drüber liegt. nächster zeitschlitz. 
						
						if ram['timeslice_runtime']['max'] < (ram['timeslice_runtime']['timeslice'])+1:
							ram['timeslice_runtime']['timeslice'] = 1
						else:
							ram['timeslice_runtime']['timeslice'] += 1
				else:
					#print('error')
					print ('neu slice') 
					loop1 = 1
					lastnumber = 0
					while ram['timeslice_runtime']['max'] >= loop1:
						#'timeslice': {'6': 833330, '5': 666664, '1': 0, '4': 499998, '3': 333332, 'schlitzzeit': 166666, '2': 166666}, 
						# 'timeslice_runtime': {'max': 6, 'second_now': 54, 'timeslice': 5},
						if loop1 == ram['timeslice_runtime']['max'] and lastnumber == 0:
							print('fast')
							ram['timeslice_runtime']['timeslice'] = 1
							sleeptime_i2c_wait = 1
						else:	
							if ram['timeslice'][str(loop1)] < now_timer and ram['timeslice'][str(loop1+1)] > now_timer:
								print('yeah')
								ram['timeslice_runtime']['timeslice'] = loop1+1
								lastnumber = 1
								sleeptime_i2c_wait = 1
						#print(loop1)
						loop1 += 1

			else:
				print('vergleich ohne switch')
				#i2ccall.comparison() #ausführen
		else:
			print('stop')
				
		
		################### I²C Call END###################
			
		################### Servercall ###################
		ministart = ms_time(0)
		if loop_server_call == 0 and ms_time(0) < 500000:
			#logger.error('checker halb')
			loop_server_call = 1
			socket_call.check()
			print (ms_time(0) - ministart )
			
			
		if loop_server_call == 1 and ms_time(0) > 500000:
			#logger.error('checker voll')
			loop_server_call = 0
			socket_call.check()
			print (ms_time(0) - ministart )
			
		
		################### ServerCall End ###################
		
		################### Plugin  ###################
		
		
		
		print ('----hier-----')
		
		#print(ram)
		
		################### Plugin END ###################
		
		
		
		################### Sensor Call ###################
		if ram['sensor'] != 0: #wenn der Server alle Sensort daten will. (system steh dann auf stop)
			data = {'funktion':'sensor','sensor':'start', 'target_key':ram['sensor'], 'name':ic_list['name'], 'host':ic_list['host']}
			while True:
				
				antwort = socket_call.sock2(data)
				
				if antwort == 'go': ## wenn server go gibt da
					
					i2ccall.switch()#switch schalten
					
					deliver = {'funktion':'sensor','sensor':'deliver', 'target_key':ram['sensor'], 'name':ic_list['name'], 'host':ic_list['host']}
					deliver['werte'] = {}

					for x in sensordic:
						deliver['werte'][x] = {}
						xx = sensordic[x][2]
		
						deliver['werte'][x] = xx.out(sensordic[x][0],sensordic[x][1])
						
					socket_call.sock2(deliver)

					break
				else:
					
					time.sleep(0.05)
		################### Sensor Call END ###################		
		
		################### prototypinm ###################	
		
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
			
		
		
		################### prototypinm END ###################	
		
		########### Loop Time Management foot #############
		stop = ms_time(0)
		run = stop - start
		if run < 0: #start Stop Between zwo seconds 
			run2 = 1000000 - start
			run = run2 + stop
		
		durchschnitt_erreichnet = 1000000 / abfragen_sec # ms / abfragen die sec.
		
		speed = (durchschnitt_erreichnet - run) / 1000000
		if speed < 0: 
			speed = 0.1 #when speed negativ
			print ('negativ speed!!!!')
		print ('footer')
		print (speed)	
		print ('footer')
		
		if sleeptime_i2c_wait == 1: #update time i2c Multiplex wait 
			if ram['timeslice_runtime']['timeslice'] == 1:
				
				speed = ((1000000 - stop) + (ram['timeslice']['1'])) / 1000000
				
				
				print ('nummer 1 speed neu: {} ,stop: {} ram: {} '.format(speed,stop,ram['timeslice']['1']))
			else:	
				speed = (ram['timeslice'][str(ram['timeslice_runtime']['timeslice'])] - stop) / 1000000 
				print ('speed neu: {} '.format(speed))
		time.sleep(speed)# calculated Sleep
		loopspeed += run
		loopcounter += 1
		########### Loop Time Management Foot #############
		
		if 'loopcountdebug' == sys.argv[1]:
			loopmaster += 1
			if loopmaster > int(sys.argv[2]):
				print(ram)
				testersa = {'funktion':'delete','name':ic_list['name'] ,'host':ic_list['host']}
			
				antwort = json.loads(socket_call.sock(json.dumps(testersa)))
				#print (ram['timeslice'])
				print ('programm ende')
				break #zum solo testen muss am schluss entfernt werden
			
			print (loopmaster)

		
		if 'singledebug' == sys.argv[1]:
			
			testersa = {'funktion':'delete','name':ic_list['name'] ,'host':ic_list['host']}
			antwort = json.loads(socket_call.sock(json.dumps(testersa)))
			break #muss zum ende entfernt werden






context = daemon.DaemonContext( #daemon konfig
	working_directory= workingpath ,
   	umask=0o002,
   	pidfile=daemon.pidfile.PIDLockFile(workingpath+'/'+pidfilename),
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
		testersa = {'funktion':'stop','name':ic_list['name'] ,'host':ic_list['host']}
			
		antwort = server_coneckt.sock2('',testersa)
		while True:
			testersa = {'funktion':'stop','name':ic_list['name'] ,'host':ic_list['host']}
			antwort = server_coneckt.sock2('',testersa)
			time.sleep(1)
			if antwort == 'kill':
				
				print('client stopped')
				break 
			
		pidfile = open(workingpath+'/'+pidfilename, 'r') #pid File suchen
		line = pidfile.readline().strip()#daten lesen
		pidfile.close()
		#print(line); #nummer ausgabe
		pid = int(line) #zur int umwandelkn
		os.kill(pid, signal.SIGKILL) #PID kill
		os.remove(workingpath+'/'+pidfilename) #alte PID löschen
		print ('Client Closed')
	elif 'restart' == sys.argv[1]:
		print ("lala") ##noch nichts geplant
	elif 'singledebug' == sys.argv[1]:
		main_loop()	
	
	elif 'loopcountdebug' == sys.argv[1]:
		print ("aa")
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

