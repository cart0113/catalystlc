<?php 
class OxTagForm extends OxTag {
	function __construct($parent = null, $tagId = null, $tagClass = null, $processUrl = ".", $method = 'POST'){
		OxTag::__construct($parent, "form", $tagId, $tagClass);
		$this->setAtt("action", $processUrl);
		$this->setAtt("method", $method);
	}
}

class OxTagInput extends OxTag {
	function __construct($parent = null, $tagType, $inputType, $tagId = null, $tagClass = null, $name, $value = null, $text = null){
		OxTag::__construct($parent, $tagType, $tagId, $tagClass, $text, true, false);
		if($inputType){
			$this->setAtt('type', $inputType);
		}
		$this->setAtt('name', $name);	
		if($value){
			$this->setAtt('value', $value);
		}
	}
	function onChangeSubmit(){
		$this->setAtt("onchange", "form.submit()");
	}
	function onChange($command){
		$this->setAtt("onchange", $command);
	}
	function onMouseup($command){
		$this->setAtt("onmouseup", $command);
	}
	function onChange_Ajax($url){
		$this->onChange("oxajax_ajaxExecute('$url')");
	}
	function onMouseup_Ajax($url){
		$this->onMouseup("oxajax_ajaxExecute('$url')");
	}
}

class OxTagInput_Hidden extends OxTagInput {
	function __construct($parent = null, $tagId = null, $tagClass = null, $name, $value){
		parent::__construct($parent, 'input', 'hidden', $tagId, $tagClass, $name, $value);
	}
}

class OxTagInput_Button extends OxTagInput {
	function __construct($parent = null, $tagId = null, $tagClass = null, $text = 'submit', $type = 'submit'){
		parent::__construct($parent, 'button', $type, $tagId, $tagClass, null, null, $text); 
	}
}

class OxTagInput_Text extends OxTagInput {
	function __construct($parent = null, $tagId = null, $tagClass = null, $name, $value = null){
		parent::__construct($parent, 'input', 'text', $tagId, $tagClass, $name, $value);
	}
}
class OxTagInput_Password extends OxTagInput {
	function __construct($parent = null, $tagId = null, $tagClass = null, $name, $value = null){
		parent::__construct($parent, 'input', 'password', $tagId, $tagClass, $name, $value);
	}
}

class OxTagInput_TextArea extends OxTagInput {
	function __construct($parent = null, $tagId = null, $tagClass = null, $name, $value = null){
		parent::__construct($parent, 'textarea', null, $tagId, $tagClass, $name, null, $value);
	}
}

class OxTagInput_Select extends OxTagInput {
	function __construct($parent = null, $tagId = null, $tagClass = null, $name, $value = '0', $choices, $text = null, $left = false){
		if($text){
			$table = new OxTagTable($parent);
			$row = new OxTagRow($table);
			$cell = new OxTagCell($row, null, $class, $text);
			$cell->setStyle("padding-top: 2px; padding-right: 10px; font-size: 14px; color: #555555;");
			$parent = new OxTagCell($row);
		}
		parent::__construct($parent, 'select', null, $tagId, $tagClass, $name, $value);
		foreach($choices as $choice){
			// this sets the value to the same as the display. 
			if(!is_array($choice)){
				$choice = array($choice, $choice);
			}
			$domValue = new OxTag($this, "option", null, null, $choice[0]);
			$domValue->setAtt("value", $choice[1]);
			if($value == $choice[1]){
				$domValue->setAtt("selected", "yes");
			}
			if($choice[2]){
				$domValue->setAtt("class", $choice[2]);
			}
		}
	}
	public static function yesNoChoices(){
		$choices[] = array("No", "0");
		$choices[] = array("Yes", "1");
		return $choices; 
	}
}

class OxTagInput_Checkbox extends OxTagInput {
	function __construct($parent = null, $tagId = null, $tagClass = null, $name, $check = false, $text = null, $left = true){
		if($text){
			$table = new OxTagTable($parent);
			$row = new OxTagRow($table);
			$parent = new OxTagCell($row);
			$parent->setStyle("text-align: left; padding: 0px; width: 25px;");
		}
		parent::__construct($parent, 'input', 'checkbox', $tagId, $tagClass, $name);
		$this->one();
		$this->setStyle("width: 25px; padding: 0px; margin-left: 0px");
		$this->one();
		if($check){
			$this->setEnd('checked');
		}
		if($text){
			$parent = new OxTagCell($row, null, "limitCell", $text);
			$parent->setStyle("padding-left: 5px; padding-bottom: 5px;");
		}
	}
}

class OxTagInput_Radio extends OxTagInput {
	function __construct($parent = null, $tagId = null, $tagClass = null, $name, $value, $checked = false, $text = null, $align = null) {
		if($text){
			$table = new OxTagTable($parent);
			$row = new OxTagRow($table);
			$cell = new OxTagCell($row, null, $tagClass, $text);
			$parent = new OxTagCell($row, null, 'input_radio');	
			if($_SESSION['OX_VISITOR_INFO']['BROWSER'] == 'Firefox'){
				$parent->addStyle("padding-top: 5px;");
			}
		}
		parent::__construct($parent, 'input', 'radio', $tagId, $tagClass, $name, $value);
		$this->one();
		$this->setStyle("width: auto;");
		if($checked){
			$this->setEnd('checked');
		}
		if($align){
			$this->setAtt("align", $align);
		}
	}
}

class OxTagInput_RadioField extends OxTagInput {
	function __construct($parent = null, $tagId = null, $tagClass = null, $name, $align = null, $choices, $leftRight = true) {
		if($leftRight){
			$table = new OxTagTable($parent);
			$row = new OxTagRow($table);
		}
		foreach($choices as $choice){
			if($leftRight){
				$parent = new OxTagCell($row);
				$parent->setStyle("padding-right: 25px;");
			}
			$radio = new OxTagInput_Radio($parent, $tagId, $tagClass, $name, $choice[1], $choice[2], $choice[0], $align);
		}
	}
}
