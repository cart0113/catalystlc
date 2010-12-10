var domdom = {
	//USER FUNCTIONS
	alert:					function(msg){
								if(arguments.length < 2){
									alert(msg);
								}
								else{
									var output = ""
									for(var i = 0; i < arguments.length; i++){
										output += i+1 + ": " + arguments[i] + "\n";
									}
									alert(output);
								}
							},
			
	// START OF CORE DOMDOM																						
	ajax_send:				function(url){
								var http_request = domdom.get_xmlhttp();
								http_request.onreadystatechange = domdom.ajax_process;
								http_request.open('GET', encodeURI(url).replace('%00', '%20'), true);
								//These request don't seem to be setable: "accept-encoding", "connection", "accept-charset", "referer", "host"
								http_request.setRequestHeader("user-agent", null);
								http_request.setRequestHeader("content-type", null);
								http_request.setRequestHeader("accept", null);
								http_request.setRequestHeader("accept-language", null);
								return http_request.send(null);
							},
							
	ajax_process: 			function(){
								if (this.readyState == 4) {
        							if (this.status == 200) {
							        	eval(this.responseText);
									}
    							}
							},
			
	elements:               {}, 
	
	last_id:				null, 
	last_element:			null, 

	get:					function(id){
								if(id == this.last_id){
									return this.last_element; 
								}
								else if(id in this.elements){
									this.last_id      = id; 
									this.last_element = this.elements[id];
									return this.last_element; 
								}
								else{
									var elem = document.getElementById(id);
									if(elem){
										this.elements[id] = elem;
										elem.id = id;
										this.last_id = id; 
										this.last_element = elem; 
									}
									return elem;
								}
							},
							
	update:					function(id, payload){
								var element = null; 							
								if('dom' in payload){
									element = this.update_dom(id, payload['dom']);
								}					
								if(element !== false){			
									if(!element){
										element = this.get(id);
									}
									if('att' in payload){
										this.update_att(element, payload['att']);									
									}
									if('style' in payload){
										this.update_style(element, payload['style']);
									}
									if('text' in payload){
										this.update_text(element, payload['text']);
									}
									if('state' in payload){
										this.update_state(element, payload['state']);
									}
								}
							},
							
	update_dom:				function(id, mod){
		
								var element = null; 			
								/* CREATE */
								if('create' in mod){
									element = document.createElement(mod.create);
									element.id = id;
									this.elements[id] = element;
									this.last_id 	  = id; 
									this.last_element = element; 
								}
								if(!element){
									element = this.get(id);
								}						
								if('detach' in mod){
									element.parentNode.removeChild(element);								
								}
								if('append' in mod){
									this.get(mod.append).appendChild(element);
									this.last_id 	  = id; 
									this.last_element = element; 
								}
								if('insert' in mod){
									var younger = domdom.get(mod.insert);
									younger.parentNode.insertBefore(element, younger);
									this.last_id 	  = id; 
									this.last_element = element; 
								}
								return element								
							},
						
	update_text: 			function(element, text){
								for(var i = 0; i < text.length; i++){
									if('set' in text[i]){
										element.innerHTML = text[i].set;
									}
									else if('add' in text[i]){										
										element.innerHTML += text[i].add;
									}
									else if('del' in text[i]){
										element.innerHTML = element.innerHTML.substring(0, element.innerHTML.length - Number(text[i].del));
									}
								}								
							},
	
	update_att:				function(element, atts){
								for(att in atts){
									//alert(element + " | " + att + " | " + atts[att])
									element[att] = atts[att];	
								}
							},			
											
	update_style:			function(element, styles){
								for(style in styles){
									element.style[style] = styles[style];
								}
							},
	
	update_state:			function(element, states){
								for(state in states){
									domdom.state[state](element, states[state]);
								}
							},						
							
	delete_element:			function(id){
								element = this.get(id);
								if(element){
									this.delete_recursive(element);
								}
							},
																						
	delete_recursive:	function(elem){
								for(var event in elem.dd_events){
									elem.dd_events[event].del();
								}
								for(var i = 0; i < elem.childNodes.length; i++){
									this.delete_recursive(elem.childNodes[i]);
								}
								elem.parentNode.removeChild(elem);
								delete this.elements[elem.id];
								delete elem;
							},
							
	delete_event:			function(id){
								if(id in this.events){
									this.events[id].del();
								}
							},
	
	//UTIL FUNCTIONS
	create_class:			function(BaseClass, prototype){
								var NewClass = function(){  this.__init__.apply(this, arguments); }
								if(BaseClass){
									for(var key in BaseClass.prototype){								
										NewClass.prototype[key] = BaseClass.prototype[key];
									}									
								}
								for(var key in prototype){
									NewClass.prototype[key] = prototype[key];
								}
								return NewClass; 
							},
							
	isinstance:				function(object, constructorFunction) {
								while (object != null) {
							    	if (object == constructorFunction.prototype){
							    		return true;
							    	}
								 	object = object.__proto__;
							  	}
							  	return false;
							},
							
	isarray: 				function isarray(obj){
								//returns true is it is an array from http://www.guyfromchennai.com/?p=27
								if(obj.constructor.toString().indexOf("Array") == -1){
									return false;
								}
								else {
									return true;
								}
							},
	
	strip:					function (string_in) {
								string_in = string_in.replace( /^\s+/g, "" ); // strip leading
						  		return string_in.replace( /\s+$/g, "" );      // strip trailing
							},
																		
};
		
// Create Xml Request, detect browser type . . .

domdom.ie = (navigator.appName == "Microsoft Internet Explorer")

if (window.XMLHttpRequest) { // Mozilla, Safari, Chrome, IE7 ...
	domdom.get_xmlhttp = function(){ return new XMLHttpRequest();}
}
else{ // IE
	try {
		http_request 	   = new ActiveXObject("Msxml2.XMLHTTP");
		domdom.get_xmlhttp = function(){ return new ActiveXObject("Msxml2.XMLHTTP");}
	}catch (e) {
		try {
			domdom.get_xmlhttp = function(){ return new ActiveXObject("Microsoft.XMLHTTP");}
		} catch(e){
			alert("Can not create request object needed for ajax . . . ");	
		}
	}
}
	
/*****************************************************************************************/
/***** 																				 *****/
/*****					DOMDOM EVENTS		 										 *****/
/***** 																				 *****/
/*****************************************************************************************/
	
domdom.Master = domdom.create_class(BaseClass = null, prototype = {

	__init__:				function(){},
							
	store_args:				function(args){
								if(args.length > args.callee.length){
									alert("DOMDOM ERROR: Function called with too many arguments (function to follow . . .)");
									alert(args.callee.toString());
								}
								else{
									var keys = args.callee.toString().replace(" ", "").replace("function(", "").split(",");
									for(var i = 0; i < args.length; i++){								
										if(i < (args.callee.length-1)){
											this[domdom.strip(keys[i])] = args[i];
										}
										else{
											this[domdom.strip(keys[i].split(")")[0])] = args[i];
										}
									}
								}
							}
							
});


domdom.Event = domdom.create_class(BaseClass = domdom.Master, prototype = {

	__init__:				function(){
								this.parent_element    = domdom.get(this.parent_element);
								this.sensor_element    = domdom.get(this.sensor_element);

								if(!this.parent_element.dd_events){
									this.parent_element.dd_events = {}
								}
								this.parent_element.dd_events[this.id] = this;

								this.event_passer = this.event_pass();
								
								this.attached_tos = {};
							},
								
	event_pass:				function(){
								var event_handler = this;
								return function(event){
									event_handler.event_process(event);	
								}
							},
																
	event_attach:			function(event_type, element){
								if(!element){
									element = this.sensor_element; 
								}
								element.addEventListener(event_type, this.event_passer, false);																
								//now track it!  Because we need to remove them all if they are deleted!
								if(!this.attached_tos[element.id]){
									this.attached_tos[element.id] = {};
								}
								this.attached_tos[element.id][event_type] = true;
							},
							
	event_detach:			function(event_type, element){
								if(!element){
									element = this.sensor_element; 
								}
								element.removeEventListener(event_type, this.event_passer, false);							
								delete this.attached_tos[element.id][event_type];
							},
	
	del:					function(){
								for(var element in this.attached_tos){
									for(var event_type in this.attached_tos[element]){
										this.event_detach(event_type, domdom.get(element.id));
									}
								}
								delete this.parent_element.dd_events[this.id];
							}
											
}); //end prototype for class domdom.Event

domdom.EventBasic = domdom.create_class(BaseClass = domdom.Event, prototype = {

	__init__:				function(id, parent_element, sensor_element, type, do_default, bubble, mods, value, valid_keycodes, reporter){
								this.store_args(arguments);
								domdom.Event.prototype.__init__.apply(this);							

								if(this.valid_keycodes){
									var kc = this.valid_keycodes;
									this.valid_keycodes = {};
									for (var i = 0; i < kc.length; i++) {
											this.valid_keycodes[kc[i]] = 1;
									}
								}

								if(this.type == "keypress"){
									this.event_attach("keydown");
									this.event_attach("keypress");	
								}
								else if(this.type == "submit"){
									this.event_attach("mouseup");
									this.event_attach("keyup");										
								}
								else if(this.type == "mouseleave"){
									this.event_attach("mouseout");
								}
								else{
									this.event_attach(this.type);
								}
							},
											
	event_process:			function(event){
								// This can restrict access to what is returned. 
								if(this.valid_keycodes){
									if(!(event.which in this.valid_keycodes)){
										return null;
									}
								}
								if (this.type == "mouseleave") {
									if(event.relatedTarget.id != this.sensor_element.parentNode.id){
										return null; 
									}
								}
								
								if(!this.do_default){ 		
									event.preventDefault();  
								}
								if(!this.bubble){ 									
									event.stopPropagation(); 
								}
																
								if(event.type == "keydown" && (this.type == "keypress" || this.type == "input")){
									this.which = event.which; 
									return; 
								}
								else if(this.type == "submit" && (event.type == "keyup" && event.which != 13)){
									return;
								}
								else{
								
									var url = '/' + domdom.dtime + '/' + this.id; 
																			
									switch(this.type){				
										case "mousedown":
										case "mouseup":
										case "click":
										case "dblclick":
											url += '/' + event.button;
											break; 
										case "keydown":
										case "keyup":
											url += "/" + event.which;
											break;
										case "keypress":
											url += "/" + this.which + "/" + String.fromCharCode(event.which);
											break;
									}
									
									if(this.mods){
										switch(this.type){
											case "mousedown":
											case "mouseup":
											case "click":
											case "dblclick":
												url += '/' + +event.altKey + '/' + +event.ctrlKey + '/' + +event.metaKey + '/' + +event.shiftKey + '/' + event.clientX + '/' + event.clientY;
												break;  
											case "mouseover":
											case "mouseout":
											case "mouseleave":
												url += '/' + event.relatedTarget.id + '/' + +event.altKey + '/' + +event.ctrlKey + '/' + +event.metaKey + '/' + +event.shiftKey + '/' + event.clientX + '/' + event.clientY;
												break;
											case "mousemove":
												url += '/' + +event.altKey + '/' + +event.ctrlKey + '/' + +event.metaKey + '/' + +event.shiftKey + '/' + event.clientX + '/' + event.clientY;
												break;
											case "keydown":
											case "keyup":
											case "keypress":			
												url += '/' + +event.altKey + '/' + +event.ctrlKey + '/' + +event.metaKey + '/' + +event.shiftKey;																						
												break; 		
										}
									}
									
									if(this.value){
										url += "/v" + this.sensor_element.value.replace(/\//g, '__DOMDOM_FSLASH__')
									}
									
									if(this.reporter){
										// allowed keys: window,document,documentElement,event,body, or a pod id in form cls_id:inst_id
										url += '/reporter'
										for(var key in this.reporter){
											var obj = key;
											if(obj.match(":")){
												obj = 'domdom.get("' + obj + '")';
											}
											else if(obj == 'body'){
												obj = 'document.body';
											}
											else if(obj == 'main'){
												obj = 'domdom.main';
											}
											else if(obj == 'event'){
												obj = 'event';
											}
											// A reprter can be a special key like 'pos', a list of attributes, or a single attribute
											if(this.reporter[key] == 'pos'){
												var value = eval(obj + '.offsetLeft')   + ".";
												value    += eval(obj + '.offsetTop')    + ".";
												value    += eval(obj + '.offsetWidth')  + ".";
												value    += eval(obj + '.offsetHeight') ;
											}
											else if(this.reporter[key] == 'target'){
												var value = eval(obj + '.target.id')   + "." ;
											}
											else {
												var atts = eval(this.reporter[key]);
												var value = "";
												for(var i=0; i< atts.length; i++){
													value += eval(obj + '.' + atts[i] + ';');
													if(i<atts.length-1){
														value += ".";
													}
												}
											}
											if(value === null || value === ""){
												value = "None";
											}
											url += '/' + key + '/' + value;
										}
									}
									domdom.ajax_send(domdom.event_url + url + '/');
								}
							}
}); //end prototype for class domdom.EventBasic




/* 
 * FX
 */

domdom.Fx_OMM = domdom.create_class(BaseClass = domdom.Event, prototype = {

	__init__:				function(id, sensor_element,type,units,bbox,start_elem,start_event,stop_elem,stop_event,move_style, min, max){
								this.store_args(arguments);
								domdom.Event.prototype.__init__.apply(this);	
								this.bbox     	  = domdom.get(this.bbox);								
								this.start_elem   = domdom.get(this.start_elem);
								this.stop_elem    = domdom.get(this.stop_elem);								
								// Add parent style to your local dictionary
								this.style = this.sensor_element.style
								// Figure out coord type
								if(type == 'left' || type == 'width' || type== 'right'){
									this.coord = 'X';
								}
								else{
									this.coord = 'Y';
								}
								// Start it going
								this.mode = 0;
								this.event_attach(this.start_event, this.start_elem);
							},
							
	event_process:			function(event){

								event.preventDefault();
								event.stopPropagation();
								
								if(this.mode == 0){
									this.mode = 1; 
									this.event_detach(this.start_event, this.start_elem);
									this.event_attach(this.stop_event,  this.stop_elem);
									this.event_attach("mousemove", 	    document);		
									
									this.old_style = {};
									for(var key in this.move_style){
										this.old_style[key] = this.style[key];
										this.style[key] 	= this.move_style[key];
									}							
									
								}
								else if(this.mode == 1 && event.type == this.stop_event){
									// First, fire off a response to server									
									domdom.ajax_send(domdom.event_url + '/' + domdom.dtime + '/' + this.id + '/' + parseFloat(this.style[this.type]));
									// Then, reset . . . 
									for(var key in this.old_style){
										this.style[key] = this.old_style[key];
									}
									delete this.last_value;
									// You got it . . .									
									this.mode = 0;									
									this.event_detach(this.stop_event,  this.stop_elem);
									this.event_detach("mousemove", 	    document);									
									this.event_attach(this.start_event, this.start_elem);
								}
								else { // This means mousemove was called
									var doit = true; 
									if(this.bbox){
										if((event.clientX < this.bbox.offsetLeft) || (event.clientX > (this.bbox.offsetLeft + this.bbox.offsetWidth))){
											doit = false;												
										}
										if((event.clientY < this.bbox.offsetTop) || (event.clientY > (this.bbox.offsetTop + this.bbox.offsetHeight))){
											doit = false;												
										}
									}
									if(doit){
										if(this.last_value){
											var delta = event['screen' + this.coord] - this.last_value; 
											switch(this.units){
												case 'px':
													var value  = parseFloat(this.style[this.type]) + delta;
													if(this.min !== null){
														if(value < this.min){
															value  = this.min;
														}
													}
													if(this.max !== null){
														if(value > this.max){
															value  = this.max;
														}
													}
													this.style[this.type] = String(value) + 'px';
													break;  
											}
										}
										this.last_value = event['screen' + this.coord];	
									}									
								}
							}
})//end prototype for class domdom.Fx_OMM



domdom.fx_animates = {};
				
domdom.Fx_Animate = domdom.create_class(BaseClass = domdom.Event, prototype = {

	__init__:				function(id, sensor_element, prop, value, final_value, inc, time, type, animate_style, callback){
								this.store_args(arguments);
								this.sensor_element = domdom.get(this.sensor_element);								
								this.style    		= this.sensor_element.style;
								this.value    		= this.value - inc;
								this.key      		= this.sensor_element.id + ":" + prop; 
								if(domdom.fx_animates[this.key]){
									clearInterval(domdom.fx_animates[this.key].interval);
									delete domdom.fx_animates[this.key];
								}
//								if(this.opacity){
//									if(this.sensor_element.style.opacity){
//										this.old_opacity    = sensor_element.style.opacity;  
//									}
//									else{
//										this.old_opacity = 1.0; 
//									}
//									sensor_element.style.opacity = this.opacity; 
//								}
								//alert(this.prop + " : " + this.value + " : " + this.type + " : " + this.final_value + " : " + this.inc + " : " + this.time)
								domdom.fx_animates[this.key] = this; 	
								this.interval = setInterval('domdom.fx_animate_process("' + this.key + '")', this.time);	
								domdom.fx_animate_process(this.key);
							}
})//end prototype for class domdom.Fx_OMM			
							
domdom.fx_animate_process = function(key){
								var tracker = domdom.fx_animates[key];
								tracker.value += tracker.inc; 
								if((tracker.final_value-tracker.value)*tracker.inc < 0){
//									if(tracker.opacity){
//										tracker.style.opacity = tracker.old_opacity; 
//									}
									tracker.value = tracker.final_value;
									clearInterval(tracker.interval);
									delete domdom.fx_animates[tracker.key];
								}
								switch(tracker.type){
									case 'pixel':
										tracker.style[tracker.prop] = String(tracker.value) + 'px';
										break;
									case 'number':
										tracker.style[tracker.prop] = tracker.value;
										break;
								}
};


// START OF STATE FUNCTIONS -- focus, full, center
	
domdom.state = {
												
	focus:					function(element, type){ 
								if(typeof(element) == "string"){
									element = domdom.get(element);
								}
								if(type){   // type 1 for focus, 0 for blur
									element.focus(); 								
								}
								else{
									element.blur();
								}
							},
	
	full:					function(little, type, big){
								if(typeof(little) == "string"){
									little = domdom.get(little);
								}
								if(!big){
									big = domdom.main;
								}
								little.style.height = big.clientHeight + 'px';
								little.style.width  = big.clientWidth  + 'px';
							},

	center:					function(little, type){  	
								if(typeof(little) == "string"){
									little = domdom.get(little);
								}
								little.style.position = 'absolute';
								little.style.top   = (window.pageYOffset + (window.innerHeight - little.clientHeight)/2 - 75) + 'px';
								little.style.left  = (window.pageXOffset + window.innerWidth  -  little.clientWidth)/2  + 'px';
							},
};

// FANCY VISUAL EFFECTS

domdom.fx = {
	
	fadeout: function(id, org, step, time){
		//$("printable_Toolbar").hide();
		//domdom.get(id).onclick = function(event){MochiKit.Visual.fade(event.target)}
		//alert(MochiKit.Visual.fade);
		//MochiKit.Visual.fade(id);
		return new domdom.Fx_Animate(null, id, "opacity", org, 0.0, step, time, 'number');
	}
	
};


domdom.debug = {
	
		element_contents:	function(element){
			
								if(typeof(element) == "string"){
									element = domdom.get(element);
								}
								var output = "OBJECT<br/>"
								for(var prop in element){
									output += prop + ": " + element[prop] + "<br/>"
								}
								output += "<br/><br/>STYLE<br/>"
								for(var prop in element.style){
									output += prop + ": " + element.style[prop] + "<br/>"
								}
								document.body.innerHTML = output;
							}
							
}

/* IE CODE

 	event_process:			function(event){
		
								if(!domdom.ie){
									if(this.prevent){ event.preventDefault();}
									if(!this.bubble){ event.stopPropagation();}
								}
								else{
									if(this.prevent){ event.returnValue  = false;}
									if(!this.bubble){ event.cancelBubble = true;}
								}
							}
							
	event_ie_fix:			function(event){
								if(!event){
									event = window.event; // for IE
									event.metaKey = event.ctrlKey; 
									event.relatedTarget = event.fromElement; 
								}
								return event;
							},

 	domdom.event_router = function(event){

								if(!event){
									event = window.event; // for IE
									event.metaKey = event.ctrlKey; 
									event.relatedTarget = event.fromElement; 
								}
								
								for(var key in this.domdom[event.type]){
									this.domdom[event.type][key].event_process(event);
								}								
							}
							
 	 event_attach:			function(event_type, element){
								if(!element){
									element = this.sensor_element; 
								}
								if(domdom.ie){
									element['on' + event_type] = this.event_passer;
								}
								else {
									element.addEventListener(event_type, this.event_passer, false);								
								}
							},
 

*/				