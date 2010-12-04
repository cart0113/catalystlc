<?php 

class OxDbColHandler {
	private $name; 
	private $value; 
	function __construct($name, $value){
		$this->name = $name; 
		$this->value = $value; 
	}
	function get(){
		return $this->value; 
	}
	function set($value){
		$this->value = $value; 
	}
}