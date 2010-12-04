function toggleId(id){
	id = "#"+id;
	$(id).toggle();
}

var i; // used for all counters. 
// AJAX Communication Engine
var http_request = false;
function oxajax_ajaxExecute(sendObject) {
    if (window.XMLHttpRequest) { // Mozilla, Safari, ...
        http_request = new XMLHttpRequest();
     } 
	 else if (window.ActiveXObject) { // IE
	 	try {
	    	http_request = new ActiveXObject("Msxml2.XMLHTTP");
	   } catch (e) {
	   try {
	        http_request = new ActiveXObject("Microsoft.XMLHTTP");
	   } catch (e) {}
	 }
   }
    if (!http_request) {
        alert('Giving up :( Cannot create an XMLHTTP instance');
        return false;
		a = new Element();
    }
	
	if(typeof(sendObject) == "string"){
		http_request.onreadystatechange = oxajax_alertContents;
		http_request.open('GET', sendObject, true);
		http_request.send(null);		
	}
	else {
		var formData = '', elem = ''; 
		for(var s=0; s<sendObject.elements.length; s++){ 
			elem = sendObject.elements[s]; 
			if(formData != ''){ 
				formData += '&'; 
			} 
			formData += elem.name+"="+elem.value; 
		}
		http_request.onreadystatechange = oxajax_alertContents;
		http_request.open(sendObject.method, sendObject.action, true); 
		http_request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded"); 
		http_request.send(formData); 
 
	}	
}
	    
function oxajax_alertContents() {
	try {
		if (http_request.readyState == 4) {
	        if (http_request.status == 200) {
	        	// Start of Response.
	        	//alert(http_request.responseText);
	        	eval(http_request.responseText); 
			} 
			else {
	            alert('There was a problem with the request.');
	        }
	    }
	} 
	catch(e) {
		alert('oxajax_alertContents ERROR');
		alert( e );
		alert(http_request.responseText);
		SetCookie('AJAX_ALERT', http_request.responseText);
	}
}

function getFilter(e, imageName){
	e.style.filter = "progid:DXImageTransform.Microsoft.AlphaImageLoader(src='" + imageName + "', sizingMethod='scale');";
}

function oxjs_changeRef(id, href){
	var e = document.getElementById(id);
 	e.href = href;
	e.ons
}

var turnOff;
function oxjs_makeBlue(idon){
	//alert(idoff);
	var e = document.getElementById(idon);
 	e.style.backgroundColor = '#F6F6FF';
	if(turnOff != null && idon != turnOff){
		var o = document.getElementById(turnOff);
 		o.style.backgroundColor = '#FFFFFF';
	}
	turnOff = idon;
}

var ison; 
function clearCheckRows(where){
	 if(ison){
	 	ison = false;
	 }
	 else {
	 	ison = true; 
	 }
	 labels = document.getElementsByTagName("input"); 
	 for( var i = 0; i < labels.length; i++ ) { 
		 if( labels[i].className == 'OXRESTORE' + where ) {	 	
			 labels[i].checked = ison;
		 }
	 } 
}

function disableLink(linkID){
 	var hlink1 = document.getElementById(linkID + '1');
 	var hlink2 = document.getElementById(linkID + '2');
 	//hlink.display = 'none';
 	//hlink.visiblity = 'hidden';
 	//alert(linkID);
 	//hlink.className = "href_nolink";
 	hlink1.innerHTML = 'pdf';
 	hlink2.innerHTML = 'unassign';
}
function changeInnerHTMLById(id, html){
 	var e = document.getElementById(id);
 	e.innerHTML = html;
}

function pauseComp(millis)
{
	date = new Date();
	var curDate = null;
	do { var curDate = new Date(); }
	while(curDate-date < millis);
} 
////////////////////////////////////
////////////////////////////////////
////////////////////////////////////
////////////////////////////////////
////     INFO WINDOW
////////////////////////////////////
////////////////////////////////////
////////////////////////////////////
////////////////////////////////////
var fWin; 
var regUrl = './?OX_REGISTER_AJAX=';
function FWindow(winName, outDiv, inDiv, jRight, jTop, jWidth, jHidden){
	//members
	this.winName = winName; 
	this.outDiv = document.getElementById(outDiv);
	this.inDiv = document.getElementById(inDiv);
	this.h1 = document.getElementById('H1');
	this.h2 = document.getElementById('H2');
	this.jRight = jRight; 
	this.jTop = jTop; 
	this.jWidth = jWidth;
	this.jHidden = jHidden; 
	this.regUrl = regUrl + this.winName;
	//methods
	
	this.hcon = function hcon(){
		document.body.style.cursor = 'col-resize';
	}
	
	this.hcoff = function hcoff(){
		document.body.style.cursor = 'default';
	}
	
	this.fDown = function fDown(event, where){
		this.where = where; 
		this.downX = event.clientX;
    	this.downY = event.clientY;
		if(where = 1){
			document.body.style.cursor = 'move';
		}
		else {
			document.body.style.cursor = 'col-resize';
		}
		document.addEventListener("mousemove", fMove, true);
   		document.addEventListener("mouseup", fUp, true);
		event.stopPropagation();
   	 	event.preventDefault();
		fWin = this;
	}
	
	function fMove(event){
		var moveLeft = event.clientX - fWin.downX;
		fWin.inDiv.style.backgroundColor = '#F5F5F5';
		fWin.downX = event.clientX;
		if(fWin.where == 1){
			document.body.style.cursor = 'move';
			var moveTop = event.clientY - fWin.downY;
			fWin.downY = event.clientY;	
			fWin.jTop = fWin.jTop + moveTop; 	
			fWin.jRight = fWin.jRight - moveLeft; 
			fWin.outDiv.style.top = fWin.jTop + 'px';
			fWin.outDiv.style.right = fWin.jRight + 'px';
		}
		else {
			document.body.style.cursor = 'col-resize';
			if(fWin.where == 0){
				fWin.jWidth = fWin.jWidth - moveLeft;
				if(fWin.jWidth < 351){ 
					fWin.jWidth = 350;
					fUp(event);
				}
				fWin.inDiv.style.width = fWin.jWidth + 'px';
			}
			else {
				fWin.jWidth = fWin.jWidth + moveLeft;
				if(fWin.jWidth < 351){ 
					fWin.jWidth = 350;	
					fUp(event);
				}
				else {
					fWin.inDiv.style.width = fWin.jWidth + 'px';
					fWin.jRight = fWin.jRight - moveLeft; 
					fWin.outDiv.style.right = fWin.jRight + 'px';
				}
			}
		}
		event.stopPropagation();
	}
	function fUp(event){	
		fWin.inDiv.style.backgroundColor = '#EEEEEE';
		document.body.style.cursor = 'default';
		document.removeEventListener("mousemove", fMove, true);
		document.removeEventListener("mouseup", fUp, true);
		// And don't let the event propagate any further
		event.stopPropagation();
		oxajax_ajaxExecute(fWin.regUrl + '&jHidden=' + fWin.jHidden
									   + '&jRight=' + fWin.jRight
									   + '&jTop=' + fWin.jTop
									   + '&jWidth=' + fWin.jWidth);
	}	
	
	this.toggleShow = function toggleShow(){
		if(this.jHidden == 'hidden'){
			this.jHidden = 'visible';
		}
		else {
			this.jHidden = 'hidden';
		}
		this.outDiv.style.visibility = this.jHidden;
		oxajax_ajaxExecute(this.regUrl + '&jHidden=' + this.jHidden);
	}
}

function SetCookie(cookieName, cookieValue) {
	 //var today = new Date();
	 //var expire = new Date();
	 //if (nDays==null || nDays==0) nDays=1;
	 //expire.setTime(today.getTime() + 3600000*24*nDays);
	 document.cookie = cookieName + "=" + escape(cookieValue); // + ";expires="+expire.toGMTString();
}

function keys(key) {
	if (!key) {
		key = event;
		key.which = key.keyCode;
	}
	switch (key.which) {
		case 8: // Backspace (Delete Mac)
			break;
		case 12: // clear (keypad)
			break;
		case 13: // return
			break;
		case 17: // Alt (PC only)
			break;
		case 18: // Ctrl (PC only)
			break;
		case 19: // Pause (PC only)
			break;
		case 27: // esc
			break;
		case 32: // space
			break;
		case 33: // page up
			break;
		case 34: // page down
			break;
		case 35: // end
			break;
		case 36: // home
			break;
		case 37: // left arrow
			break;
		case 38: // up arrow
			break;
		case 39: // right arrow
			break;
		case 40: // down arrow
			break;
		case 44: // Print Screen
			break;
		case 45: // Insert (Help mac)
			break;
		case 46: // Delete (Del mac)
			break;
		case 48: // 0
			break;
		case 49: // 1
			break;
		case 50: // 2
			break;
		case 51: // 3
			break;
		case 52: // 4
			break;
		case 53: // 5
			break;
		case 54: // 6
			break;
		case 55: // 7
			break;
		case 56: // 8
			break;
		case 57: // 9
			break;
		case 59: // ;
			break;
		case 61: // =
			break;
		case 65: // a
			break;
		case 66: // b
			break;
		case 67: // c
			break;
		case 68: // d
			break;
		case 69: // e
			break;
		case 70: // f
			break;
		case 71: // g
			break;
		case 72: // h
			break;
		case 73: // i
			break;
		case 74: // j
			break;
		case 75: // k
			break;
		case 76: // l
			break;
		case 77: // m
			break;
		case 78: // n
			break;
		case 79: // o
			break;
		case 80: // p
			break;
		case 81: // q
			break;
		case 82: // r
			break;
		case 83: // s
			break;
		case 84: // t
			break;
		case 85: // u
			break;
		case 86: // v
			break;
		case 87: // w
			break;
		case 88: // x
			break;
		case 89: // y
			break;
		case 90: // z
			break;
		case 91: // Left Windows (PC only)
			break;
		case 92: // Right Windows (PC only)
			break;
		case 93: // Application (PC only)
			break;
		case 96: // 0 (keypad)
			break;
		case 97: // 1 (keypad)
			break;
		case 98: // 2 (keypad)
			break;
		case 99: // 3 (keypad)
			break;
		case 100: // 4 (keypad)
			break;
		case 101: // 5 (keypad)
			break;
		case 102: // 6 (keypad)
			break;
		case 103: // 7 (keypad)
			break;
		case 104: // 8 (keypad)
			break;
		case 105: // 9 (keypad)
			break;
		case 106: // * (keypad)
			break;
		case 107: // + (keypad)
			break;
		case 109: // - (keypad)
			break;
		case 110: // . (keypad)
			break;
		case 111: // / (Keypad)
			break;
		case 112: // F1
			break;
		case 113: // F2
			break;
		case 114: // F3
			break;
		case 115: // F4
			break;
		case 116: // F5
			break;
		case 117: // F6
			break;
		case 118: // F7
			break;
		case 119: // F8
			fWin_OxInfoWindow.toggleShow();
			break;
		case 120: // F9
			//alert(regUrl + 'none&reset=true');
			oxajax_ajaxExecute(regUrl + 'none&reset=true');
			break;
		case 121: // F10
			break;
		case 122: // F11
			break;
		case 123: // F12
			
			break;
		case 124: // F13
			break;
		case 125: // F14
			break;
		case 126: // F15
			break;
		case 145: // Scoll Lock (PC only)
			break;
		case 188: // ,
			break;
		case 190: // .
			break;
		case 191: // /
			break;
		case 192: // `
			break;
		case 219: // [
			break;
		case 220: // \
			break;
		case 221: // ]
			break;
		case 222: // '
			break;
		default: 
			break;
	}
}
