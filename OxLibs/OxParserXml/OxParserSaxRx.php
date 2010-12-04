<?php
require_once("/var/local/svn/data/php_old/OxLibs/OxParserXml/OxParserXmlRx.php");
class OxParserSaxRx extends OxParserXmlRx {
	public $theTag;
	function processTag(OxTagFromString $theTag){		
		$methodName = $theTag->getName() . '_' . $theTag->getType();	
		if($methodName == "parser_exit_1"){
			return false; 
		}
		else{
			$this->setTag($theTag);
			//print $methodName; print '<br/>';
			if(method_exists($this, $methodName)){		
				$funName = '$continue = $this->' . $methodName . '();'; 
				eval($funName);
			}
			else{
				$this->orphanTag();
			}
			if($continue == 'stop'){		
				return false;
			}
			else {
				return true; 	
			}
		}	
	}	
	function setTag(OxTag $theTag){
		$this->theTag = $theTag; 
	}
}