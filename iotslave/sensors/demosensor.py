import daemon, os, time, sys, signal, lockfile, socket, logging, datetime, json, random

class demosensor():
	
	def out(self,adresse,speicher):
		
		ret = {'demo_temp':'22:5', 'demo_feucht':'56,4'}
		return(ret)
