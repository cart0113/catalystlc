<?php
// AJAX HANDLER -- DONE FOR SPEED -- SETTING AND GETTING REGISTER VARIABLES. 
if($_GET['OX_REGISTER_AJAX']){
	//print "alert('" . $_SERVER['QUERY_STRING'] . "');";
	//print "alert('" . $_GET['reset'] . "');";
	if($_GET['reset'] == 'true'){
		//print 'alert("hi");';
		$_SESSION = array();
	}
	elseif($_GET['superuser'] == 'true'){
		$_SESSION['OX_REGISTERS']['OX_SUPERUSER'] = !$_SESSION['OX_REGISTERS']['OX_SUPERUSER'];
		if($_SESSION['OX_REGISTERS']['OX_SUPERUSER']){
			print '$("#SUONID").html("ON");';
		}
		else {
			print '$("#SUONID").html("OFF");';
		}
	}
	else {
		$regKey = $_GET['OX_REGISTER_AJAX'];
		unset($_GET['OX_REGISTER_AJAX']);
		foreach($_GET as $key => $value){
			//print "alert('" . $regKey . ": " . $key . " = " . $value . "');";
			$_SESSION['OX_REGISTERS'][$regKey][$key]['value'] = $value;
		}
	}
	exit();
}

class OxRegister {
	public $regKey;
	function __construct($regKey, $clear = false){
		$this->regKey = $regKey;
		if($clear){
			unset($_SESSION['OX_REGISTERS'][$this->regKey]);
		}
		$new = true;
		if(isset($_SESSION['OX_REGISTERS'][$this->regKey])){
			foreach($_SESSION['OX_REGISTERS'][$this->regKey] as $key => $value){
				if($value['object']){
					$this->$key = unserialize($value['value']);
				}
				else {
					$this->$key = $value['value'];
				}
			}
			$new = false; 
		}
		else {
			$_SESSION['OX_REGISTERS'][$this->regKey] = array();
		}
		return $new; 
	}
	
	function __destruct(){
		if(isset($_SESSION['OX_REGISTERS'][$this->regKey])){
			foreach(get_object_vars($this) as $key => $value){
				//print $key . ": " . print_r($value) . "<br/>";
				if(gettype($value) == 'object'){
					$_SESSION['OX_REGISTERS'][$this->regKey][$key]['value'] = serialize($value);
					$_SESSION['OX_REGISTERS'][$this->regKey][$key]['object'] = true; 				
				}
				else {
					//$value->__destruct();
					$_SESSION['OX_REGISTERS'][$this->regKey][$key]['value'] = $value;
					$_SESSION['OX_REGISTERS'][$this->regKey][$key]['object'] = false; 				
				}
				//print $key . ": " . $value . "<br/>";
			}
		}
	}
	//////////////////////////////////////////////
	//////////////////////////////////////////////
	////   PUBLIC STATIC FUNCTIONS
	//////////////////////////////////////////////
	//////////////////////////////////////////////
	public static function getRegister($regKey, $defaultValue = null){
		if(!isset($_SESSION['OX_REGISTERS'][$regKey])){
			//OxInfoWindow::addVar($default);
			$_SESSION['OX_REGISTERS'][$regKey] = $defaultValue; 
		}
		return $_SESSION['OX_REGISTERS'][$regKey];
	}
	public static function setRegister($regKey, $value){
		$_SESSION['OX_REGISTERS'][$regKey] = $value; 
	}
	public static function isSuperuser(){
		return OxRegister::getRegister('OX_SUPERUSER', false); 
	}
	public static function setSuperuser($value = false){
		OxRegister::getRegister('OX_SUPERUSER', $value);
	}
	
	
	public static function getGlobal($regKey, $defaultValue = null){
		if(!isset($GLOBALS['OX_REGISTERS'][$regKey])){
			$GLOBALS['OX_REGISTERS'][$regKey] = $defaultValue; 
		}
		return $GLOBALS['OX_REGISTERS'][$regKey];
	}
	public static function setGlobal($regKey, $value){
		$GLOBALS['OX_REGISTERS'][$regKey] = $value; 
	}
}


