<?php
class OxDomPage extends OxDomElement
{	
	protected $domHtml;
	public $domHead;
	protected $domTitle; 
	protected $domCss;
	public $domBody;
	protected $domJs;
	
	function __construct(){}
	function addPageHead(){
		return '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">';
	}
	function makeBaseDom(){
		OxDomElement::__construct(null);
		$this->addText($this->addPageHead());
		$this->domHtml = new OxTagHtml($this);
		$this->domHead = new OxTagHead($this->domHtml); 
	    $this->domTitle = new OxTagTitle($this->domHead);
	    $this->domCss = new OxCss($this->domHead);
		$this->domBody = new OxTagBody($this->domHtml);
		$this->domJs = new OxJs($this->domHtml);
	}
	
	function addToTitle($text){
		$this->domTitle->addText($text);
	}
	function addCssFile($file){ 
		$this->domCss->addCssFile($file);
	}
	function addBrowserIcon($icon = null){
		if($icon != null){
			$icon = new OxTagIcon($this->domHead, $icon);
		}
	}
	function makeJustJs(){
		$this->domJs = new OxJs($this);
		$this->loadJs();
	}
	function addJsFile($file){
		$this->domJs->addJsFile($file);
	}
	function addJsCommand($command){
		$this->domJs->addJsCommand($command);
	}
	function addAjaxCommand($sendUrl){
		print $this->domJs->addJsCommand("oxajax_ajaxExecute('$sendUrl')");
	}
	
 	function addOxAjax($sendUrl){
 		$this->domJs->addJsCommand('oxajax_ajaxExecute(' . OxString::getQ($sendUrl) . ');');
 	}
 	
 	function addJsFun($funcArgs){
		$jsFun = $this->getFun_main(func_get_args());
		$this->addJsCommand($jsFun);
	}
	function getFun_main($argList){
		$funName = array_shift($argList);
		$funName .= "("; 
		if(sizeof($argList) > 0)
		{
			foreach($argList as $funArg){
				$funName .= $funArg . ","; 
			}
			$funName = substr($funName, 0, strlen($funName) - 1); 
		}	
		$funName .= ")"; 
		return $funName; 
	}	
}