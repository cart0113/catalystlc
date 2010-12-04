// Define a NodeFilter function to accept only <img> elements
function imgfilter(n) {
   if (n.tagName == 'IMG') return NodeFilter.FILTER_ACCEPT;
   else return NodeFilter.FILTER_SKIP;
}

// Create a NodeIterator to find <img> tags
var images = document.createNodeIterator(document, // traverse entire document
	/* only look at Element nodes */ NodeFilter.SHOW_ELEMENT,
	  /* filter out all but <img> */ imgfilter,
	  /* unused in HTML documents */ false);

// Use the iterator to loop through all images and do something with them
var image;
while((image = images.nextNode()) != null) {
    image.style.visibility = "hidden";  // Process the image here
}
