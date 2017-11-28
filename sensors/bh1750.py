import os, time, sys, signal

from module.i2c_driver import i2c_treiber

class bh1750():
	
	def out(self,adresse,speicher):
		
		i2c = i2c_treiber(adresse)
		i2c.write('zero',0x01) #sensor wacke up
		data = i2c.write('zero',0x21) #sensor start
		time.sleep(0.20) # sensor colecting
		data = i2c.read(0x21) #sensor read out
		
		i2c.write('zero',0x00) #sensor sleep
		i2c.close() 
		light2 = round(((data[1] + (data[0]*256)) / 1.2),2) #Manufacturer best pratice math
		ret = {'Licht':light2}
		return(ret)
		
		



#test = bh1750()
#print (test.out(0x23,0))