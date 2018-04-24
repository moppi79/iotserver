from multiprocessing import Process, Queue
import os, time, random, datetime, json

class dict_copy :

	def copy(self,source,target): #source must a Dictonary, Target dictonary musst be a string 'target' and deklared as global 
		
		loop = {}
		loop[0] = 0
		self.rekursive(source,target,loop)

	def rekursive (self,data,target,loop): #Diktonary inhalt copy from Dict zu dict 

		for k,v in data.items():

			if type (data[k]) == dict:
				loop[0] = loop[0] + 1
				loop[loop[0]] = k
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





class basic:
	
	def install(self,logger): #install im ram 
		logger.debug('install theard')
		ret = {}
		
		ret['name'] = 'basic'
		
		ret['iss'] = {}
		ret['iss'][1] = {}
		ret['iss'][1]['id'] = 'lampe'
		ret['iss'][1]['typ'] = 'on_off'
		ret['iss'][1]['value'] = '0'
		
		return(ret)
		
	def work (self,data_work):
		
		returner = {}
		
		if data_work != '':
			
			
			
			now = datetime.datetime.now()
			ttt = now.second
			if 'time' in self.ram:
				
				if ttt != self.ram['time']:
					self.ram['time'] = ttt
					print (self.ram)
					logger.error('new time {}'.format(ttt))
					#if self.ram['gir']['']
				
			else:
				self.ram['time'] = ttt
			
			'''
			array = {}
			array[1] = {}
			array[1]['data'] = {}
			array[1]['update'] = {}
			
		#ram['gir'][data_work['host']][data_work['zone']][data_work['system']][data_work['id']]['value']
		
			array[1]['update']['new'] = 0
			array[1]['data']['id'] = 'lampe'
			array[1]['data']['value'] = data_work['data']['value']
			'''
		else:
			

			x = 2
			'''
			array = {}
			array[1] = {}
			array[1]['target'] = {}
			array[1]['target']['host'] = 'raspi2' #target host
			array[1]['target']['zone'] = 'balkon' #target zone
			array[1]['target']['system'] = 'plugin' #i2c,SPI,plugin
			array[1]['target']['name'] = 'basic' #ic nr,Plugin name
			array[1]['data'] = {}
			array[1]['data']['id'] = 'lampe'   #spzifig target data 
			
			if self.ram['gir']['raspi2']['balkon']['plugin']['basic']['lampe']['value'] == '1':
				array[1]['data']['value'] = '0'
				print ('hier die 0')
			else:
				array[1]['data']['value'] = '1'
				print ('hier die 1')
			'''
		
		
		'''
		
		target return data
		array = {}
		array[*N] = {}
		array[*N]['target']['host'] #target host
		array[*N]['target']['zone'] #target zone
		array[*N]['target']['system'] #i2c,SPI,plugin
		array[*N]['target']['name'] #ic nr,Plugin name
		array[*N]['data'] #spzifig target data 
		
		or update gir data 
		array[*N]['update']['new'] = 0
		array[*N]['data']['id'] = x
		array[*N]['data']['value'] = x
		
		*N running number or oneway chars
		
		when nothing changed ... return ''
		
		
		'''
		
		return (returner)
		
	
	def run(self,in_data,out_data,config,girdata,logger):
		
		self.ram = {}
		self.ram['config'] = config
		if girdata == '':
			#self.ram['gir'] = {}
			gir = {}
			global gir
		else:
			#self.ram['gir'] = gir
			gir = girdata
			global gir
		
		time.sleep(2)
		copx = dict_copy()
		while True:
			#logger.error('test while in theard')
			logger.error(json.dumps(self.ram))
			print (self.ram)
			returndata = ''
			z = 1
			if in_data.empty() != True:
				
				array = {}
				while in_data.qsize() != 0: #alle verfügabren daten abrufen 
					logger.error('z!=1')
					data1 = in_data.get()
					array[z] = data1
					z = z + 1
			
			if z != 1:
				logger.error('z!=1')
				for x in array:
					logger.error('for schleife')
					logger.error(json.dumps(array[x]))
					if 'gir' in array[x]:
						print ('############################################################')
						print (array[x])
						copx.copy(array[x]['gir'],'gir')
						print (gir)
						print ('############################################################')
						
						
						
					else:
						
						returndata = self.work(array[x]['gir']) #iss data komplete
				
				del array	
			else:
				returndata = self.work('')
			
			if returndata != '':

				for h in returndata:
					print (returndata[h])
					out_data.put(returndata[h]) #send data to clientserver
							
				returndata.clear()
			

			
			time.sleep(1.5)
			
	
	
	
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
			

'''			
			if random.randrange(0,5) == 4:
				
				dataout = {}
				dataout['sender'] = {}
				dataout['sender']['system'] = 'plugin'
				dataout['sender']['name'] = ram['config']['name']
				dataout['sender']['host'] = ram['config']['host']
				dataout['sender']['zone'] = ram['config']['zone']
				dataout['data'] = {}
				dataout['data']['name'] = 'hubbabubba'
				
				
				out_data.put(dataout)
				
'''