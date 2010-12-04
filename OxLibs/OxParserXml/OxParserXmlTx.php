<?php
class OxParserXmlTx {
	// An array of handlers.  Each item MUST have tagMatch(), processTag, and processText defined. 
	public $rx; 
	function __construct(OxParserXmlRx $rx){
		$this->rx = $rx;
	}
	function processBuffer($buffer)
	{	 
		//$this->exchangeChar();	
		$cString = ""; 
		$inTag = 0; 
	 	for($i = 0; $i < strlen($buffer); $i++)
	 	{
	 		$char =  $buffer[$i];
	 		if($inTag == 0){
	 			if($char == "<"){
	 				$cString = trim($cString, "\t\n\r\0");
	 				//$cString = trim($cString);
	 				//$cString = trim($cString);
	 				if(strlen($cString)>0 && $this->rx != null){			
	 					$this->rx->processText($cString);
	 				}
	 				$cString = "";
	 				$inTag = 1;
	 			}
	 			else{
	 				$cString .= $char;
	 			}
	 		}
	 		elseif ($inTag == 1){
				if($char == ">"){
					if(stristr($cString, "!--") == false){
						//$cString = str_replace("!--", "dd_comment", $cString);
						$theTag = new OxTagFromString($cString);
		 				$continue = $this->rx->processTag($theTag); 
		 				$inTag = 0;
		 				$cString = "";
		 				if($continue == false){
		 					return; 
		 				}
					}
					else{
						$inTag = 0; 
						$cString = ""; 
					}
				}
	 			else{
	 				$cString .= $char;
	 			}
	 		}
	 	}		 
	 }
	 
	function exchangeChar($buffer){
		$buffer = str_ireplace("&lt;", "<", $buffer); 
		$buffer = str_ireplace("&gt;", ">", $buffer);
		$buffer = str_ireplace("&nbsp;", "&#160;", $buffer);
		for ($i = 9; $i <= 13; $i++)
		{
			$buffer = str_ireplace(chr($i), "", $buffer);
		}
	}
	
}


class OxTagFromString extends OxTag {
	
	public $type; 
	function __construct($xmlString){
		OxTag::__construct();
		$this->type = 0; 
		
//		$this->processXmlString(&$xmlString); 
//	}
//	//*****************************************************************
//	//**  This function takes in a VALID xml string and turns
//	//**  it into a OxTag object. 
//	//**  Is used for parsing files. 
//	//*****************************************************************
//	function processXmlString($xmlString)
//	{
		$this->atts = array(); 
			
		if($xmlString{0} === "/"){
			$xmlString = substr($xmlString, 1, strlen($xmlString)); 
			$this->type = 2;
		}
		$ep = strpos($xmlString, " ");
		if($ep === false && strlen($xmlString) > 0){
			$ep = strlen($xmlString); 
		}
		$this->tagName = substr($xmlString, 0, $ep);
		if($this->type == 2){
			return; 
		}
		$xmlString = substr($xmlString, $ep+1, strlen($xmlString));
		$xmlString = trim($xmlString);  
		$run = true; 
		while($run){
			$ep = strpos($xmlString, "=");
			if($ep === false){
				$run = false; 
			}
			else{
				$atName = substr($xmlString, 0, $ep);
				$xmlString = substr($xmlString, $ep+1, strlen($xmlString));
				$xmlString = trim($xmlString); 
				// get rid of first quote;  	
				$xmlString = substr($xmlString, 1, strlen($xmlString));
				$ep = strpos($xmlString, chr(34));
				$atValue = substr($xmlString, 0, $ep);
				$xmlString = substr($xmlString, $ep+1, strlen($xmlString));
				$xmlString = trim($xmlString); 
				$this->atts[strtolower($atName)] = $atValue;
			} 
		} 
		
		/// THIS CHECKS VALID XML TAGS THAT CLOSE THEMSELVES
		$ep = strpos($xmlString, "/");
		if($ep !== false){
			$this->type = 1; 
			$this->one();
		}	
		$ep = strpos($this->tagName, "/");
		if($ep !== false){
			$this->type = 1; 
			$this->one();
			$this->tagName = str_replace("/", "", $this->tagName);
		}	 
	}
	function getType(){
		return $this->type; 
	}
	function makeTag(){
		return OxTag::makeTag($this->type);
	}
}