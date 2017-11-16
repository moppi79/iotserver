import daemon, os, time, sys, signal, lockfile, daemon.pidfile, socket, logging, datetime, json, random

class mcp23017():	
	def install(self,data):
		return ('lala',data)

'''
class mcp23017():	
	def install(self,data):

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
						
						#hier dann die einzelenen funktionen abrufen
						#muss noch programmiert und getestet werden
					

					print (chip_array)
			
			ic2.close()
'''