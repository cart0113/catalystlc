<?php

	session_start(); 
	 
	require_once("file:///c:/xampp/projects/lc/www/www_svn/lc_root/www/LcPageMaker/LcPageMaker.php");
	
	$pageMaker = new LcPageMaker(1, 0, false, false, true, false, false, false); 
	$pageMaker->addCssFile($pageMaker->url . "/css/overview.css");
	$picNum = $_SESSION['overview_picnum'];
	if($picNum == null){
		$picNum = 1;
	} 
	else{
		$picNum = $_SESSION['overview_picnum'];		
	}
	if($picNum == 4){
		$picNum = 1; 
	}
	
	$_SESSION['overview_picnum'] = $picNum+1; 
	
	if($picNum == 2){
		$text = "Rocio and Andrew work on rounding.";
	}
	elseif($picNum == 1){
		$text = "Erika and Ali talk about different polygons.";
	}
	elseif($picNum == 3){
		$text = "Andrew puts a Catalyst printable in a three-ring
		binder for a student to take home.";
	}
	
	$pageMaker->addCssFile("overview.css");
	$pageMaker->makeMainPage("Overview");
	
	$table = new XmlDocTable($pageMaker->lcPage);
	$row = new XmlDocRow($table);
	$cell = new XmlDocCell($row, null, "jumpList");
	$cell->addStyle("padding-right: 10px; padding-bottom: 10px;");
	$div = new XmlDocDiv($cell);
	$div->addStyle("padding-top: 8px; padding-left: 5px; padding-bottom: 30px;");
	$img = new XmlDocImage($div, "reteach.jpg");
	
	
//	$jumpList[] = array("About Us", $_SESSION['lc_url'] . "/overview/aboutus.php");
//	$jumpList[] = array("Frequently Asked Questions", "faq.php");
//	$jumpList[] = array("Sign up to Become a Tutor", $_SESSION['lc_url'] . "/overview/contact.php");
//	$jumpList[] = array("Contact Us", $_SESSION['lc_url'] . "/overview/contact.php");
//	$pageMaker->addJumpList($cell, $jumpList);
	
	
	$cell = new XmlDocCell($row);
	$cell->addStyle("padding-left: 30px");
	$table = new XmlDocTable($cell); 
	$row = new XmlDocRow($table);
	$cell = new XmlDocCell($row);
	$cell->addStyle("padding-top: 10px;");
	$img = new XmlDocImage($cell, "$picNum.jpg");
	$img->addStyle("padding-bottom: 0px; padding-left: 25px;");
	$row = new XmlDocRow($table);
	$cell = new XmlDocCell($row);
	$cell->addStyle("padding-left: 15px; height: 50px;");
	$cell = new XmlDocDiv($cell);
	$cell->addStyle("font-size:6pt; font-style: italic; width: 300px; padding-top: 10px; padding-left: 10px; text-align: center;");
	$cell->addText("$text -- ");
	$ref = new XmlDocRef($cell); 
	$ref->addText("<i>next</i>");
	$ref->addRef("overview.php");

	$div = new XmlDocDiv($pageMaker->lcPage, null, "lcTextMain");
	$div->addStyle("padding-right: 10px;");
	$content = $pageMaker->parseXml(file_get_contents("../web_content/overview.xml"));
	$div->addText($content);
	
	$pageMaker->makeLogin();
	print $pageMaker->output();
	exit(); 

?>