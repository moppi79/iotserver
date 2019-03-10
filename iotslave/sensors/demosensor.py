import daemon, os, time, sys, signal, lockfile, socket, logging, datetime, json, random

class demosensor():
	
	def install(self,data):
		ret = {}
		'''
		ret['name'] = {}
		ret['name']['value'] = '0'
		ret['name']['unit'] = "C°"
		'''
		
		ret['temperature'] = {}
		ret['temperature']['value'] = '0'
		ret['temperature']['unit'] = "C°"
		
		ret['humidity'] = {}
		ret['humidity']['value'] = '0'
		ret['humidity']['unit'] = "%"
		
		return(ret)
		

	def out(self,config):
		print ('aaa')
		ret = {'temperature':'22:5', 'humidity':'56,4'}
		return(ret)
