import os, time, sys, signal, socket, logging, datetime, json, random

server_address = ('localhost', 5050)#server adresse


def sock2(data):#befehl an Server senden und Rückanwort empfangen
	
	if 'funktion' in data:
		json_string = json.dumps(data)
		print('connecting to {} port {}'.format(*server_address))
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#art der verbingdung
		sock.connect(server_address)#verbindung herstellen
		sock.sendall(json_string.encode('utf8'))#befehl senden
		datain = sock.recv(1024).strip()#daten empfangen und leerzeichen entfernen
		sock.close()
		try:
			returner = json.loads(datain.decode('utf-8'))
		except ValueError as error:
			print ("error");
			
		return returner #return daten
	else:
		
		return 'error'
			
			
			
			
testers = {'funktion':'sensor','sensor':'new'}
		
key = sock2(testers)
					
time.sleep(2.0)
data = {'funktion':'sensor','sensor':'return', 'target_key':key}
		
print (sock2(data))
