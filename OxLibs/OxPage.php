<?php
session_start();  
/// STATIC HTML / GUI GENERATION
require_once("/var/local/svn/data/php_old/OxLibs/OxDom/OxDomElement.php");
require_once("/var/local/svn/data/php_old/OxLibs/OxDom/OxBlock.php"); 
require_once("/var/local/svn/data/php_old/OxLibs/OxDom/OxDomPage.php");
///  CSS AND JS HANDLERS
require_once("/var/local/svn/data/php_old/OxLibs/OxDom/OxCss.php"); 
require_once("/var/local/svn/data/php_old/OxLibs/OxDom/OxJs.php"); 
///	STATIC UTILITY FUNCTIONS
require_once("/var/local/svn/data/php_old/OxLibs/OxFunctions/OxString.php");
require_once("/var/local/svn/data/php_old/OxLibs/OxFunctions/OxFile.php");
require_once("/var/local/svn/data/php_old/OxLibs/OxFunctions/OxError.php");
require_once("/var/local/svn/data/php_old/OxLibs/OxFunctions/OxTrace.php");
/**
 * Enter description here...
 *
 */

class OxPage extends OxDomPage
{	
	private $path; 
	// filtered $_GET and $_POST
	public $oxRuri; 
	public $oxData; 
	//public $visitorInfo; 
	
	public $domLcInfo;
	
	public $reg_domLcDebug; 
	function __construct() {
		//$_SESSION['OX_PRINT_SQL'] = true; 
		OxVisitor::getPlatformAndOS();
		//$this->reg_domLcDebug = OxDebugWindow::recall('reg_domLcDebug', $this->domBody);
		//$this->reg_searchDir = OxRegString::recall('reg_dir', "http://www.google.com/");
		
		//$this->reg_domLcDebug = new OxRegString('reg_domLcDebug', "Hello Vietnam");
		
		//This is from OxDispatch.
		$this->oxRuri = $_SESSION['OX_RURI'];
		unset($_SESSION['OX_RURI']);
		if(sizeof($_POST) > 0){
			$this->oxData = $_POST; 
		}
		elseif(sizeof($_GET) > 0 ){
			$this->oxData = $_GET;
		}

		// Then perform any setup actions. 
		$this->setupAll();
		// If there's data, see if there are any ox_actions.  If not, reload the page with oxdata set. 
		
		if(sizeof($this->oxData) > 0){
			// You must supply a handler -- if no handler is supplied, ox_action_form_submit is called. 
			if(isset($this->oxData['ox_action'])){
				$action = '$this->ox_action_' . $this->oxData['ox_action'] . '();';
				unset($this->oxData['ox_action']);
				eval($action);
				//This is set in OxDom_Ajax 		
			}
//			else {
//				$this->ox_action_form_submit();
//			}
			if($GLOBALS['OXAJAX_EXECUTE']){
				$GLOBALS['OXAJAX_EXECUTE'] = false; 
				exit();
			}
			//This makes ox_data persistent
			$_SESSION['ox_data'] = $this->oxData; 
			$this->oxHeader();
		}
		else {
			$this->oxData = $_SESSION['ox_data'];
			//Setup logic and base dom structure.
			$this->makeBaseDom();
			//Current Add-ons to main page. 
			$this->makePageDom();
			$this->doIt();
			unset($_SESSION['ox_data']);
			exit();
		}
	}
	function setupAll($path = null, $file = null, $url = null){
		if($path){
			$this->setPath($path);
		}
		if($file){
			$this->newPath('main', $file, $url);
		}
	}
	function setPath($httpPath = 'null'){
		$filePath = "file:///C:/xampp/projects/Ox/OxMaker/";
		$this->path['ox'] = new OxPath($filePath, $httpPath);
	}
	function newPath($name, $filePath, $httpPath){
		$this->path[$name] = new OxPath($filePath, $httpPath);
	}
	function oxHeader($urlWhere = "."){
		header("Location: $urlWhere");
		exit();
	}	
	function makeBaseDom($addCss = false){
		$page = $this->getHttp('main') . substr($_SERVER['REQUEST_URI'], 1);
		if($_SESSION['ox_last_page'][0] != $page){
			$_SESSION['ox_last_page'][3] = $_SESSION['ox_last_page'][2];
			$_SESSION['ox_last_page'][2] = $_SESSION['ox_last_page'][1];
			$_SESSION['ox_last_page'][1] = $_SESSION['ox_last_page'][0];
			$_SESSION['ox_last_page'][0] = $page;
		}
		OxDomPage::makeBaseDom();
		if($addCss){
			$this->addCssFile($this->getHttp('ox') . 'css/ox.css');
		}
	}
	function makePageDom(){}
	function loadOxJs($error = true){
//		if(!isset($_SESSION["OX_JS_ISON"])){
//			$_SESSION["OX_JS_ISON"] = false; 
//			$this->addJsFile($this->getHttp('ox') . '/js/ox.js');
//			OxJs::ajaxExecute($this, './?ox_action=ox_check_js');
//			print $this->domJs->output();
//			sleep(2);
//			header("Location: . "); exit();
//			//unset($_SESSION["OX_JS_ISON"]);
//		}
//		if($_SESSION["OX_JS_ISON"]){
//			$this->addJsFile($this->getHttp('ox') . '/js/ox.js');
//		}
//		else {
			if($error){
				$this->domBody->addText("
					<noscript>
						<div style='font-family: Verdana, sans-serif; width: 100%; text-align: center; padding-top: 10px;'>
							<div style='padding: 10px; text-align: center; font-size: 20px; background-color: #FAD163;'> 
								You need to have JavaScript enabled to correctly view this page.
							</div>	
						</div>
					</noscript>
				"); 
			}	
			$this->addJsFile($this->getHttp('ox') . 'js/ox.js');
//		}
	}
	function addToTitle($text){
		$this->domTitle->addText($text);
	}
	function doIt(){
		print $this->output(); 
	}
	function extendPath($basePathName, $newPathName, $extension){
		$file = $this->path[$basePathName]->getFile(); 
		$http = $this->path[$basePathName]->getHttp();
		$this->path[$newPathName] = new OxPath($file, $http, $extension);
	}
	
	function getFile($pathName = null, $unixStyle = true){
		if(isset($this->path[$pathName]) == false){
			dodie($this, 'getHttp', "Path name: $pathName not found. All names are: <br/><br/>" . print_r($this->path));
		}
		$file = $this->path[$pathName]->getFile();
		if($unixStyle == false){
			$file = unixToWindows($file);
		} 
		return $file; 
	}
	function getHttp($pathName = null){
		if(isset($this->path[$pathName]) == false){
			OxError::dodie("Path name: $pathName not found. Current path names are: <br/><br/>" . print_r($this->path));
		}
		return $this->path[$pathName]->getHttp(); 
	}
	
	function getFiles($pathName, $fileTypes, $ext = ''){
		$pathName = $this->getFile($pathName) . $ext;
		$files = getFiles($pathName, $fileTypes);
		return $files; 
	}
	function getHttps($pathName, $fileTypes, $ext = ''){
		$files = $this->getFiles($pathName, $fileTypes, $ext);
		$f = $this->getFile($pathName); 
		$h = $this->getHttp($pathName);
		foreach($files as $file){
			$newFiles[] = str_replace($f, $h, $file);
		}
		return $newFiles; 
	}	
	/// SESSION VARIABLES. 
	function setSessionVar($key, $value){
		$_SESSION['OX_VARS'][$key] = $value;
	}
	public static function getSessionVar($key, $default = null){
		if(!isset($_SESSION['OX_VARS'][$key])){
			$_SESSION['OX_VARS'][$key] = $default;
		}
		return $_SESSION['OX_VARS'][$key];
	}
	function unsetSessionVer($key){
		unset($_SESSION['OX_VARS'][$key]);
	}
	
	function lastPage($n = 1){
		Header("Location: " . $_SESSION['ox_last_page'][$n]); 
		exit();
	}
	public static function getLastPage($n = 1){
		return $_SESSION['ox_last_page'][$n];
	}
	public function getPageRuri(){
		$key = get_class($this);
		$key = str_replace('LcPage_', "", $key);
		return $this->oxRuri[$key];
	}
	public static function getOxData($key){
		return $_SESSION['ox_data'][$key];
	}
	//////////////////////////
	///// FORMS 
	//////////////////////////
	function ox_action_form_delete_row(){
		$class = $this->oxData['class'];
		$id = $this->oxData['id'];
		eval('$row = new ' . $class . '(' . $id . ');');
		$row->deleteById();
		$this->ox_action_form_reset();
		$this->lastPage();
	}
	function ox_action_form_cancel($formId = null){
		if($formId == null){
			$formId = $this->oxData['id'];
		}
		unset($_SESSION['ox_forms'][$formId]); 
		$this->oxHeader($this->getLastPage());
	}
	function ox_action_form_submit_standard(){
		$row = OxForm::processOxData($this, $this->oxData);
	}
	function ox_action_class_handler(){
		$class = explode("?", $this->oxData['class']);
		$method = $class[1];
		$class = $class[0];
		unset($this->oxData['class']);
		eval('$handler = new ' . $class . '();');
		$handler->$method($this->oxData);
	}
	
	///////////////////////////////
	///// Public Static Functions
	///////////////////////////////
	function globalCounter($varName){
		if(isset($GLOBALS[$varName])){
			$GLOBALS[$varName] = $GLOBALS[$varName]+1;
		}
		else{
			$GLOBALS[$varName] = 0;
		}
		return $GLOBALS[$varName];
	}
	///////////////////////////////
	///// Info Windows
	///////////////////////////////
	function output(){
		//print $_SESSION['OX_INFO_STRING2']; exit();
		new OxDomText($this->domLcInfo[1], $_SESSION['OX_INFO_STRING1']);
		new OxDomText($this->domLcInfo[2], $_SESSION['OX_INFO_STRING2']);
		return parent::output();
	}
	function domMakeInfos($parent){
		$this->domMakeInfo($parent, "Info DB", 1);
		$this->domMakeInfo($parent, "Info Vars", 2);
		$this->domMakeInfo($parent, "Commands", 3);	
	}
	function domMakeInfo($parent, $title, $n = 1){
		$div = new OxTagDiv($parent, "lc_info$n", "lc_info");
		$block = new OxBlockRefList_Ajax($div, null, "header3", $title); 
		if($n != 3){	
			$on = $this->getSessionVar('OX_INFO_ON'. $n, "off");
			if($on == "off"){
				$text = "turn on";
			}
			else {
				$text = "turn off";
			}
			$block->addRef($text, "./?ox_action=info_window_on&n=$n", 'ajax', "OX_INFO_ON$n");
		}
		$block->addRefs("25", "./?ox_action=info_window_width&w=25&n=$n");
		$block->addRefs("50", "./?ox_action=info_window_width&w=50&n=$n");
		$block->addRefs("100", "./?ox_action=info_window_width&w=96&n=$n");
		$block->addRefs("hide", "./?ox_action=info_window_show&n=$n");
		if($n != 3){
			$block->addRefs("clear", "./?ox_action=clear_info&n=$n");
		}
		$this->domLcInfo[$n] = new OxTagDiv($div, "lc_info_text$n");
		$key = 'OX_INFO_WINDOW_SHOW' . $n;
		if($this->getSessionVar($key, 'off') == 'off'){
			$this->addJsCommand("document.getElementById('lc_info$n').style.visibility = 'hidden';");
		}
		$width = $this->getSessionVar('OX_INFO_WINDOW_WIDTH' . $n, '25');
		$div->width("$width%");
	}	
	
	public static function getThickWindow(){
		print "TB_show();";
		return new OxDom_Ajax('OX_THICK_WINDOW');
	}
}
/**
 * Simple class that holds a file and an http path. 
 *
 */
class OxPath {
	protected $file; 
	protected $http; 
	function __construct($rootFilePath, $rootHttpPath, $extPath = ""){
		$this->file = $rootFilePath . $extPath;
		$this->http = $rootHttpPath . $extPath; 
	}
	function getFile(){
		return $this->file; 
	}
	function getHttp(){
		return $this->http; 
	}
}

class OxDate {
	public static function getDate($time = null, $style = 0){
		if($time == null){
			$time = time();
		}
		switch($style){
			case 0:		
				return date("F j, Y, g:i a", $time); 
				break; 
			case 1:
				return date('m-d-y', $time); 
				break;
			case 2:
				return date('h:i:s A');
				break;
			case 3: 
				list($usec, $sec) = explode(" ", microtime());
				return $sec . $usec; 
				break; 
			case 4: 
				return date('l', $time) . ' ('. date('m-d-y', $time) . ')'; 
				break;
			case 5:
				return date("g:i a", $time);
				break; 
		}
	}
}

class OxProcess {
	public static function callTool ($path,$file) {
   		chdir($path); $call = $path.$file;
   		pclose(popen('start /b "window_name" '.$call.'', 'r'));
	}
	public static function urlExec($url){	
		OxProcess::callTool('C:\\xampp\\xampp\\php', "\\php.exe $url");
	}
}

class OxVisitor {
	public static function getPlatformAndOS(){
		if(!isset($_SESSION['OX_VISITOR_INFO'])){
			$useragent = $_SERVER['HTTP_USER_AGENT'];	
			if (preg_match('|MSIE ([0-9].[0-9]{1,2})|',$useragent,$matched)) {
			    $browser_version=$matched[1];
			    $browser = 'IE';
			} elseif (preg_match( '|Opera ([0-9].[0-9]{1,2})|',$useragent,$matched)) {
			    $browser_version=$matched[1];
			    $browser = 'Opera';
			} elseif(preg_match('|Firefox/([0-9\.]+)|',$useragent,$matched)) {
			        $browser_version=$matched[1];
			        $browser = 'Firefox';
			} elseif(preg_match('|Safari/([0-9\.]+)|',$useragent,$matched)) {
			        $browser_version=$matched[1];
			        $browser = 'Safari';
			} else {
			        // browser not recognized!
			    $browser_version = 0;
			    $browser= 'other';
			}
			
			if (strstr($useragent,'Win')) {
				    $os='Win';
				} else if (strstr($useragent,'Mac')) {
				    $os='Mac';
				} else if (strstr($useragent,'Linux')) {
				    $os='Linux';
				} else if (strstr($useragent,'Unix')) {
				    $os='Unix';
				} else {
				    $os='Other';
				}
			$_SESSION['OX_VISITOR_INFO']['BROWSER'] = $browser; 
			$_SESSION['OX_VISITOR_INFO']['VERSION'] = $browser_version;
			$_SESSION['OX_VISITOR_INFO']['OS'] = $os;
			$_SESSION['OX_VISITOR_INFO']['IP'] = $_SERVER['REMOTE_ADDR'];	
//			$gb = get_browser(null, true);
//			$_SESSION['OX_VISITOR_INFO']['JS'] = $gb['javascript'];
//			print $_SESSION['OX_VISITOR_INFO']['JS']; exit();
		}
	}
}

//$WshShell = new COM("WScript.Shell");
//$oExec = $WshShell->Run("cmd /C C:\\xampp\\xampp\\php\\k.bat", 0, false);
//$oExec = $WshShell->Run("cmd /C dir /S %windir%", 0, false);
//print $oExec; 

//exec('start /B "window_name" "C:\\xampp\\xampp\\php\\k.bat"',$output,$return);

//callTool('C:\\xampp\\xampp\\php', '\\php.exe C:\\a.php');

//$oExec = popen("C:\\xampp\\xampp\\php\\psexec.exe -d C:\\xampp\\xampp\\php\\k.bat", 'r');			
//exec("C:\\xampp\\xampp\\php\\psexec.exe -d C:\\xampp\\xampp\\php\\k.bat");

//exec("C:\\xampp\\xampp\\php\\php-win.exe -q C:\\xampp\\xampp\\php\\a.php &");// a.php >/dev/null &"); 
//exit();
//$this->loadJs();
//$this->addOxAjax('?ox_action=createPdf&assigned_print_id=' . 
//$_SESSION['lc_cp_id1'] . '&print_id=' . 
//$_SESSION['lc_cp_id2']);
//unset($_SESSION['lc_cp_id1']);
//unset($_SESSION['lc_cp_id2']);	
