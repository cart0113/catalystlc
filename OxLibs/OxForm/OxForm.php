<?php
class OxForm extends OxTagDiv {
	//$id is the same as $formName
	//$id kept to be consistent with OxDomElements
	public $form; 
	public $formId; 
	function __construct(OxDomElement $parent, $id = null, $class = 'OxForm_medium_w',  $text = null, $button = 'submit', $cancel = true, $processUrl = './', $cancelUrl = null, $method = 'POST') {
		$div = new OxTagDiv($parent, $id, $class);
		$title = new OxTagDiv($div, null, 'header1', $text);
		$this->form = new OxTagForm($div, $id, null, $processUrl, $method);
		// copy pointer for later use. 
		$this->form->domForm = $this->form;
		OxTagDiv::__construct($this->form);
		$this->formId = $this->form->id; 
		$this->addHidden('ox_form_id', $this->form->id);
		$div = new OxTagDiv($this->form);
		$div->addStyle("padding-top: 10px; padding-right: 5px;");
		if($button){
			$button = new OxTagInput_Button($div, null, 'ox_gui_button', $button);	
			if($cancel){
				$span= new OxTagSpan($div, null, null, "&nbsp;&nbsp;or&nbsp;&nbsp;");
				$span->setStyle("font-size: 13px; font-weight: bold;");
				if($cancel){
					if($cancelUrl){
						$ref = new OxTagRef($span, null, null, "cancel", $cancelUrl);
					}
					else {
						$ref = new OxTagRef($span, null, null, "cancel", "./?ox_action=form_cancel&id=" . $this->formId);
					}
				}
				$ref->setStyle("font-size: 14px; color: #6666FF");
			}
		}
	}
	function setValue($key, $value){
		if(!isset($_SESSION['ox_forms'][$this->formId][$key]['value'])){
			$_SESSION['ox_forms'][$this->formId][$key]['value'] = $value; 
		}
	}
	function addOxAction($oxAction = 'form_submit_standard'){
		$this->addHidden('ox_action', $oxAction);
	}
	function addCompleteUrl($url = null){
		if($url == null){
			$url = OxPage::getLastPage();
		}
		$this->addHidden('ox_form_complete_url', $url);
	}
	function addDataHandler_Page($function){
		$this->addHidden("ox_data_handler_page", $function);
	}
	
	function setName($name){
		$this->domForm->setAtt("name", $name);
	}
	
	function loadFormValues($values){
		foreach($values as $key => $value){
			$_SESSION['ox_forms'][$this->formId][$key]['value'] = $value;
		}
	}
	public static function unsetForm($key){
		unset($_SESSION['ox_forms'][$key]);
	}
	public static function processOxData(OxDomPage $page, $oxData){
		$formName = $oxData['ox_form_id'];
		// Perform simple 'is required' validation and stores form values. 
		$okay = true;
		foreach($oxData as $key => $value){
			if($value == null && $_SESSION['ox_forms'][$formName][$key]['required']){
				$okay = false; 
			}
			$_SESSION['ox_forms'][$formName][$key]['value'] = $value; 
		}
		
		if($okay){
			unset($_SESSION['ox_forms'][$formName]);
			$completeUrl = $oxData['ox_form_complete_url'];
			unset($oxData['ox_form_complete_url']);
			$inHandle = false;
			foreach($oxData as $key => $value){
				if($key == "ox_data_handler_page"){
					unset($oxData['ox_data_handler_page']);
					$page->$value($oxData);
				}
				elseif(substr($key, 0, 23) == "ox_data_handler_class_0"){	
					$inHandle = true;
					$class = explode("?", $value);
					$method = $class[1];
					$class = $class[0];
					$sendData = array();
				}
				elseif(substr($key, 0, 23) == "ox_data_handler_class_1"){
					$handler = new $class();
					$handler->$method($sendData);
					$inHandle = false; 
				}
				elseif($inHandle){
					$sendData[$key] = $value;
				}
				elseif($key == "ox_data_handler_class"){
					$class = explode("?", $value);
					$method = $class[1];
					$class = $class[0];
					$handler = new $class();
					unset($this->oxData[$key]);
					$handler->$method($this->oxData);
				}
			}
			if($completeUrl){
				header("Location: $completeUrl");
			}
			exit();
		}
		else {
			header("Location: ./");
		}
	}
	public static function completeHeader($oxData){
		$where = $oxData['ox_form_complete_url'];
		header("Location: $where");
		exit();
	}
}

class OxFormHandler extends OxDomElement {
	function __construct($parent, $handlerClass){
		$hn = OxPage::globalCounter('OX_FORM_HANDLER');
		new OxTagInput_Hidden($parent, null, null, "ox_data_handler_class_0_$hn", $handlerClass);
		OxDomElement::__construct($parent);
		new OxTagInput_Hidden($parent, null, null, "ox_data_handler_class_1_$hn", "end_handler");
	}
}

