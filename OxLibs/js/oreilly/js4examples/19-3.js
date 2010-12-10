/**
 * PortableDrag.js:
 * beginDrag() is designed to be called from an onmousedown event handler.
 * elementToDrag may be the element that received the mousedown event, or it
 * may be some containing element.  event must be the Event object for the
 * mousedown event.  This implementation works with both the DOM Level 2
 * event model and the IE Event model.
 **/
function beginDrag(elementToDrag, event) {
    // Compute the distance between the upper-left corner of the element
    // and the mouse click. The moveHandler function below needs these values.
    var deltaX = event.clientX - parseInt(elementToDrag.style.left);
    var deltaY = event.clientY - parseInt(elementToDrag.style.top);

    // Register the event handlers that will respond to the mousemove events
    // and the mouseup event that follow this mousedown event.  
    if (document.addEventListener) {  // DOM Level 2 Event Model
	// Register capturing event handlers
        document.addEventListener("mousemove", moveHandler, true);
	document.addEventListener("mouseup", upHandler, true);
    }
    else if (document.attachEvent) {  // IE 5+ Event Model
	// In the IE Event model, we can't capture events, so these handlers
	// are triggered when only if the event bubbles up to them.
	// This assumes that there aren't any intervening elements that
	// handle the events and stop them from bubbling.
	document.attachEvent("onmousemove", moveHandler);
	document.attachEvent("onmouseup", upHandler);
    }
    else {                            // IE 4 Event Model
	// In IE 4 we can't use attachEvent(), so assign the event handlers
	// directly after storing any previously assigned handlers so they 
        // can be restored.  Note that this also relies on event bubbling.
	var oldmovehandler = document.onmousemove;
	var olduphandler = document.onmouseup;
	document.onmousemove = moveHandler;
	document.onmouseup = upHandler;
    }

    // We've handled this event.  Don't let anybody else see it.  
    if (event.stopPropagation) event.stopPropagation();   // DOM Level 2
    else event.cancelBubble = true;                       // IE

    // Now prevent any default action.
    if (event.preventDefault) event.preventDefault();     // DOM Level 2
    else event.returnValue = false;                       // IE

    /**
     * This is the handler that captures mousemove events when an element
     * is being dragged.  It is responsible for moving the element.
     **/
    function moveHandler(e) {
	if (!e) e = window.event;  // IE event model

        // Move the element to the current mouse position, adjusted as
	// necessary by the offset of the initial mouse click.
	elementToDrag.style.left = (e.clientX - deltaX) + "px";
	elementToDrag.style.top = (e.clientY - deltaY) + "px";

	// And don't let anyone else see this event.
	if (e.stopPropagation) e.stopPropagation();       // DOM Level 2
	else e.cancelBubble = true;                       // IE
    }

    /**
     * This is the handler that captures the final mouseup event that
     * occurs at the end of a drag.
     **/
    function upHandler(e) {
	if (!e) e = window.event;  // IE event model

	// Unregister the capturing event handlers.
	if (document.removeEventListener) {    // DOM Event Model
	    document.removeEventListener("mouseup", upHandler, true);
	    document.removeEventListener("mousemove", moveHandler, true);
	}
	else if (document.detachEvent) {       // IE 5+ Event Model
	    document.detachEvent("onmouseup", upHandler);
	    document.detachEvent("onmousemove", moveHandler);
	}
	else {                                 // IE 4 Event Model
	    document.onmouseup = olduphandler;
	    document.onmousemove = oldmovehandler;
	}

	// And don't let the event propagate any further.
	if (e.stopPropagation) e.stopPropagation();       // DOM Level 2
	else e.cancelBubble = true;                       // IE
    }
}
