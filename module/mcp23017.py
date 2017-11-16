import daemon, os, time, sys, signal, lockfile, daemon.pidfile, socket, logging, datetime, json, random

from module.i2c_driver import i2c_treiber
'''
class mcp23017():	
	def install(self,data):
		return ('lala',data)
		
	Standart Variable
	
	ic_chip[1] ={'icname':'mcp23017',
			'adresse':0x20,
			'num':6,#anzahl ports
			'bank':2,#anzahl banken
			'pins':8,#anzahlpins
			100:[0x00,0x00,0x12], #adresse der bank, start wert, export register MCP23017
			101:[0x01,0xff,0x13], #adresse der bank, start wert, export register MCP23017 1 in 0 out
			#1:[0x12,0x01,'aktor','beschreibung',1,[ziel bei schalter]], #register,startwert,typ,beschreibung,'fürwebseite Schaltbar' ("0"nein, "1"ja)optionaler wert für schalter
			pins:{
			1:[0x12,0x01,'aktor','Aussen beleuchtung','1'],#IRLZ-relay. aussenbeläuchtung
			2:[0x13,0x01,'on_off','Schalter draussen','0',[0x12,0x01]], #Schalter für aussenbleuchtung draussen
			3:[0x12,0x02,'aktor','LED','0'],#LED signal lampe draussen
			4:[0x13,0x02,'regen','Regensensor','0',[0x12,0x04]],#erkennung Regensensor
			5:[0x12,0x04,'heizung','Heizung','0'],#IRLZ schalter - heizung für regensensor
			6:[0x12,0x08,'Heartbeat','led','0'],#LED heartbeat
			}}
		
'''

class mcp23017():	
	def install(self,config,number):

			looplist = 0 #ic loop
			loopbank = 0 #register bank Loop
			loopchip = 0 #ic Pin Loop
			#return_var = defaultdict(object)
			return_var={}
			return_var[config['icname']] = {}
			return_var[config['icname']][number] = {}
			return_var[config['icname']][number]['bank'] = {}
			return_var[config['icname']][number]['pin'] = {}
			
			return_var[config['icname']][number]['bank']['100'] = config[100][1] #der zu vergleichende speicher
			return_var[config['icname']][number]['bank']['101'] = config[101][1] #der zu vergleichede speicher
			
			for x in config['pins']:
				return_var[config['icname']][number]['pin'][x] = {}
				return_var[config['icname']][number]['pin'][x]['value'] = 0
				return_var[config['icname']][number]['pin'][x]['chache'] = 0
			
			
			
			ic2 = i2c_treiber(config['adresse'])
			ic2.write(config[100][0],return_var[config['icname']][number]['bank']['100'])
			ic2.write(config[101][0],return_var[config['icname']][number]['bank']['101'])
			ic2.close() #verbindung schliessen 
			
			return (return_var)
		
	
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
						
						#hier dann die einzelenen funktionen abrufen
						#muss noch programmiert und getestet werden
					

					print (chip_array)
			
			ic2.close()