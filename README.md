# iotserver
is under construktion. 

es ist ein IoT framework , für pyhton 3.x 

- iotserver

es ist der anmelde server und ISS nachrichten proxy 
alle clients melden sich hier (IoTclient und Web-clients)

er gibt alle ISS nachrichten raus, und stellt auch das GIS bei aufforderung
und gibt sammelt alle sensor daten

- iotslave
der IoT slave stellt die verbindung zum I²C/SPI her. (hat eine offene Schnittstelle )
desweiteren kann er kenn er autonome Scripte per Plugin bedinen und ausführen
alle plugins werden per ISS bedient. 

der IoT slave kann auf einem sytem mehrfach gestartet werden wenn man ein Multiplexer modul verwendet. 
und somit auf einem gerät mehre zonen haben. die dann auch ein eigenes timing auf dem I²C/SPI haben. 


Wiki seite erstellt 
