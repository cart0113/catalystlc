<?php
class OxCss extends OxDomElement {
	function __construct(OxDomElement $parent){
		OxDomElement::__construct($parent, "css_inc");
		$this->newLine();
		$this->addText($this->makeHtmlComment("External CSS Includes")); 
	}
	function addCssFile($incFile){
		$a = new OxTagLink($this); 
		$a->setAtt("rel", "stylesheet");
		$a->setAtt("href", $incFile);
		$a->setAtt("type", "text/css");
		//$a->setAtt("media", "print");
		$a->one();
	}
	function output(){
		if(sizeof($this->contents)>2){
			return $theOutput = OxDomElement::output();
		} 
	}
}

?>