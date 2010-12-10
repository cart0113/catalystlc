<?php
	
	session_start(); 
	 
	require_once("./LcPageMaker.php");
	
	$pageMaker = new LcPageMaker(1, 0, false, false, true, false, false, false);
	
	$pageMaker->makeMainPage("Home");
	
	$n = $_SESSION["quoteNumber"];
	
	if($n == null){
		$n = 0;
	}
	if($n > 16){
		$n = 0; 
	}
	
	$_SESSION["quoteNumber"] = $n+1;
	
	$pageMaker->makeLogin();
	$div = new XmlDocDiv($pageMaker->lcPage, null, "pageTitle");
	$div->addText("Quotables&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;");
	$ref = new XmlDocRef($div);
	$ref->addText(" next quote");
	$ref->addRef("./quotables.php");
	$ref->addClass("sidebarItem");
	
	$divq = new XmlDocDiv($pageMaker->lcPage);
	$divq->addStyle("font-size: 12pt; padding-top: 100px; padding-left: 20px;");
	$_SESSION['log_div'] = $divq;
	getQuote($n);
	 
	print $pageMaker->output();
	
	exit(); 
	
?>