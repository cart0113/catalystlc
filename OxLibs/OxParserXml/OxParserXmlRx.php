<?php
class OxParserXmlRx{
	function processTag(OxTagFromString $theTag){
		print "OxParserXmlTx processTag function is abstract"; 
		exit();
	}	
	function processText($text){
		print "You must implement processText"; 
		exit();
	}
	function orphanTag(){
		print "OxParserXmlRx orphanTag method is abstract and must be implemented."; 
		exit();
	}
}