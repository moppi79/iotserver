
[GLOBAL]
workingpath = /net/html/iotserver/


#################################################
#												#
#					Server						#
#												#
#################################################


[SERVER]
Adress = 192.168.1.30
Port = 5050
logname = Server.log

#max count IP Threads 
clients_max = 5


#################################################
#												#
#					Client						#
#												#
#################################################


[Slave_Basic]
#name slave
Name = Raspi2
#zone on slave. wenn you run multiple slaves on one Rasberry. but must be filled
Zone = balkon

logname = slave.log

#if i²c Mulitplex installed default 0
switch = 1 
switch_adress = 0x70
switch_port = 1


#################################################
#												#
#			Client Module/Sensor Load			#
#												#
#################################################


##################SENSORS#########################

[sensors]

#time in Seconds
update = 4

demosensor = 1
bh1750 = 1
htu21d = 1

##################MODULS#########################

[module]

mcp23017 = 1
pcf8574 = 1
demoic = 1
