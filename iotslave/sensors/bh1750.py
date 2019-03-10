import os, time, sys, signal

from module.i2c_driver import i2c_treiber

class bh1750():
	
	def install (self,data):
		ret = {}
		ret['Light'] = {}
		ret['Light']['value'] = '0'
		ret['Light']['unit'] = "Lux"
		
		return (ret)
		
	
	def out(self,config):
		print (config)
		i2c = i2c_treiber(config['adresse'])
		i2c.write('zero',0x01) #sensor wacke up
		data = i2c.write('zero',0x21) #sensor start
		time.sleep(0.20) # sensor colecting
		data = i2c.read(0x21) #sensor read out
		
		i2c.write('zero',0x00) #sensor sleep
		i2c.close() 
		light2 = round(((data[1] + (data[0]*256)) / 1.2),2) #Manufacturer best pratice math
		ret = {'Light':light2}
		
		#ret = {'temperature':'22:5', 'humidity':'56,4'}
		return(ret)
		
		



#test = bh1750()
#print (test.out(0x23,0))