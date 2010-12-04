<?php
class OxJs extends OxDomElement {
	private $jsFiles;
	private $jsTag; 
	
	function __construct(OxDomElement $parent){
		OxDomElement::__construct($parent, "js_code");		
		$this->jsFiles = new OxDomElement($this, "js_inc");
		$this->jsFiles->newLine();
		$this->jsFiles->addText($this->makeHtmlComment("External JavaScript Includes"));
		$this->jsTag = new OxTag($this, "script");
		$this->jsTag->setAtt("type", "text/javascript");
	}
	function output(){
		$theOutput = ""; 
		if(sizeof($this->jsFiles->contents) > 2){
			$theOutput .= $this->jsFiles->output(); 
		}
		if(sizeof($this->jsTag->contents) > 0){
			$theOutput .= $this->jsTag->output(); 
		}
		return $theOutput; 
	}
	function addJsFile($incFile){
		$t = '<script type="text/javascript" src="'. $incFile .'"></script>';
		$this->jsFiles->newLine();
		$this->jsFiles->addText($t);
	}
	function addJsCommand($jsCommand){
		//$this->jsTag->newLine(); 
		$this->jsTag->addText("\n\t\t" . $jsCommand);
	}
	
	function changeClassById($id, $class){
		return "document.getElementById('" . $id . "').className='" . $class . "';"; 
	}
	public static function escapeJS($string){
		$string = OxString::removeReturn($string);
		$string = str_replace("'", "\'", $string);
		$string = str_replace('"', '\"', $string);
		//$string = str_replace(":", "\:", $string);
	    //$string = str_replace(";", "\;", $string);
	    return $string; 
	}
	function ajaxExecute(OxPage $page, $action){
		$page->addJsCommand("oxajax_ajaxExecute('$action')");
	}
}

class OxDom_Ajax extends OxDomElement  {
	public $parentId; 
	function __construct($parentId){
		parent::__construct(null);
		$this->parentId = $parentId; 
		$GLOBALS['OXAJAX_EXECUTE'] = true; 
	}
	function __destruct(){
		print $this->output();
	}
	function newAjax($domElement = null, $parentId){
		if($domElement){
			return $domElement;
		}
		else {
			return new OxDom_Ajax($parentId);
		}
	}
	function output(){
		$js = "var domElement = document.getElementById('" . $this->parentId . "');";
		$js .= "domElement.innerHTML = '" . OxJs::escapeJs(parent::output()) . "';";
		return $js;
	}
}

?>