<?php

class OxDbQ  {
	public $col; 
	public $value; 
	function __construct($col, $value = null){
		// By reference so rows can update themselves!
		$this->col = $col;
		$this->value = $value;
	}
	function getQ(){
	}
}

class OxDbQ_Col extends OxDbQ {
	function getQ() {
		if($this->value){
			return " $this->col = '$this->value' ";
		}
		else {
			return " $this->col ";
		}
	}
	
}

class OxDbQ_Where extends OxDbQ {
	public $cond; 
	public $and; 
	function __construct($col, $value, $cond = '=', $and = true){
		parent::__construct($col);
		$this->value = $value; 
		$this->cond = $cond;
		$this->and = $and;  
	}
	function getQ(){
		$qs = $this->col . " " . $this->cond . " " . "'" . $this->value . "'";
		if($this->and){
			return $qs .= " AND ";
		}
		else {
			return $qs .= " OR  ";
		}
	}
}

class OxDbQ_In extends OxDbQ {
	public $values;
	function __construct($col, $values, $and = true){
		parent::__construct($col);
	}
}

//class OxDbQ_Like extends OxDbQ {
//	public $value;
//	function __construct($value, $and = true){
//		parent::__construct($and);
//		$this->value = $value; 
//	}
//}

class OxDbQ_Order extends OxDbQ {
	public $asc; 
	function __construct($col, $asc = true){
		parent::__construct($col);
		$this->asc = $asc;
	}
	function getQ(){
		$asc = ' DESC ';
		if($this->asc){
			$asc = ' ASC ';
		}
		return $this->col . $asc; 
	}
}