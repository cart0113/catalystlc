<?php
class OxFormBlock extends OxTagDiv {
	public $domTitle; 
	public $blockId; 
	// note, domForm and domBlock are passed through from the other side. 
	function __construct($parent = null, $id = null, $class = null, $text = null){
		$n = OxPage::globalCounter('OXFORMBLOCK_NUMBER');
		$idFull = "OXFORMBLOCK_" . $n;
		if($id != null){
			$idFull = $idFull . "_" . $id; 
		}
		$div = new OxTagDiv($parent, null, "OxFormBlock_container");
		$div = new OxTagDiv($div, $idFull, "OxFormBlock");
		$this->blockId = $div->getId();
		$table = new OxTagTable($div, $id, $class);
		$row = new OxTagRow($table);
		$this->domTitle = new OxTagCell($row, $id, "OxFormBlock_text", $text);
		parent::__construct($div, $id);
		$this->domBlock = $this;
	}
}

/////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////
////////  INPUT BLOCKS
/////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////

class OxFormBlockInput extends OxTagDiv {
	public $name; 
	public $value; 
	public $input; 
	
	function __construct($parent, $name = null, $isRequired = false){
		parent::__construct($parent);
		$this->name = $name;
		$this->value = $_SESSION['ox_forms'][$this->domForm->getId()][$this->name]['value'];
		$_SESSION['ox_forms'][$this->domForm->getId()][$this->name]['required'] = $isRequired;
	}
	
	function output(){
		if($this->domBlock != null){
			$id = $this->domBlock->blockId;	
			//$this->addAtt("onclick", "oxjs_makeBlue('$id')");
			if(is_array($this->input)){
				foreach($this->input as $input){
					$input->setAtt("onfocus", "oxjs_makeBlue('$id')");
				}
			}
			else {
				$this->input->setAtt("onfocus", "oxjs_makeBlue('$id')");
			}
		}
		return parent::output();
	}
}


// These are self-standing blocks. 
class OxFormBlockInput_Text extends OxFormBlockInput {
	function __construct($parent = null, $id = null, $class = null, $text, $name, $isRequired = false){
		$block = new OxFormBlock($parent, $id, $class, $text);
		parent::__construct($block, $name, $isRequired);
		if($isRequired && $this->value == null){
			new OxTagDiv($block->domTitle, null, 'ox_gui_required', '*');
		}
		$this->input = new OxTagInput_Text($this, $id, $class, $this->name, $this->value);
	}
}

class OxFormBlockInput_TextArea extends OxFormBlockInput {
	function __construct($parent = null, $id = null, $class = null, $text, $name, $isRequired = false){
		$block = new OxFormBlock($parent, $id, $class, $text);
		parent::__construct($block, $name, $isRequired);
		if($isRequired && $this->value == null){
			new OxTagDiv($block->domTitle, null, 'ox_gui_required', '*');
		}
		$this->input = new OxTagInput_TextArea($this, $id, $class, $this->name, $this->value);
	}
}


class OxFormBlockInput_Select extends OxFormBlockInput {
	function __construct($parent = null, $id = null, $class = null, $text, $name, $isRequired = false, $choices){
		$block = new OxFormBlock($parent, $id, $class, $text);
		parent::__construct($block, $name, $isRequired);
		if($isRequired && $this->value == null){
			new OxTagDiv($block->domTitle, null, 'ox_gui_required', '*');
		}
		$this->input = new OxTagInput_Select($this, $id, $class, $this->name, $this->value, $choices);
	}
}

/// Sub Blocks 
/////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////
////////  OxFormBlock_Row
/////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////

class OxFormBlock_Row extends OxFormBlock {
	public $table; 
	public $row;
	public $lastCell;
	function __construct($parent = null, $id = null, $class = null, $text = null){
		parent::__construct($parent, $id, $class, $text);
		$this->addRow();
	}
	function makeCell($width){
		$cell = new OxTagCell($this->row);
		$cell->width($width . "%");
		if($this->lastCell){
			$this->lastCell->padding("20px", "right");
		}
		$this->lastCell = $cell;
		return $cell;
	}
	function addText($text){	
		$cell = new OxTagCell($this->row, null, null, $text);
		$cell->setStyle("padding-right: 12px;");
	}
	function fillSpace($width = 100){
		$cell = new OxTagCell($this->row);
		$cell->setStyle("width: $width%;");
	}
	function addRow(){
		$this->table = new OxTagTable($this);
		$this->table->width("99%");
		$this->row = new OxTagRow($this->table);
		// Destroy last cell pointer so no padding is added. 
		$this->lastCell = null;
	}
	function addInput($text, $name, $isRequired = false, $width,  $type = null){
		$input = new OxFormBlockInput_UnderText($this->makeCell($width), null, null, $text, $name, $isRequired, $type); 
	}
	function addSelect($text, $name, $isRequired = false, $width, $choices, $value = null){
		$input = new OxFormBlockInput_UnderSelect($this->makeCell($width), null, null, $text, $name, $isRequired, $choices, $value = null);
	}
}

class OxFormBlockInput_Under extends OxFormBlockInput {
	function __construct($parent, $id = null, $class = null, $text = null, $name = null, $isRequired = false){
		parent::__construct($parent, $name, $isRequired);
		$this->input = new OxTagDiv($this);
		$text = new OxTagDiv($this, null, 'OxFormInput_TextUnder', $text);
		if($isRequired && $this->value == null){
			new OxTagDiv($text, null, 'ox_gui_required', '*');
		}
	}
}

class OxFormBlockInput_UnderText extends OxFormBlockInput_Under {
	function __construct($parent, $id = null, $class = null, $text = null, $name = null, $isRequired = false){
		parent::__construct($parent, $id, $class, $text, $name, $isRequired);
		$this->input = new OxTagInput_Text($this->input, $id, $class, $this->name, $this->value);
	}
}

class OxFormBlockInput_UnderSelect extends OxFormBlockInput_Under {
	function __construct($parent, $id = null, $class = null, $text = null, $name = null, $isRequired = false, $choices){
		parent::__construct($parent, $id, $class, $text, $name, $isRequired);
		$this->input = new OxTagInput_Select($this->input, $id, $class, $this->name, $this->value, $choices);
	}
}


class OxFormBlockInput_Left extends OxFormBlockInput {
	public $text; 
	public $row;
	function __construct($parent = null, $id = null, $class = null, $text = null, $name = null, $isRequired = false){
		parent::__construct($parent, $name, $isRequired);
		$this->setStyle("padding-top: 2px; padding-bottom: 3px;");
		$table = new OxTagTable($this);
		$this->row = new OxTagRow($table);
		$this->text = new OxTagCell($this->row, $id, $class, $text);
		$this->text->setStyle("padding-right: 10px;");
		if($isRequired && $this->value == null){
			$req = new OxTagDiv($this->text, null, 'ox_gui_required', '*');
		}
	}
}
class OxFormBlockInput_RadioLeft extends OxFormBlockInput_Left {
	function __construct($parent, $id = null, $class = null, $text = null, $name = null, $isRequired = false, $choices){
		parent::__construct($parent, $id, $class, $text, $name, $isRequired, $choices);
		//$this->input = new OxTagInput_RadioField($this->input, null, null, $name, null, $choices);
		foreach($choices as $choice){
			$cell= new OxTagCell($this->row);
			$cell->setStyle("padding-right: 35px;");
			$this->input[] = new OxTagInput_Radio($cell, $id, $class, $name, $choice[1], $choice[2], $choice[0], $align);
		}
	}
}



//      A DATE EXAMPLE;
//		$form->setValue("M", "12");
//		$block->addInput("M", "M", true, 5);
//		$block->addText("/");
//		
//		$form->setValue("D", "5");
//		$block->addInput("D", "D", true, 5);
//		$block->addText("/");
//		
//		$form->setValue("Y", "2006");
//		$block->addInput("Y", "Y", true, 10);

?>