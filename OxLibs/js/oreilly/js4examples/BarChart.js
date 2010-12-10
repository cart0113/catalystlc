/**
 * BarChart.js:
 * This file defines makeBarChart(), a function that creates a bar chart to
 * display the numbers from the data[] array. The chart is a block element
 * inserted at the current end of the document.  The overall size of the chart 
 * is specified by the optional width and height arguments, which include the
 * space required for the chart borders and internal padding.  The optional
 * barcolor argument specifies the color of the bars. The function returns the
 * chart element it creates, so the caller can further manipulate it by
 * setting a margin size, for example.
 * 
 * Import this function into an HTML file with code like this:
 *    <script src="BarChart.js"></script>
 * Use this function in an HTML file with code like this:
 *    <script>makeBarChart([1,4,9,16,25], 300, 150, "yellow");</script>
 **/
function makeBarChart(data, width, height, barcolor) {
    // Provide default values for the optional arguments
    if (!width) width = 500;
    if (!height) height = 350;
    if (!barcolor) barcolor = "blue";
    
    // The width and height arguments specify the overall size of the
    // generated chart. We have to subtract the border and padding
    // sizes from this to get the size of the element we create.
    width -= 24;  // subtract 10px padding and 2px border left and right
    height -= 14; // Subtract 10px top padding and 2px top and bottom border

    // Now create an element to hold the chart.  Note that we make the chart
    // relatively positioned so that can have absolutely positioned children,
    // but it still appears in the normal element flow.
    var chart = document.createElement("DIV");
    chart.style.position = "relative";          // Set relative positioning
    chart.style.width = width + "px";           // Set the chart width
    chart.style.height = height + "px";         // Set the chart height
    chart.style.border = "solid black 2px";     // Give it a border
    chart.style.paddingLeft = "10px";           // Add padding on the left
    chart.style.paddingRight = "10px";          // and on the right
    chart.style.paddingTop = "10px";            // and on the top
    chart.style.paddingBottom = "0px";          // but not on the bottom
    chart.style.backgroundColor = "white";      // Make chart background white

    // Compute the width of each bar
    var barwidth = Math.floor(width/data.length);
    // Find largest number in data[].  Note clever use of Function.apply()
    var maxdata = Math.max.apply(this, data);
    // The scaling factor for the chart: scale*data[i] gives height of a bar
    var scale = height/maxdata;

    // Now loop through the data array and create a bar for each datum
    for(var i = 0; i < data.length; i++) {
        var bar = document.createElement("div"); // Create div for bar
        var barheight = data[i] * scale;         // Compute height of bar
        bar.style.position = "absolute";         // Set bar position and size
        bar.style.left = (barwidth*i+1+10)+"px"; // Add bar border & chart pad
        bar.style.top = height-barheight+10+"px";// Add chart padding
        bar.style.width = (barwidth-2) + "px";   // -2 for the bar border
        bar.style.height = (barheight-1) + "px"; // -1 for the bar top border
        bar.style.border = "solid black 1px";    // Bar border style
        bar.style.backgroundColor = barcolor;    // Bar color
        bar.style.fontSize = "1px";              // IE bug workaround
        chart.appendChild(bar);                  // Add bar to chart
    }

    // Now add the chart we've built to the document body
    document.body.appendChild(chart);

    // Finally, return the chart element so the caller can manipulate it
    return chart;
}
