<?php
class OxDomElement {
	
	public $id;
	
	public $prettyPrint; 
	public $tabString;
	public $tab;
	public $newline; 
	// The names of the content!
	public $contents;
	//POINTERS
	public $parent; 
	public $xmlRoot; 
	//These pointers are form OxForm and OxFormBlock
	public $domForm; 
	public $domBlock;
	
	function __construct($parent = null, $id = null){	
		$this->contents = array();
		$this->prettyPrint = true; 
		$this->tabString = "";
		if($parent != null){
			$parent->addElement($this);
		}
		else{
			$this->xmlRoot = $this;
		}
		$this->id = $id; 
		
		// This are pointers that cannot be nest -- if you are in a form you are in a form. 
		$this->domForm = $parent->domForm;
		$this->domBlock = $parent->domBlock; 
	}
	function __destruct(){
		unset($this->parent);
		unset($this->xmlRoot);
	}

	function addElement(OxDomElement $element, $toBack = true){
		if($toBack){
			$this->contents[] = $element;	
		}
		else{	
			array_unshift($this->contents, $element);
		} 
		$element->parent = $this; 
		$element->xmlRoot = $this->xmlRoot; 
		//$element->setLevel($this->tabString);
	}
	function getId(){
		return $this->id; 
	}
	function clearContents(){
		foreach($this->contents as $content){
			$content->clearContents(); 
		}
		unset($this->contents);
		$this->contents = array(); 
	}
//	function setLevel($tabString){
//		$this->xmlRoot = $this->parent->xmlRoot; 
//		$this->docLevel = $this->parent->docLevel+1; 
//		$this->tabString = $tabString . $this->tabString;
//		foreach($this->contents as $content){	
//			$content->setLevel($tabString); 	
//		}
//	}
	function prettyPrintOn(){
		$this->xmlRoot->prettyPrint = true; 
	}
	function prettyPrintOff(){
		$this->xmlRoot->prettyPrint = false;
	}
	function upTab(){
		if($this->parent != null && $this->xmlRoot->prettyPrint){
			$this->tabString .= "\t"; 
		}
	}
	function addText($theText = ""){
		new OxDomText($this, $theText, null);
	}
	function addSpace($n=1){
		for($i = 0; $i < $n; $i++){
			$text .= "&nbsp;";
		}
		$this->addText($text);
	}
	function addHidden($name, $value){
		new OxTagInput_Hidden($this, null, null, $name, $value);
	}
	function appendText($theText = ""){
		foreach($this->contents as $content){
			if($content instanceof OxDomText ) {
				$content->appendText($theText);
				break;  
			}
		}
		return; 
	}
	function prependText($theText = ""){
		foreach($this->contents as $content){
			if($content instanceof OxDomText ) {
				$content->prependText($theText);
				break;  
			}
		}
		return; 
	}
	function replaceText($oldText, $newText){
		foreach($this->contents as $xmlItem){
			$xmlItem->replaceText($oldText, $newText);
		}
	}
	function makeHtmlComment($comment){
		$comment = "<!-- " . $comment . "-->";
		return $comment; 
	}
	function addHtmlComment($comment){
		$this->addText($this->makeHtmlComment($comment));
	}
	function newLine($n = 1){
		for($i = 0; $i < $n; $i++){
			$this->addText("\n" . $this->tabString);
		}
	}
	function upperCase(){
		foreach($this->contents as $content){
			$content->upperCase(); 
		}
	}
	function lowerCase(){
		foreach($this->contents as $content){
			$content->lowerCase(); 
		}
	}
	function output(){
		$theOutput = "";
		foreach($this->contents as $xmlItem){
			$theOutput .= $xmlItem->output();
		}
		return $theOutput; 
	}
}

class OxDomText extends OxDomElement {
	
	protected $isText; 
	protected $theText; 
	
	
	
	function __construct(OxDomElement $parent = null, $theText = "", $id = null){
		OxDomElement::__construct($parent, $id);
		$this->theText = $theText; 
		$this->isText = true; 
//		$this->tab = $parent->tab && $parent->newline;  
//		if($this->tab){
//			$this->upTab();
//		}
	}

	function addElement(){
		die("OxDomText::addElement ->  You cannot do this ");
	}
	function addText(){
		die("OxDomText::addText -> You cannot do this");
	}
	function replaceText($oldText, $newText){
		$this->theText = str_replace($oldText, $newText, $this->theText);
	}
	function prependText($theText){
		$this->theText = $theText . $this->theText; 
	}
	function appendText($theText){
		$this->theText .= $theText; 
	}
	function upperCase(){
		OxDomElement::upperCase();
		$this->theText = strtoupper($this->theText);
	}
	function lowerCase(){
		OxDomElement::upperCase();
		$this->theText = strtolower($this->theText);
	}
	function output(){
		if($this->xmlRoot->prettyPrint && $this->tab){
			$this->theText = "\n". $this->theText;
			$this->theText = str_replace(chr(10), chr(10) . $this->tabString, $this->theText);
			$this->theText = str_replace(chr(12), chr(12) . $this->tabString, $this->theText);
			return $this->theText;
		}
		else{
//			$this->theText = str_replace(chr(10), "", $this->theText);
//			$this->theText = str_replace(chr(12), "", $this->theText);
//			$this->theText = str_replace(chr(13), "", $this->theText);
			return $this->theText;
		}
	}
}

class OxTag extends OxDomElement {
	
	public $tagName; 
	protected $atts; 
	protected $type; 
	// THIS IS FOR CHECKBOXES ONLY
	public $end; 
	
	public $commentOn; 
	
	function __construct($parent = null, $tagName = null, $tagId = null, $tagClass = null, $text = null, $tab = true, $newline = true){ 		
		OxDomElement::__construct($parent, $tagId);
		$this->tagName = $tagName; 
		//By default these tags are NOT xml one tags. 
		$this->type = 0; 
		$this->doComment = false;
		$this->atts = array(); 
		if($tagId != null){
			$this->setId($tagId);
		}
		if($tagClass != null){
			$this->setClass($tagClass);
		}
		$this->tab = $tab;
		$this->newline = $newline; 
		if($this->tab){
			$this->tabString = $this->parent->tabString . "\t";
			//$this->upTab();
		}
		if($text != null){
			$this->addText($text);
		}
	}
	
	function commentOn(){  $this->doComment = true; }
	function commentOff(){ $this->doComment = false; }
	
	function setEnd($end){
		$this->end = " " . $end; 
	}
	
	function setAtt($key, $item){
		if($key == $id){
			$this->id = $id; 
		}
		else
		{
			$this->atts[$key] = $item;
		}
	}
	function getAtts(){
		return $this->atts;
	}
	function addAtt($key, $item){
		if(isset($this->atts[$key]) == false){
			$this->setAtt($key, $item);
		}
		else{
			$this->atts[$key] .= " " . $item; 
		}
	}
	function setId($id){
		$this->id = $id; 
		$this->setAtt('id', $this->id);
		return $this->id; 
	}
	function setClass($class){
		$this->setAtt("class", $class);
	}
	function addClass($class){
		$this->addAtt("class", $class);
	}
	function setStyle($style){
		$this->setAtt("style", $style);	
	}
	function addStyle($style){
		$this->addAtt("style", $style);	
	}
	function width($width){
		$this->addStyle("width: $width;");
	}
	function height($height){
		$this->addStyle("height: $height;");
	}
	function padding($padding, $where = ""){
		if($where != ""){
			$where = "-" . $where; 
		}
		$this->addStyle("padding$where: $padding;");
	}
	function one(){
		$this->type = 1; 
	}
	function getName(){
		return $this->tagName;
	}
	function getAtt($key, $default = null){
		if(isset($this->atts[$key])){
			return $this->atts[$key]; 
		}
		else {
			return $default; 
		}
	}
	function getClass(){
		return $this->getAtt("class");
	}
	function deleteAtt($key){
		unset($this->atts[$key]);
	}
	function clearAtts(){
		$this->atts = array();
	}
	function makeTag($type = 0)
	{
		$outString = "";
		if($type == 2){
			$outString .= "/"; 
		}
		
		$outString .= $this->tagName; 
			
		if($type != 2){
			foreach($this->atts as $key => $value){
				$outString .= " " . $key . "=" . OxString::getQ($value); 
			}
		}	
		if($type == 1):
			$outString .= " /"; 
		endif; 
		
		$outString = "<" . $outString . "$this->end>"; 
		return $outString; 
	}
	function output(){	
		
		$theOutput = "";
		
		if($this->xmlRoot->prettyPrint){
			if($this->newline == true){
				$theOutput .= "\n";
			} 
			if($this->tab){
				$theOutput .= $this->tabString;
			}
		}
		
		$theOutput .= $this->makeTag($this->type);
		
		$theOutput .= OxDomElement::output();
		
		if($this->type != 1){	 
			$outString = $endNewLine . $this->makeTag(2); 
			if($this->comment == true){
				$outString .= $this->makeHtmlComment($this->tagName);
			}
			if($this->xmlRoot->prettyPrint){
				if($this->newline){
					$theOutput .= "\n";
					if($this->tab){
						$theOutput .= $this->tabString;
					}	
				}
			}
			$theOutput .= $outString; 		
		}
		return $theOutput; 
	}
}

class OxTagHtml extends OxTag {
	function __construct($parent = null, $tagId = null, $tagClass = null, $text = null){
		OxTag::__construct($parent, "html", $tagId, $tagClass, $text, false);
	}
}
class OxTagTitle extends OxTag {
	function __construct($parent = null, $tagId = null, $tagClass = null, $text = null){
		OxTag::__construct($parent, "title", $tagId, $tagClass, $text);
	}
}
class OxTagHead extends OxTag {
	function __construct($parent = null, $tagId = null, $tagClass = null, $text = null){
		OxTag::__construct($parent, "head", $tagId, $tagClass, $text);
	}
}
class OxTagLink extends OxTag {
	function __construct($parent = null, $tagId = null, $tagClass = null, $text = null){
		OxTag::__construct($parent, "link", $tagId, $tagClass, $text);
	}
}
class OxTagIcon extends OxTag {
	function __construct($parent = null, $icon = null){
		OxTag::__construct($parent, "link");
		$this->setAtt("rel", "Shortcut Icon"); 
		$this->setAtt("href", $icon);
	}
}
class OxTagBody extends OxTag {
	function __construct($parent = null, $tagId = null, $tagClass = null, $text = null){
		OxTag::__construct($parent, "body", $tagId, $tagClass, $text);
	}
}

class OxTagDiv extends OxTag {
	function __construct($parent = null, $tagId = null, $tagClass = null, $text = null){
		OxTag::__construct($parent, "div", $tagId, $tagClass, $text);
	}
}

class OxTagSpan extends OxTag {
	function __construct($parent = null, $tagId = null, $tagClass = null, $text = null){
		OxTag::__construct($parent, "span", $tagId, $tagClass, $text, false, false);
	}
}

class OxTagTable extends OxTag {
	function __construct($parent = null, $tagId = null, $tagClass = null){
		OxTag::__construct($parent, "table", $tagId, $tagClass);
	}
}

class OxTagRow extends OxTag {
	function __construct($parent = null, $tagId = null, $tagClass = null, $text = null){
		OxTag::__construct($parent, "tr", $tagId, $tagClass, $text);
	}
}
class OxTagCell extends OxTag {
	function __construct($parent = null, $tagId = null, $tagClass = null, $text = null){
		OxTag::__construct($parent, "td", $tagId, $tagClass, $text);
	}
}

///////////////////////////////////////////////////
///    OxTagImage
//////////////////////////////////////////////////
class OxTagImage_Master extends OxTag {
	public $tpie;
	function __construct($parent = null, $tagId = null, $tagClass = null, $src = null, $transparentPng = false){
		OxTag::__construct($parent, "img", $tagId, $tagClass);
		if($transparentPng && $_SESSION['OX_VISITOR_INFO']['BROWSER'] == 'IE' && $_SESSION['OX_VISITOR_INFO']['VERSION'] < 7){
			$blank = "http://" . $_SERVER['SERVER_NAME'] . "/blank.gif";
			$this->addWH($src);
			$this->addStyle("filter: progid:DXImageTransform.Microsoft.AlphaImageLoader(src='" . $src . "', sizingMethod='scale');");  
			$this->setAtt("src", $blank);
			$this->tpie = true; 
		}
		else {
			$this->setAtt("src", $src);
			$this->tpie = false; 
		}
		$this->one();
	}
	function getImageSize($src){
		return getimagesize($src);
	}
	function addWH($src){
		$xy = $this->getImageSize($src);
		$this->addAtt("width" , $xy[0] . "px;");
		$this->addAtt("height", $xy[1] . "px;");
	}
}
class OxTagImage extends OxTagImage_Master {
	function __construct($parent = null, $tagId = null, $tagClass = null, $src = null){
		parent::__construct($parent, $tagId, $tagClass, $src);
	}
}
class OxTagImage_TransparentPng extends OxTagImage_Master {
	function __construct($parent = null, $tagId = null, $tagClass = null, $src){
		parent::__construct($parent, $tagId, $tagClass, $src, true);
	}
}
/////////////////////////////////////////////////
//// OxTagRef
/////////////////////////////////////////////////
class OxTagRef_Master extends OxTag {
	function __construct($parent = null, $tagId = null, $tagClass = null, $text = null, $href = null, $js = false, $altRef = null){
		OxTag::__construct($parent, "a", $tagId, $tagClass, $text, true, false);
		if($js == false){	
			$this->setAtt("href", $href);
		}
		else {
			//Alt Refs are so Js or Ajax Commands degrade gracefully.  
			//$GLOBALS['OXAJAX_EXECUTE'] makes sure you are not in an AJAX call -- if you're
			//in a Ajax call, you do not want to change the reference. 
			if($altRef != null && $GLOBALS['OXAJAX_EXECUTE'] == false){
				$this->setAtt("href", $altRef);
				if($tagId == null){
					if(!isset($GLOBALS['OX_AJAX_REF'])){
						$GLOBALS['OX_AJAX_REF'] = 0;
					}
					$tagId = 'OX_AJAX_REF_' . $GLOBALS['OX_AJAX_REF'];
					$GLOBALS['OX_AJAX_REF'] = $GLOBALS['OX_AJAX_REF']+1;
					$tagId = $this->setId($tagId);
					if($js == 'js'){
						//This adds script command to bottom of current page. 
						$this->xmlRoot->addJsCommand("oxjs_changeRef('$tagId', 'javascript:$href');");
					}
					elseif($js == 'ajax'){
						$this->xmlRoot->addJsCommand("oxjs_changeRef('$tagId', 'javascript:oxajax_ajaxExecute(" . OxString::getQ($href) . ")');");
					}
				}
			}
			else {
				if($js == 'js'){
					$this->setAtt("href", "javascript:$href");
				}
				elseif($js == 'ajax'){
					$this->setAtt("href", "javascript:oxajax_ajaxExecute('$href')");					
				}
			}
		}
	}
	function addTitle($title){
		$this->setAtt("title", $title);
	}
	function addAnchor($name){
		$this->setAtt("name", $name); 
	}
	function output(){
		$href = $this->getAtt("href", null); 
		if($href == null){
			$this->addClass("link_no_ref");
		}
		return OxTag::output();
	}
}

class OxTagRef extends OxTagRef_Master {
	function __construct($parent = null, $tagId = null, $tagClass = null, $text = null, $href = null){
		parent::__construct($parent, $tagId, $tagClass, $text, $href);
	}
}
class OxTagRef_Js extends OxTagRef_Master {
	function __construct($parent = null, $tagId = null, $tagClass = null, $text = null, $href = null, $altRef = null){
		parent::__construct($parent, $tagId, $tagClass, $text, $href, 'js', $altRef);
	}
}
class OxTagRef_Ajax extends OxTagRef_Master {
	function __construct($parent = null, $tagId = null, $tagClass = null, $text = null, $href = null, $altRef = null){
		parent::__construct($parent, $tagId, $tagClass, $text, $href, 'ajax', $altRef);
	}
}

//////////////////////////////////////////////
//////  Simple Elements
//////////////////////////////////////////////
class OxTagBr extends OxTag {
	function __construct($parent = null, $tagId = null, $tagClass = null){
		OxTag::__construct($parent, "br", $tagId, $tagClass);
		$this->one();
	}
}
class OxTagP extends OxTag {
	function __construct($parent = null, $tagId = null, $tagClass = null, $text = null){
		OxTag::__construct($parent, "p", $tagId, $tagClass, $text);
	}
}
class OxTagB extends OxTag {
	function __construct($parent = null, $tagId = null, $tagClass = null, $text = null){
		OxTag::__construct($parent, "b", $tagId, $tagClass, $text, false, false);
	}
}
class OxTagI extends OxTag {
	function __construct($parent = null, $tagId = null, $tagClass = null, $text = null){
		OxTag::__construct($parent, "i", $tagId, $tagClass, $text, false, false);
	}
}
class OxTagU extends OxTag {
	function __construct($parent = null, $tagId = null, $tagClass = null, $text = null){
		OxTag::__construct($parent, "u", $tagId, $tagClass, $text, false, false);
	}
}
class OxTagO extends OxTagSpan  {
	function __construct($parent = null, $tagId = null, $tagClass = null, $text = null){
		parent::__construct($parent, null, null, $text);
		$this->addStyle("text-decoration: overline;");
	}
}
class OxTagOl extends OxTag {
	function __construct($parent = null, $tagId = null, $tagClass = null){
		OxTag::__construct($parent, "ol", $tagId, $tagClass);
	}
}

class OxTagUl extends OxTag {
	function __construct($parent = null, $tagId = null, $tagClass = null){
		OxTag::__construct($parent, "ul", $tagId, $tagClass);
	}
}

class OxLi extends OxTag {
	function __construct($parent = null, $tagId = null, $tagClass = null, $text = null){
		OxTag::__construct($parent, "li", $tagId, $tagClass, $text);
	}
}

?>