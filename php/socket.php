
<?php
error_reporting(E_ALL);

class iot{
	public $vars = array();
	
	public function func_create ($data){ //funktion array vorbereiten 
		
		$this->vars[function_list]['funktion'] = 'iot';
		
		$this->vars[function_list]['iotfunk'] = $data;

		if ($this->vars['session_id'] != ''){
			#print ('funk');
			$this->vars[function_list]['session_id'] = $this->vars['session_id'];
		}
	}
		
	
	public function servervalue ($var,$data){ #Daten von ausserhalb der Klasse in das standart Array kopiern
		
		$this->vars[$var] = $data;
	}
	
	public function coneckt (){
		
		if ($this->vars['session_id'] != ''){
			iot::func_create('web_exist'); 
			$data = iot::send_read();
			#print_r($data);
			
			if ($data['return'] == 'not exist'){
				
				$this->vars['session_id'] = '';
				
			}
			
		}
		
		
		if ($this->vars['session_id'] == ''){
			
			iot::func_create('web_new'); 
			$data = iot::send_read();
			#print_r($data);
			$this->vars['session_id'] = $data['session_id'];
			$return['new_session_id'] = $data['session_id'];
		}
		
		iot::func_create('web_array');
		
		$return['array'] = iot::send_read();
		
		
		return($return);
	}
	
	public function push_data ($num,$var,$data){
		//print $num;
		
		$this->vars[function_list]['new'][$num][$var] = $data;
		
	}
	
	public function push (){
		print "aaaa";
		if ($this->vars['session_id'] != ''){
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
		if ($this->vars['session_id'] != ''){
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

		socket_recv($socket , $buf , 10204 , MSG_WAITALL );
		#print($buf);
		$returner = json_decode($buf,true);
		socket_close($socket);
		return($returner);
		
	}
}

$a = new iot();

$a->servervalue('session_id','');
$a->servervalue('host','localhost');
$a->servervalue('port',5050);

print_r($a->coneckt());
/**
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
**/
?>