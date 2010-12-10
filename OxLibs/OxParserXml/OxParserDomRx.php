<?php
require_once("/var/local/svn/data/php_old/OxLibs/OxParserXml/OxParserXmlRx.php");
class OxParserDomRx extends OxParserXmlRx {
	
	public $domTop; 
	public $domStack; 
	
	public $domHead; 
	public $prefix; 
	
	function __construct($prefix = ''){
		$this->setHead();
	}
	function setHead(){
		$this->domHead = new OxDomElement(); 
		$this->domTop = $this->domHead;
		$this->prefix = $prefix; 
	}
	function processTag(OxTagFromString $theTag){
		if($theTag->type == 2){
			$this->domTop = array_pop($this->domStack);	
		}
		else{
			$name = $theTag->getName();
			$this->domStack[] = $this->domTop;
			//print '$this->domTop = new ' . $this->prefix . $name . '($this->domTop, $theTag);';  
			eval('$this->domTop = new ' . $this->prefix . $name . '($this, $this->domTop, $theTag);');  
		}
		if($theTag->type == 1){
			$this->domTop = array_pop($this->domStack);	
		}
		return true; 
	}
	function processText($text){
		//$text = trim($text);
		if(strlen(trim($text)) > 0){
			new OxParserText($this->domTop, $text);
		}
	}
	function getXml(){
		return $this->domHead->contents[0]->output();
	}
	function xDom(){
		$parent = new OxTag(null, 'x_root');
		$this->domHead->contents[0]->xRun($parent);
		return $parent->contents[0]->output();
	}
}

class OxParserTag extends OxTag {
	public $rx; 
	public $xParent; 
	
	function __construct(OxParserDomRx $rx, OxDomElement $parent, $theTag = null){	
		
		if($theTag == null){
			$theTag = new OxTag(null, get_class($this));
		}
		
		OxTag::__construct($parent, $theTag->getName());
		
		$this->rx = $rx; 
		$this->atts  = $theTag->getAtts();
		if($theTag->type == 1){
			$this->one();
		}
	}	
	
	function xRun(OxDomElement $xParent){
		$this->xParent = $xParent; 
		$this->xDom();
		foreach($this->contents as $content){
			$this->xPreChild($content);
			$content->xRun($this->xParent);
			$this->xPostChild($content);
		}
		$this->xPostRun();
	}
	
	function xDom(){
		$this->xParent = new OxDomElement($this->xParent);
	}
	function xPreChild(){}
	function xPostChild(){}
	function xPostRun(){}
	function addText($theText){
		new OxParserText($this, $theText);
	}
}

class OxParserText extends OxDomText {

	function xRun(OxTag $parent){
		new OxDomText($parent, $this->theText);
	}
}