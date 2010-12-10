<?php
class OxError {
	public static function dodie($warning){
		print "<br/><br/>*dodie* fatal error from class: " . OxTrace::lastClass() . " method: " . OxTrace::lastFunction() . " with message: $warning<br/><br/>";	
	}
	
	function ox_print_r($array, $exit = false){
		$i = 0; 
		print '<br/><br/>';
		foreach($array as $key => $value){
			print $i . ": key=$key value=$value<br/>";
			$i++; 
		}
		if($exit){
			exit();
		}
	}
	public static function pe($a){
		print $a;
		exit();
	}
	public static function alert($string){
		print "alert('$string');";
	}
	public static function eTime($start = 0){
		if($start == 0){
			return $GLOBALS['OxError_time_start'] =  microtime(true);	
		}
		else {
			$te = microtime(true) - $GLOBALS['OxError_time_start'];
			if($te < 0.001){
				return "<br/>Elapsed Time in micro seconds (us): " . 1000000*$te;
			}
			elseif($te < 1){
				return "<br/>Elapsed Time in milli seconds (ms): " . 1000*$te;
			}
			else {
				return "<br/>Elapsed Time in seconds (s): " . $te;
			}
			//print "<br/><br/>";
			//return $te;
		}
	}
}