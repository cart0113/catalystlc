<?php
require_once("file:///var/local/svn/data/php_old/OxLibs/OxPage.php");
require_once("file:///var/local/svn/data/php_old/OxLibs/OxForm/OxForm.php"); 
require_once("file:///var/local/svn/data/php_old/OxLibs/OxForm/OxFormBlock.php"); 
require_once("file:///var/local/svn/data/php_old/OxLibs/OxForm/OxTagInput.php"); 

require_once("getQuote.php");	


class LcPageMaker extends OxPage {
	
	public $where; 
	function __construct($where = 'home') {
		$this->where = $where; 
		
		$url = $_SERVER['SERVER_NAME'];
		$_SESSION['lc_url'] = 'http://' . $url; 
	
		unset($_SESSION['lc_username']);
		unset($_SESSION['lc_password']);
			
		// Learning Center Specific Loading
		$url = $_SESSION['lc_url'];
		// These variables are used to work 'pdf loading' splash screen.
		$_SESSION['lc_lastpage'] = $url . $_SERVER['REQUEST_URI'];
		$_SESSION['lc_pdfon'] = false;
		// Create Path for Catalyst 
		$this->newPath('main', '', $url);
		OxPage::__construct();
		
	}
	
	function makePageDom(){
		$this->addBrowserIcon("./css/catalyst.ico");
		if($_SERVER['SERVER_NAME'] == "www.catalystlc.org"){
			//$this->addCssFile("http://disk.catalystlc.org/public/clc/css/catalystlc.css");
			//$fastUrl = "http://disk.catalystlc.org/public/clc/";
			$this->addCssFile("http://" . $_SERVER['SERVER_NAME'] . "/css/catalystlc.css");
			$fastUrl = "http://" . $_SERVER['SERVER_NAME'];
		}
		else {
			$this->addCssFile($this->getHttp('main') . '/css/catalystlc.css');
		}
		$this->addToTitle("Catalyst Learning Center");

		
		for($i = 0; $i < 5; $i++){
			new OxTagDiv($this->domBody, "p_$i");
		}
		
		$domPageMain = new OxTagDiv($this->domBody, 'lc_all'); 	
		
		$domPageMain = new OxTagDiv($domPageMain, 'lc_center'); 
	
		
		$domTableMain = new OxTagTable($domPageMain, 'lc_table_main');
		$domBodyRow = new OxTagRow($domTableMain);
		$domBodyLeft = new OxTagCell($domBodyRow, 'lc_body_left');
		$domBodyRight = new OxTagCell($domBodyRow, 'lc_body_right');
		
		//$login = new OxTagDiv($domBodyRight, 'lc_login');	
		//$this->makeLogin($login);
		
		//$this->makeSidebar($domBodyRight);
				
		$left0 = new OxTagDiv($domBodyLeft, 'lc_left_0');
		$left1 = new OxTagDiv($domBodyLeft, 'lc_left_1');
		
		$main0 = new OxTagDiv($left0, 'lc_main_0');
		
		
		if($this->where == 'home'){
			$photo = new OxTagDiv($main0, 'lc_main_photo');
			$tag = new OxTagDiv($main0, 'lc_main_tag');
		}
		
		$this->makeHeaderTabs($main0);
		
		$main1 = new OxTagDiv($main0, 'lc_main_1');
		$spacer = new OxTagDiv($main0, 'lc_main_spacer');
		
		/*********************************
		*****  HOME  
		**********************************/
		if($this->where == 'home'){
			
//			$quote = new OxTagDiv($main1, 'lc_quote');
//			$quote2 = new OxTagDiv($quote, 'lc_quote_1');
//			$contact = $this->contactUs(null, "send us a quote!");
//			$quotejump = new OxTagDiv($main1, 'lc_quote_jump', null, '<a name="lcquote"> </a>');
//			$quote3 = new OxTagDiv($quote, 'lc_quote_2', null, '<a href="nq.php">next</a> &nbsp;|&nbsp; ' . $contact);
//				
//			$_SESSION['log_div'] = $quote2;
//			getQuote($n);		
			
			$textMain = new OxTagDiv($main0, 'lc_text');
			
			$headers = array('mission', 'about');
			
			$more0 = "<a class='lc_more' href='faq.php?#sec01'> [more...] </a>"; 
			$more44 = "<a class='lc_more' href='faq.php?#sec44'> [more...] </a>"; 
			$more55 = "<a class='lc_more' href='faq.php?#sec55'> [more...] </a>"; 
			$more66 = "<a class='lc_more' href='faq.php?#sec66'> [more...] </a>"; 
			$more77 = "<a class='lc_more' href='faq.php?#sec77'> [more...] </a>"; 
			$more88 = "<a class='lc_more' href='faq.php?#sec88'> [more...] </a>"; 
			$more99= "<a class='lc_more' href='faq.php?#sec99'> [more...] </a>"; 
			$more1010= "<a class='lc_more' href='faq.php?#sec1010'> [more...] </a>"; 

			
			
			$textAlls[] = "
				<p>    
					We are dedicated to helping Minneapolis students achieve their highest mathematical potential. 
			    	Currently, we offer homework help at the Hosmer Community Library in South Minneapolis, MN.
				</p>
			    <p>
			        We are also working towards creating a remediation program
					for students who need a little more than homework help can offer. 
				</p>
				";
							
		$textAlls[] = " 
				<p>
					We are a Minneapolis, MN based startup 501(c)(3).  Catalyst was founded by a dedicated group of 
					teachers, tutors, and professionals working in math related careers. <br/><br/>
				</p>
				<p>  
					Currently, Catalyst is not funded, is entirely a volunteer effort, and 
					offers homework help services at 
					<a href='http://www.ci.minneapolis.mn.us/hpc/landmarks/36th_St_E_347_Hosmer_Library.asp'>Hosmer Community Library</a>
					in South Minneapolis.  
				</p>
				<p>We offer tutoring services from 6:00 to 8:00 PM on Tuesday and Thursday in the community room at Hosmer whenever
					Minneapolis Public Schools are in session.  
				</p>
			    <p>Please <a href='./contact.php'>contact us</a> for more information, if you would like to tutor, or if you would like to get involved as a tutor</p>
				";
		
//				<p>
//					We have plans for a much larger pilot project beginning August 2007.  Please <a href='./contact.php'>contact us</a>
//					if you are 1) interested in working as a volunteer tutor or 2) a student who is looking for some tutoring. 
//				</p>
		
			foreach($headers as $header){
				$hd = new OxTagDiv($textMain, null, 'lc_text_block');
				$header = new OxTagDiv($hd, null, "lc_header lc_header_$header"); 
				$ht = new OxTagDiv($hd, null, 'lc_text_chunk');
				$textAdd = array_shift($textAlls);
				$ht->addText($textAdd);
			}
			
			
			//$hd = new OxTagDiv($textMain, 'lc_text_approach');
			
			//$hd->setStyle("z-index: 102; position: absolute; padding-top: 20px;");

			//$header = new OxTagDiv($hd, null, "lc_header lc_header_approach"); 
			//$ht = new OxTagDiv($hd, null, 'lc_text_chunk');
			
			//$text = 
			//	"Some students just need a little help with homework.  That's great and we
			//	offer homework help for these students.  But other students have greater foundational 
			//	problems and need more intensive remediation.  Due to these problems, 
			//	they are having trouble passing state mandated exams necessary for graduation.
			//	<br/><br/>
			//	So in addition to offering homework help, we are also working towards developing
			//	assessment and teaching materials to offer reteaching services.  These materials
			//	will be designed so 
			//	tutors can easily locate, download, and print out materials necessary teaching materials.  This way, tutors have the materials
			//	necessary to go back and work on fundamental mathematical concepts as outlined in
			//	the Minnesota Department of Education's state standards.  Unlike textbooks designed for the classroom, these materials 
			//	are designed to be taught by volunteers and other nonprofessional math educators during
			//	face-to-face one-on-one tutoring sessions. 
			//	<br/><br/>
			//	We have developed an initial set of printables.  Also, we have created an 
			//	underlying \"printable creation\" engine that allows fast and easy creation of printables
			//	without using cumbersome tools like Microsoft Word. 
			//	<br/><br/>
			//	This effort is a work in progress, so please <a href='./contact.php'>contact us</a> to find
			//	out where we are at or if you want access to our current library of printables. 
			//	<br/><br/>
			//	Below are three examples that show how we related our lesson to the MCA-II math exams: 
			//	";
			//$ht->addText($text);
			//
			//for($i = 1; $i < 4; $i++){
			//	$div = new OxTagDiv($hd);
			//	$image = new OxTagImage($div, null, null, "ex$i.gif");
			//	$image->setStyle("padding-top: 10px; padding-bottom: 10px;");
			//	$table = new OxTagTable($div);
			//	$table->setStyle("width: 100%; padding-left: 10px;");
			//	$row = new OxTagRow($table);
			//	$cell = new OxTagCell($row);
			//	$image = new OxBlockImageRef($cell, null, null, "A$i" . "_off.gif", "pdf.php?pdf=A$i.pdf");
			//	$cell = new OxTagCell($row);
			//	$cell->setStyle("vertical-align: middle; padding-left: 20px; padding-right: 20px;");
			//	$image = new OxTagImage($cell, null, null, 'arrow.gif');
			//	$cell = new OxTagCell($row);
			//	$image = new OxBlockImageRef($cell, null, null, "L$i" . "_off.gif", "pdf.php?pdf=L$i.pdf");
			//}
			
			$text = "
				<br/><br/>
				More Sample Printables:
				<div class='pdf_sample'>
					<a href='pdf.php?pdf=2.pdf'/>Estimation and Mental Math -- Addition</a>
				</div>
				<div class='pdf_sample'>
					<a href='pdf.php?pdf=3.pdf'/>Fractions -- Pieces of a Whole</a>
				</div>" . 
				"<div class='pdf_sample'>
					<a href='pdf.php?pdf=5.pdf'/>Worksheet: Fractions -- Pieces of a Whole</a>
				</div>".
				"<div class='pdf_sample'>
					<a href='pdf.php?pdf=4.pdf'/>Worksheet: Fractions -- Pieces of a Whole</a>
				</div>".
				"<div class='pdf_sample'>
					<a href='pdf.php?pdf=6.pdf'/>Introduction to Fraction Multiplication</a>
				</div>
				<div class='pdf_sample'>
					<a href='pdf.php?pdf=1.pdf'/>Introduction to Rounding</a>
				</div>
				"; 
				
			//$hd->addText($text);
			
		}
		else{
			$textMain = new OxTagDiv($main0, 'lc_text_all');
		}
		/*********************************
		*****  FAQ 
		**********************************/
		if($this->where == 'faq'){
			require_once("LcFaq.php");
			$this->addCssFile($fastUrl . "css/lc_faq.css");
			
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
			
			if($picNum == 1){
				$text = "Rocio and Andrew work on rounding.";
			}
			elseif($picNum == 2){
				$text = "Erika and Ali talk about different polygons.";
			}
			elseif($picNum == 3){
				$text = "Andrew puts a Catalyst printable in a three-ring
				binder for a student to take home.";
			}
			
			//$divp = new OxTagDiv(null, null, "faq_pic");
			//$divp->addStyle("padding: 10px; float: right;");
			//$div = new OxTagDiv($divp);
			
			//$img = new OxTagImage($div, null, null, $fastUrl . "$picNum.jpg");
			//$img->addStyle("padding-bottom: 0px; padding-left: 25px;");
			
			$div = new OxTagDiv($divp);
			$div->addStyle("font-size:9px; font-style: italic; width: 310px; padding-top: 10px; padding-left: 18px; text-align: center;");
			$div->addText("$text -- ");
			$ref = new OxTagRef($div, null, null, "<i>next</i>", "faq.php"); 
			
			$faq = new LcFaq($textMain, "./web_content/faq.xlcml", $divp);
			$faq->output();
		}
		/*********************************
		*****  CONTACT 
		**********************************/
		if($this->where == 'contact'){
			$content = $this->parseXml(file_get_contents("./web_content/contact.xml"));
			$textMain->addText($content);
		}
		if($this->where == 'map'){
			$textMain->addText("<br/><br/>");
			$image = new OxTagImage($textMain, 'lc_map', null, $fastUrl . 'map.jpg');
			$textMain->addText("<br/><br/>");
		}
		
		
		$this->addStat($this->domBody);
	}
	
	function contactUs($parent, $text = "contact us"){
		$contact = new OxTagRef($parent, null, 'lc_contact', $text, "mailto:andrew@catalystlc.org");
		return $contact->output(); 
	}
	
	function makeLogin($parent){
		$space = new OxTagDiv($parent, 'lc_right_top');
		
		$formDiv = new OxTagDiv($parent, "login_form");
		$formDiv->addStyle("padding: 0px; margin: 0px;");
		$form = new OxTagForm($formDiv, "login_form", null, "login.php");
		$form->addStyle("padding: 0px; margin: 0px;");
		
		$d1 = new OxTagDiv($form, null, 'lc_login lc_login_1');
		//$d1->addStyle("padding: 0px; margin: 0px;");
		$username = new OxTagInput_Text($d1, "username", "right", "username", "username"); 
		$d2 = new OxTagDiv($form, null, 'lc_login lc_login_2');
		$password = new OxTagInput_Password($d2, "password", "right", "password", "password"); 
		$password->setAtt("onKeyPress", "return submitenter(this,event)");	
		
		$d3 = new OxTagDiv($form, null, 'lc_login lc_login_3');
		$buttonb = new OxTagInput_Button($d3, 'login_button', null, 'login');

		$loggedIn = new OxTagDiv($parent, 'lc_youare'); 
		$loggedIn->addText("For full access to our library please log in.  If you need a username and password please ");
		$this->contactUs($loggedIn); 
		$loggedIn->addText(".");
		$parent->addText("<br/><br/><br/><br/><br/><br/>");
		$text = "Like the look of our teaching materials . . . <br/><br/>";
		$text .= "They are created using <a href='http://www.princexml.com'>Prince XML</a> -- the
		best tool on the web for dynamically creating pdf documents.";  
		
		$new = new OxTagDiv($parent, null, null, $text);  
		$new->setStyle("color: #777777; font-style: italic;");

//		The license used to generate our
//		printables library was geneoursly provided by Prince XML.";
//		$new = new OxTagDiv($parent, null, null, $text);  
//		$new->setStyle("color: #777777; font-style: italic;");
//		$parent->addText("<br/><br/>");
//		
//		$pic = new OxTagRef($parent, null, null, null, "http://www.princexml.com");
//		$pic = new OxTagImage_TransparentPng($pic, null, null, "prince.png");
		
	}
	
	function makeHeaderTabs($parent){
		$hc = new OxTagDiv($parent, "lc_tabs_container"); 
		$ht = new OxTagTable($hc, 'lc_tabs_table');
		$row = new OxTagRow($ht);
		
		
		if($this->where == 'home'){
			$t1 = new OxTagCell($row, 'lc_home_on');
			$d1 = new OxTagDiv($t1, 'lc_home_on');
		}
		else {
			$t1 = new OxTagCell($row, 'lc_home_off');
			$d1 = new OxTagDiv($t1, 'lc_home_off');
			$r1 = new OxTagRef($d1, 'lc_home_off', null, null, './index.php');
			$i1 = new OxTagImage($r1, 'lc_home_off', null, './css/blank.gif');
		}
		
		$t2= new OxTagCell($row, null, 'lc_dot');
		
		if($this->where == 'faq'){
			$t3 = new OxTagCell($row, 'lc_faq_on');
			$d3 = new OxTagDiv($t3, 'lc_faq_on');
		}
		else {
			$t3 = new OxTagCell($row, 'lc_faq_off');
			$d3 = new OxTagDiv($t3, 'lc_faq_off');
			$r3 = new OxTagRef($d3, 'lc_faq_off', null, null, './faq.php');
			$i3 = new OxTagImage($r3, 'lc_faq_off', null, './css/blank.gif');
		}
	
		
		$t4 = new OxTagCell($row, null, 'lc_dot');
		
		if($this->where == 'contact'){
			$t5 = new OxTagCell($row, 'lc_contact_on');
			$d5 = new OxTagDiv($t5, 'lc_contact_on');
		}
		else{
			$t5 = new OxTagCell($row, 'lc_contact_off');
			$d5 = new OxTagDiv($t5, 'lc_contact_off');
			$r5 = new OxTagRef($d5, 'lc_contact_off', null, null, './contact.php');
			$i5 = new OxTagImage($r5, 'lc_contact_off', null, './css/blank.gif');
		}
		
	}
		
	function parseXml($xml){
		$xml = str_replace("/lc_a", "/a" ,$xml);
		$xml = str_replace("<lc_content>", "" ,$xml);
		$xml = str_replace("</lc_content>", "" ,$xml);
		$xml = str_replace("lc_a", 'a class="lcTextRef"', $xml);
		return $xml; 
	}
	
	
	function addStat($parent){
		$a = '<!-- Start of StatCounter Code -->
		  <script type="text/javascript" language="javascript">
		  var sc_project=1578846; 
          var sc_invisible=1; 
          var sc_partition=14; 
          var sc_security="f280e49c"; 
          var sc_remove_link=1; 
          </script>
          <script type="text/javascript" language="javascript" src="http://www.statcounter.com/counter/counter.js"></script><noscript><img  src="http://c15.statcounter.com/counter.php?sc_project=1578846&java=0&security=f280e49c&invisible=1" alt="frontpage hit counter" border="0"> </noscript>
		  <!-- End of StatCounter Code -->
          ';
		$parent->addText($a);
	}
	
}


?>
