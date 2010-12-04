// Recursively reverse all nodes beneath Node n, and reverse Text nodes
function reverse(n) { 
    if (n.nodeType == 3 /*Node.TEXT_NODE*/) { // Reverse Text nodes
        var text = n.data;                        // Get content of node
        var reversed = "";
        for(var i = text.length-1; i >= 0; i--)   // Reverse it
            reversed += text.charAt(i);
        n.data = reversed;                        // Store reversed text
    }
    else { // For non-Text nodes recursively reverse the order of the children
        var kids = n.childNodes;
        var numkids = kids.length;
        for(var i = numkids-1; i >= 0; i--) {       // Loop through kids
            reverse(kids[i]);                       // Recurse to reverse kid
            n.appendChild(n.removeChild(kids[i]));  // Move kid to new position
        }
    }
}
