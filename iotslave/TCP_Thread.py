import daemon, os, time, sys, signal, lockfile, socket, logging, datetime, json, random, configparser, fileinput


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



class TCP_run:
	
	def start(host,port,para,logger):
		tcp = server_coneckt(host,port,logger)
		
		TCP_data = tcp.server_install(para)
		#TCP_data = 'demo'
		print ("start TCP server")
		return(TCP_data) 
		
	
	
		
	def run(self,host,port,sess_id,data_out,data_in,logger):
		
		tcp = server_coneckt(host,port,logger)

		while True:
			
			print ("server run")
			z = 0
			if data_in.empty() != True:
				
				array = {}
				while data_in.qsize() != 0: #alle verfügabren daten abrufen 
					z = z + 1
					#logger.error('z!=1')
					data1 = data_in.get()
					array[z] = data1
			iss = {}		
			if z != 0:
				print(array)
				print('data in')
				hashes = tcp.sock2({'funktion':'iot','iotfunk':'new_slot','count':z})
				submit= {}
				for x in array:
					print (hashes)
					submit[hashes[str(x)]] = array[x]
				
				print (submit)
				iss = tcp.sock2({'funktion':'iot','iotfunk':'iss','messages':submit,'token':sess_id})
				print ('###########')
				print (sess_id)
				print (iss)
				print ('###########')
			else:
				
				now = datetime.datetime.now()
				print (now.microsecond)
				iss = tcp.sock2({'funktion':'iot','iotfunk':'iss','messages':'','token':sess_id})
				print (iss)
				now = datetime.datetime.now()
				print (now.microsecond)
			#host,port,
			
			if iss != {}:
				print ('lalala')
				for x in iss:
					print ('mumumu')
					print(x)
					data_out.put(iss[x])
			
			time.sleep(0.5)
			
			#break