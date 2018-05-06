import daemon, os, time, sys, signal, lockfile, daemon.pidfile, socket, socketserver, json, logging, random,datetime, threading
from collections import defaultdict
from multiprocessing import Process, Queue

HOST, PORT = "localhost", 5051 ##adresse und port vom server-server

logger = logging.getLogger()
logger.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh = logging.FileHandler("/net/html/iotserver/server.log")
fh.setFormatter(formatter)
logger.addHandler(fh)

stopper = 0 

class data_server(): #demo server
	
	def io(self):
		
		
		while True:
			
			
			
			time.sleep(0.2)
			


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        # self.request is the TCP socket connected to the client
        cur_thread = threading.current_thread()
        loop_count = 0
        anwser = 0 
        exit = 0 
        loop_control = True
        
        print ('TCP thread')
        while loop_control:
        	print ('hier')
        	if anwser == 0:
        		loop_count = loop_count+ 1
        	
        	if TCP2Server_queue_stack[loop_count]['lock'].empty() == True:
        		TCP2Server_queue_stack[loop_count]['lock'].put(cur_thread.name)
        		TCP2Server_queue_stack[loop_count]['ready'].put(cur_thread.name)
        		print (loop_count)
        		print (cur_thread.name)
        		
        		anwser == 1
        		exit = 1
        	else:
        		print ('TCP thread full')

        	if exit == 1:
        		loop_control = False
        		break
        	
        
        data = self.request.recv(10024).strip()
        rawdata = data.decode('utf-8')
        
        #call = server()
        #dataout = call.new_data(rawdata)
        dataout = 'hup'
        ausgabe = dataout.encode('utf8')
        self.request.sendall(ausgabe)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class data_handle_TCP2Server ():
	
	def start():
		
		loop_count = 0
		TCP_handler_stack = {}
		
		
		while loop_count < TCP2Server_queue_stack['max_client']:
			TCP_handler_stack[loop_count] = {}
			TCP_handler_stack[loop_count]['name'] = ''
			TCP_handler_stack[loop_count]['stage'] = 0
			TCP_handler_stack[loop_count]['data'] = ''
			loop_count = loop_count + 1
		loop_count = 0
		while True:
			print ('server_data_handle')
			print ('##########')
			print (loop_count)
			print (TCP2Server_queue_stack['max_client'])
			print ('##########')
			while loop_count < TCP2Server_queue_stack['max_client']:
				loop_count = loop_count + 1
				print ('while')
				
				if TCP_handler_stack[loop_count]['stage'] == 0:
					
					if TCP2Server_queue_stack[loop_count]['lock'].empty() != True:
						aaa = TCP2Server_queue_stack[loop_count]['ready'].get()
						print (aaa)
						TCP_handler_stack[loop_count] = 1
				
				elif TCP_handler_stack[loop_count]['stage'] == 1:
					print('stage')
				elif TCP_handler_stack[loop_count]['stage'] == 2:
					print('stage')
				elif TCP_handler_stack[loop_count]['stage'] == 3:
					print('stage')
				elif TCP_handler_stack[loop_count]['stage'] == 4:
					print('stage')
				
				print (loop_count)
			
			print ('ende ???')
			loop_count = 0
			time.sleep(1)
			print ('ende !!!???')


def do_something():
	while True:
		print (PORT)
		server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
		ip, port = server.server_address
		# Start a thread with the server -- that thread will then start one
		# more thread for each request
		
		global TCP2Server_queue_stack
		TCP2Server_queue_stack = {}
		TCP2Server_queue_stack['max_client'] = 10
		TCP2Server_queue_stack['home'] = {}
		loop_count = 0
		
		while loop_count < TCP2Server_queue_stack['max_client']:
			loop_count = loop_count + 1
			TCP2Server_queue_stack[loop_count] = {}
			TCP2Server_queue_stack[loop_count]['lock'] = Queue() 
			TCP2Server_queue_stack[loop_count]['ready'] = Queue() 
			TCP2Server_queue_stack[loop_count]['in'] = Queue() 
			TCP2Server_queue_stack[loop_count]['out'] = Queue() 
			print (loop_count)
		
		
		#############
		
		data_server_prozess = Process(target=data_serve.io) #Starte Dataserver
		data_server_prozess.start()
		
		tcp2server_prozess = Process(target=data_handle_TCP2Server.start) #Start Data progress for TCP Stack
		tcp2server_prozess.start()
		
		#######################
		
		server_thread = threading.Thread(target=server.serve_forever) #Start Main TCP servive
		server_thread.daemon = False
		server_thread.start()
		testcount = 0

		while True: #basic run 
			testcount = testcount + 1 
			print ('hier haupt prozess')
			#print (server_thread.enumerate())
			time.sleep(1) 
			if testcount == 20:
				stopper = 1
				break
				
		
		if stopper == 1:
			
			tcp2server_prozess.terminate()
			
			loop_count = 0
			
			server.shutdown()
			server.server_close()
		
			while loop_count < TCP2Server_queue_stack['max_client']:
				loop_count = loop_count + 1
				TCP2Server_queue_stack[loop_count]['lock'].close
				TCP2Server_queue_stack[loop_count]['ready'].close
				TCP2Server_queue_stack[loop_count]['in'].close
				TCP2Server_queue_stack[loop_count]['out'].close
				
				
			print(TCP2Server_queue_stack)
			break


context = daemon.DaemonContext( #daemon konfig
	working_directory='/net/html/iotserver/iotserver',
   	umask=0o002,
   	pidfile=daemon.pidfile.PIDLockFile('/net/html/iotserver/iotserver/testpid'),
   	files_preserve = [
   		fh.stream,
    ],

)

do_something()
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
				do_something()
				
	elif 'stop' == sys.argv[1]:
		pidfile = open('/net/html/iotserver/iotserver/testpid', 'r') #pid File suchen
		line = pidfile.readline().strip()#daten lesen
		pidfile.close()
		#print(line); #nummer ausgabe
		pid = int(line) #zur int umwandelkn
		os.kill(pid, signal.SIGKILL) #PID kill
		os.remove('/net/html/iotserver/iotserver/testpid') #alte PID löschen
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
