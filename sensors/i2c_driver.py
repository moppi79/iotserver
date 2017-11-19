import struct, array, io, fcntl, sys
import logging
I2C_SLAVE=0x0703

class i2c_treiber():
	
	def __init__ (self, adresse):#adresse vom Slave baustein
		bus = int(1) #bus selekt
		path = "/dev/i2c-%d" % (bus,) #pfad vom controller
		self.wr = io.open(path, "wb", buffering=0)#zuschreibender io
		self.rd = io.open(path, "rb", buffering=0)#lesender io
		fcntl.ioctl(self.wr, I2C_SLAVE, adresse)#Bus verbindung herstelen
		fcntl.ioctl(self.rd, I2C_SLAVE, adresse)#Bus verbindung herstellen
	
	def write (self, bank, werte): #schreiben Slave, Slave Register, Zu seztender wert 'zero' wert bei sensoren die ohne bank ansprechbar sind.
		if bank == 'zero':
			try:
				self.wr.write(bytearray([werte]))#in bus schreiben
			except :
				logging.warning('Fehler in i2c_treiber/write')
			
		else:
			try:
				self.wr.write(bytearray([bank,werte]))#in bus schreiben
			except :
				logging.warning('Fehler in i2c_treiber/write')
	
	def read (self, bank):#lesen Slave, slave register
		self.wr.write(bytearray([bank]))#in den bus schreiben
		try:
			ausgabe = self.rd.read(2)#rück gabe aus dem bus
		except:
			logging.warning('Fehler in i2c_treiber/read')
		else:	
			return array.array('B', ausgabe) #rücke als array
		
	def readswitch (self):#lesen Slave, slave register
	
		try:
			ausgabe = self.rd.read(2)#rück gabe aus dem bus
		except :
			logging.warning('Fehler in i2c_treiber/readswitch')
			return [0,99]
		else:
			return array.array('B', ausgabe) #rücke als array
		
	def close(self):
		
		self.wr.close()
		self.rd.close()
