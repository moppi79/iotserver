import os, time, sys, signal, io, fcntl, sys, array

from module.i2c_driver import i2c_treiber

class htu21d():
	
	def owncall(self,i2adress): #manuelles i²c 
		bus = int(1) #bus selekt
		I2C_SLAVE=0x0703 #addresse vom I²C controller
		path = "/dev/i2c-%d" % (bus,) #pfad vom controller
		fd = io.open(path, "rb", buffering=0) #verbindung erstellen 
		fcntl.ioctl(fd, I2C_SLAVE, 0x40) #anzusprechender I²C baustein
		dataowncall = fd.read(3) #daten aus baustein abrufen
	
		return array.array('B', dataowncall) #3 byte in arry zurück geben
	
	def out(self,adresse,speicher):
		
		i2c = i2c_treiber(adresse)
		
		i2c.write('zero',0xE3) #messung starten
		i2c.close() 
		time.sleep(0.2) #chip zum messen zeit lassen
		
		temp = self.owncall(0x40)
		
		i2c = i2c_treiber(adresse)
		i2c.write('zero',0xE5) #messung starten
		i2c.close() 
		time.sleep(0.2) #chip zum messen zeit lassen
		
		hum = self.owncall(0x40)
		temp2 = float((temp[0] * 256) - temp[1])
		
		temp_return = str(round((-46.85 + (175.72 * (temp2 / 65536.0))),2)) 
		
		hum2 = float((hum[0] * 256) - hum[1])#daten in 16bit umwandeln

		hum_return = str(round((-6.0 + (125.0 * (hum2 / 65536.0))),2))#ausgabe umrechnen
		
		
		#light2 = round(((data[1] + (data[0]*256)) / 1.2),2) #Manufacturer best pratice math
		ret = {'temp':temp_return,'hum':hum_return}
		return(ret)
		
		



#test = htu21d()
#print (test.out(0x40,0))