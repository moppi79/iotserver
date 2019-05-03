

class iss_create:
	
	def __init__(self):
		self.check_update = 0
		self.check_target = 0
		self.ram = {}
		self.ram['data'] = {}
	
	def sender (self,host,zone,name,system): 
		self.ram['sender'] = {}
		self.ram['sender']['host'] = host
		self.ram['sender']['zone'] = zone
		self.ram['sender']['name'] = name
		self.ram['sender']['system'] = system
		
	def update (self,host,zone,name,system,new): #update or target, New must 1 or 0 
		self.check_update = 1
		self.ram['update'] = {}
		self.ram['update']['host'] = host
		self.ram['update']['zone'] = zone
		self.ram['update']['name'] = name
		self.ram['update']['system'] = system
		self.ram['update']['new'] = new
		
	def target (self,host,zone,name,system):
		self.check_target = 1
		self.ram['target'] = {}
		self.ram['target']['host'] = host
		self.ram['target']['zone'] = zone
		self.ram['target']['name'] = name
		self.ram['target']['system'] = system
		
	def delete (self):#delete Target and update
		if self.check_target == 1:
			del self.ram['target']
			self.check_target = 0
			
		if self.check_update == 1:
			del self.ram['update']
			self.check_update = 0

	def install_data (self,id_name,value,typ):
		
		if self.check_target != self.check_update:
			
			self.ram['data']['id'] = id_name
			self.ram['data']['value'] = value
			self.ram['data']['typ'] = typ
			
			return (self.ram)
		else:
			print ('error')
