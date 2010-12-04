/*
 * File: browser.js
 * Include with: <script SRC="browser.js"></script>
 * 
 * A simple "sniffer" that determines browser version and vendor.
 * It creates an object named "browser" that is easier to use than
 * the "navigator" object.
 */
// Create the browser object.
var browser = new Object();

// Figure out the browser major version.
browser.version = parseInt(navigator.appVersion);

// Now figure out if the browser is from one of the two
// major browser vendors. Start by assuming it is not.
browser.isNetscape = false;
browser.isMicrosoft = false;
if (navigator.appName.indexOf("Netscape") != -1) 
    browser.isNetscape = true;
else if (navigator.appName.indexOf("Microsoft") != -1)
    browser.isMicrosoft = true;
