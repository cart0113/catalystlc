<?php
//require_once("OxDbColHandler.php");
class OxDbRow {
	public $OXDB_DESC = "A Generic OxDbRow Table (You Should Fill Out A Description).";
	public $db; 
	public $dbTableName;
	private $colList; 	
	// start of columns. 
	public $id; 
	public $col_ox_isHidden;
	function __construct(OxDbSQLite $db, $row = null, $stopClass){
		$this->db = $db; 
		$this->defineTable($stopClass);
		if($row != null){
			if(!is_array($row)){
				$this->id = $row;
			}
			else {
				foreach($row as $key => $value){
					$this->$key = $value; 
				}
			}
		}
	}
	function defineTable($stopClass){
		$class = get_class($this);
		if(isset($GLOBALS['OXDBROW'][$this->dbTableName])){
			$this->dbTableName = $GLOBALS['OXDBROW'][$class]['DBTABLENAME'];
			$this->colList = $GLOBALS['OXDBROW'][$class]['COLLIST'];
		}
		else {
			$run = true; 
			while($run){
				if(get_parent_class($class) == $stopClass){
					$this->dbTableName = $class;
					$run = false;
				}
				else {
					$class = get_parent_class($class);
				}
			}
			$GLOBALS['OXDBROW'][$class]['DBTABLENAME'] = $this->dbTableName;
			$cols = get_object_vars($this);
			unset($cols['OXDB_DESC']);
			unset($cols['dbTableName']);
			unset($cols['db']);
			unset($cols['id']);
			$this->colList[] = 'id';
			foreach(get_object_vars($this) as $key => $value){
				if(substr($key, 0, 4) == 'col_'){
					$this->colList[] = $key;
				}
			}
			$GLOBALS['OXDBROW'][$class]['COLLIST'] = $this->colList;
		}
	}	
	function clearCols(){
		foreach($this->colList as $col){
			$this->$col = null;
		}
	}
	function getDesc(){
		return $this->OXDB_DESC;
	}
	/// This is used for form processing. 
	function fillColumnNames() {
		foreach($this->colList as $col){
			$this->$col= $col;
		}
	}
	/////////////////////////
	/////////////////////////
	/////////////////////////
	/////////////////////////
	/////////////////////////
	/// INSERT AND UPDATE
	/////////////////////////
	/////////////////////////
	/////////////////////////
	/////////////////////////
	/////////////////////////
	function updateById(){
		$cols = $this->getCurrentCols();
		unset($cols['id']);
		$this->db->updateRowById($this->dbTableName, $cols, $this->id);
	}
	function insert(){
		$row = $this->getCurrentCols();
		return $this->db->insertRow($this->dbTableName, $row);
	}
	function getCurrentCols(){
		$row = array(); 
		foreach($this->colList as $col){
			if($this->$col != null){
				$row[$col] = $this->$col;
			}
		}
		return $row;
	}
	/// delete
	function deleteById(){
		$this->db->query("DELETE FROM $this->dbTableName WHERE id='$this->id';");
	}	
	function deleteByCol($col, $value){
		$this->db->query("DELETE FROM $this->dbTableName WHERE $col='$value';");
	}
	function delete(){
		$row = $this->getCurrentCols();
		$this->db->deleteRowsByWhere($this->dbTableName, $row, $or);		
	}
	function deleteByWhereNotEqual($col, $notEquals){
		$qs = "DELETE FROM $this->dbTableName WHERE ";
		foreach($notEquals as $ne){
			$qs .= "$col <> '$ne' AND ";
		}
		$qs = substr($qs, 0, -4) . ";";
		$this->db->query($qs);
	}
	/// select 
	function selectAllRows($limit = null){
		$qs = "SELECT * FROM $this->dbTableName";
		if($limit){
			$qs .= " LIMIT $limit";
		}
		$qs .= ";";
		return $this->db->query($qs, get_class($this));
	}
	function selectAllCols($col = null, $limit = null){
		$qs = "SELECT $col FROM $this->dbTableName";
		if($limit){
			$qs .= " LIMIT $limit";
		}
		$qs .= ";";
		$result = $this->db->query($qs);
		while($result->valid()){
			$cols[] = $result->column($col);
			$result->next();
		}
		return $cols; 
	}
	function selectById(){}
	function updateByQ($cols, $wheres){
		$this->clearCols();
		$this->fillColumnNames();
		$qs = "UPDATE $this->dbTableName " . " SET " . $this->getColsQ($cols) . $this->getWhereQ($wheres) . ";";
		$this->db->query($qs);
	}
	function selectByQ($cols = null, $wheres = null, $orders = null, $limit = null){
		//$this->clearCols();
		//$this->fillColumnNames();
		$qs = 'SELECT ';
		if($cols == null){
			$cols = '*';
		}
		else {
			$cols = $this->getColsQ($cols);
		}
		$qs .= $cols;
		$qs .= " FROM $this->dbTableName " . $this->getWhereQ($wheres);
		if($orders){
			$qs .= "ORDER BY ";
			foreach($orders as $order){
				$qs .= $order->getQ();
			}
		}
		if($limit){
			$qs .= " LIMIT $limit ";
		}
		$qs .= ";";
		return $this->db->query($qs, $this->dbTableName);
	}
	function getColsQ($cols){
		if($cols){
			foreach($cols as $col) {
				$qs .= $col->getQ() . ',';
			}
			$qs = substr($qs, 0, -1);
		}
		return $qs;
	}
	function getWhereQ($wheres){
		if($wheres){
			$qs .= " WHERE ";
			foreach($wheres as $where){
				$qs .= $where->getQ();
			}
			$qs = substr($qs, 0, -4);
		}
		return $qs; 
	}
	
	
	/// straight to the database
	function updateRow($row){
		$this->db->updateRowById($this->dbTableName, $row, $this->id);
	}
	function insertRow($row){
		return $this->db->insertRow($this->dbTableName, $row);
	}
	function getRowById(){
	}
	function loadById(){
		$row = $this->db->query("SELECT * FROM $this->dbTableName WHERE id ='$this->id';");
		if($row->valid()){
			$row = $row->current(0);
			foreach($row as $key => $value){
				$this->$key = $value; 
			}
			return $row;
		}
		else {
			$this->clearCols();
			return false;
		}
	}
		
	/////////////////////////////////
	/////////////////////////////////
	/////////////////////////////////
	/////////////////////////////////
	/////////////////////////////////
	/////////////////////////////////
	/////////////////////////////////
	////  OxDbSQLite PASS THRUS
	/////////////////////////////////
	/////////////////////////////////
	/////////////////////////////////
	/////////////////////////////////
	/////////////////////////////////
	/////////////////////////////////
	
	function dropTable(){
		$this->db->dropTable($this->dbTableName);
	}

	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///    MAKE/PRINT TABLE
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	
	function makeTable($refill = true, $time = true, $user = true){
		if($this->db->doesTableExist($this->dbTableName) == false){
			$refill = false; 
		}
		if($refill){
			$rows = $this->db->selectAllRows($this->dbTableName); 
		}
		$this->db->dropTable($this->dbTableName);
		$this->defineCols_Master();
		foreach($this->colList as $col){
			$cols[$col] = $this->$col;
		}
		$this->db->createTable($this->dbTableName, $cols, $time, $user);
		if($refill){
			$this->db->refillTable($this->dbTableName, $rows);
		}
		$this->clearCols();
	}
	
	function defineCols_Master(){
		$this->defineCols();
		foreach($this->colList as $col){
			if($col == 'id' && $this->id == null){
				$this->id = new OxDbColDef_IntPrimaryKey();
			}
			elseif($this->$col == null){
				$this->$col = new OxDbColDef_Text();			
			}
		}
	}
	function defineCols(){}

	function printTable($parent = null, $n = null, $ae = false){
		$this->db->printTable($this->dbTableName, $parent, $n, $ae);
	}
	
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	////  FORM LAYOUT / PROCESSING
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	
	function domAdminFormRef($full = false){ 
		//$ref = "./oxdb_row/" . get_class($this) . '/';
		$ref = "http://" . $_SERVER['SERVER_NAME'] . "/admin/oxdb_row/row/" . get_class($this) . '/';
		if($full){
			$ref .= "type/full/";
		}
		if($this->id){
			$ref .= "id/" . $this->id . "/";
		}
		return $ref; 
	}
	// form
	function domAdminForm_Standard($parent, $text = null, $title = null){
		if($title == null){
			if($this->id == null & $text != null){
				$title = "Add a $text"; 
			}
			elseif ($text != null) {
				$title = "Edit $text";
			}
		}
		if($this->id == null){
			$id = get_class($this); 
		}
		else {
			$id = get_class($this) . "_" . $this->id;
		}
		$form = new OxForm($parent, $id, 'OxForm_medium_w', $title);
		//load values for edit
		if($this->id){
			$form->loadFormValues($this->loadById()); 
		}
		return $form; 
	}
	function domAddToForm_Standard($form){
		$form->addHidden("ox_action", "form_submit_standard");
		$form->addCompleteUrl(OxPage::getLastPage());
		$formHandler = new OxFormHandler($form, get_class($this) . "?processForm_Standard");
		if($this->id){
			$formHandler->addHidden("OX_CURRENT_ID", $this->id);
		}
		// This fills the current name of columns for processing 
		$this->fillColumnNames();
		return $formHandler; 
	}	
	function processForm_Standard($row){
		if($row['OX_CURRENT_ID']){
			$id = $row['OX_CURRENT_ID'];
			unset($row['OX_CURRENT_ID']);
			$this->db->updateRowById($this->dbTableName, $row, $id);
		}
		else{
			$this->insertRow($row);
		}
	}
	
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	////  BACKUP
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	///////////////////////////////////
	
	function backup(OxDbSQLite $db, $id = null){
		$dbTableName = get_class($this);
		$qs = "CREATE TABLE $dbTableName (";
		$cols = $this->db->getColNames($dbTableName, false);
		foreach($cols as $col){
			$qs .= "$col, ";
		}
		$qs = substr($qs, 0, -2);
		$qs .= ");";
		$db->query($qs);
		if($id == null){
			$rows = $this->db->selectAllRows($dbTableName);
		}
		else{
			$rows = $this->db->selectRowById($dbTableName, $id);
		}
		while($rows->valid()){
			$row = $rows->current(0);
			$db->insertRow($dbTableName, $row);
			$rows->next();
		}
	}
	function backupTable(){
		if($this->db->doesTableExist($this->dbTableName)){
			$ts = $this->dbTs();
			$table = get_class($this);
			$file = "C:/xampp/projects/Lc/web/tutor/db/BACKUPS/TABLES/$table/TABLES/$ts/";
			OxFile::mkdirs($file, 0);
			$dbBackup = new LcDb_TutorSite_Backup($file, $table);
			$this->backup($dbBackup);
		}
	}
	function backupRow(){
		if($this->db->doesTableExist($this->dbTableName)){
			$ts = $this->dbTs();
			$table = get_class($this);
			$ts = $this->getId() . "." . $ts;
			$file = "C:/xampp/projects/Lc/web/tutor/db/BACKUPS/TABLES/$table/ROWS/$ts/";
			OxFile::mkdirs($file, 0);
			$dbBackup = new LcDb_TutorSite_Backup($file, $table);
			$this->backup($dbBackup, $this->getId());		
		}
	}
	function dbTs(){
		return date("Y.m.d.H.i.s");
	}
}

class OxDbRow_SubClass extends OxDbRow {
	
}

?>