import daemon, os, time, sys, signal, lockfile, daemon.pidfile, socket, logging, datetime, json, random

from collections import defaultdict
from i2cdriver import i2c_treiber
#from i2ccall import i2c_abruf

logging.basicConfig(format='%(asctime)s %(message)s',filename='example.log',level=logging.DEBUG) #!!!!!!verzeichniss anpassen am schluss !!!!!!
	#logging.warning('And this, too')


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
ic_list = {'name':'balkon', 'switch':1, 'sensor':1, 'num':1, 1:0x20} #anzahl I2C slaves mit adresse
'''
ic_list {
'name':'balkon', #name des client-server
'switch':1, ## ist ein switch angeschlossen TI-PCA9548A
'sensor':1, (hat dieser server-Client sensor daten zum auslesen 1. oder nur aktoren 0)
'num':1, # anzahl Ic´s 

1:0x20 ## laufende nummer mit hex werten für IC´s 
'''

ic_chip = defaultdict(object)

ic_chip[1] ={'num':6,#anzahl ports
			'bank':2,#anzahl banken
			'pins':8,#anzahlpins
			100:[0x00,0x00,0x12], #adresse der bank, start wert, export register MCP23017
			101:[0x01,0xff,0x13], #adresse der bank, start wert, export register MCP23017 1 in 0 out
			#1:[0x12,0x01,'aktor','beschreibung',1,[ziel bei schalter]], #register,startwert,typ,beschreibung,'fürwebseite Schaltbar' ("0"nein, "1"ja)optionaler wert für schalter
			1:[0x12,0x01,'aktor','Aussen beleuchtung','1'],#IRLZ-relay. aussenbeläuchtung
			2:[0x13,0x01,'on_off','Schalter draussen','0',[0x12,0x01]], #Schalter für aussenbleuchtung draussen
			3:[0x12,0x02,'aktor','LED','0'],#LED signal lampe draussen
			4:[0x13,0x02,'regen','Regensensor','0',[0x12,0x04]],#erkennung Regensensor
			5:[0x12,0x04,'heizung','Heizung','0'],#IRLZ schalter - heizung für regensensor
			6:[0x12,0x08,'Heartbeat','led','0'],#LED heartbeat
			}
			
ram = defaultdict(object)
ram = {}


class i2c_abruf:
	
	def __init__(self):
		if 'firstrun' in ram:
			ram['firstrun'] = 1 #platzhalter
		else:
			ram['firstrun'] = 1
			looplist = 0 #ic loop
			loopbank = 0 #register bank Loop
			loopchip = 0 #ic Pin Loop
								
			while looplist < ic_list['num']:
				looplist += 1

				ic2 = i2c_treiber(ic_list[looplist]) #verbfung zum IC aufbauen
				
				#bank while für start werte install
				while loopbank < ic_chip[looplist]['bank']:
					bankcount = 100 + loopbank
					wert = (self.ramlokation(ic_list[looplist], ic_chip[looplist][bankcount][0], bankcount))#wert im speicher IC adresse, Bank programmier adresse, bank nummer im ic_chip array
					ram.update({wert:ic_chip[looplist][bankcount][1]})
					wert = (self.ramlokation(ic_list[looplist], ic_chip[looplist][bankcount][2], 'value')) #der immer zu sehende Bank wert beim auslesen
					ram.update({wert:0})
					loopbank += 1
					ic2.write(ic_chip[looplist][bankcount][0],ic_chip[looplist][bankcount][1]) #IC speicher schreiben
					loopblank = 0
					blankintern = 1
			
					while loopblank < ic_chip[looplist]['pins']:#Für jeden pin in der bank einen blanko array punkt erstellen
						wert = (self.ramlokation(ic_list[looplist], blankintern, ic_chip[looplist][bankcount][2]))#IC adresse, Pin, Bank
						ram.update({wert:0}) #soll wert, wenn anders muss funktion ausgeführt werden
						chache = wert + 'chache' #zwischenspeicher für einzel funktionen,
						ram.update({chache:0})
						funktion = wert + 'funktion'
						ram.update({funktion:0}) #hier array adresse für funktion
						blankintern = blankintern * 2
						loopblank += 1

				while loopchip < ic_chip[looplist]['num']:
					wert=0
					#print (ic_chip[looplist][1]
					loopchip += 1 
					wert = (self.ramlokation(ic_list[looplist], ic_chip[looplist][loopchip][1], ic_chip[looplist][loopchip][0])) #wert im speicher: IC adresse, Pin speicher wert, bank ausgabe
					ram[wert]= loopchip #hinterlegte funktion im array 
					
	
				loopchip = 0 #reset vom IC-Pin loop
				ic2.close() #verbindung schliessen 			

	
	def ramlokation (self, slaveadress, dictorylokation, bank): #zum berechnen der postion im ram jedes einzelen aktoren
		return str(slaveadress) + str(dictorylokation) + str(bank)
		
	def integertobyte (self,wert): #den Hex wert aus der bank in einen 8 bit array umschreiben
		array = [i for i in range(9)]
		count = 128;
		count2 = 8
		while count2 > 0:
			new = wert - count
				
			if new < 0:
				array[count2] = 0			
			elif new == 0:
				wert = 0
				array[count2] = 1
			else:
				array[count2] = 1
				wert = new
			
			count = count / 2
			count2 -= 1
		return(array)		

	def abgleich (self): # fragt die bänke ab und vergleicht es mit dem Ram abbild um veränderungen festzustellen
		looplist = 0 #ic loop
		loopchip = 0 #ic Pin Loop
		
		while looplist < ic_list['num']:
			looplist += 1
			
			ic2 = i2c_treiber(ic_list[looplist]) 
			while loopchip < ic_chip[looplist]['bank']:
				bank = 100 + loopchip
				loopchip += 1
				data = ic2.read(ic_chip[looplist][bank][2])
				
				ramobjekt = self.ramlokation(ic_list[looplist], ic_chip[looplist][bank][2], 'value')
				if data[1] != ram[ramobjekt]:
					ram[ramobjekt] = data[1]
					loopchip2 = 1
					bitcharge = 128
					chip_array = self.integertobyte(data[1]) 
					while loopchip2 < 8:
						 
						wert = self.ramlokation(ic_list[looplist], bitcharge, ic_chip[looplist][bank][2])
						bitcharge = bitcharge / 2 
						loopchip2 += 1
						'''
						#hier dann die einzelenen funktionen abrufen
						#muss noch programmiert und getestet werden
						'''

					print (chip_array)
			
			ic2.close()
			
			
class server_coneckt:
	
	def __init__(self):
		
		if 'server_install' in ram:
			ram['server_install'] = 1 #platzhalter
		else:
			ram['server_install'] = 1 #platzhalter
			transfer = defaultdict(object)
			transfer = {'funktion':'add'} #auszuführende Funktion im server
			transfer.update(ic_list) #funktions infos client
			for x in ic_chip:
				transfer[x] = ic_chip[x] #aktorenliste
		
			jsonstring = json.dumps(transfer)
			ret = self.sock(jsonstring)
			if ret != '"ok"':
				logging.error('Fehler bei install daten in Master Server')
				print (ret)

	def check(self):
	
		verbindung = server_coneckt()
		
		data = {'funktion':'check','name':ic_list['name']}
		#jsonstring = json.dumps(data)
		antwort = json.loads(verbindung.sock(json.dumps(data))) #daten senden und holen
		#antwort = json.loads(verbindung.sock(jsonstring))
		print (antwort)
		
		if antwort != 'ok':
			ram['stop'] = antwort['stop']
			
			ram['webupdate'] = antwort['webupdate']#!!!! muss eine ifabrfrage werden (aber auchg nur wichtig wenn KEIN Switch eingebaut ist !!!!!!!)
			
			ram['sensor'] = antwort['sensor']
			
			if antwort['tsupdate'] == 1:
				
				ram['timeslice'] = self.timeslice()
				
		return ('---') ### 
		
	def timeslice(self):
			transfer = defaultdict(object)
			transfer = {'funktion':'timeslice', 'name':ic_list['name']} #auszuführende Funktion im server
			transfer.update(ic_list) #funktions infos client
			jsonstring = json.dumps(transfer)
			ret = self.sock(jsonstring)
			
			umwandel = json.loads(ret)
			
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


		
def main_loop():
	loopmaster = 0
	while True:
		
		ramm = i2c_abruf()
		
		tester = server_coneckt()
		
		
		tester.check()
		
		
		
		print (tester.timeslice())
		
		print(ram)	
		
		testers = {'funktion':'sensor','sensor':'new'}
		
		antwort = json.loads(tester.sock(json.dumps(testers)))
		
		
		print (antwort)
		
		testers = {'funktion':'delete','name':ic_list['name']}
		
		antwort = json.loads(tester.sock(json.dumps(testers)))
		
		

		
		print (antwort)
		
		#if ram[] # hier dann sensoer
		
		''' sensortester
		
		tester = {'funktion':'sensor','sensor':'new'}
		jsonstring = json.dumps(tester)
		print (test.sock(jsonstring))
		
		'''
		#print (test.timeslice())
		
		
		'''
		test = timer_san()
		test.new_client('mops')
		test.new_client('mops3')
		#print (len(variable))
		test.timeslicer()
		print(variable)
		print(timeschlitz)
		'''
		
		##siehe tester.py für mehr alten kram
		
		#print (loopmaster)
		time.sleep(0.01)
		loopmaster += 1
		if loopmaster > 1000:
			break #zum solo testen muss am schluss entfernt werden
		break #muss zum ende entfernt werden



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
