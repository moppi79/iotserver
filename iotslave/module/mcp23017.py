import daemon, os, time, sys, signal, logging, datetime, json, random

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
			100:[0x00,0x00,0x12], #adresse der bank, start wert, export register MCP23017
			101:[0x01,0xff,0x13], #adresse der bank, start wert, export register MCP23017 1 in 0 out
			#1:[0x12,0x01,'in/out','aktor','beschreibung',1,[ziel bei schalter]], #register,startwert,Direction,typ,beschreibung,'fürwebseite Schaltbar' ("0"nein, "1"ja)optionaler wert für schalter
			pins:{
			1:[0x12,0x01,'out','aktor','Aussen beleuchtung','1'],#IRLZ-relay. aussenbeläuchtung
			2:[0x13,0x01,'in','on_off','Schalter draussen','0',[0x12,0x01]], #Schalter für aussenbleuchtung draussen
			3:[0x12,0x02,'out','aktor','LED','0'],#LED signal lampe draussen
			4:[0x13,0x02,'in','regen','Regensensor','0',[0x12,0x04]],#erkennung Regensensor
			5:[0x12,0x04,'out','heizung','Heizung','0'],#IRLZ schalter - heizung für regensensor
			6:[0x12,0x08,'out','Heartbeat','led','0'],#LED heartbeat
			}}
		
'''

class mcp23017:	
	def install(self,config,number):

		looplist = 0 #ic loop
		loopbank = 0 #register bank Loop
		loopchip = 0 #ic Pin Loop
		#return_var = defaultdict(object)
		return_var={}
		return_var['adress'] = config['adresse']
		return_var['bank'] = {}
		return_var['pin'] = {}
		return_var['iot'] = {}
		
		return_var['bank'][config[100][2]] = config[100][1] #der zu vergleichende speicher
		return_var['bank'][config[101][2]] = config[101][1] #der zu vergleichede speicher
		
		numberwhile = 1
		
		while numberwhile <= 128:
			bank1 = self.ramlokation(config['adresse'],numberwhile,config[100][2])
			bank2 = self.ramlokation(config['adresse'],numberwhile,config[101][2])
				
			#print (bank1)
			return_var['pin'][bank1] = {}
			return_var['pin'][bank2] = {}
			return_var['pin'][bank1]['exist'] = 0
			return_var['pin'][bank2]['exist'] = 0
				
			numberwhile = numberwhile * 2
			
			
		for x in config['pins']:
			
			ownlokation = self.ramlokation(config['adresse'],config['pins'][x][1],config['pins'][x][0])
				
			return_var['pin'][ownlokation]['value'] = 0
			return_var['pin'][ownlokation]['chache'] = 0
			return_var['pin'][ownlokation]['exist'] = 1
			return_var['pin'][ownlokation]['config'] = {}
			return_var['pin'][ownlokation]['config'] = config['pins'][x]
			
			
			return_var['iot'][x] = {'name':config['pins'][x][4],'value':0, 'typ':config['pins'][x][2],'usable':config['pins'][x][5],'id':ownlokation}
			
		return (return_var)
			
	
	def icinit(self,config):# config write into Ic 
		
		ic2 = i2c_treiber(config['adresse'])
		ic2.write(config[100][0],config[100][1])
		ic2.write(config[101][0],config[101][1])
		ic2.close() #verbindung schliessen 
	
	
	def ramlokation (self, slaveadress, pin, bank): #zum berechnen der postion im ram jedes einzelen aktoren
		return str(slaveadress) + str(pin) + str(bank)
		
	def integertobyte (self,wert): #den Hex wert aus der bank in einen 8 bit array umschreiben
		array = {}
		count = 128;
		count2 = 8
		while count2 > 0:
			new = wert - count
				
			if new < 0:
				array[int(count)] = 0			
			elif new == 0:
				wert = 0
				array[int(count)] = 1
			else:
				array[int(count)] = 1
				wert = new
			
			count = count / 2
			count2 -= 1
		return(array)		


	def comparison (self,ram):
		
		ic2 = i2c_treiber(ram['adress']) 
		
		for x in ram['bank']:
			
			data = ic2.read(int(x))
			#print(data[0])
			byteinarray = (self.integertobyte(data[0]))
			
			print(data)
			print (byteinarray)
			for y in byteinarray:
				
				if ram['pin'][self.ramlokation(ram['adress'],y,x)]['exist'] == 1:
					#if ram['pin'][self.ramlokation(ram['adress'],y,x)]['value'] != byteinarray[y]:
					print ("tu was")
					returndata = self.function(ram['adress'],ram['pin'][self.ramlokation(ram['adress'],y,x)],byteinarray[y])
					print (returndata)
				else:
					#if ram['pin'][self.ramlokation(ram['adress'],y,x)]['value'] != byteinarray[y]:
					print ("tu was toter pin")
					gg = 0
		
		ic2.close() 
		
		return(ram)
		
		
	def function (self,adress,data,dataic):
		return(data)
