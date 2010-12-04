<?php

class OxTrace {
	function lastClass($n = 2){
		$bt = debug_backtrace();
		return $bt[$n]['class'];
	}
	function lastFunction($n = 2){
		$bt = debug_backtrace();
		return $bt[$n]['function'];
	}
}