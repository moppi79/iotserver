from multiprocessing import Process, Queue
import os, time, random, datetime, json



class time_managent ():
	
	def __init__(self):
		
		self.freq = 5
		
		self.loops = 0
 		
		self.last = 0
		
		self.runtime = 0
		
		self.set_freq(self.freq)
		
		time_ms = self.ms_time(0)
		print(self.runtime)
		print(time_ms)
		
		
		
	
	def ms_time(self,select): #return 0 ms 1 Second 2 array with both
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
	
	def set_freq (self,new_freq):
		
		self.freq = new_freq
		
		self.runtime = 1000 / self.freq
		
	
	def stop(self):
		print ('aa')
		
		
		
		time.sleep(0.2) 
		
		

loop = 0


a = time_managent()

while True:
	
	a.stop()
	loop = loop + 1 
	print (loop)
	if (loop >= 10):
		break
	