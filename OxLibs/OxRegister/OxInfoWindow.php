<?php
class OxInfoWindow extends OxRegister {	
	public $jRight;
	public $jTop; 
	public $jWidth;
	public $jHidden;
	public $jWindow; 
	public $jWindowStatus; 
	public $jText; 
	function __construct(){
		if(parent::__construct("fWin_" . get_class($this))){
			$this->jRight = 0; 
			$this->jTop = 200; 
			$this->jWidth = 500; 
			$this->jHidden = 'hidden'; 
			$this->jWindow = 'DB';
			$this->jWindowStatus['DB'] = 'OFF';
			$this->jWindowStatus['DEBUG'] = 'OFF';
			$this->jText['DB'] = "";
			$this->jText['DEBUG'] = "";
		}
		$GLOBALS['OX_INFO_WINDOW'] = $this;
	}
	public static function makeDom($parent){
		$oxWin = OxInfoWindow::getInfoWindow();
		$domMain = new OxTagDiv($parent, $oxWin->regKey . "_MAIN", 'iMain');
		$tableMain = new OxTagTable($domMain, null, 'fT');
		$rowMain = new OxTagRow($tableMain);
		
		$cell = new OxTagCell($rowMain);
		$cell->setAtt("onmouseover", "$oxWin->regKey.hcon()");
		$cell->setAtt("onmouseout", "$oxWin->regKey.hcoff()");
		$cell->setAtt("onmousedown", "$oxWin->regKey.fDown(event, 0)");
		$div = new OxTagDiv($cell, null, 'fH');
		
		$cell = new OxTagCell($rowMain);
		$div = new OxTagDiv($cell, $oxWin->regKey . "_CENTER", 'iCenter');
		$div->setStyle("width: $oxWin->jWidth" . "px;");
		$div->setAtt("onmousedown", "$oxWin->regKey.fDown(event, 1)");
		$centerId = $div->getId();
		
		$windows = array('DB', 'DEBUG', 'COMMANDS');
		$headerM = new OxTagDiv($div, null, 'iHeader');
		$t = new OxTagTable($headerM);
		$t->width("100%");
		$r = new OxTagRow($t);
		$c = new OxTagCell($r);
		$table = new OxTagTable($c);
		$row = new OxTagRow($table);
		foreach($windows as $window){
			$cell = new OxTagCell($row, $oxWin->regKey . '_BUTTON_' . $window, 'ox_info_window_header');
			if($oxWin->jWindow == $window){
				$button = new OxTagDiv($cell, null, 'ox_info_window_header_on', $window);
			}
			else {
				$class = get_class($oxWin) . "?" . 'changeCurrentWindow&window=' . $window;
				$ref = new OxTagRef_Ajax($cell, null, null, null, './?ox_action=class_handler&class=' . $class);
				$button = new OxTagDiv($ref, null, 'ox_info_window_header', $window);
			}
		}
		
		$c = new OxTagCell($r);
		$c->width("100%");
		$c = new OxTagCell($r, null, 'ox_info_window_header');
		$c->setStyle("text-align: right;");
		$class = get_class($oxWin) . "?" . 'toggleOnOff';
		$ref = new OxTagRef_Ajax($c, null, null, null, './?ox_action=class_handler&class=' . $class);
		$button = new OxTagDiv($ref, $oxWin->regKey . '_ONOFF', 'ox_info_window_header', $oxWin->jWindowStatus[$oxWin->jWindow]);
	
		$c = new OxTagCell($r);
		$c->width("100%");
		$c = new OxTagCell($r, null, 'ox_info_window_header');
		$c->setStyle("text-align: right;");
		$class = get_class($oxWin) . "?" . 'refresh';
		$ref = new OxTagRef_Ajax($c, null, null, null, './?ox_action=class_handler&class=' . $class);
		$button = new OxTagDiv($ref, null, 'ox_info_window_header', "REFRESH");	
		
		$textM = new OxTagDiv($div, $oxWin->regKey . "_text", 'iText', $oxWin->jText[$oxWin->jWindow]);
		foreach($windows as $window){
			$textH = new OxTagDiv($div, $oxWin->regKey . "_text_" . $window, 'iTextHide', $oxWin->jText[$window]);
			$textH->setStyle('visibility: hidden;');
			if($window == "COMMANDS"){
				$g = new OxBlockHoverRef_Ajax($textH, null, null, false, "Clear Session", 'Clear the entire "$_SESSION" variable.', "./?OX_REGISTER_AJAX=none&reset=true");
				$g->setStyle("width: 90%;");
				if(OxRegister::isSuperuser()){
					$on = "<span id='SUONID'>ON</span>";
				}
				else {
					$on = "<span id='SUONID'>OFF</span>";
				}
				$z = new OxBlockHoverRef_Ajax($textH, null, null, false, "Superuser $on (toggle)", 'Affects page display for development.', "./?OX_REGISTER_AJAX=none&superuser=true");
				$z->setStyle("width: 90%;");
				if($oxWin->jWindow == "COMMANDS"){
					$textM->addText($g->output());
					$textM->addText($z->output());
				}
			}
		}
		
		$cell = new OxTagCell($rowMain);
		$cell->setAtt("onmouseover", "$oxWin->regKey.hcon()");
		$cell->setAtt("onmouseout", "$oxWin->regKey.hcoff()");
		$cell->setAtt("onmousedown", "$oxWin->regKey.fDown(event, 2)");
		$div = new OxTagDiv($cell, null, 'fH');	

		$domMain->setStyle("right: $oxWin->jRight" . "px; top: $oxWin->jTop" . "px; visibility: $oxWin->jHidden;");
		$mId = $domMain->getId();
		$cId = $centerId;
		$jsCommand = "$oxWin->regKey = new FWindow('$oxWin->regKey', '$mId', '$cId', $oxWin->jRight, $oxWin->jTop, $oxWin->jWidth, '$oxWin->jHidden');";
		$parent->xmlRoot->addJsCommand($jsCommand);
	}
	public static function getInfoWindow(){
		if(isset($GLOBALS['OX_INFO_WINDOW'])){
			return $GLOBALS['OX_INFO_WINDOW'];
		}
		else {
			$GLOBALS['OX_INFO_WINDOW'] = new OxInfoWindow();
			return $GLOBALS['OX_INFO_WINDOW']; 
		}
	}
	function toggleOnOff($data){
		//print "alert('hi');";
		if($this->jWindowStatus[$this->jWindow] == 'OFF'){
			$this->jWindowStatus[$this->jWindow] = 'ON';
			print "document.getElementById('$this->regKey" . "_ONOFF').innerHTML = 'ON';";
		}
		else {
			$this->jWindowStatus[$this->jWindow] = 'OFF';
			print "document.getElementById('$this->regKey" . "_ONOFF').innerHTML = 'OFF';";
			//clear text
			$this->jText[$this->jWindow] = "";
			$key = '' . $this->regKey . "_text_" . $this->jWindow;
			print "document.getElementById('$key').innerHTML = '';";
			$key = '' . $this->regKey . "_text";
			print "document.getElementById('$key').innerHTML = '';";
		}
		exit();
	}
	function refresh($data){
		if($this->jWindow != 'COMMANDS'){
			foreach($this->jText as $key => $value){
				$key = '' . $this->regKey . "_text_" . $key;
				$value = OxJs::escapeJS($value);
				print "document.getElementById('$key').innerHTML = '$value';";
			}
			$key = '' . $this->regKey . "_text";
			$value = OxJs::escapeJS($this->jText[$this->jWindow]);
			print "document.getElementById('$key').innerHTML = '$value';";
		}
		exit();
	}
	
	function changeCurrentWindow($data){
		$id = $this->regKey . '_BUTTON_' . $this->jWindow;
		$cell = new OxDom_Ajax($id);
		$class = get_class($this) . "?" . 'changeCurrentWindow&window=' . $this->jWindow;
		$ref = new OxTagRef_Ajax($cell, null, null, null, './?ox_action=class_handler&class=' . $class);
		$button = new OxTagDiv($ref, null, 'ox_info_window_header', $this->jWindow);
		// reset the new window. 
		$this->jWindow = $data['window'];
		$id = $this->regKey . '_BUTTON_' . $this->jWindow;
		$cell = new OxDom_Ajax($id);
		$button = new OxTagDiv($cell, null, 'ox_info_window_header_on', $this->jWindow);	
		
		$key = '' . $this->regKey . "_text";
		$keyText = '' . $this->regKey . "_text_" . $this->jWindow;
		print "document.getElementById('$key').innerHTML = document.getElementById('$keyText').innerHTML;";
		
		if($this->jWindow == 'COMMANDS'){
			print "document.getElementById('$this->regKey" . "_ONOFF').innerHTML = '';";
		}
		else {
			if($this->jWindowStatus[$this->jWindow] == 'OFF'){
				print "document.getElementById('$this->regKey" . "_ONOFF').innerHTML = 'OFF';";
			}
			else {
				print "document.getElementById('$this->regKey" . "_ONOFF').innerHTML = 'ON';";
			}	
		}
		
		exit();
	}
//	function __destruct(){
//		parent::__destruct();
//		$domMain->xmlRoot = null; 
//	}
//
	public static function addHeader($window, $header){
		$text = "<div style='color:#999999; padding-top: 10px; padding-bottom: 4px; font-size: 14px;'> $header AT " . OxDate::getDate(null, 2) . "</div>";
		OxInfoWindow::addText($window, $text);
	}
	public static function addText($window, $text){
		//if($GLOBALS['OX_INFO_WINDOW']->jText[$window] .= $text; 
		$info = $GLOBALS['OX_INFO_WINDOW']; //new OxInfoWindow();
		//print $that->jWindowStatus[$window];
		if($info->jWindowStatus[$window] == 'ON'){	
			//print_r($_SESSION);
			$info->jText[$window] .= $text;
		}
	}
	public static function addVar($value, $message = "", $window = 'DEBUG'){
		if(is_array($value)){
			OxInfoWindow::addArray($value, $message, $window);
		}
		elseif(is_object($value)){
			OxInfoWindow::addArray(get_object_vars($value), 'OBJECT: ' . get_class($value) . '. ' . $message, $window);	
		}
		else {
			OxInfoWindow::addHeader($window, "Print Variable $message");
			OxInfoWindow::addText($window, "Value: $value<br/>");
		}
	}
	private function addArray($array, $message = "", $window = 'DEBUG'){
		OxInfoWindow::addHeader($window, "Print Array $message");
		$c = 0; 
		foreach($array as $key => $value){
			if(is_object($value)){
				$d = 0; 
				$vt = get_class($value);
				OxInfoWindow::addText($window, "$c . $key as $vt <br/>");
				foreach(get_object_vars($value) as $key=>$value){		
					if(is_object($value)){
						$value = "Object-> " . get_class($value);
					}
					OxInfoWindow::addText($window, "$c . $d: $key as $value<br/>");
					$d++;
				}
				OxInfoWindow::addText($window, "<br/>");
			}
			elseif(is_array($value)){
				OxInfoWindow::addText($window, "$c . $key as ARRAY <br/>");
				foreach($value as $key=>$value){		
					if(is_object($value)){
						$value = "Object-> " . get_class($value);
					}
					OxInfoWindow::addText($window, "$c . $d: $key as $value<br/>");
					$d++;
				}
				OxInfoWindow::addText($window, "<br/>");				
			}
			else {
				OxInfoWindow::addText($window, "$c: $key as $value<br/>");
			}
			$c++;
		}
	}
	public static function hi(){
		OxInfoWindow::addVar("Hi :)");
	}
}