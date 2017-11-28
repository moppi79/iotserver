import daemon, os, time, sys, signal, lockfile, daemon.pidfile, socket, logging, datetime, json, random

from module.i2c_driver import i2c_treiber

class pcf8574 ():
	
	def ___init___(self):
		
		