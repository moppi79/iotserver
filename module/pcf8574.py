import daemon, os, time, sys, signal, lockfile, daemon.pidfile, socket, logging, datetime, json, random

#from module.i2c_driver import i2c_treiber

from i2c_driver import i2c_treiber

'''
Aktoren rechen nach pin
pin		1		2		3		4		5		6		7		8
dezimal	1		2		4		8		16		32		64		128
hex		0x01 	0x02	0x04	0x08	0x10	0x20	0x40	0x80

Clear display 	0 	0 	0 	0 	0 	0 	0 	0 	0 	1 	Clears display and returns cursor to the home position (address 0). 	1.64mS
Cursor home 	0 	0 	0 	0 	0 	0 	0 	0 	1 	* 	Returns cursor to home position (address 0). Also returns display being shifted to the original position. DDRAM contents remains unchanged. 	1.64mS
Entry mode set 	0 	0 	0 	0 	0 	0 	0 	1 	I/D 	S 	Sets cursor move direction (I/D), specifies to shift the display (S). These operations are performed during data read/write. 	40uS
Display On/Off control 	0 	0 	0 	0 	0 	0 	1 	D 	C 	B 	Sets On/Off of all display (D), cursor On/Off (C) and blink of cursor position character (B). 	40uS
Cursor/display shift 	0 	0 	0 	0 	0 	1 	S/C 	R/L 	* 	* 	Sets cursor-move or display-shift (S/C), shift direction (R/L). DDRAM contents remains unchanged. 	40uS
Function set 	0 	0 	0 	0 	1 	DL 	N 	F 	* 	* 	Sets interface data length (DL), number of display line (N) and character font(F). 	40uS
Set CGRAM address 	0 	0 	0 	1 	0	0	0	0	0   RAM address 	Sets the CGRAM address. CGRAM data is sent and received after this setting. 	40uS
Set DDRAM address 	0 	0 	1 	0	0	0	0	0	0	DDRAM address 	Sets the DDRAM address. DDRAM data is sent and received after this setting. 	40uS
Read busy-flag and address counter 	0 	1 	BF 	CGRAM / DDRAM address 	Reads Busy-flag (BF) indicating internal operation is being performed and reads CGRAM or DDRAM address counter contents (depending on previous instruction). 	0uS
Write to CGRAM or DDRAM 	1 	0 	write data 	Writes data to CGRAM or DDRAM. 	40uS
Read from CGRAM or DDRAM 	1 	1 	read data 	Reads data from CGRAM or DDRAM. 	40uS



'''

# commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80
# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00
# flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00
# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00


	
# flags for backlight control
#LCD_BACKLIGHT = 0x08
LCD_BACKLIGHT = 0x00
LCD_NOBACKLIGHT = 0x00
	
En = 0b00000100 # Enable bit
Rw = 0b00000010 # Read/Write bit
Rs = 0b00000001 # Register select bit


ic_chip = {}

ic_chip[1] ={'icname':'display_pcf8574',
			'adress':0x27,
			'lines':4,
			'lineadress':{1:0x80,
						2:0xC0,
						3:0x94,
						4:0xD4}}





class display_pcf8574 ():
	
	def install(self,config,number):
		display  = 'dummy'
		return_var = {}
		
		return_var['adress'] = config['adress']
		return_var['lines'] = config['lines']
		return_var['write'] = 0 #Write - 0 nothing change, 1 Display light on/off, 2 write text
		

		
		return_var['light'] = 0 #light - 0 off, 1 on
		return_var['property'] = 0 #property - 0 off,  1 When the Content to show until the user is quiting this bit, the display is not refresh the display

		return_var['pre_property'] = 0 #last run bevor property bit is set and display goes closed
		
		self.i2c = i2c_treiber(config['adress'])

		self.formating(0x03)
		self.formating(0x03)
		self.formating(0x03)
		self.formating(0x02)
		self.formating(0x01)
		#self.i2c.write('zero',(LCD_FUNCTIONSET | LCD_2LINE ))
		
		self.formating(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS | LCD_4BITMODE)
		
		#self.formating(LCD_DISPLAYCONTROL | LCD_DISPLAYON | LCD_BLINKON)
		#self.formating(LCD_DISPLAYMOVE | LCD_MOVERIGHT )
		#self.formating(LCD_ENTRYMODESET | LCD_ENTRYRIGHT )
		
		
		#self.textsend('*****Moppi*****',0x80)
		
		for x in config['lineadress']:
			return_var['line'+str(x)] = {'adress':config['lineadress'][x],'value':''}
			self.textsend('Line {}'.format(str(x)),(config['lineadress'][x]))
			print ('Line{}'.format(str(x)))
		
		return_var['string'] = '' #string long string
		#self.formating(0x08)
		time.sleep(.1)
		self.i2c.close()
		
		return(return_var)
		
		
		
		
		
		
		
		#property - 0 off,  1 When the Content to show until the user is quiting this bit, the display is not refresh the display

	def comparison (self,ram):
		
		if ram['property'] == 1:
			
			#disply write 
			display  = 'dummy'
	
	'''
	def __init__(self):
		print('lalal')
		self.i2c = i2c_treiber(0x27)

		self.formating(0x03)
		self.formating(0x03)
		self.formating(0x03)
		self.formating(0x02)
		self.formating(0x01)
		#self.i2c.write('zero',(LCD_FUNCTIONSET | LCD_2LINE ))
		
		self.formating(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS | LCD_4BITMODE)
		
		#self.formating(LCD_DISPLAYCONTROL | LCD_DISPLAYON | LCD_BLINKON)
		#self.formating(LCD_DISPLAYMOVE | LCD_MOVERIGHT )
		#self.formating(LCD_ENTRYMODESET | LCD_ENTRYRIGHT )
		
		
		
		self.textsend('*****Moppi*****',0x80)
		self.textsend('*****Kagari*****',0xC0)
		self.textsend('*****Kim*****',0x94)
		self.textsend('*****Lucy*****',0xD4)
		self.formating(0x00)
	
		self.i2c.close()
	'''
	
	def textsend(self,string,line):
		print ('string:{} line:{}'.format(string,line))
		self.formating(line)
		for char in string:
			self.formating(ord(char), Rs)
			#time.sleep(0.5)
		
		
	def formating(self, data, mode=0): #8 bit in 4 bit teilen.
		self.write(mode | (data & 0xf0)) #obere 4 bit
		self.write((mode | ((data << 4) & 0xf0))) #untere 4 bit

	def write(self, data):
		self.i2c.write('zero',data) # Display in bereitschaft setzen
		time.sleep(.0001)
		self.i2c.write('zero',(data | En | LCD_BACKLIGHT)) #wr bit setzen daten schreiben
		time.sleep(.0006)
		self.i2c.write('zero',((data & ~En) | LCD_BACKLIGHT)) #daten bestätigen
		time.sleep(0.0001)







test = display_pcf8574()

print (test.install(ic_chip[1],11))
