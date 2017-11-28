import daemon, os, time, sys, signal, lockfile, daemon.pidfile, socket, logging, datetime, json, random

from collections import defaultdict
from module.i2c_driver import i2c_treiber
#from i2ccall import i2c_abruf

from sensors.demosensor import demo_sensor
from sensors.bh1750 import bh1750
from sensors.htu21d import htu21d
from module.mcp23017 import mcp23017

logger = logging.getLogger()
logger.setLevel(logging.ERROR)
fh = logging.FileHandler("/net/html/i2cclient/client.log")
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
			'pins':8,#anzahlpins
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


sensordic = defaultdict(object)		
			
sensordic = {1:[0x99,'options',demo_sensor(),'temperatur/feuchtigkeit'],
			2:[0xa0,'options',demo_sensor(),'licht'],
			3:[0x23,'options',bh1750(),'licht'],
			4:[0x40,'options',htu21d(),'temperatur_feuchtigkeit']
}
			
ram = defaultdict(object)
ram = {}

ic_class = {'mcp23017':mcp23017()}

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
			for x in ic_chip:
				transfer[x] = ic_chip[x] #aktorenliste
			
			#jsonstring = json.dumps(transfer)
			#ret = self.sock(jsonstring)
			ret = self.sock2(transfer)
			if ret != '"ok"':
				logger.error('Fehler bei install daten in Master Server')
				print (ret)

	def check(self):
	
		verbindung = server_coneckt()
		
		data = {'funktion':'check','name':ic_list['name'], 'host':ic_list['host']}
		#jsonstring = json.dumps(data)
		#antwort = json.loads(verbindung.sock(json.dumps(data))) #daten senden und holen
		antwort = verbindung.sock2(data)
		#antwort = json.loads(verbindung.sock(jsonstring))
		if antwort != 'ok':
			
			ram['stop'] = antwort['stop']
			
			ram['webupdate'] = antwort['webupdate']#!!!! muss eine ifabrfrage werden (aber auchg nur wichtig wenn KEIN Switch eingebaut ist !!!!!!!)
			
			ram['sensor'] = antwort['sensor']
			
			if antwort['tsupdate'] == 1:
				
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
			print (data)
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

def ms_time(select): #return 0 ms 1 Second 2 array with both
	now = datetime.datetime.now()
	if select == 0:
		return (now.microsecond)
	elif select == 1:
		return (now.second)
	else:
		return ({0:now.microsecond,1:now.second})
		
def main_loop():
	loopmaster = 0
	secondloop = 70
	loopspeed = 1
	loopcounter = 1
	
	now = datetime.datetime.now()
	calc = {now.microsecond}
	
	loop_server_call = 0
	
	i2ccall = i2c_abruf()#umgebung starten 
	print('hier')
	socket_call = server_coneckt()#Server verbindung starten
	socket_call.check()
	
	while True:

		########### Loop Time Management head #############
		start = ms_time(0)
		print (start)
		print('start')

		if secondloop != ms_time(1): #every new second
			secondloop = ms_time(1)
			#print ('loopcounter {} / loopspeed{} = {}'.format(loopcounter,loopspeed,(int(loopspeed/loopcounter))))
			speed = (int(1000000 - (int(loopspeed/loopcounter))*10)/10)/1000000
			loopspeed = 0
			loopcounter = 0
			if speed < 0: 
				speed = 0.1 #when speed negativ
				print ('negativ speed!!!!')
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
		
		if ic_list['switch'] == 1:
			now_timer = ms_time(0) 
			maxruntime = ram['timeslice'][str(ram['timeslice_runtime']['timeslice'])] + ram['timeslice']['schlitzzeit']
			
			if now_timer < ram['timeslice'][str(ram['timeslice_runtime']['timeslice'])]:
				print ('FEHLER ZEIT')
				print ('aktuelle zeit: {} -- Timeslot: {}'.format(now_timer,ram['timeslice'][str(ram['timeslice_runtime']['timeslice'])]))
				wait = round((ram['timeslice'][str(ram['timeslice_runtime']['timeslice'])] - now_timer) /1000000,3)
				print (wait)
				time.sleep(wait)
				older = now_timer 
				now_timer = ms_time(0) 
				print ('alt:{} -- neu{}'.format(older,now_timer ))
				
			if ram['timeslice_runtime']['max'] < (ram['timeslice_runtime']['timeslice'])+1:
				next_slice = 1
			else:
				next_slice =  (ram['timeslice_runtime']['timeslice'])+1
			
			if ram['timeslice'][str(ram['timeslice_runtime']['timeslice'])] < now_timer and maxruntime > now_timer:
				#print ('now timeslice')
				#print (ram['timeslice'][str((ram['timeslice_runtime']['timeslice'])+1)])
				
				zahl = now_timer - ram['timeslice'][str(ram['timeslice_runtime']['timeslice'])]
				prozentzahl = int((zahl / ram['timeslice']['schlitzzeit']) * 100)
				#print ( 'ergebniss {}. now: {}'.format(zahl, ram['timeslice']['schlitzzeit']))
				print ( 'hier die zahl {} %'.format(prozentzahl))
				#print ('{} < {} and {} > {}'.format(ram['timeslice'][str(ram['timeslice_runtime']['timeslice'])], now_timer, maxruntime, now_timer))
				
				if prozentzahl > 50:
					
					if ram['timeslice_runtime']['max'] < (ram['timeslice_runtime']['timeslice'])+1:
						ram['timeslice_runtime']['timeslice'] = 1
					else:
						ram['timeslice_runtime']['timeslice'] += 1
			else:
				#print('error')
				ram['server_install'] = 1
				print ('maxruntime:{}  ,next_slice:{} ram-timeslice_runtime-timeslice:{} aktuelltime slice:{}'.format(maxruntime,next_slice,ram['timeslice'][str(next_slice)] ,ram['timeslice_runtime']['timeslice']))	
				print ('{} < {} and {} > {}'.format(maxruntime, now_timer, ram['timeslice'][str(next_slice)] , now_timer))
					
					#i2ccall.switch()# wenn Multiplexer vorhanden dann nun multiplexer einstellen
		else:
			i2ccall.comparison() #ausführen
		
		################### I²C Call END###################
			
		################### Servercall ###################
		ministart = ms_time(0)
		if loop_server_call == 0 and ms_time(0) < 500000:
			loop_server_call = 1
			socket_call.check()
			
		if loop_server_call == 1 and ms_time(0) > 500000:
			loop_server_call = 0
			socket_call.check()
			
		print (ms_time(0) - ministart )
		################### ServerCall End ###################
		
		#			
		
		
		#i2ccall.switch()
		#print(ram)
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
		
		########### Loop Time Management foot #############
		stop = ms_time(0)
		run = stop - start
		if run < 0: #start Stop Between zwo seconds 
			run2 = 1000000 - start
			run = run2 + stop
		time.sleep(speed)# calculated Sleep
		loopspeed += run
		loopcounter += 1
		########### Loop Time Management Foot #############
		loopmaster += 1
		if loopmaster > 50:
			testersa = {'funktion':'delete','name':ic_list['name'] ,'host':ic_list['host']}
		
			antwort = json.loads(socket_call.sock(json.dumps(testersa)))
			print (ram['timeslice'])
			break #zum solo testen muss am schluss entfernt werden
		
		#testersa = {'funktion':'delete','name':ic_list['name'] ,'host':ic_list['host']}
		
		#antwort = json.loads(tester.sock(json.dumps(testersa)))
		#break #muss zum ende entfernt werden



main_loop()

'''

context = daemon.DaemonContext( #daemon konfig
	working_directory=master_pfad,
   	umask=0o002,
   	pidfile=daemon.pidfile.PIDLockFile(master_pidfile),

)

if len(sys.argv) == 2:
	if 'start' == sys.argv[1]:
		print("wird gestartet ...")
		with context:
			main_loop()
	elif 'stop' == sys.argv[1]:
		pidfile = open(master_pidfile, 'r') #pid File suchen
		line = pidfile.readline().strip()#daten lesen
		pidfile.close()
		print(line); #nummer ausgabe
		pid = int(line) #zur int umwandelkn
		os.kill(pid, signal.SIGKILL) #PID kill
		os.remove(master_pidfile) #alte PID löschen
		print ('beendet.....')
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

'''