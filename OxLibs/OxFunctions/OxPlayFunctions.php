<?php 

	

function arrayArray($arrayIn){
	for($i = 0; $i < sizeof($arrayIn); $i++){
		if(is_array($arrayIn[$i]) == false){
			$arrayIn[$i] = array($arrayIn[$i]);
		}
	}
	return $arrayIn; 
}

function getDashDate(){
	$date = getdate();
	return $date['mon'] . '-' . $date['mday'] . '-' . $date['year'];
}
function getFiles($rootSearchDir, $fileExt) {
	if(is_array($rootSearchDir)){
		$fileArray = array(); 
		foreach($rootSearchDir as $aRootSearchDir){
			$fileArray += getFiles($aRootSearchDir, $fileExt);
		}
	}
	else {
		if(is_array($fileExt)){
			$fileArray = array(); 
			foreach($fileExt as $aFileExt){
				$fileArray += getFiles($rootSearchDir, $aFileExt);
			}
		}
		else{
			$fileArray = array(); 
			$n = strlen($fileExt);
			if ($handle = opendir($rootSearchDir)) {
			   while (false !== ($file = readdir($handle))) {
			   	    if ($file != "." && $file != "..") {
			           $fileName = $rootSearchDir . "/" . $file; 
			           if(is_dir($fileName)){
			           		$fileArray += getFiles($fileName, $fileExt);
			           }
			           if(strtoupper(substr($file, strlen($file)-$n)) == strtoupper($fileExt)){
			           		$name = substr($file, 0, strlen($file)-$n); 
			           		//print "<br>$name"; 
			           		//$fileName = str_replace("/x", "//x", $fileName);
			           		
			           			$names = explode("/", $fileName);
			           			$name = array_pop($names);
			           			$name = array_pop($names) .  "." . $name;
			           			
			           		$name = strtolower($name);
			           		$fileArray[$name] = $fileName;
			           }
			       }
			   }
			   closedir($handle);
			}
		}
	}
	return $fileArray;  
}

function compareFileTimes($fileOne, $fileTwo){
	return filemtime($fileOne) - filemtime($fileTwo);
}

function printTable($data, $colNames = null, $rowNames = null, $tableClasses = null){
	// Table class is an array of table classes
	if($tableClasses == null){
		$tableClasses = array(null, null, null, null, null);
	}
	
	$classes = array("simple_table", "simple_table_header", "simple_table_row", "simple_table_x");
	
	foreach($tableClasses as &$class){
		$a = array_shift($classes);
		if($class === null){
			$class = $a; 
		}
	}
	
	$tableClass = array_shift($tableClasses);
	$headerClass = array_shift($tableClasses);
	$rowClass = array_shift($tableClasses);
	$xClass = array_shift($tableClasses);
	
	$theTable = new OxTable(null, null, $tableClass);
	
	if($colNames != null){
		$aRow = new OxRow($theTable, null, $headerClass);
		if($rowNames != null){
			$aCell = new OxCell($aRow, null, $xClass);
		}
		foreach($colNames as $colName){
			$aCell = new OxCell($aRow, null, $headerClass);
			$aCell->addText($colName);
		}
	}
	foreach($data as $row){
		$aRow = new OxRow($theTable, null, $tableClass);
		if($rowNames != null){
			$rowName = array_shift($rowNames);
			$aCell = new OxCell($aRow, null, $rowClass);
			$aCell->addText($rowName);
		}
		foreach($colNames as $colName){
			$aCell = new OxCell($aRow, null, $tableClass);
			$aCell->addText($row[$colName]); 
		}
	}
	return $theTable; 
}

function dodie($class, $method, $message){
	print "A critical error from " . get_class($class) . "::" . $method . "<br />";
	print $message . "<br />"; 
	exit(); 
}
function array_delete(&$array, $item){
	foreach($array as $key => $arrayItem){
		if($item === $arrayItem){
			unset($array[$key]);
			return; 
		}
	}
}

function getMicrotime(){
	list($usec, $sec) = explode(" ", microtime());
	return $sec . $usec; 	
}

function getFun(){
	$argList = func_get_args(); 
	return getFun_main($argList); 
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
function explode_shift($sep, $haystack){
	$x = explode($sep, $haystack); 
	array_shift($x);
	return $x; 
}

function unixToWindows($file){
	$file = str_replace('file:///', '', $file); 
	$file = str_replace('/', "\\", $file); 
	$file = str_replace('\\x', '\\\\x', $file);
	return $file; 
}

function loadPNG($imgname) 
{
   $im = @imagecreatefrompng($imgname); /* Attempt to open */
   if (!$im) { /* See if it failed */
       $im  = imagecreatetruecolor(150, 30); /* Create a blank image */
       $bgc = imagecolorallocate($im, 255, 255, 255);
       $tc  = imagecolorallocate($im, 0, 0, 0);
       imagefilledrectangle($im, 0, 0, 150, 30, $bgc);
       /* Output an errmsg */
       imagestring($im, 1, 5, 5, "Error loading $imgname", $tc);
   }
   return $im;
}

?>