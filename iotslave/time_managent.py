from multiprocessing import Process, Queue
import os, time, random, datetime, json



class time_managent ():
	
	def __init__(self):
		self.counter_plus = 0
		
		self.engerie_save = 0
		
		self.engerie_save1 = 0
		
		self.freq = 6 #schaf bare aktualisirungen pro sekunde minimumist 6
		
		self.wait = 1
		
		self.loops = 0 #aktueller count
 		
		self.last = 0
		
		self.runtime = 0 #zeit pro abrfrage 
		
		self.runtime_ts = 0 #stop zeit pro time slot und hz
		
		self.ts = {} #Timeslots
		
		self.set_freq(self.freq)#set freq
		
		self.start = self.ms_time() #ermittelen laufzeit scrip
		
		self.stop = 0 #ermittelen laufzeit scrip
		
		self.second = self.second_func()
		
		self.count_per_ts = 0
		
		self.count_per_ts_loop = 0 #loop anzeiger für TS
		
		self.count_per_ts_zeiger = 1 #Dic anzeiger für TS slots
		
		self.frq_overhead = 0 #Dic anzeiger für TS slots
		
		self.frq_overhead_value = 0
		
		self.max_lenght = 0 #maximale zeit die dsa scrip zeit hat pro durchgang
		
		self.aprox = {'time':0,'aprox':0}
		time_ms = self.ms_time()
		print(self.runtime)
		print(time_ms)
	
	def time_calc(self): #errechnen der standart variablen
		
		if self.ts != {}:
			#tn = self.ms_time()
			self.count_per_ts = round(self.freq / 6) #maximale anzahl abdfragen pro Timeslot
			self.max_lenght = round((self.ts['lenght'] *6) /self.freq) #maximale lenge Timesolt
			self.runtime_ts = (self.ts['lenght'] *6) / (self.count_per_ts*6)#laufzeit von einer abfrage
			self.frq_overhead_value = self.max_lenght-self.runtime_ts #standart Overhead pro abfrage
			

	def add_timeslot (self,new_ts):#wenn neuer Tineslot gekommen ist 
		
		self.ts = {}
		
		for x in new_ts:
			if x != 'lenght':
				self.ts[int(x)] = int(new_ts[x])
			else:
				self.ts['lenght'] = int(new_ts[x])
				
		self.time_calc()
	
	def second_func(self):#ausgabe Sekunde
		now = datetime.datetime.now()
		return (now.second)
	
	def ms_time(self): #ausgabe Ms in maximal 3 stellig
		now = datetime.datetime.now()
		timestr = str(now.microsecond)

		f = (6 - len(timestr))
		zero = ''
		
		while f > 0:
			
			zero += str("0")
			f = f - 1 
		timestring2 = zero+timestr
		
		return (int(timestring2[0:3]))

	def set_e_save (self,var):#set 2 hz 0/1
		
		self.engerie_save = int(var)
	
	def set_freq (self,new_freq):#set freq
		
		self.freq = int(new_freq)
		
		if self.ts != {}:
			self.time_calc()
		
	def runtime_calc(self):#runtime calc. 
		
		self.loops = self.loops +1
		
		if self.stop >= self.start:
			self.runtime = self.stop - self.start
		else:
			self.runtime = self.stop + (1000 -self.start) 
		self.aprox['time'] = self.aprox['time'] + self.runtime
		self.aprox['aprox'] = round(self.aprox['time']/self.loops)

	def pause(self):#haupt stück
		error={}
		if self.ts != {}:#wenn kein Timeslot vorhanden ist
			
			while self.wait == 1:#start pause. erster abruf
				if self.second != self.second_func():
					self.wait = 0
					self.start = self.ms_time()
			
			if self.engerie_save == 1:
				
				if self.engerie_save1 == 1:
					self.engerie_save1 = 0
					time.sleep(0.4)
				else: 
					self.engerie_save1 = 1
					time.sleep(0.4)
			
			self.stop = self.ms_time() #ermittelen laufzeit scrip
			if self.second != self.second_func():
				error['loop'] = self.loops
				self.second = self.second_func()
				self.aprox['time'] = 0
				self.aprox['aprox'] = 0
				self.loops = 0
				self.count_per_ts_zeiger = 1
				self.count_per_ts_loop = 1
				self.frq_overhead = 0
				self.loops = 0
			
			
			self.runtime_calc()

			if self.frq_overhead >= self.max_lenght:#pausiern

				self.count_per_ts_loop = self.count_per_ts_loop + 1
				self.frq_overhead = self.frq_overhead - self.max_lenght

				time.sleep(self.max_lenght/1000)
			
			if self.count_per_ts_loop <= self.count_per_ts:#counting overhead

				self.count_per_ts_loop = self.count_per_ts_loop + 1
				self.frq_overhead = self.frq_overhead + self.frq_overhead_value

			else:
				self.counter_plus = 1
			
			#print ('self.count_per_ts_zeiger: {}'.format(self.count_per_ts_zeiger))
			stop = self.runtime_ts - self.aprox['aprox']
			
						
			if stop < 0: #wenn zeit negativ (script brauchte zu viel zeit )
				stop = 0
				error['stop_time']='Script was too slow '
			else:
				stop = stop / 1000
			
			if self.count_per_ts_zeiger+1 == 7:
				vorstufe = 1
			else:
				vorstufe = self.count_per_ts_zeiger+1
			now = self.ms_time()

			if (self.ts[self.count_per_ts_zeiger] + self.ts['lenght']) < now:
				self.counter_plus = 1
				stop = (self.ts[vorstufe] - now) /1000

			
			if (now + self.runtime_ts) > (self.ts[self.count_per_ts_zeiger] + self.ts['lenght']):
				self.counter_plus = 1
				stop = (self.ts[vorstufe] - now) /1000
				
			if self.counter_plus == 1:
				self.counter_plus = 0
				self.count_per_ts_zeiger +=1
				if self.count_per_ts_zeiger == 7:
					self.count_per_ts_zeiger = 1
				self.count_per_ts_loop = 0
				
			if stop < 0: #wenn anderer zeit block ist 
				stop = (1000 - now)/1000 
				
			#print('stop: {}'.format(stop))
			time.sleep(stop) 
			
			self.start = self.ms_time() #ermittelen laufzeit scrip
			#print('start, Timeslot :{} - {} und nr {}'.format(self.ts[self.count_per_ts_zeiger],(self.ts[self.count_per_ts_zeiger] + self.ts['lenght'])  ,self.count_per_ts_zeiger))
			return(error)
			
		else:
			error['timeslot']='no time slot'
			time.sleep(0.2)
			return(error)
		
		
'''
loop = 0


a = time_managent()

#time_slot = {"1": '0', "lenght": '166', "2": '166', "6": '830', "5": '664', "3": '332', "4": '498'}
time_slot = {"1": '0', "lenght": '166', "2": '166', "6": '830', "5": '664', "3": '332', "4": '498'}

a.set_freq('6')
a.add_timeslot(time_slot)

a.set_e_save(0)
sec = a.second_func()
while True:
	#break
	
	if a.second_func() != sec:
		sec = a.second_func()
		a.set_freq(random.randrange(6, 50))
		
		if random.randrange(1, 9) == 4:
			a.set_e_save(1)
		else:
			a.set_e_save(1)
		
	error = a.pause()
	if error != {}:
		print (error)
	loop = loop + 1 
	time.sleep(random.randrange(4, 7)/1000)
	print (loop)
	if (loop >= 10):
		break
'''