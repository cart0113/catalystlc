<?php
class OxDbColDef {
	public $index;
	public $indexUnique;
	function __construct($index = false, $indexUnique = false){
		$this->index = $index;
		$this->indexUnique = $indexUnique;
	}
	function doIndex(){
		return $this->index; 
	}
	function isIndexUnique(){
		return $this->indexUnique;
	}
	function getColHandler($name){
		return new OxDbColHandler($name);
	}
}
class OxDbColDef_IntPrimaryKey extends OxDbColDef {
	function __construct(){
		parent::__construct(true);
	}
	function getType(){
		return "INTEGER PRIMARY KEY";
	} 
}
class OxDbColDef_TextPrimaryKey extends OxDbColDef {
	function __construct(){
		parent::__construct(true);
	}
	function getType(){
		return "TEXT PRIMARY KEY";
	} 
}
class OxDbColDef_Text extends OxDbColDef {
	function getType(){
		return "TEXT";
	}
}
class OxDbColDef_Int extends OxDbColDef {
	function getType(){
		return "INT";
	}
}
//class OxDbColDef {
//	public $name; 
//	public $index;
//	public $primaryKey; 
//	function __construct($cols, $name, $index = false, $primaryKey = false){
//		// This is so you can pass in objects as names to enforce correct naming. 
//		if(is_object($name)){
//			$name = get_class($name);
//		}
//		$this->name = $name; 
//		$this->index = $index;
//		$this->primaryKey = $primaryKey;
//		$cols[$this->getName()] = $this;
//	}
//	function getName($name = ""){
//		return $this->name . $name;
//	}
//	function getType(){
//		$type = $this->getType();
//		if($this->primaryKey){
//			$type .= " PRIMARY KEY";
//		}
//		return $type;
//	}
//	function getType(){
//		return "TEXT";
//	}
//	function doIndex(){
//		return $this->index; 
//	}
//}
//
//class OxDbColDef_IntPrimaryKey extends OxDbColDef {
//	function getType(){
//		return "INTEGER PRIMARY KEY";
//	} 
//}
//class OxDbColDef_TextPrimaryKey extends OxDbColDef {
//	function getType(){
//		return "TEXT PRIMARY KEY";
//	} 
//}
//
//class OxDbColDef_XID extends OxDbColDef {
//	function getName($name = ""){
//		return parent::getName("_OXC_XID" . $name);
//	}
//}
//class OxDbColDef_XID_DATA extends OxDbColDef_XID {
//	function getName($name = ""){
//		return parent::getName("_DATA" . $name);
//	}
//}
//class OxDbColDef_XID_MASTER extends OxDbColDef_XID {
//	function getName(){
//		return parent::getName("_MASTER" . $name);
//	}
//}
//
//class OxDbColDef_Int extends OxDbColDef {
//	function getType(){
//		return "INTEGER";
//	} 
//}
//
//class OxDbColDef_UnixTime extends OxDbColDef_Int {}
//
//class OxDbColDef_Float extends OxDbColDef {}
//
//class OxDbColDef_Binary extends OxDbColDef {
//	function getType(){
//		return "BINARY";
//	}
//}
//class OxDbColDef_Subclass extends OxDbColDef_Binary {
//	function getName($name = ""){
//		return parent::getName("_OXC_SC" . $name);
//	}
//}
//
//class OxDbColDef_Text extends OxDbColDef {}
//class OxDbColDef_Username extends OxDbColDef_Text {}
//class OxDbColDef_Password extends OxDbColDef_Text {}
//class OxDbColDef_City extends OxDbColDef_Text {}
//class OxDbColDef_State extends OxDbColDef_Text {}
//class OxDbColDef_ZIP extends OxDbColDef_Text {}
//class OxDbColDef_Geocode extends OxDbColDef_Text {}
//
//class OxDbColDef_Blob extends OxDbColDef {}
//class OxDbColDef_Blog extends OxDbColDef_Blob {}
//class OxDbColDef_Picture extends OxDbColDef_Blob {}
//class OxDbColDef_Video extends OxDbColDef_Blob {}
//


?>