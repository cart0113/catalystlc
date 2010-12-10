<?php
class OxString {
	function getQ($stringIn) 
	{
		return chr(34) . $stringIn . chr(34); 
	}
	function removePeriod($stringIn){
		$ns = trim($stringIn, "\x00..\x1F");
		//remove any periods from name.
		if(substr($ns, -1, 1) == '.'){
			$ns = substr($ns, 0, -1);
		}
		return $ns; 
	}
	function addPeriod($stringIn){
		if(strlen($stringIn) > 1){
			return OxString::removePeriod(trim($stringIn)) . '.';
		}
		else{
			return $stringIn;
		}
	}
	function removeReturn($stringIn){
		$stringIn = str_replace(chr(9), "", $stringIn);		
		$stringIn = str_replace(chr(10), "", $stringIn);	
		$stringIn = str_replace(chr(13), "", $stringIn);
		return $stringIn;
	}
	function removeEndSlash($stringIn){
		while(substr($stringIn, -1, 1) == '/'){
			$stringIn = substr($stringIn, 0, -1);
		}
		return $stringIn;
	}
}

