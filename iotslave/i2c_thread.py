import daemon, os, time, sys, signal, lockfile, socket, logging, datetime, json, random, configparser, fileinput
from multiprocessing import Process, Queue
from time_managent import time_managent

ic_class = {}

iss = {}

glo_ram = {}

glo_ram['Massage_counter'] = 0

ic_chip = {}

sensordic = {}

sensor_ram = {}

sensor_conf = {}

sensor_class = {}

sensor_data_standart = {}

Sensor_timer = {}

class i2c_abruf:
	
	def sensor_install(self,ic):
		
		#print('aaaaa')
		#print(ic)
		#print('aaaaa')
		sensor_class ={}
		
		#print ('from sensors.'+ic['sensor_class']+' import '+ic['sensor_class']+'') 
		#print ("sensor_class['"+ic['sensor_class']+"'] = "+ic['sensor_class']+"()")
		
		exec('from sensors.'+ic['sensor_class']+' import '+ic['sensor_class']+'') 
		exec("sensor_class['"+ic['sensor_class']+"'] = "+ic['sensor_class']+"()")
		
		data = sensor_class[ic['sensor_class']].install(ic)
		ret = {}
		ret[1] = {}
		ret[2] = {}
		for x in data:
			#print ('aaabbbb')
			#print (data[x])
			ret[1][x] = {} 
			ret[1][x] = data[x]
			
			new_iss_number = skirmish(30)
			ret[2][new_iss_number] = {}
			ret[2][new_iss_number]['data'] = {}
			ret[2][new_iss_number]['data'] = {}
			ret[2][new_iss_number]['data']['id'] = x
			ret[2][new_iss_number]['data']['value'] = data[x]['value']
			ret[2][new_iss_number]['data']['unit'] = data[x]['unit']
			ret[2][new_iss_number]['data']['usable'] = '0'
			ret[2][new_iss_number]['update'] = {}
			ret[2][new_iss_number]['update']['new'] = 1
			
		return (ret)
	
	def install(self,ic):
		ret = {}
		#for x in ic: #Dynamik Load classes
		exec('from module.'+ic['ic_class']+' import '+ic['ic_class']+'') 
		exec("ic_class['"+ic['ic_class']+"'] = "+ic['ic_class']+"()")
			
		#for x in ic: ##Declare all ic Dic (drivers own ram)

		
		#for x in ic:
		classcall = ic_class[ic['ic_class']]
			
		ret['ram'] = {}
		data_install = classcall.install(ic)
		ret['ram'] = data_install[0]
		#iot_ram['data']['i2c_'+str(x)] = ram[ic_chip[x]['icname']][x]['iot']
		
		#for y in ram[ic_chip[x]['icname']][x]['iss']: #create ISS update for gir 
		for y in data_install[1]: #create ISS update for gir 
			
			new_iss_number = skirmish(30)
			
			ret[new_iss_number] = {}
			ret[new_iss_number]['update'] = {}
			
			ret[new_iss_number]['update']['new'] = 1
			ret[new_iss_number]['data'] = {}
			ret[new_iss_number]['data'] = data_install[1][y]
			ret[new_iss_number]['data']['new'] = 1
			ret[new_iss_number]['counter'] = glo_ram['Massage_counter'] 
			
		
		return(ret)

				
				
	def icinit(self):
		for x in ic_chip: ##Declare all ic Dic
			ram[ic_chip[x]['icname']] = {}

		for x in ic_chip:
			classcall = ic_class[ic_chip[x]['ic_class']]
				
			ram[ic_chip[x]['icname']][x] = {}
			ram[ic_chip[x]['icname']][x].update(classcall.install(ic_chip[x]))
	
	def comparison(self,ram,data,logger):
		ret= {}
		ram[1]=2

		classcall = ic_class[ram['class']]
		
		data_return = classcall.comparison(ram['ram'],data,logger)
		glo_ram[ram['ic_name']]['ram'] = data_return[0]

		for y in data_return[1]:
			
			new_iss_number = skirmish(30)
			ret[new_iss_number] = {}
			ret[new_iss_number]['sender'] = {}
			ret[new_iss_number]['update'] = {}
			#ret[new_iss_number]['sender']['name'] = {}
			ret[new_iss_number]['sender']['name'] = ram['ic_name']
			
			ret[new_iss_number]['data'] = {}
			ret[new_iss_number]['data'] = data_return[1][y]
			ret[new_iss_number]['update']['new'] = 0
			
			ret[new_iss_number]['counter'] = glo_ram['Massage_counter'] 
			glo_ram['Massage_counter'] = glo_ram['Massage_counter'] + 1
			#logging.error(json.dumps(iss[new_iss_number]))
		#return sollte dann 1:1 in den jeweiligen RAM 
		#zurückspielbar sein 
		
		return(ret)
		
		'''
		iot Return in den stack 
		
		'''
		
	def sensor (self,sensor_conf,sensor_ram,iss_data,logger):

		data = {}
		
		#return({1:2})
		ret = {}
		for x in sensor_ram:
			#print ('senor def')
			#print (x)
			#print (sensor_ram)
			
			data[x] = sensor_class[sensor_ram[x]['sensor_class']].out(sensor_ram[x]['data'])
			#data_insert = {}
			#data_insert = iss_data[x]
			for z in data[x]:

				new_iss_number = skirmish(30)
				ret[new_iss_number] = {}
				ret[new_iss_number]['sender'] = {}
				ret[new_iss_number]['update'] = {}
				#ret[new_iss_number]['sender']['name'] = {}
				ret[new_iss_number]['sender']['name'] = 'sensor'
				
				ret[new_iss_number]['data'] = {}
				ret[new_iss_number]['data']['value'] = data[x][z]
				ret[new_iss_number]['data']['id'] = z
				ret[new_iss_number]['update']['new'] = 0
				
				ret[new_iss_number]['counter'] = glo_ram['Massage_counter'] 
				glo_ram['Massage_counter'] = glo_ram['Massage_counter'] + 1
			
				
		
				
		#print ('aussgabe')
		#print (ret)
		return (ret)
	
	def sensor_timer (self,x): # gibt false/True aus ob der counter abgelaufen ist  
		
		timer = datetime.datetime.now()
		#print('asdasdsadasd')
		#print (x) 
		if Sensor_timer == {}:
			Sensor_timer['count'] = 0
			Sensor_timer['last_time'] = timer.second
		
		if  Sensor_timer['last_time'] != timer.second:
			Sensor_timer['last_time'] = timer.second
			Sensor_timer['count'] = Sensor_timer['count'] + 1
			
		if Sensor_timer['count'] == x: 
			Sensor_timer['count'] = 0
			ret = True
			#print ('true')
		else:
			#print ('false')
			ret = False
		
		return (ret)
		
	def switch(self): ##switch schalten
		
		switch = i2c_treiber(i2cswitch['adress']) 
		zustand = switch.readswitch()
		
		if zustand[1] == 99: #wenn switch nicht mehr erreichbar ist, programm termination
			logging.error('Switch nicht erreichbar')
			
		
		if zustand[1] != i2cswitch['port']: #hier muss drin ste
			switch.write(0x00,i2cswitch['port'])
		switch.close()
		
			
def skirmish(length): #zufallsgenerator
	ausgabe = ''
	for x in range(0,length):
		##print (x)
		zufall = random.randrange(1,4)
	
		if (zufall == 1):
			ausgabe = ausgabe + str(random.randrange(0,10))
		if (zufall == 2):
			ausgabe = ausgabe + chr(random.randrange(65,91))
		if (zufall == 3):
			ausgabe = ausgabe + chr(random.randrange(97,123))
	return(ausgabe)			
			
class thread_i2c: #Thread 
	
	def run(system,chips,data_in,data_out,logger):
		
		count = 1
		#print (chips)
		sensor_install = 0
		if 'sensor' in chips: ##sorting sensor data aus chips raus
			sensor_install = 1
			#print('SENSORCONF')
			#print (chips['sensor'])
			sensor_ram = chips['sensor'] 
			sensor_conf = chips['sensor_update'] #alle ladbaren module und zeit 
			sensor_data_standart = chips['data_standart'] #ISS data{} inhalte
			#print (chips['sensor_update'])
			del chips['sensor_update']
			del chips['data_standart']
			del chips['sensor']
			
			#print ('######################aaaaaaaaaaaaaaaaaa############')
			#print (sensor_conf)

			for x in sensor_conf:
				if x != 'update':
					#print('#####update####')
					#print (x)
					exec('from sensors.'+x+' import '+x+'') 
					exec("sensor_class['"+x+"'] = "+x+"()")
					
			
		
		#print (sensor_ram)
		for x in chips: #intialisre Thread
			exec('from module.'+chips[x]['ic_class']+' import '+chips[x]['ic_class']+'') 
			exec("ic_class['"+chips[x]['ic_class']+"'] = "+chips[x]['ic_class']+"()")
			glo_ram[x] = {}
			glo_ram[x]['ram']  = chips[x]['ram']
			glo_ram[x]['class']  = chips[x]['ic_class']
			glo_ram[x]['ic_name']  = chips[x]['icname']
			glo_ram[x]['sensor_update']  = 2
			glo_ram[x]['sensor_update_time']  = 0
		call = i2c_abruf()
		
		chipname_list = {}
		for x in chips:
			
			chipname_list[x] = {}
			
		##time management
		a = time_managent()
		counter_time = 0 #countes aktitäten
		time_vars = {}
		time_vars['ts'] = ''
		time_vars['freq'] = 6
		time_vars['wake'] = 1
		time_vars['e-save'] = 0
		
		time_vars_copy = time_vars.copy()
		thread_name = 'i2c'
		data_out.put({'global':'wake','value':'1','name':thread_name})#set your name 
		##time management

		while True: #Haupt schleife
			
			
			#wenn zeit abgelaufen ist, werden daten von den sensoren geholte und in den bus versand
			if sensor_install == 1:
				if call.sensor_timer(int(sensor_conf['update'])) == True:
					data = call.sensor(sensor_conf,sensor_ram,sensor_data_standart,logger)
					data_out.put(data)

			#print ('loop thread i2c '+str(count))
			count = count + 1
			
			################### ISS Abfrage Vom Haupt Prozess ANFANG #####################

			glo_ram['loop'] = chipname_list
			#new_data = ''
			new_data = {}
			while data_in.qsize() != 0: #new data from Server/plugin
				data1 = data_in.get()
				if 'global' in data1:#host in data
					#print(data1)
					#print ('#############data in i2c ############')
					#print(data1)
					time_vars[data1['global']] = data1['value']
						
						
					##time management
				else:#standart ISS
				
					vardd = skirmish(10)
					new_data[vardd] = {}
					new_data[vardd] = data1
			
			new_var = ''
			if new_data != {}: #send data to Hardware
				shadow_copy = new_data.copy()
				for x in shadow_copy:
					counter_time += 1 #time counter
					new_var = call.comparison(glo_ram[new_data[x]['target']['name']],new_data[x],logger)
					data_out.put(new_var)
					if new_data[x]['target']['name'] in glo_ram['loop']:
						del glo_ram['loop'][new_data[x]['target']['name']]
					#print('old delte')
					
			for x in glo_ram['loop']: #call Hardware to checkup
				new_var = call.comparison(glo_ram[x],'',logger)
				if new_var != {}:
					counter_time += 1 # counter aktivität
					data_out.put(new_var)
			################### ISS Abfrage Vom Haupt Prozess ENDE #####################
			##print (new_var)
			#print(data_in.get())
			
			
			######## System Timer  ENDE #######	
			####!!!!!!!!!!!!!!
			# immer durch rechenen ob der E mode deakjtivert werdenb muss 
			# dann schickt er message an host das er alle auf wecken muss 
			# selbst kann er das E auf heben für ein ppaar durch gänge und dann wieder E
			#####!!!!!!!!!!!!!!
			if counter_time >=2 :#wake up
				if time_vars['wake'] != 1:
					time_vars['wake'] = 1
					data_out.put({'global':'wake','value':1,'name':thread_name})
					a.set_e_save(0)
				counter_time -= 1
			else:
				if time_vars['wake'] == 1:#Sleep now
					time_vars['wake'] = 0
					data_out.put({'global':'wake','value':0,'name':thread_name})
					if time_vars['e-save'] == 1:
						a.set_e_save(1)
			
			counter_time -= 1
			if time_vars['ts'] == '':
				data_out.put({'global':'data','value':'need','name':thread_name})
			
			if time_vars['freq'] != time_vars_copy['freq']:
				a.set_freq(time_vars['freq'])
				time_vars_copy['freq'] = time_vars['freq']
				data_out.put({'global':'freq','value':time_vars['freq'],'name':thread_name})
			
			if time_vars['e-save'] != time_vars_copy['e-save']:
				#self.engerie_saveprint('ESAVE VARIABLE: {}'.format(time_vars['e-save']))
				a.set_e_save(time_vars['e-save'])
				time_vars_copy['e-save'] = time_vars['e-save']
				data_out.put({'global':'e-save','value':time_vars['e-save'],'name':thread_name})
			
			
			error = a.pause()
			
			if 'timeslot' in error:
				print('aaaaaa')
				a.set_freq(time_vars['freq'])
				a.add_timeslot(time_vars['ts'])
			
			if counter_time > 0 :
				counter_time = 0
				
			######## System Timer  ENDE #######	
			
			#time.sleep(1.1)
			
			#if count == 100:
			#	break
			
	