<?
/** 				
 * \brief	A general purpose SQL database wrapper class. 
 * 
 * <b>Overview</b>
 * 
 * Wraps a SQL table and provides protected methods that execute SQL statements on that table. 
 * 
 * Items of note: 
 * 
 * 1. You must subclass this class and have that class return OxDbResult results.  All methods that
 * execute SQL are protected. 
 * 
 * 2. Tables contain not result data, just return it.  This is to prevent data concurrency issues. 
 *
 * <b>Naming Conventions</b>
 * 
 * Method naming follows SQL naming conventions.  Hence, methods that perform SELECT statemeets start. 
 * 
 */
class OxDbSQLite {
	private $dbSQLiteDir;
	private $dbSQLiteName; 
	public $db; 
	function __construct($dbDir, $dbName){
		//print "hi";
		$this->dbSQLiteDir = $dbDir;
		$this->dbSQLiteName= $dbName;  
		$this->db = $this->connect();
		$this->begin();		
	}
	function __destruct(){
		$this->commit();
	}
	function connect(){
		return new SQLiteDatabase("$this->dbSQLiteDir/$this->dbSQLiteName.lcsqlite.db");
	}
	function begin(){
		//OxInfoWindow::addHeader('DB', "BEGIN LCDB SQL TRANSACTION");
		//$this->query("BEGIN;");
	}
	function commit(){
		$this->query("COMMIT;");
		//OxInfoWindow::addText('DB', "<br/><br/>"); 
	}
	public function query($qs, $rowClass = null){
		//OxInfoWindow::addText('DB', "$qs<br/>");
		//print_r($_SESSION['OX_REGISTERS']['fWin_OxInfoWindow']);
		//print $qs . "<br/>\n";
		$result = $this->db->query($qs);		
		if($rowClass == null){
			return $result; 
		}
		else {
			if($result->valid()){
				return $this->castRows($result, $rowClass);
			}	
			else {
				return array();
			}
		}
	}
	function castRows($result, $rowClass){
		$rows = array(); 
		while($result->valid()){
			//print '$newRow = new ' . $rowClass . '();'; exit();
			$row = $result->current(0);
			//$id = array_shift($row);
			//print('$rows[] = new ' . $rowClass . '($row);');
			//print_r($row);
			eval('$rows[] = new ' . $rowClass . '($row);');
			$result->next();
		}
		return $rows; 		
	}

	///////////////////////
	///////////////////////
	///////////////////////
	///////////////////////
	///////////////////////
	///////////////////////
	///////////////////////
	///////////////////////
	// CREATE / DROP
	///////////////////////
	///////////////////////
	///////////////////////
	///////////////////////
	///////////////////////
	///////////////////////
	///////////////////////

	function createTable($dbTableName, $cols, $time = true, $user = true){
		$qs = 'CREATE TABLE ' . $dbTableName . ' ( ';
		foreach($cols as $key => $value){
			$colName = $key;
			//OxInfoWindow::addVar(get_class($value));
			$colName .= " " . $value->getType();
			$qs .= $colName . ', ';
		}
		
		$qs = substr($qs, 0, strlen($qs)-2);
		$qs .= ");";
		$this->query($qs);
		
		foreach($cols as $key => $value){
			if($value){
				if($value->doIndex()){
					$this->makeIndex($dbTableName, $key, $value->isIndexUnique());
				}
			}
		}	
	}
	function makeIndex($dbTableName, $index, $isUnique = false){
		$iOne = 'IDX_' . $dbTableName . '_' . $index; // . '_ind';
		$iTwo = $index;
		$qs = "CREATE "; 
		if($isUnique){
			$qs .= "UNIQUE "; 
		}
		$qs .= "INDEX $iOne ON $dbTableName ( $iTwo );";
		//print $qs . "<br/>";
		$this->query($qs); 
	}
	
	function dropTable($dbTableName){
		if($this->doesTableExist($dbTableName)){
			unset($_SESSION[$dbTableName . '_cols_oxdb']);
			$this->query("DROP TABLE " . $dbTableName . ";");
		}
	}
	function doesTableExist($dbTableName){
		$result = $this->query("SELECT name FROM sqlite_master WHERE type='table' AND name='$dbTableName';");
		return $result->numRows() > 0;
	}
	
	function getColNames($dbTableName, $cutPrimaryKey = true){
		if(!isset($_SESSION[$dbTableName . '_cols_oxdb'])){
			$qs = "PRAGMA table_info($dbTableName);";
			$result = $this->query($qs);
			while($result->valid()){
				$row = $result->current(0);
				$cols[] = $row['name']; 
				$result->next();
			}
			$_SESSION[$dbTableName . '_cols_oxdb'] = $cols; 
		}
		else{
			$cols = $_SESSION[$dbTableName . '_cols_oxdb'];
		}
		//This command locks the database. 
		//$raws = $this->db->fetchColumnTypes($this->tableName);
		if($cutPrimaryKey == true){
			array_shift($cols);
		}
		return $cols; 
	}
	
	///////////////////////
	///////////////////////
	///////////////////////
	///////////////////////
	///////////////////////
	///////////////////////
	///////////////////////
	///////////////////////
	// INSERT / UPDATE
	///////////////////////
	///////////////////////
	///////////////////////
	///////////////////////
	///////////////////////
	///////////////////////
	///////////////////////
	
	public function insertRow($dbTableName, $row){
		$qs = '(';
		$vs = '(';
		foreach($row as $key => $value){
			$qs .= " " . $key . " "; 
			//string escape; 
			$vs .= " '" . sqlite_escape_string(trim($value)) . "' ";
			$qs .= ",";
			$vs .= ",";
		}
		$qs = substr($qs, 0, -1);  // returns "abcde"
		$vs = substr($vs, 0, -1);  // returns "abcde"
		$qs .= ")";
		$vs .= ")";
		$qs = "INSERT INTO " . $dbTableName . " " . $qs . " VALUES " . $vs .";"; 
		$this->query($qs);
		return $this->db->lastInsertRowId();
	}
	
	///////////////////////
	// Select Methods
	///////////////////////
	
	//	Operator 	Description
	//	= 			Equal
	//	<> 			Not equal
	//	> 			Greater than
	//	< 			Less than
	//	>= 			Greater than or equal
	//	<= 			Less than or equal
	//	BETWEEN 	Between an inclusive range
	//  IN			In a list. 
	//	LIKE		Search for a pattern
	
	/// CONDITIONALS
	//  AND			All conditions must be meet
	//  OR 		    One condition must be meet
	//  NOT			This condition cannot be meet. 
	//  EX: SELECT LastName FROM Clients Where City = 'Boston' AND FirstName = 'Anita'
	//  EX: SELECT * FROM s WHERE sno='S3' OR city = 'London'
	//  NOTE: AND has a higher precedence than OR, so the following expression a OR b AND c
	//  is equivalent to: a OR (b AND c)
	//  EX: SELECT * FROM sp WHERE NOT sno = 'S3'
	
	//  Using Between 
	//  SELECT * FROM sp WHERE qty BETWEEN 50 and 500
	
	//  Using In
	//  IN operator implements comparison to a list of values, that is, it tests whether a value 
	//  matches any value in a list of values. IN comparisons have the following general format:
	//	SELECT name FROM s WHERE city IN [NOT] ('Rome','Paris')
	
	//  Using LIKE
	//	Using LIKE. The following SQL statement will return persons with first names that start with an 'O':
	//	SELECT * FROM Persons WHERE FirstName LIKE 'O%'
	//
	//	The following SQL statement will return persons with first names that end with an 'a':
	// 	SELECT * FROM Persons WHERE FirstName LIKE '%a'
	//
	//	The following SQL statement will return persons with first names that contain the pattern 'la':
	//	SELECT * FROM Persons WHERE FirstName LIKE '%la%'
	 
	//  Sorting the results
	//
	//  You use the ORDER BY clause to sort the result rows. The following SQL statement returns an alphabetic list of people sorted by last name then first name from the Clients table:
	//  SELECT * FROM Clients Order By LastName, FirstName
	//
	//  The default is to return the results in ascending order (top to bottom). 
	//  If you include the DESC keyword in the ORDER BY clause, the rows are returned in descending order (bottom to top).
	//
	//  The following statement returns a reverse alphabetic list of the Clients table:
	//  SELECT * FROM Clients Order By LastName, FirstName DESC

	function selectAllRows($dbTableName, $rowClass = null, $limit = null){
		if($limit == null){
			return $this->query("SELECT * FROM $dbTableName;", $rowClass);
		}
		else {
			return $this->query("SELECT * FROM $dbTableName LIMIT $limit;", $rowClass);
		}
	}
	
	protected function selectColsByWheres($dbTableName, $cols, $whereCols, $whereValues = null, $whereConds = null, $orderCols = null, $orderOrders = null, $limit = null){
		$this->makeArray($cols);
		$qs = '';
		for($i=0; $i<sizeof($cols); $i++){
			$qs .= $cols[$i];
			if($i < sizeof($cols)-1){
				$qs .= ", ";
				$vs .= ", ";
			}
			else{
				$qs .= " ";
				$vs .= " ";
			}
		}
		$qs = "SELECT $qs FROM $dbTableName" . " ";
		if($whereCols != null){
			$qs .= $this->getWhere($whereCols, $whereValues, $whereConds) . $this->getOrder($orderCols, $orderOrders);
		}
		if($limit){
			$qs .= " LIMIT $limit";
		}
		$qs .= ";";
		//print $qs;
		return $this->query($qs);
	}
	
	/////////////////////////
	// Update Methods
	///////////////////////
	protected function updateRowsByWheres($cols, $vals, $whereCols, $whereValues, $whereConds = null){
		$this->makeArray(&$cols, $vals); 
		//print_r($cols); 
		$this->makeArray($whereCols, $whereValues, $whereConds);
		$qs = '';
		for($i=0; $i<sizeof($cols); $i++){
			$qs .= $cols[$i];
			$qs .= " = '" . sqlite_escape_string($vals[$i]) . "'";
			if($i < sizeof($cols)-1){
				$qs .= ", ";
				$vs .= ", ";
			}
			else{
				$qs .= " ";
				$vs .= " ";
			}
		}
		$qs = "UPDATE $this->tableName SET $qs" . $this->getWhere($whereCols, $whereValues, $whereConds) . ";";
		//print $qs; exit();
		$return = $this->query($qs);
	}
	
	public function updateRowById($dbTableName, $row, $id){
		$qs = '';
		$i = 0; 
		foreach($row as $key => $value){
			$qs .= $key;
			$qs .= " = '" . sqlite_escape_string($value) . "'";
			if($i < sizeof($row)-1){
				$qs .= ", ";
				$vs .= ", ";
			}
			else{
				$qs .= " ";
				$vs .= " ";
			}
			$i++; 
		}
		$qs = "UPDATE $dbTableName SET $qs WHERE id='$id';";
		//print $qs; exit();
		$return = $this->query($qs);
	}
	
	
	
	///////////////////////
	// Delete Methods
	///////////////////////
	function deleteRowById($dbTableName, $id){
		$this->query("DELETE FROM $dbTableName WHERE id='$id';"); 
	}
	function deleteRowsByWhere($dbTableName, $where){
		$qs = "DELETE FROM $dbTableName " . $this->getWhere($where) . ";";
		$this->query($qs);
	}
	
	///////////////////////
	// Support Methods
	///////////////////////
	
	private function makeArray(&$val1, &$val2 = null, &$val3 = null){
		if($val2 != null){
			$check = true; 
		}
		if(is_array($val1) == false){
			$val1 = array($val1);
			$val2 = array($val2);
			$val3 = array($val3);
		}
		if(sizeof($val1) != sizeof($val2) && $check == true){
			dodie($this, "makeArray", "Arrays not the same size");
		}
	}
	private function getWhere($where, $or = false){
		$and = "AND";
		if($or){
			$and = "OR";
		}
		$qs = "WHERE";
		foreach($where as $key => $value){
			$qs .= " $key = '$value' " . $and;
		}
		$qs = substr($qs, 0, -1*strlen($and));
		return $qs; 
	}
	
	private function getOrder($orderCols, $orderOrders){
		$order = "";
		if($orderCols != null){
			$this->makeArray($orderCols, $orderOrders);
			for($i = 0; $i<sizeof($orderCols); $i++){
				if($i == 0){
					$order = " ORDER BY ";
				}
				else{
					$order .= ", ";
				}
				if($orderOrders[$i] == null){
					$cond = ' DESC';
				}
				else{
					$cond = ' ' . $orderOrders[$i];
				}
				$order .= $orderCols[$i] . $cond;
			}
		}
		return $order; 

	}

	
	function printTable($dbTableName, $parent = null, $limit = null, $ae = false, $restore = false){
		$div = new OxTagDiv($parent); 
		$div->addStyle("padding: 20pX;");
		if($this->doesTableExist($dbTableName)){
			$cols = $this->getColNames($dbTableName, false);
			$result = $this->selectAllRows($dbTableName, null, $limit);	
			
			if($restore){
				$div = new OxForm($div, null, null, "./../", 'restore', 'restore_table', ".", 'GET');
				$div->setName("restoreForm");
				$div->addHidden('XTABLE', $dbTableName);
				$parent->addText("<br/>");
				$block = new OxBlockRefList_Master($div, null, "header2", $dbTableName);
				$block->addRef("toggle row 'checks'", "clearCheckRows('ROWS')", 'js');
				$block->addRef("toggle column 'checks'", "clearCheckRows('COLS')", 'js');
				$block->addRef("restore", "document.restoreForm.submit()", 'js');
			}
		
			
			$title = new OxTagDiv($div); 
			$title->addStyle("font-family: Myriad Pro, Verdana; padding: 14px; text-align:center; font-size:11pt; font-weight:bold;");
			$title->addText("Table: $dbTableName");
			
			$table = new OxTagTable($div, null, "db_table");
			$table->addStyle("margin: 10px; font-family: Myriad Pro, Verdana; font-size: 14px; padding: 5px; border-collapse: collapse;");
			
			if($restore){
				$cell = new OxTagCell($row);
				$row1 = new OxTagRow($table);	
				$cell = new OxTagCell($row1);
				$div = new OxTagDiv($cell);
				$div->width("85px");
				$dr = new OxTagDiv($div);
				
			}
			$row = new OxTagRow($table);
			if($restore or $ae){
				new OxTagCell($row);
			}
			foreach($cols as $col){
				if($restore){
					$cell = new OxTagCell($row1);
					$cell->addStyle("border-left: 1px solid #AAAAAA; border-right: 1px solid #AAAAAA;");
					$div = new OxTagDiv($cell);
					$div->addStyle("padding: 5px");
					$div->addText('<INPUT TYPE="CHECKBOX" CLASS="OXRESTORECOLS" NAME="XCOL_' . $col . '" checked></INPUT>');
				}
				$cell = new OxTagCell($row); 
				$cell->addStyle("background-color: #E9E9E9; padding: 5pt; border: 2px solid #CCCCCC;");
				$cell->addText($col);
			}
			$current = true;
			$c = 0; 
			while($result->valid()){
				$row = new OxTagRow($table);
				$current = $result->current(0);	
				if($restore){
					$cell = new OxTagCell($row);
					$cell->addStyle("border-top: 1px solid #AAAAAA; border-bottom: 1px solid #AAAAAA;");
					$div = new OxTagDiv($cell);
					$div->addStyle("padding: 5px; padding-top: 10px;");
					$div->addText('<INPUT TYPE="CHECKBOX" CLASS="OXRESTOREROWS" NAME="XROW_' . $current['id'] . '" checked> </INPUT>');
				}
				if($ae){
					$id = $current['id'];
					$cell = new OxTagCell($row);
					$cell->addStyle("padding: 10px; border-top: 1px solid #AAAAAA; border-bottom: 1px solid #AAAAAA;");
					$refs = new OxBlockRefList($cell);
					$refs->width("75px");
					$refs->addRefs("edit", "?ox_action=edit&id=$id", "delete", "?ox_action=delete&id=$id");
				}
				foreach($current as $item){
					$cell = new OxTagCell($row); 
					$cell->addStyle("background-color: #F9F9F9; padding: 5pt; border: 2px solid #CCCCCC;");
					$divc = new OxTagDiv($cell);
					//$divc->addStyle("max-width: 120px; word-wrap: break-word;");
					if($editAll){
						$input = new OxTagInput($divc, null, null, null, $item, 'text');
						$input->width("auto");
					}
					else{
						$divc->addText($item);
					}
				}
				$result->next();
			}
			if($parent == null){
				print $div->output();
			}
		}
		else {
			$div->addText("This table does not exist.");
		}
		//file_put_contents("c:\\xampp\dbxml\dbone.dbxml", $table->output());
	}
	
	//////////////////////////////////
	/// UPDATE AND EDIT AND BACKUP FUNCTIONS 
	//////////////////////////////////
	function refillTable($dbTableName, SQLiteResult $rows, $replaces = null){ //, $newRow = false){
		$cols = $this->getColNames($dbTableName, false);
		$one = true;
		while($rows->valid()){
			$row = $rows->current(0);
			// find not keys
			if($one){
				$notKeys = array();
				foreach($row as $key => $value){
					if(!in_array($key, $cols)){
						$notKeys[] = $key;
					}
				}
				$one = false; 
			}
			// replace
			if($replaces){
				foreach($replaces as $replace){
					$row[$replace[1]] = $row[$replace[0]];
					unset($replace[0]);
				}
			}
			foreach($notKeys as $notKey){
				unset($row[$notKey]);
			}
//			if($newRow){
//				unset($row['id']);
//			}
			$this->insertRow($dbTableName, $row);
			$rows->next();
		}
	}
}
