<?php
function getQuote($t = null){
		if($t === null){
			$t = floor(intval(rand(0,16+1)*.999999));
		}
		switch($t){	
			case 0: 
				addQuote("In this age which believes that there is a shortcut for everything, the greatest lesson to be learned is that the most difficult way is, in the long run, the easiest.", "Henry Miller", "Henry_Miller");
				break; 	
			case 1: 
				addQuote("If you are planning for a year, sow rice; if you are planning for a decade, plant trees; if you are planning for a lifetime, educate people.", "Chinese Proverb"); 
				break; 
			case 2: 
				addQuote("He who asks a question is a fool for a minute; he who does not remains a fool forever.", "Chinese Proverb"); 
				break; 	
			case 3:
				addQuote("An ounce of action is worth a ton of theory.", "Friedrich Engels", "Friedrich_Engles"); 
				break; 
			case 4:
				addQuote("If I have seen further than others, it is by standing upon the shoulders of giants.", "Sir Issc Newton", "Issac_newton"); 
				break;
			case 5:
				addQuote("There is nothing education cannot do. Nothing is above its reach. It can turn bad morals to good; it can destroy bad principles and recreate good ones; it can lift men to angelship.", "Mark Twain", "Mark_Twain");
				break; 
			case 6:
				addQuote("The beautiful thing about learning is that no one can take it away from you.", "B.B. King", "BB_King");
				break; 
			case 7:
				addQuote("Only the educated are free", "Epictetus", "Epictetus");
				break; 
			case 8:
				addQuote("More money is put into prisons than into schools. That, in itself, is the description of a nation bent on suicide. I mean, what is more precious to us than our own children? We are going to build alot more prisons if we do not deal with the schools and their inequalities.", "Jonathan Kozol", "Jonathan_Kozol");
				break; 
			case 9:
				addQuote("If you can read this, thank a teacher.", "Anonymous teacher");
				break; 
			case 10:
				addQuote("If you think education is expensive, try ignorance.", "Unknown");
				break; 
			case 11:
				addQuote("Education is our passport to the future, for tomorrow belongs to the people who prepare for it today.", "Malcolm X", "Malcom_X");	
				break; 
			case 12:
				addQuote("Do not call for black power or green power. Call for brain power.", "Barbara Jordan", "Barbara_Jordan");		
				break; 
			case 13: 
				addQuote("Every man must decide whether he will walk in the creative light of altruism or the darkness of destructive selfishness. This is the judgment. Life's persistent and most urgent question is 'What are you doing for others?", "Dr. Martin Luther King, Jr.", "Martin_Luther_King%2C_Jr."); 
				break;
			case 14: 
				addQuote("The function of education is to teach one to think intensively and to think critically... Intelligence plus character - that is the goal of true education.", "Dr. Martin Luther King, Jr.", "Martin_Luther_King%2C_Jr."); 
				break;
			case 15:
				addQuote("Nothing ever comes to one, that is worth having, except as a result of hard work.", "Booker T. Washington", "Booker_T_Washington"); 
				break;
			case 16:
				addQuote("One of the best ways of enslaving a people is to keep them from education.", "Eleanor Roosevelt", "Eleanor_Roosevelt"); 
				break;		
		}
	}
	
	function addQuote($quote, $name, $wiki=null){
		$q = $_SESSION['log_div'];
	
		$q->addText('"' . $quote . '"');

		$d = new OxTagDiv($q, 'lc_quoter');
		if($wiki != null){
			$d->addtext("--");
			$ref = new OxTagRef($d, null, "quoteRef", "&nbsp;" . $name, "http://en.wikipedia.org/wiki/$wiki"); 
		}
		else{
			$d->addText("-- $name");
		}
	
//		if($_SESSION['inOrOut'] == 0){
//			$q->addText("<br/><br/>");
//			$div = new OxDiv($q, null, "sendQuote");
//			$ref = new OxRef($div);
//			$ref->addRef("mailto:andrewjcarter@gmail.com");
//			$ref->addClass("sendQuote");
//			$ref->addText("send us a quote!");
//		} 
	
		
	}

?>