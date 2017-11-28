import daemon, os, time, sys, signal, lockfile, daemon.pidfile, socket, logging, datetime, json, random

class demo_sensor():
	
	def out(self,adresse,speicher):
		
		ret = {'demo_temp':'22:5', 'demo_feucht':'56,4'}
		return(ret)
