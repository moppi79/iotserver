<?php 
include('socket.php');
$datei = "../io_basic.json";

$Functions_list = array();
$Functions_list['on_off'] = array("description"=>'on While Button Pressed',"list"=>true,"options"=>'');
$Functions_list['on_off_touch'] = array("description"=>'On When Button pressd, off after second Push',"list"=>true,"options"=>''); 
$Functions_list['Timer_on_off'] = array("description"=>'on for X sec. example for heating',"list"=>true,"options"=>array('value'=>'time','html'=>'Time:<input name="time" value="sec">')); 
$Functions_list['auto_on_off'] = array("description"=>'Auto On off, Like Heartbeat.',"list"=>false,"options"=>array('value'=>'time_on,time_off','html'=>'Time on:<input name="time_on" value="sec"><br>Time off:<input name="time_off" value="sec">'));
$Functions_list['value_Transfer'] = array("description"=>'value Transver with converter, from hex to percent (255 to 100)',"list"=>true,"options"=>array('value'=>'min-in,min-out,max-in,max-out','html'=>'min-in:<input type="text" name="min-in" value="0"><br>min-out:<input type="text" name="min-out" value="0"><br>max-in:<input type="text" name="max-in" value="255"><br>max-out:<input type="text" name="max-out" value="100"><br>'));
$Functions_list['start_x'] = array("description"=>'automatic on: X time, off After X time',"list"=>false,"options"=>array('value'=>'time_on,time_off','html'=>'Time start:<input name="time_on" value="08:30"><br>Time end:<input name="time_off" value="08:40">'));
$Functions_list['over_max'] = array("description"=>'reach Max Value',"list"=>true,"options"=>array('value'=>'value_to_reach,value','html'=>'To reach:<input name="value_to_reach" value="5"><br>to set:<input name="value" value="1">'));
$Functions_list['under_min'] = array("description"=>'reach min Value',"list"=>true,"options"=>array('value'=>'value_to_reach,value','html'=>'To reach:<input name="value_to_reach" value="5"><br>to set:<input name="value" value="1">'));

if ($_POST['send'] == 'render'){ //insert data in datei
	
	if (!is_readable($datei)){
		
		$arry = json_encode(array('version'=>'1','count'=>'1'));
		$handler = fopen($datei,"w+");
		fwrite($handler,$arry,strlen($arry)); 
		fclose($handler);	
	}
		
		$weiter = unserialize($_POST['ser_data']);
		$arr = json_decode(file_get_contents($datei),TRUE);
		
		++$arr['count'];
		
		if (isset($_POST['id_2'])){
			
			$arr[$arr['count']]['target'] = $weiter[$_POST['id_2']];
			
		}else{
			if ($_POST['liste'] == 1){
				
				die('daten satz nicht ausgewählt abgebrochen, zurück gehen');
			}
		}
		
		$arr[$arr['count']]['source'] = $weiter[$_POST['id']];
		
		$arr[$arr['count']]['function'] = $_POST['funktion'];
		
		if ($Functions_list[$_POST['funktion']]['options'] != ''){
			
			$Pieces = explode("," ,$Functions_list[$_POST['funktion']]['options']['value']);
			foreach ($Pieces as $key => $dataew){
				$arr[$arr['count']][$dataew] = $_POST[$dataew];
			}
		}
		
		
		###Rewrite data in File 
		++$arr['version'];
		#print_r($arr);
		#print json_encode($arr);
		$handler = fopen($datei,"w+");
		fwrite($handler,json_encode($arr),strlen(json_encode($arr))); 
		fclose($handler);	
		print_r($arr[$arr['count']]);
	$Back_button = "<form method='post'>
		<input type='hidden' value='' name='send'>
		<input type='submit' name='aa' value='New'></td></tr>
		</form>";

print($Back_button);


}

if ($_POST['del']==1){
	
	
	$weiter = unserialize($_POST['ser_data']);
	$arr = json_decode(file_get_contents($datei),TRUE);
	
	print_r($_POST);
	unset($arr[$_POST['id']]);
	
	print_r($arr);
	$handler = fopen($datei,"w+");
	fwrite($handler,json_encode($arr),strlen(json_encode($arr))); 
	fclose($handler);	

	
}


if ($_POST['send'] == ''){//firstpage

	$a = new iot();
	
	$a->servervalue('session_id','');
	$a->servervalue('host','192.168.1.30');
	$a->servervalue('port',5050);
	
	$data= $a->coneckt();
	
	#print_r($data);
	$count = 1;
	
	foreach($data['install'] as $key => $data2){

		$weiter[$count] = $data2;
		
		$count++;
	}
	print_r($weiter);
	array_multisort ($weiter,SORT_ASC,SORT_REGULAR);
	$Data_ser = serialize($weiter);
 	
	foreach ($weiter as $key => $data){
		#$table = "";
		$table .= "<tr><td>".$data['sender']['host']."</td><td>".$data['sender']['zone']."</td><td>".$data['sender']['system']."</td><td>".$data['sender']['name']."</td><td>".$data['data']['id']."</td><td>".$data['data']['value']."</td><td><input type='radio' name='id' value='".$key."'></td></tr>";
	}
	
	print ('<form method="post"><table>
	<tr><td>host</td><td>zone</td><td>system</td><td>name</td><td>id</td><td>value</td><td>Select</td></tr>
	'.$table.'
	<tr><td colspan="5"><input type="submit" name="aa" value="Next"></td></tr>
	
	<input type="hidden" value="1" name="send">
	
	');
	print("<input type='hidden' value='".$Data_ser."' name='ser_data'></form>");
	
	
	if (is_readable($datei)){
	
		$arr = json_decode(file_get_contents($datei),TRUE);
	
		foreach ($arr as $key => $array){
			print ($key);
			if ($key != 'version' and $key != "count"){
				
				
				$delte .= "<tr><td>".$arr[$key]['function']."</td><td>".$arr[$key]['source']['sender']['name']."</td><td>".$arr[$key]['target']['sender']['name']."</td><td><button name='id' value='".$key."'>Delete</button></td></tr>";
		
			}
		}
		$Head .= "<Table><form method='post'><tr><td>Funktion</td><td>Auslöser</td><td>Ziel</td><td></td></tr>
		<input type='hidden' name='del' value='1'>
		";
		
		$foot = "</form></table>";
		print $Head;
		print $delte;
		print $foot;
		
	}

}


if ($_POST['send'] == '1'){//option Wahl
	$data = unserialize($_POST['ser_data']);
	$Back_button = '<form method="post">
		<input type="hidden" value="" name="send">
		<input type="submit" name="aa" value="back"></td></tr>
		</form>';
	
	//print"aaa";
	foreach ($Functions_list as $key => $array){
		
		$option_data .= ('<option value="'.$key.'">'.$array['description'].'</option>');
	}
	print ('<tr><td>'.$Back_button.'</td><td></td></tr>');
	if ($_POST['id'] == ''){
		
		
		die('no Actor Selected');
	}
	print ('<form method="post">
			<input type="hidden" value="1" name="send">');
	print ('<table>
	<tr><td>'.$data[$_POST['id']]['sender']['name'].'</td><td>
	');
	print ('<select name="funktion">'.$option_data.'</select></td></tr>');
	
	print("<input type='hidden' value='".$_POST['ser_data']."' name='ser_data'>");
	print ('<tr><td></td><td><input type="submit" name="aa" value="Next"></td></tr></table>
	<input type="hidden" value="2" name="send">
	<input type="hidden" value="'.$_POST['id'].'" name="id">
	</form>');
}



if ($_POST['send'] == '2'){//second step 
	if ($Functions_list[$_POST['funktion']]['options'] != ''){
		
		$opti = $Functions_list[$_POST['funktion']]['options']['html'];
		
	}
	
	if ($Functions_list[$_POST['funktion']]['list'] == true){
		$weiter = unserialize($_POST['ser_data']);
		foreach ($weiter as $key => $data){
			#$table = "";
			$des = '<tr><td>host</td><td>zone</td><td>system</td><td>name</td><td>id</td><td>Select</td></tr>
			<input type="hidden" value="1" name="liste">';
			$table .= "<tr><td>".$data['sender']['host']."</td><td>".$data['sender']['zone']."</td><td>".$data['sender']['system']."</td><td>".$data['sender']['name']."</td><td>".$data['data']['id']."</td><td><input type='radio' name='id_2' value='".$key."'></td></tr>";
		}
	}else{
		$des = '<tr><td></td><td></td><td></td><td></td><td></td><td></td></tr>';	
	}

	
	print ('<form method="post"><table>
	'.$des.'
	'.$table.'
	<tr><td colspan="5">'.$opti.'</td></tr>
	<tr><td colspan="5"><input type="submit" name="aa" value="Next">
	<input type="hidden" value="'.$_POST['funktion'].'" name="funktion">
	<input type="hidden" value="'.$_POST['id'].'" name="id">
	<input type="hidden" value="render" name="send"></td></tr>');
	print "<input type='hidden' value='".$_POST['ser_data']."' name='ser_data'></form>";
	
	
	
	$Back_button = "<form method='post'>
		<input type='hidden' value='".$_POST['ser_data']."' name='ser_data'>
		<input type='hidden' value='1' name='send'>
		<input type='hidden' value='".$_POST['id']."' name='id'>
		<input type='submit' name='aa' value='back'></td></tr>
		</form>";

print($Back_button);

}
?>