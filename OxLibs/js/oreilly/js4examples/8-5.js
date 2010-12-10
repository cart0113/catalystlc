function Circle(radius) {   // The constructor defines the class itself.
    // r is an instance property; defined and initialized in the constructor.
    this.r = radius;
}

// Circle.PI is a class property--it is a property of the constructor function.
Circle.PI = 3.14159;
 
// Here is a function that computes a circle area.
function Circle_area() { return Circle.PI * this.r * this.r; }

// Here we make the function into an instance method by assigning it
// to the prototype object of the constructor.
// Note: with JavaScript 1.2, we can use a function literal to
// define the function without naming it Circle_area.
Circle.prototype.area = Circle_area;

// Here's another function. It takes two circle objects as arguments and
// returns the one that is larger (has the larger radius). 
function Circle_max(a,b) {
    if (a.r > b.r) return a;
    else return b;
}

// Since this function compares two circle objects, it doesn't make sense as 
// an instance method operating on a single circle object. But we don't want
// it to be a standalone function either, so we make it into a class method
// by assigning it to the constructor function:
Circle.max = Circle_max;

// Here is some code that uses each of these fields:
var c = new Circle(1.0);      // Create an instance of the Circle class.
c.r = 2.2;                    // Set the r instance property.
var a = c.area();             // Invoke the area() instance method. 
var x = Math.exp(Circle.PI);  // Use the PI class property in our own computation.
var d = new Circle(1.2);      // Create another Circle instance.
var bigger = Circle.max(c,d); // Use the max() class method.
