<?php
///////////////////////////////////////////
///////////////////////////////////////////
///////////////////////////////////////////
///////////////////////////////////////////
////  OxBlockRef
///////////////////////////////////////////
////  This is a simple image that is also
////  a href link. 
///////////////////////////////////////////
///////////////////////////////////////////
///////////////////////////////////////////
class OxBlockRef_Master extends OxTagDiv {
	function __construct($parent = null, $id = null, $class = null, $text = null, $href = null, $js = false, $altRef = null){
		parent::__construct($parent, $id, $class);
		new OxTagRef_Master($this, $id, $class, $text, $href, $js, $altRef); 
	}
}
class OxBlockRef extends OxBlockRef_Master {
	function __construct($parent = null, $id = null, $class = null, $text = null, $href = null){
		parent::__construct($parent, $id, $class, $text, $href);
	}
}


///////////////////////////////////////////
///////////////////////////////////////////
///////////////////////////////////////////
///////////////////////////////////////////
////  OxBlockImageRef
///////////////////////////////////////////
////  This is a simple image that is also
////  a href link. 
///////////////////////////////////////////
///////////////////////////////////////////
///////////////////////////////////////////
class OxBlockImageRef_Master extends OxTagRef_Master {
	function __construct($parent = null, $id = null, $class = null, $src = null, $href = null, $ajax = false, $altRef = null, $transparentPng = false, $blank = "blank.gif"){
		parent::__construct($parent, $id, $class, null, $href, $ajax, $altRef);
		new OxTagImage_Master($this, $id, $class, $src, $transparentPng, $blank); 
	}
}
class OxBlockImageRef extends OxBlockImageRef_Master {
	function __construct($parent = null, $id = null, $class = null, $src = null, $href = null){
		parent::__construct($parent, $id, $class, $src, $href);
	}
}
class OxBlockImageRef_TransparentPng extends OxBlockImageRef_Master {
	function __construct($parent = null, $id = null, $class = null, $src = null, $blank = "blank.gif", $href = null){
		parent::__construct($parent, $id, $class, $src, $href, false, null, true, $blank);
	}
}
class OxBlockImageRef_Js extends OxBlockImageRef_Master {
	function __construct($parent = null, $id = null, $class = null, $src = null, $href = null, $altRef = null){
		parent::__construct($parent, $id, $class, $src, $href, 'js', $altRef);
	}
}
class OxBlockImageRef_Ajax extends OxBlockImageRef_Master {
	function __construct($parent = null, $id = null, $class = null, $src = null, $href = null, $altRef = null){
		parent::__construct($parent, $id, $class, $src, $href, 'ajax', $altRef);
	}
}
class OxBlockImageRef_Js_TransparentPng extends OxBlockImageRef_Master {
	function __construct($parent = null, $id = null, $class = null, $src = null, $blank = "blank.gif", $href = null, $altRef = null){
		parent::__construct($parent, $id, $class, $src, $href, 'js', $altRef, true, $blank);
	}
}
class OxBlockImageRef_Ajax_TransparentPng extends OxBlockImageRef_Master {
	function __construct($parent = null, $id = null, $class = null, $src = null, $blank = "blank.gif", $href = null, $altRef = null){
		parent::__construct($parent, $id, $class, $src, $href, 'ajax', $altRef, true, $blank);
	}
}
///////////////////////////////////////////
///////////////////////////////////////////
///////////////////////////////////////////
///////////////////////////////////////////
////  OxBlockRow
///////////////////////////////////////////
////  A 'quick' table row. 
///////////////////////////////////////////
///////////////////////////////////////////
///////////////////////////////////////////
class OxBlockRow extends OxTagRow {
	function __construct($parent, $id = null, $class = null){
		$table = new OxTagTable($parent, $id, $class);
		OxTagRow::__construct($table, $id, $class);
	}
	function addElement($element){
		$td = new OxTagCell();
		$td->addElement($element);
		parent::addElement($td);
	}
}
///////////////////////////////////////////
///////////////////////////////////////////
///////////////////////////////////////////
///////////////////////////////////////////
////  OxBlockHoverButton
///////////////////////////////////////////
////  Image hrefs that change when you
////  hover over them. 
///////////////////////////////////////////
///////////////////////////////////////////
///////////////////////////////////////////
class OxBlockHoverButton_Master extends OxTagDiv {
	function __construct($parent, $id = null, $class = null, $name, $on = 'on', $ref = ".", $ajax = false, $altRef = null, $type = 'gif', $transparentPng = false){
		parent::__construct($parent, $id, $class);
		$name_off = $name . "_off.$type";
		$name_on = $name . "_on.$type";
		if($on == "on"){
			$image = new OxTagImage_Master($parent, null, null, $name_on, $transparentPng);
		}
		if($on == "off"){
			//$jsId = "HB_HOVER_$id$name"; 
			$a = new OxTagRef_Master($this, null, null, null, $ref, $ajax, $altRef);
			$imageOff = new OxTagImage_Master($a, $jsId, null, $name_off, $transparentPng);
			//$jsId = $imageOff->getId(); // adds OXIMG_ prefix
			if($imageOff->tpie == false){
				$imageOff->setAtt("onmouseover", "this.src='$name_on'");
				$imageOff->setAtt("onmouseout", "this.src='$name_off'");
			}
			else {
				$imageOff->setAtt("onmouseover", "getFilter(this, '$name_on')");
				$imageOff->setAtt("onmouseout", "getFilter(this, '$name_off')");
			}
		}
	}
}
class OxBlockHoverButton extends OxBlockHoverButton_Master {
	function __construct($parent, $id = null, $class = null, $name, $on = 'on', $ref = "."){
		parent::__construct($parent, $id, $class, $name, $on, $ref);
	}
}
class OxBlockHoverButton_Js extends OxBlockHoverButton_Master {
	function __construct($parent, $id = null, $class = null, $name, $on = 'on', $ref = null, $altRef = null){
		parent::__construct($parent, $id, $class, $name, $on, $ref, 'js', $altRef);
	}
}
class OxBlockHoverButton_Ajax extends OxBlockHoverButton_Master {
	function __construct($parent, $id = null, $class = null, $name, $on = 'on', $ref = ".", $altRef = null){
		parent::__construct($parent, $id, $class, $name, $on, $ref, 'ajax', $altRef);
	}
}
class OxBlockHoverButton_TransparentPng extends OxBlockHoverButton_Master {
	function __construct($parent, $id = null, $class = null, $name, $on = 'on', $ref = "."){
		parent::__construct($parent, $id, $class, $name, $on, $ref, false, null, 'png', true);
	}
}
class OxBlockHoverButton_Js_TransparentPng extends OxBlockHoverButton_Master {
	function __construct($parent, $id = null, $class = null, $name, $on = 'on', $ref = null, $altRef = null){
		parent::__construct($parent, $id, $class, $name, $on, $ref, 'js', $altRef, 'png', true);
	}
}
class OxBlockHoverButton_Ajax_TransparentPng extends OxBlockHoverButton_Master {
	function __construct($parent, $id = null, $class = null, $name, $on = 'on', $ref = ".", $altRef = null){
		parent::__construct($parent, $id, $class, $name, $on, $ref, 'ajax', $altRef, 'png', true);
	}
}

///////////////////////////////////////////
///////////////////////////////////////////
///////////////////////////////////////////
///////////////////////////////////////////
////  OxBlockRefList
///////////////////////////////////////////
////  Image hrefs that change when you
////  hover over them. 
///////////////////////////////////////////
///////////////////////////////////////////
///////////////////////////////////////////
class OxBlockRefList_Master extends OxTagDiv {
	function __construct($parent = null, $id = null, $class = null, $text = null){
		OxTagDiv::__construct($parent, $id, $class, $text);
	}
	function addRefs($refs, $js = false){
		for($i = 0; $i < sizeof($refs); $i = $i+2){
			$this->addText(" | ");
			new OxTagRef_Master($this, $this->getId(), $this->getClass(), $refs[$i], $refs[$i+1], $js);
		}
	}
	function addRef($ref0, $ref1, $js = false, $id = null){
		$this->addText("&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;");
		if($id == null){
			$id = $this->getId(); 
		}
		new OxTagRef_Master($this, $id, "lc_mid_ref", $ref0, $ref1, $js);
	}
}
class OxBlockRefList extends OxBlockRefList_Master {
	function addRefs(){
		parent::addRefs(func_get_args(), false);
	}
}
class OxBlockRefList_Js extends OxBlockRefList_Master {
	function addRefs(){
		parent::addRefs(func_get_args(), 'js');
	}
}
class OxBlockRefList_Ajax extends OxBlockRefList_Master {
	function addRefs(){
		parent::addRefs(func_get_args(), 'ajax');
	}
}

// This is like a block area with side tags 
//class OxBlockSideList_Master extends OxTagCell {
//	public $cell1; 
//	function __construct($parent, $id = null, $class = null){
//		$table = new OxTagTable($parent, $id, "$class ox_split_A");
//		$row = new OxTagRow($table);
//		parent::__construct($row, null, 'ox_split_A_0');
//		$this->cell1 = new OxTagCell($row, null, 'ox_split_A_1');
//	}
//	function addRefs($refs, $type = null){
//		$this->div->addStyle("display: table-row;");
//		$this->width("85%");
//		$this->cell1->width("15%");
//		$this->cell1->addStyle("padding-top: 10px; padding-left: 5px;");
//		$rightDiv = new OxTagDiv($this->cell1);
//		$rightDiv->addStyle("padding-top: 3px; padding-left: 15px; width: 10px; text-align: right");
//		for($i = 0; $i < sizeof($refs); $i = $i+2){
//			$r = new OxTagDiv($rightDiv, null, 'OxBlockSideList_Master_ref');
//			$r = new OxTagRef($r, null, null, $refs[$i], $refs[$i+1]);
//		}
//	}
//}
//class OxBlockSideList extends OxBlockSideList_Master {
//	function addRefs(){
//		parent::addRefs(func_get_args());
//	}
//}
//class OxBlockSideList_Js extends OxBlockSideList_Master {
//	function addRefs(){
//		parent::addRefs(func_get_args(), 'js');
//	}
//}
//class OxBlockSideList_Ajax extends OxBlockSideList_Master {
//	function addRefs(){
//		parent::addRefs(func_get_args(), 'ajax');
//	}
//}


// This is a block area that highlights when you go over it 
class OxBlockHoverRef_Master extends OxTagDiv {
	public $t1; 
	public $t2; 
	public $t3;
	function __construct($parent = null, $id = null, $class = null, $on = false, 
												$text1 = null,
												$text2 = null, 
												$ref, 
												$js = false, 
												$altRef = null){
		if($class == null){
			$class = 'ox_blue_ref';
		}
		parent::__construct($parent, null, $class . '_c');
		if($on){
			$div = new OxTagDiv($this, $id, $class . "_on");	
		}
		else {
			$div = new OxTagDiv($this, $id, $class);
			$div->setAtt("onmouseover", "this.className='" . $class . "_on'");
			$div->setAtt("onmouseout", "this.className='" . $class . "'"); 
		}
		$refTag = new OxTagRef_Master($div, $id, $class, null, $ref, $js, $altRef);
		$this->t1 = new OxTagDiv($refTag, null, $class . '_t1', $text1);
		$refTag = new OxTagRef_Master($div, $id, $class, null, $ref, $js, $altRef);
		$this->t2 = new OxTagDiv($refTag, null, $class . '_t2', $text2);
		$refTag = new OxTagRef_Master($div, $id, $class, null, $ref, $js, $altRef);
		$this->t3 = new OxTagDiv($refTag, null, $class . '_t3', $text3);
	}
}

class OxBlockHoverRef extends OxBlockHoverRef_Master {
	function __construct($parent = null, $id = null, $class = null, $on = false, $text1 = null, $text2 = null, $ref){
		parent::__construct($parent, $id, $class, $on, $text1, $text2, $ref);												
	}
}
class OxBlockHoverRef_Js extends OxBlockHoverRef_Master {}
class OxBlockHoverRef_Ajax extends OxBlockHoverRef_Master {
	function __construct($parent = null, $id = null, $class = null, $on = false, $text1 = null, $text2 = null, $ref, $altRef = null){
		parent::__construct($parent, $id, $class, $on, $text1, $text2, $ref, 'ajax', $altRef);												
	}
}

?>