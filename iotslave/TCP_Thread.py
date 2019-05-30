import daemon, os, time, sys, signal, lockfile, socket, logging, datetime, json, random, configparser, fileinput

from time_managent import time_managent
class server_coneckt:
	
	def __init__(self,host,port,logger):
		self.host = host
		self.port = port
		self.logger = logger
	
	def server_install(self,para):
		transfer = {}
		transfer = {'funktion':'add'} #auszuführende Funktion im server
		transfer.update(para) #funktions infos client
		ret = self.sock2(transfer)
		#print (ret)
		self.logger.error(json.dumps(ret))
		if 'sesession_id' in ret:
			
			return (ret['sesession_id'])
		else:
			self.logger.error('Fehler bei install daten in Master Server')	

	def sock2(self,data):#befehl an Server senden und Rückanwort empfangen
		
		if 'funktion' in data:
			json_string = json.dumps(data)
			print (json_string)
			if data['funktion'] != 'check':
				self.logger.error('send data to server: {}'.format(json_string))
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
				sock.connect((self.host,self.port))
				#### SEND DATA #####
				length = len(json_string)
				sock.sendall(bytes(str(length), 'utf8'))
				response = str(sock.recv(30), 'utf8')
				sock.sendall(bytes(json_string, 'utf8'))
				#### SEND DATA #####
				###Bekome data #####
				count = str(sock.recv(30).strip(), 'utf8')
				#print("Received count: {}".format(count))
				sock.sendall(bytes('ok', 'utf8'))
        
				datain = str(sock.recv(int(count)).strip(), 'utf8')
				#print("Received inhalt: {}".format(datain))
				###Bekome data #####
				sock.close()
			
			try:
				returner = json.loads(datain)
			except ValueError as error:
				self.logger.error('Fehlerhafte daten bekommen',datain)
			
			if returner != 'ok':
				self.logger.error('data from server: {}'.format(json.dumps(returner)))	
			return returner #return daten
		else:
			self.logger.error('keine funktion übermittelt')
			return 'error'


def ms_time_tcp(select): #return 0 ms 1 Second 2 array with both
	now = datetime.datetime.now()
	if select == 0:
		return (now.microsecond)
	elif select == 1:
		return (now.second)
	elif select == 2:
		return (now.minute)
	elif select == 3:
		return (now.hour)
	else:
		return ({0:now.microsecond,1:now.second})	


class TCP_run:
	
	def start(host,port,para,logger):
		tcp = server_coneckt(host,port,logger)
		
		TCP_data = tcp.server_install(para)
		#TCP_data = 'demo'
		print ("start TCP server")
		return(TCP_data) 
	

		
	
		
	def run(self,host,port,sess_id,data_out,data_in,logger):
		
		tcp = server_coneckt(host,port,logger)
		time_sec = 0 # sekündlicher update zum server
		#ram={} ##time mangemant
		##time management
		a = time_managent()
		counter_time = 0 #countes aktitäten
		time_vars = {}
		time_vars['ts'] = ''
		time_vars['freq'] = 6
		time_vars['wake'] = 1
		time_vars['e-save'] = 0
		
		time_vars_copy = time_vars.copy()
		thread_name = 'TCP_thread'
		data_out.put({'global':'wake','value':'1','name':thread_name})#set your name 
		##time management
		while True:
			print('hier Thread')
			#print ("server run")
			z = 0
			if data_in.empty() != True:
				
				array = {}
				while data_in.qsize() != 0: #alle verfügabren daten abrufen 
					data1 = data_in.get()
					##time management
					if 'global' in data1:#host in data
						#print(data1)
						print ('#############data in############')
						time_vars[data1['global']] = data1['value']
						
						
					##time management
					else:#standart ISS
						counter_time += 1 # counter aktivität
						z = z + 1
						array[z] = data1
					
			iss = {}		
			if z != 0:
				#print(array)
				#print('data in')
				hashes = tcp.sock2({'funktion':'iot','iotfunk':'new_slot','count':z})
				submit= {}
				for x in array:
					#print (hashes)
					submit[hashes[str(x)]] = array[x]
					counter_time += 1 # counter aktivität
					
				print('with data sock')
				#print (submit)
				iss = tcp.sock2({'funktion':'iot','iotfunk':'iss','messages':submit,'token':sess_id})
				#print ('###########')
				#print (sess_id)
				##print (iss)
				#print ('###########')
			else:
				print('else sock')
				#now = datetime.datetime.now()
				#print (now.microsecond)
				#print (ms_time_tcp(1))
				if ms_time_tcp(1) != time_sec : #Sekündliche abfrage vom server
					time_sec = ms_time_tcp(1)
					iss = tcp.sock2({'funktion':'iot','iotfunk':'iss','messages':'','token':sess_id})
				#print (iss)
				#now = datetime.datetime.now()
				#print (now.microsecond)
			#host,port,
			
			if iss != {}:
				#print ('lalala')
				for x in iss:
					counter_time += 1 # counter aktivität
					#print ('mumumu')
					#print(x)
					data_out.put(iss[x])
			
			
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
			#time.sleep(0.5)
			
			#break