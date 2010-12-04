<?php
class LcFaq extends XmlDocDiv {
	
	public $xlcmlDocParser;
	public $theTag; 
	public $state;
 
	public $sections; 
	
	public $currentSection; 
	public $currentFaq; 
		
	public $pic; 
	function __construct($xlcmlFile, $pic){	
		XmlDocDiv::__construct(null, "lc_faq");
		$this->xlcmlDocParser = new XmlDocParser($this);
		$this->state = null; 
		$this->processXlcml($xlcmlFile);
		$this->pic = $pic; 
	}
	function processXlcml($xlcmlFile){
		$xlcml = file_get_contents($xlcmlFile);
		$this->xlcmlDocParser->processBuffer($this, $xlcml);
	}
	function output(){	

		$title = new XmlDocDiv($this, null, "h1");
		$title->addText("Frequently Asked Questions -- The Questions");
	
		$c = 0;
		$firstSec = true;  
		foreach($this->sections as $section){	
			$sec = new XmlDocDiv($this, null, "lc_faq_sec1");
			if($firstSec){
				$sec->addElement($this->pic);
				$firstSec = false; 
			}
			$secName = new XmlDocDiv($sec, null, "lc_faq_sec_name1");
			$secName->addText($section->section);
			foreach($section->faqs as $faq){
				$faqName = new XmlDocDiv($sec, null, "lc_faq_ref1");
				$faqName = new XmlDocRef($faqName, null, "lc_faq_ref1");
				$faqName->addText("Q: " . $faq->q);
				$faqName->addRef("#sec$c$c");
				$c++; 
			}
		}
		$title = new XmlDocDiv($this, null, "h1");
		$title->addText("Frequently Asked Questions -- The Answers");
	
		$c = 0; 
		foreach($this->sections as $section){	
			$sec = new XmlDocDiv($this, null, "lc_faq_sec1");
			$secName = new XmlDocDiv($sec, null, "lc_faq_sec_name1");
			$secName->addText($section->section);
			foreach($section->faqs as $faq){
				$faqName = new XmlDocDiv($sec, null, "lc_faq_ref2");
				$faqName = new XmlDocRef($faqName, null, "lc_faq_ref2");
				$faqName->addText("Q: " . $faq->q);
				$faqName->addAnchor("sec$c$c");
				$c++; 
				$text = new XmlDocDiv($sec, null, "lc_faq_text");
				$text->addText($faq->text);
			}
		}

		return XmlDocDiv::output(); 
	}
	function orphanTag(){
		if($this->state == "faq"){
			$this->currentFaq->text .= $this->theTag->makeTag(); 
		}
		else{
			$tagName = $this->theTag->makeTag();
			$tagName = str_replace("<", "|", $tagName);
			$tagName = str_replace(">", "|", $tagName); 
			echo "Tag: " . $tagName . " not supported";
			die();
		}
	}
	function processText($text){
		switch($this->state){
			case "faq":
				$this->currentFaq->text .= $text; 
				break; 
		}
	}
	function dd_faq_0(){
	}
	function dd_faq_2(){
	}
	function dd_section_0(){
		$name = $this->theTag->getAtt("name", null);
		$section = new LcFaqSection($name);
		$this->sections[] = $section;
		$this->currentSection = $section;
	}
	function dd_section_2(){
	}
	function dd_f_0(){
		$this->state = "faq";
		$q = $this->theTag->getAtt("q", null);
		$faq = new LcFaqFaq($q); 
		$this->currentSection->faqs[] = $faq; 
		$this->currentFaq = $faq; 
	}
	function dd_f_2(){
		$this->state = null; 
	}
	function dd_comment_0(){
		$this->state = "faq";
	}
	function dd_comment_2(){
		
	}
}

class LcFaqSection {
	public $faqs; 
	public $section; 
	function __construct($section){
		$this->section = $section; 
	}
}
class LcFaqFaq {
	public $q; 
	public $text; 
	function __construct($q){
		$this->q = $q; 
		$this->text = ""; 
	}
}

?>
