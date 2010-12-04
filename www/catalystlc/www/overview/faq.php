<?php	
	session_start(); 
	 
	require_once("file:///c:/xampp/projects/lc/www/www_svn/lc_root/www/LcPageMaker/LcPageMaker.php");
	
	$pageMaker = new LcPageMaker(1, 0, false, false, true, false, false, false); 
	
	$pageMaker->makeMainPage("FAQ");
	
	require_once("LcFaq.php");
	$pageMaker->addCssFile("faq.css");
	
	
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
	
	
	$divp = new XmlDocDiv(null, null, "faq_pic");
	$divp->addStyle("padding: 10px; float: right;");
	$div = new XmlDocDiv($divp);
	
	$img = new XmlDocImage($div, "$picNum.jpg");
	$img->addStyle("padding-bottom: 0px; padding-left: 25px;");
	
	$div = new XmlDocDiv($divp);
	$div->addStyle("font-size:6pt; font-style: italic; width: 310px; padding-top: 10px; padding-left: 18px; text-align: center;");
	$div->addText("$text -- ");
	$ref = new XmlDocRef($div); 
	$ref->addText("<i>next</i>");
	$ref->addRef("faq.php");
	
	$faq = new LcFaq("file:///c:/xampp/projects/lc/www/www_svn/lc_root/www/web_content/faq.xlcml", $divp);
	$pageMaker->lcPage->addElement($faq);
	
	$pageMaker->makeLogin();
	
	print $pageMaker->output();
	exit(); 
	
?>	