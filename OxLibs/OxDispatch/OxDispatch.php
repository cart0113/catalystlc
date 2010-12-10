<?php
class OxDispatch {
	function __construct($dirIn = "", $where ="", $userKey = "LcPage_"){
		$rUri = OxString::removeEndSlash($_SERVER['REQUEST_URI']);
		$rUri = str_replace(strrchr($rUri, "?"), "", $rUri); 
		
		//print $rUri; exit();
		$dir =  $dirIn . $rUri; 
		$dir = OxString::removeEndSlash($dir);
		$dirs = array();
		while(!is_dir($dir)){
			$dir = explode("/", $dir);
			//ox_print_r($dir); exit();
			$d = array_pop($dir);
			if(substr($d, 0, 1) != "?"){
				$dirs[] = $d;
			}
			$dir = implode("/", $dir);
		}
		
		$ruris = array();
		if(sizeof($dirs) > 0){
			foreach($dirs as $out){
				$ruris[] = $out;
			}
		}
		$ruris = array_reverse($ruris);
		for($i = 0; $i < sizeof($ruris)-1; $i++){
			$_SESSION['OX_RURI'][$ruris[$i]] = $ruris[$i+1];
		}	
		$ruris = array_reverse($ruris);
		//print_r($_SESSION['OX_RURI']); exit();
		
		// The base directory cannot be the end url.  You must redirect to something like 'home'. 
		if($dir == $dirIn){
			$dir = $dirIn . "/$where";
		}
		$a = OxFile::getFiles($dir, '.php', false, false); 
		foreach($a as $key => $value){
			$phpFile = $value; 
			$baseClass = $key;
			break;
		}
		require_once($phpFile);
		foreach($ruris as $key){
			$class = $userKey . $key;
			if(class_exists($class)){
				//print $class; exit();
				new $class();
				exit();
			}
		}
		// no subclasses were found
		new $baseClass();
		exit();
	}
}
?>