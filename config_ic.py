'''
Aktoren rechen nach pin
pin		1		2		3		4		5		6		7		8
dezimal	1		2		4		8		16		32		64		128
hex		0x01 	0x02	0x04	0x08	0x10	0x20	0x40	0x80

ic_list und ic_chip
sind nur zum festlegen der START optionen
im laufenden betrieb sind alle werte im ram Bindend vorallem wenn sich ein IC neu starten sollte
werden alle daten aus dem ram gezogen 

'''

'''
ic_chip[1] ={'icname':'mcp23017',
			'ic_class':'mcp23017',
			'bus':'i2c',

			'adresse':0x20,
			'num':7,#anzahl ports
			'bank':2,#anzahl banken
			100:[0x00,0x00,0x12], #adresse der bank, start wert, export register MCP23017
			101:[0x01,0xff,0x13], #adresse der bank, start wert, export register MCP23017 1 in 0 out
			#1:[0x12,0x01,'aktor','beschreibung',1,[ziel bei schalter]], #register,startwert,typ,beschreibung,'fürwebseite Schaltbar' ("0"nein, "1"ja)optionaler wert für schalter
			'pins':{
			1:[0x12,0x01,'out','aktor','Aussen beleuchtung','1'],#IRLZ-relay. aussenbeläuchtung
			2:[0x13,0x01,'in','on_off','Schalter draussen','0',[0x12,0x01]], #Schalter für aussenbleuchtung draussen
			3:[0x12,0x02,'out','aktor','LED','0'],#LED signal lampe draussen
			4:[0x13,0x02,'in','regen','Regensensor','0',[0x12,0x04]],#erkennung Regensensor
			5:[0x12,0x04,'out','heizung','Heizung','0'],#IRLZ schalter - heizung für regensensor
			6:[0x12,0x08,'out','Heartbeat','led','0'],#LED heartbeat
			7:[0x12,0x40,'in','on_off','Schalter draussen','0',[0x12,0x01]],
			}}




ic_chip[2] ={'icname':'schreibtisch_display',
			'ic_class':'pcf8574',
			'bus':'i2c',

			'display_name':'schreibisch_display',
			'display_typ':'text', 
			'adress':0x27,
			'lines':4,
			'symbol':20,
			'lineadress':{1:0x80,
						2:0xC0,
						3:0x94,
						4:0xD4}}
						
'''

ic_chip[1] ={'icname':'demoic',
			'ic_class':'demoic',
			'bus':'i2c',
			'data':{'test':3}
}

ic_chip[2] ={'icname':'demoic2',
			'ic_class':'demoic',
			'bus':'i2c',
			'data':{'test':5}
}

ic_chip[3] ={'icname':'Schalter 0',
			'bus':'gpio',
			'data':{'id':6,'typ':'in','test':5} ###achtung ID geändert !!! nicht die ausklammuergn entfernene
}
'''
ic_chip[4] ={'icname':'Schalter 1 up',
			'bus':'gpio',
			'data':{'id':5,'typ':'in_up','test':5}
}

ic_chip[5] ={'icname':'Schalter 2 down',
			'bus':'gpio',
			'data':{'id':6,'typ':'in_down','test':5}
}
'''

ic_chip[6] ={'icname':'LED statisch',
			'bus':'gpio',
			'data':{'id':5,'typ':'out','value':1}###achtung ID geändert !!! nicht die ausklammuergn entfernene
}
'''
ic_chip[7] ={'icname':'LED PWM',
			'bus':'gpio',
			'data':{'id':19,'value':100,'typ':'pwm',
					'hz':50
					}
}

#Mods müssen als Typ mod gekennzeichnet werden, es wird ein sonder eointrag in eine tablle geschrieben
ic_chip[8] ={'icname':'demomod',
			'bus':'gpio',
			'data':{'id':88,'typ':'demo','mod':'1'
					}
}

sensor[1] = {'name':'demosensor',
			'sensor_class':'demosensor',
			'bus':'i2c',
			'data':{'test':1}
}

sensor[2] = {'name':'Licht',
			'sensor_class':'bh1750',
			'bus':'i2c',
			'data':{'adresse':0x23}
			}

sensordic = {1:[0x23,'options',bh1750(),'licht'],
2:[0x40,'options',htu21d(),'temperatur_feuchtigkeit']
}
'''