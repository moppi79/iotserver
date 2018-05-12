import daemon, os, time, sys, signal, lockfile, daemon.pidfile, socket, socketserver, json, logging, random,datetime, threading
from collections import defaultdict
from multiprocessing import Process, Queue

HOST, PORT = "localhost", 5051 ##adresse und port vom server-server

global logger

logger = logging.getLogger()
logger.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh = logging.FileHandler("/net/html/iotserver/server.log")
fh.setFormatter(formatter)
logger.addHandler(fh)

stopper = 0 

class data_server(): #demo server
	
	def io():
		
		in_data = {}
		
		while True:
			
				
			sleepi = True
			while sleepi:
				time.sleep(0.01)
				if TCP2Server_queue_stack['aktive'].empty() != True:
					print ('aktive verbindung')
					sleepi = False

			io = datahelper()
			in_data = io.transmit('',0)## abfragen ob neue daten anstehen
			ret = ''
			#logging.error('test')
			print (in_data)
			print ('server')
			in_data_copy = in_data.copy()
			
			for x in in_data_copy:
				try:
					umwandel = json.loads(in_data_copy[x])
    		
				except ValueError as err:
					logging.error('JSON fehlerhaft')
					umwandel = {'server_control':'Error data'}
					logging.error('Fehlerhafte JSON data')
					logging.error(err)
				
				if ret == '':
					ret = {}
				print (umwandel)
				if 'server_control' in umwandel: ## abfangen von server deamon befehle 
					print ('close')
					demon_queue_data['close'].put('1')
					ret[x] = json.dumps({'data':'end'})
				else:
					print ('do server stuff !!!')
					try:
						ret[x] = json.dumps({'ret':umwandel['data']+' hier mit verbesserten inhalt'})
						logging.error('thread: {}, data: {}'.format(x,json.dumps(in_data[x])))
					except ValueError as err:
						logging.error('Fehlerhafte JSON data')
						logging.error(err)
						ret[x] = {'error':'Error data'}
					except KeyError as err:
						logging.error('Fehlerhafte JSON data')
						logging.error('thread: {}, data: {}'.format(x,json.dumps(in_data[x])))
						ret[x] = {'error':'Error data'}
				
				del in_data[x]
			
			print (ret)
			if ret != '':
				logging.error('Return data from server: {}'.format(json.dumps(ret)))
				in_data = io.transmit(ret,0)
			
			time.sleep(0.02)
			


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

	def handle(self):
		# self.request is the TCP socket connected to the client
		cur_thread = threading.current_thread()
		loop_count = 0
		anwser = 0 
		exit = 0 
		loop_control = True

        ###########to become a free Data Slot #################
		while loop_control: 
			if TCP2Server_queue_stack['aktive'].empty() == True:
				TCP2Server_queue_stack['aktive'].put('1')
				print ('TCP thread neu gestartet')
				logging.error('thread start: {}'.format(cur_thread.name))
			if anwser == 0:
				loop_count = random.randrange(1,TCP2Server_queue_stack['max_client'])

			if TCP2Server_queue_stack[loop_count]['lock'].empty() == True:
				logging.error('Obtain slot: {}, thread: {}'.format(loop_count,cur_thread.name))
				TCP2Server_queue_stack[loop_count]['lock'].put(cur_thread.name)
				TCP2Server_queue_stack[loop_count]['ready'].put(cur_thread.name)
				print (loop_count)
				print (cur_thread.name)
				own_slot = loop_count
				anwser == 1
				exit = 1

			if exit == 1:
				loop_control = False
				break
        
        ######### Put data in the slot ##############
		data = self.request.recv(10024).strip() #### hier muss ich die bytes noch dynamisch erstellen lassen
		rawdata = data.decode('utf8')
        
		TCP2Server_queue_stack[own_slot]['data'].put(rawdata)
		TCP2Server_queue_stack[own_slot]['ready'].put(own_slot)
        
        #########
		trigger = True
		loop = 0
		while trigger:
			if TCP2Server_queue_stack[own_slot]['ready_return'].empty() != True:
				dataout = TCP2Server_queue_stack[own_slot]['data'].get()
				trigger = False
			else:
				print('not ready')

			time.sleep(0.2)
			loop = loop + 1
			print (loop)
			if loop > 20:
				dataout='Server error'

				logging.error('TCP servre error, thread: {}'.format(cur_thread.name))
				trigger = False
				if TCP2Server_queue_stack[own_slot]['ready'].empty() != True:
					garbage = TCP2Server_queue_stack[own_slot]['ready'].get()
				if TCP2Server_queue_stack[own_slot]['ready_return'].empty() != True:
					garbage = TCP2Server_queue_stack[own_slot]['ready'].get()
				if TCP2Server_queue_stack[own_slot]['data'].empty() != True:
					garbage = TCP2Server_queue_stack[own_slot]['data'].get()
        		
				garbage = TCP2Server_queue_stack[own_slot]['lock'].get()
        
        #call = server()
        #dataout = call.new_data(rawdata)
        #dataout = 'hup'
		ausgabe = dataout.encode('utf8')
		print ('serversend')
		print (own_slot)
		TCP2Server_queue_stack[own_slot]['ready'].put(own_slot)
		self.request.sendall(ausgabe)
		self.request.close()

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class datahelper (): #data transver helper TCP Multiplexer <--> Server Thread
	
	def transmit(self,in_data,typ):
		if typ == 1:
			target, me = 'server', 'client'
		else:
			target, me = 'client', 'server'
		
		loop_control = True
		loopnum = 1
		ret = {}
		one = 0
		two = 0
		count = 1
		while loop_control:
			#print ('one {} : two {}, loopnum:{},typ:{},me:{},target:{} ### datain : {} #####'.format(one,two,loopnum,typ,me,target,in_data))
			if Io_stack[loopnum]['lock'].empty() == True:
				Io_stack[loopnum]['lock'].put('data')
				
				if Io_stack[loopnum]['data_to_'+target+''].empty() != True:
					ret = Io_stack[loopnum]['data_to_'+target+''].get()
					print (ret)
					
				if type (in_data) == dict:
					
					Io_stack[loopnum]['data_to_'+me+''].put(in_data)
					in_data = ''
				
			
				garbage = Io_stack[loopnum]['lock'].get()
				
				
			
			if loopnum == 1:
				one = 1
				loopnum = 2
			else:
				loopnum = 1
				two = 1
			#loop_control = False
			count = count + 1	
			#time.sleep(0.05)
			if count == 10:
				loop_control = False
			
			if one == 1 and two == 1:
				loop_control = False
	
		return (ret)

	


class data_handle_TCP2Server (): ##### TCP Multiplex Service
	
	def start():
		
		loop_count = 0
		TCP_handler_stack = {}
		
		
		while loop_count < TCP2Server_queue_stack['max_client']:
			loop_count = loop_count + 1
			TCP_handler_stack[loop_count] = {}
			TCP_handler_stack[loop_count]['name'] = ''
			TCP_handler_stack[loop_count]['stage'] = 0
			TCP_handler_stack[loop_count]['data'] = ''
			
			
		
		datasend = {}
		stage_one_helper = 0	
		loop_count = 0
		sleep_loop_delay = 0
		while True:
			
			sleepi = True
			while sleepi: ### Sleep loop when non aktive TCP Transmit
				time.sleep(0.01)
				if TCP2Server_queue_stack['aktive'].empty() != True:
					print ('aktive verbindung')
					sleepi = False
					
			sleeper = 0	
			while loop_count < TCP2Server_queue_stack['max_client']: #stageing system 0 to 4
				loop_count = loop_count + 1
				
				
				if TCP_handler_stack[loop_count]['stage'] == 0: ### TCP new Slot #####
					
					
					if TCP2Server_queue_stack[loop_count]['lock'].empty() != True:
						sleeper = 1 #checker for aktive connecktion
						print ('obtain slot')
						
						name = TCP2Server_queue_stack[loop_count]['ready'].get()
						TCP_handler_stack[loop_count]['name'] = name
						TCP_handler_stack[loop_count]['stage'] = 1
						logging.error('multiplex slot: {}, thread: {},stage: {}'.format(loop_count,TCP_handler_stack[loop_count]['name'],TCP_handler_stack[loop_count]['stage']))
				
				elif TCP_handler_stack[loop_count]['stage'] == 1: ### Get Data from TCP stack #####
					sleeper = 1 #checker for aktive connecktion
					
					if TCP2Server_queue_stack[loop_count]['ready'].empty() != True: ## when data has been written
						print('stage Get Data from TCP stack')
						datasend[TCP_handler_stack[loop_count]['name']] = TCP2Server_queue_stack[loop_count]['data'].get()
						carbage = TCP2Server_queue_stack[loop_count]['ready'].get()
						TCP_handler_stack[loop_count]['stage'] = 2
						stage_one_helper = 1
						logging.error('multiplex slot: {}, thread: {},stage: {}'.format(loop_count,TCP_handler_stack[loop_count]['name'],TCP_handler_stack[loop_count]['stage']))
						
				elif TCP_handler_stack[loop_count]['stage'] == 2: #### Return data to TCP stack
					sleeper = 1 #checker for aktive connecktion
					
					if TCP_handler_stack[loop_count]['data'] != '':
						print('stage return to TCP stack')
						print ('datinhalt{}'.format(TCP_handler_stack[loop_count]['data']))
						TCP2Server_queue_stack[loop_count]['data'].put(TCP_handler_stack[loop_count]['data']) ###
						TCP2Server_queue_stack[loop_count]['ready_return'].put('1')
						TCP_handler_stack[loop_count]['stage'] = 3
						logging.error('multiplex slot: {}, thread: {},stage: {}'.format(loop_count,TCP_handler_stack[loop_count]['name'],TCP_handler_stack[loop_count]['stage']))
					
				elif TCP_handler_stack[loop_count]['stage'] == 3: #### freeing space Handle space
					
					sleeper = 1 #checker for aktive connecktion
					if TCP2Server_queue_stack[loop_count]['ready'].empty() != True:
						print (TCP_handler_stack)
						TCP_handler_stack[loop_count]['stage'] = 0
						TCP_handler_stack[loop_count]['name'] = ''
						TCP_handler_stack[loop_count]['data'] = ''
						print (TCP_handler_stack)
						#garbage = TCP2Server_queue_stack[loop_count]['data'].get()
						garbage = TCP2Server_queue_stack[loop_count]['ready'].get()
						garbage = TCP2Server_queue_stack[loop_count]['ready_return'].get()
						garbage = TCP2Server_queue_stack[loop_count]['lock'].get()
						print ('ALL CLEAR')
					
					
				else:
					print('MASSIVE ERROR')
			################ Ende WHILE ####################################					
			
			if stage_one_helper == 1:
				stage_one_helper = 0
			else:
				datasend = ''
				

			
			#print (datasend)
			io = datahelper()
			in_data = io.transmit(datasend,1)## daten an server übermittelen 
			datasend = {}
			print (in_data)
			for x in in_data: 
				#print ('xxxxxx hier ist x = {}'.format(x))
				for y in TCP_handler_stack:
					#print ('xxxxxx hier ist y = {}'.format(y))
					if TCP_handler_stack[y]['name'] == x:
						TCP_handler_stack[y]['data'] = in_data[x]
						logging.error(json.dumps('data from server, Thread: {}, data: {}'.format(x,in_data[x])))
			
			
			print (TCP_handler_stack)
			
			print ('ende ???')
			
			if sleeper == 0: ###sleep delay
				sleep_loop_delay = sleep_loop_delay + 1
			else:
				sleep_loop_delay = 0
				
			if sleep_loop_delay == 5:
				print ('sleper')
				logging.error('multiplex sleep')
				sleep_loop_delay = 0
				garbage = TCP2Server_queue_stack['aktive'].get()
			loop_count = 0
			datasend = {}
			time.sleep(0.03)
			


def Demon_start():
	logging.error(json.dumps('Server Start'))
	while True:

		# Start a thread with the server -- that thread will then start one
		# more thread for each request
		
		global TCP2Server_queue_stack
		global Io_stack
		global demon_queue_data
		
		demon_queue_data = {}
		demon_queue_data['close'] = Queue()
		
		
		TCP2Server_queue_stack = {}
		TCP2Server_queue_stack['max_client'] = 10
		TCP2Server_queue_stack['aktive'] = Queue() ## income TCP aktive
		loop_count = 0
		
		#TCP stack data
		while loop_count < TCP2Server_queue_stack['max_client']: #data stac for TCP Multiplexer
			loop_count = loop_count + 1
			TCP2Server_queue_stack[loop_count] = {}
			TCP2Server_queue_stack[loop_count]['lock'] = Queue() 
			TCP2Server_queue_stack[loop_count]['ready'] = Queue() 
			TCP2Server_queue_stack[loop_count]['ready_return'] = Queue() 
			TCP2Server_queue_stack[loop_count]['data'] = Queue() 

		
		#intern Stack to server data
		Io_stack = {} 
		
		Io_stack[1] = {}
		Io_stack[1]['data_to_server'] = Queue()
		Io_stack[1]['data_to_client'] = Queue()
		Io_stack[1]['lock'] = Queue()
		
		Io_stack[2] = {}
		Io_stack[2]['data_to_client'] = Queue()
		Io_stack[2]['data_to_server'] = Queue()
		Io_stack[2]['lock'] = Queue()
		
		#############
		
		data_server_prozess = Process(target=data_server.io) #Starte Dataserver
		data_server_prozess.start()
		
		tcp2server_prozess = Process(target=data_handle_TCP2Server.start) #Start Data progress for TCP Stack
		tcp2server_prozess.start()
		
		#######################
		server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
		ip, port = server.server_address
		#2 = server.handle_timeout()
		
		server_thread = threading.Thread(target=server.serve_forever) #Start Main TCP servive
		server_thread.daemon = False
		server_thread.start()
		testcount = 0
		
		############  Debugger run #########
		stopper = 0
		while True: #basic run
		
			if data_server_prozess.is_alive() != True:
				print ('server tot')
				logging.error(json.dumps('server tot'))
				stopper = 1
			if tcp2server_prozess.is_alive() != True:
				print ('TCP Multiplexer tot')
				logging.error(json.dumps('TCP Multiplexer tot'))
				stopper = 1
			if server_thread.is_alive() != True:
				print ('TCP Thread tot')
				logging.error(json.dumps('TCP Multiplexer tot'))
				stopper = 1
		
			if demon_queue_data['close'].empty() != True: ### close signal
				time.sleep(1)
				stopper = 1
				
			testcount = testcount + 1 
			print ('haupt prozess {}'.format(testcount))
			#print (server_thread.enumerate())
			time.sleep(1) 
			
			if testcount == 50:
				stopper = 1
			
			
			if stopper == 1:
				break
		############  Debugger run #########		
		
		if stopper == 1:
			
			loop_count = 0
			
			if data_server_prozess.is_alive() == True:
				data_server_prozess.terminate()	
			if tcp2server_prozess.is_alive() == True:
				tcp2server_prozess.terminate()
			if server_thread.is_alive() == True:
				server.shutdown()
				server.server_close()

			while loop_count < TCP2Server_queue_stack['max_client']:
				loop_count = loop_count + 1
				TCP2Server_queue_stack[loop_count]['lock'].close
				TCP2Server_queue_stack[loop_count]['ready'].close
				TCP2Server_queue_stack[loop_count]['ready_return'].close
				TCP2Server_queue_stack[loop_count]['data'].close
			
			Io_stack[1]['data_to_server'].close
			Io_stack[2]['data_to_client'].close
			Io_stack[1]['data_to_server'].close
			Io_stack[2]['data_to_client'].close
			Io_stack[1]['lock'].close
			Io_stack[2]['lock'].close
			
			demon_queue_data['close'].close
			logging.error(json.dumps('Server Shutdown'))
			#print(TCP2Server_queue_stack)
			break


context = daemon.DaemonContext( #daemon konfig
	working_directory='/net/html/iotserver/iotserver',
   	umask=0o002,
   	pidfile=daemon.pidfile.PIDLockFile('/net/html/iotserver/iotserver/testpid'),
   	files_preserve = [
   		fh.stream,
    ],

)

Demon_start()
if len(sys.argv) == 2:
	if 'start' == sys.argv[1]:
		
		loop = 0;
		loopcount = 1;
		# Create the server, binding to localhost on port 9999
		while loop == 0:
			if loopcount > 10:
				loop = 1
			try:
				testverbindung = socketserver.TCPServer((HOST, PORT), ThreadedTCPRequestHandler)
				
			except OSError as err:
				print('port noch in nutzung ***warte***', err)
				time.sleep(1)
				loopcount = loopcount +1
			else:
				loop = 1
		
		try:	
			testverbindung.server_close()
		except AttributeError:
			print('Port ist dauerhaft in nutzung')
		except NameError:
			print('Unbekannter fehler')
		else:	
			print("wird gestartet ...")
			logging.error('server start')
			with context:
				Demon_start()
				
	elif 'stop' == sys.argv[1]:
		def client(ip, port, message):
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
				sock.connect((ip, port))
				sock.sendall(bytes(message, 'utf8'))
				response = str(sock.recv(1024), 'utf8')
				print("Received: {}".format(response))
				sock.close()
		        
		client(HOST, PORT, json.dumps({'server_control':'close','data':'hier client:'}))
		print ('beendet.....')
		logging.error('server stop')
	elif 'restart' == sys.argv[1]:
		print ("lala") ##noch nichts geplant
	elif 'help' == sys.argv[1]:
		print ('start|stop|add|get|end')
	else:
		print ("Unknown command")
		sys.exit(2)
		
else:
   	print ("usage: %s start|stop|restart") 
sys.exit(2)


#####Junk zum testen ######
