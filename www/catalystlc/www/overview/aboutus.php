<?php		
	session_start(); 
	 
	require_once("file:///c:/xampp/projects/lc/www/www_svn/lc_root/www/LcPageMaker/LcPageMaker.php");
	
	$pageMaker = new LcPageMaker(1, 0, false, false, true, false, false, false); 
	
	$pageMaker->makeMainPage("About Us");
	
	$content = $pageMaker->parseXml(file_get_contents("../web_content/aboutus.xml"));
	$pageMaker->lcPage->addText($content);
	
	$pageMaker->makeLogin();
	print $pageMaker->output();
	exit(); 

?>