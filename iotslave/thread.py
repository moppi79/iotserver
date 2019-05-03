from multiprocessing import Process, Queue
import os, time, random, datetime, json

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
		

	def run(self,in_data,out_data,config,girdata,logger):
		
		self.ram = {}
		self.ram['config'] = config
		global gir
		Thread_ram = {} 
		
		thread_run = eval(self.ram['config']['name']+'()')
		
		if girdata == '':
			#self.ram['gir'] = {}
			
			gir = {}
			
		else:
			#self.ram['gir'] = gir
		
			gir = girdata
			
		
		time.sleep(1) ###### muss am schluss entfernt werden
		copx = dict_copy()
		while True:
			
			no_direkt_data = 1
			#logger.error('test while in theard')
			#logger.error(json.dumps(self.ram))
			
			returndata = ''
			z = 1
			if in_data.empty() != True:
				
				array = {}
				while in_data.qsize() != 0: #alle verfügabren daten abrufen 
					#logger.error('z!=1')
					data1 = in_data.get()
					array[z] = data1
					z = z + 1
			
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
						returndata = thread_run.work(array[x]['gir'],gir,Thread_ram,logger) #Send Direkt Data to Thread 

						Thread_ram = returndata[1]
						if returndata[0] != '':
			
							for h in returndata[0]:
								#print ('########### return data ############')
								#print (returndata[0][h])
								#print ('########### return data ############')
								out_data.put(returndata[0][h]) #send data to clientserver
										
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
						out_data.put(returndata[0][h]) #send data to clientserver
								
					returndata.clear()


			time.sleep(0.05)  #### should be triggert by thread him self .... must be correctet later

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
			
