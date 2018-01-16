
<?php
error_reporting(E_ALL);

class iot{
	public $vars = array();
	
	public function func_create ($data){ //funktion array vorbereiten 
		
		$this->vars[function_list]['funktion'] = 'iot';
		
		$this->vars[function_list]['iotfunk'] = $data;

		if ($this->vars['sesession_id'] != ''){
			print ('funk');
			$this->vars[function_list]['sesession_id'] = $this->vars['sesession_id'];
		}
	}
		
	
	public function setvalue ($var,$data){ #Daten von ausserhalb der Klasse in das standart Array kopiern
		
		$this->vars[$var] = $data;
	}
	
	public function get (){
		
		if ($this->vars['sesession_id'] == ''){
			
			iot::func_create('array'); 
			$data = iot::send_read();
			
			$this->vars['sesession_id'] = $data['sesession_id'];
		}
		
		iot::func_create('array');
		//print_r($this->vars);
		$data = iot::send_read();
		print_r($data);
		
		return('---->>>>>   hallllooooooo    <<<---');
	}
	
	public function push_data ($num,$var,$data){
		//print $num;
		
		$this->vars[function_list]['new'][$num][$var] = $data;
		
	}
	
	public function push (){
		print "aaaa";
		if ($this->vars['sesession_id'] != ''){
			iot::func_create('push'); 
			$data = iot::send_read();
			print_r($data);
			//print_r($this->vars);
		unset($this->vars[function_list]['new']);
		}else return('error no session ID');
		
	}
		
	public function update_data ($var,$data){
		//print $num;
		
		$this->vars[function_list]['update'][$var] = $data;
		
	}
	
	public function update (){
		print "bbbb";
		if ($this->vars['sesession_id'] != ''){
			iot::func_create('update'); 
			$data = iot::send_read();
			
			//print_r($this->vars);
		unset($this->vars[function_list]['update']);
		
		return($data);
		}else return('error no session ID');
		
	}
	
	
	function send_read($data){ //daten austausch PHP/IoT server
	
		$address = gethostbyname($this->vars['host']);
		$socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
		$result = socket_connect($socket, $address, $this->vars['port']);

		$transfer =  json_encode($this->vars[function_list]);
		
		socket_send($socket,$transfer,1024 ,MSG_DONTROUTE);

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

print($a->get());

$a->push_data(1,'host','raspi2');
$a->push_data(1,'location','balkon');
$a->push_data(1,'ic_chip','2');
$a->push_data(1,'id','80');
$a->push_data(1,'value','Iot-Server test');

$a->push();


$a->update_data(1,'host','raspi2');
$a->update_data(1,'location','balkon');
$a->update_data(1,'ic_chip','2');

print_r($a->update());

?>