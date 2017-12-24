
<?php
error_reporting(E_ALL);

class iot{
	public $vars = array();
	
	public function func_create ($data){ //funktion array vorbereiten 
		
		$this->vars[function_list]['funktion'] = 'iot';
		
		$this->vars[function_list]['iotfunk'] = $data;

		if ($this->vars['sesession_id'] != ''){

			$this->vars[function_list]['sesession_id'] = $this->vars['sesession_id'];
		}
	}
		
	
	public function setvalue ($var,$data){ #Daten von ausserhalb der Klasse in das standart Array kopiern
		
		$this->vars[$var] = $data;
	}
	
	public function get (){
		print $data;
		print_r($this->vars);
		
		if ($this->vars['sesession_id'] == ''){
			
			iot::func_create('array'); 
			$data = iot::send_read();
			print_r($data);
			//iot::setvalue('sesession_id',$data['sesession_id']);
			$this->vars['sesession_id'] = $data['sesession_id'];
		}
		print "hiuer hier";
		
		iot::func_create('array');
		print_r($this->vars);
		$data = iot::send_read();
		print_r($data);
	}
	
	function send_read($data){ //daten austausch PHP/IoT server
	
		$address = gethostbyname($this->vars['host']);
		$socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
		$result = socket_connect($socket, $address, $this->vars['port']);

		$transfer =  json_encode($this->vars[function_list]);
		
		print socket_send($socket,$transfer,1024 ,MSG_DONTROUTE);

		socket_recv ($socket , $buf , 10204 , MSG_WAITALL );
		
		$returner = json_decode($buf,true);
		socket_close($socket);
		return($returner);
		
	}
}

$a = new iot();

$a->setvalue('sesession_id','');
$a->setvalue('host','localhost');
$a->setvalue('port',5050);

$a->get();
?>