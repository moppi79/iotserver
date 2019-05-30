from multiprocessing import Process, Queue
import os, time, random, datetime, json

from time_managent import time_managent

#import all data from plugin Dictonary
for a in os.listdir("plugin"):
	if a != '__pycache__':
		
		exec('from plugin.'+a.replace('.py','')+' import *') 

class dict_copy :

	def copy(self,source,target): #source must a Dictonary, Target dictonary musst be a string 'target' and deklared as global 
		
		loop = {}
		loop[0] = 0
		self.rekursive(source,target,loop)

	def rekursive (self,data,target,loop): #Diktonary inhalt copy from Dict zu dict 

		for k,v in data.items():

			if type (data[k]) == dict:
				loop[0] = loop[0] + 1
				loop[loop[0]] = str(k)
				self.create(loop,target,'')
				self.rekursive(data[k],target,loop)
			else:
				self.create(loop,target,{1:k,2:v}) #übertragen daten create
	
	def create (self,loop,target,value): #create dict strukture in the new Target
		counter = 0
		dicker = target+''
		dicker2 = ''
		while loop[0] > counter: #erzeuge pfad (needs eval)
			dicker+=dicker2
			counter = counter + 1
			dicker2 = '[\''+str(loop[counter])+'\']'

		vorstufe_dicker = dicker
		dicker+=dicker2

		if value == '': #erzeugen lehres Dictonary

			if loop[counter] not in eval(vorstufe_dicker) :
				exec (dicker+' = {}')

		else:#insert values in Dictonary
			 
			exec (dicker+'[\''+str(value[1])+'\'] = \''+str(value[2])+'\'')



class thread_class:
	
	def install_thread_data(self,target,logger): #install im ram 
		#exec('from plugin.'+target+' import basic2 as test') 
		#logger.debug('install theard')
		thread_install = eval(target+'()')
		ret = {}
		ret = thread_install.install(logger)
		'''
		ret['name'] = 'basic'
		
		ret['iss'] = {}
		ret['iss'][1] = {}
		ret['iss'][1]['id'] = 'lampe'
		ret['iss'][1]['typ'] = 'on_off'
		ret['iss'][1]['value'] = '0'
		'''
		
		return(ret)
		

	def run(self,data_in,data_out,config,girdata,logger,name):
		
		self.ram = {}
		self.ram['config'] = config
		global gir
		Thread_ram = {} 
		print('hier config')
		print(config)
		thread_run = eval(self.ram['config']['name']+'()')
		
		if girdata == '':
			#self.ram['gir'] = {}
			
			gir = {}
			
		else:
			#self.ram['gir'] = gir
		
			gir = girdata
			
		
		time.sleep(1) ###### muss am schluss entfernt werden
		copx = dict_copy()
		
		##time management
		a = time_managent()
		counter_time = 0 #countes aktitäten
		time_vars = {}
		time_vars['ts'] = ''
		time_vars['freq'] = 6
		time_vars['wake'] = 1
		time_vars['e-save'] = 0
		
		time_vars_copy = time_vars.copy()
		thread_name = name
		data_out.put({'global':'wake','value':'1','name':thread_name})#set your name 
		##time management
		
		
		while True:
			
			no_direkt_data = 1
			#logger.error('test while in theard')
			#logger.error(json.dumps(self.ram))
			
			returndata = ''
			z = 1
			if data_in.empty() != True:
				
				array = {}
				while data_in.qsize() != 0: #alle verfügabren daten abrufen 
					data1 = data_in.get()
					##time management
					if 'global' in data1:#host in data
						#print(data1)
						#print ('#############data in############')
						#print (data1)
						time_vars[data1['global']] = data1['value']
						
						
					##time management
					else:#standart ISS
						counter_time += 1 # counter aktivität
						z = z + 1
						array[z] = data1
			
			if z != 1:
				#logger.error('z!=1')
				for x in array:
					#logger.error('for schleife')
					#logger.error(json.dumps(array[x]))
					if 'gir' in array[x]:
						#print ('new data in')
						#print (array[x])
						#print ('new data in')
						copx.copy(array[x]['gir'],'gir') #put data in Thread GIR 
						#print ('innter GiR')
						#print (gir)
						#print ('innter GiR')
					else:
						print ('############### with data #############')
						no_direkt_data = 0
						counter_time += 1 #time counter
						returndata = thread_run.work(array[x]['gir'],gir,Thread_ram,logger) #Send Direkt Data to Thread 

						Thread_ram = returndata[1]
						if returndata[0] != '':
			
							for h in returndata[0]:
								#print ('########### return data ############')
								#print (returndata[0][h])
								#print ('########### return data ############')
								data_out.put(returndata[0][h]) #send data to clientserver
										
							returndata.clear()
						
				
				
				del array # Delete data. last entry from if z != 1:
				
			if no_direkt_data == 1 and gir != {}: #is aktive when not data submited
				#print ('############### no data #############'+self.ram['config']['name'])
				#print (gir)
				#print (Thread_ram)
				#print ('############### no data #############')
				returndata = thread_run.work('',gir,Thread_ram,logger)
				#print (returndata)
				Thread_ram = returndata[1]
				if returndata[0] != '':
					
					for h in returndata[0]:
						#print (returndata)
						counter_time += 1 # counter aktivität
						data_out.put(returndata[0][h]) #send data to clientserver
								
					returndata.clear()

			
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
				a.set_freq(time_vars['freq'])
				a.add_timeslot(time_vars['ts'])
			
			if counter_time > 0 :
				counter_time = 0
				
			######## System Timer  ENDE #######	
			#time.sleep(0.05)  #### should be triggert by thread him self .... must be correctet later

	def time (self,data):
		if data == 'get':
			
			now = datetime.datetime.now()
			
			return (str(now.day)+':'+str(now.hour)+':'+str(now.minute)+':'+str(now.second))
		
		else:
			now = datetime.datetime.now()
			
			d,h,m,s = data.split(':')
			
			nowstamp = ((now.day*86400)+(now.hour*3600)+(now.minute*60)+(now.second))
			
			laststamp = ((int(d)*86400)+(int(h)*3600)+(int(m)*60)+(int(s)))
	
			return (nowstamp - laststamp)
			
