<?php
require_once("file:///var/local/svn/data/php_old/OxLibs/OxPage.php");

require_once("getQuote.php");	


class LcMark extends OxPage {
	
	public $where; 
	function __construct($where = 'home') {
		$this->where = $where; 
		
		$url = $_SERVER['SERVER_NAME'];
		$_SESSION['lc_url'] = 'http://' . $url; 
	
		unset($_SESSION['lclogin']);
		unset($_SESSION['lcusername']);
			
		// Learning Center Specific Loading
		$url = $_SESSION['lc_url'];
		// These variables are used to work 'pdf loading' splash screen.
		$_SESSION['lc_lastpage'] = $url . $_SERVER['REQUEST_URI'];
		$_SESSION['lc_pdfon'] = false;
		// Create Path for Catalyst 
		$this->newPath('main', '', $url);
		OxPage::__construct();
		
	}
	
	function makeDom(){
		OxPage::makeDom();
		$this->addBrowserIcon("./css/catalyst.ico");
		$this->addCssFile($this->getHttp('main') . '/css/catalystlc.css');
		$this->addToTitle("Catalyst Learning Center");

		
		for($i = 0; $i < 5; $i++){
			new OxTagDiv($this->domBody, "p_$i");
		}
		
		$domPageMain = new OxTagDiv($this->domBody, 'lc_all'); 	
		
		$form = new OxTagForm($domPageMain, null, null, ".");
		$input = new OxTagInput($form, null, null, 'Enter Your Name');
		
		
	}

}	

	session_start(); 
	$pageMaker = new LcMark("home"); 
	$pageMaker->doIt();


?>