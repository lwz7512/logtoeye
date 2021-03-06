//========== JSAnimationEngine ==========================
//----- 2013/05/10 @lwz7512 --------------

/**
 * Radar chart simulate the military scenery
 * @param canvas
 * @param radius
 * @constructor
 */
function RadarChart (canvas, radius) {        
    this.radius = radius;
    this.angle = 0;
    this.speed = Math.PI/180;
    this.ctx = canvas.getContext('2d');
    this.ctx.translate(radius, radius);
    this.colors = ["#FF0000", "#FFB90F", "#FFFF00", "#0000FF"];
    this.targets = [];//cache the targets to be shown
    this.circles_in_track = [3, 3+5, 3+5+8, 3+5+8+10];//12, 15, 17, 20
    this.list = null;//to be setted outside

    this.__last_level = null;

    this.onchanged = function(level){
        var highlitedItems = this.__searchTargetsBy(level);
        if(this.list) this.list.highliteItems(highlitedItems);//render the list
        console.log("level onchanged!");
    }

}//end of constructor


RadarChart.prototype.__drawTargets = function(){
    var currentPosition = this.angle/Math.PI % 2;
    var obj_groups = [0, 0, 0, 0];
    for(var i=0; i<this.targets.length; i++){
        if(this.targets[i]['level'] == 'alert') obj_groups[0] += 1;
        if(this.targets[i]['level'] == 'crit') obj_groups[1] += 1;
        if(this.targets[i]['level'] == 'error') obj_groups[2] += 1;
        if(this.targets[i]['level'] == 'warn') obj_groups[3] += 1;
    }

    var current_level;
    if(currentPosition>0 && currentPosition<1/2){//put in alert quadrant
        this.__draw_quadrant(0, obj_groups[0], this.colors[0]);
        current_level = "alert";
    }
    if(currentPosition>1/2 && currentPosition<1){//put in crit quadrant
        this.__draw_quadrant(Math.PI/2, obj_groups[1], this.colors[1]);
        current_level = "crit";
    }
    if(currentPosition>1 && currentPosition<3/2){//put in error quadrant
        this.__draw_quadrant(Math.PI, obj_groups[2], this.colors[2]);
        current_level = "error";
    }
    if(currentPosition>3/2 && currentPosition<2){//put in warn quadrant
        this.__draw_quadrant(-Math.PI/2, obj_groups[3], this.colors[3]);
        current_level = "warn";
    }

    if(current_level != this.__last_level){
        this.onchanged(current_level);
        this.__last_level = current_level;
    }
};

RadarChart.prototype.__searchTargetsBy = function(level){
    var results = [];
    for(var i in this.targets){
        if(this.targets[i]['level'] == level) results.push(this.targets[i]);
    }

    return results;
};

RadarChart.prototype.__draw_quadrant = function(offsetRadian, ptNum, circleColor){
    if(offsetRadian === undefined) offsetRadian = 0;
    if(circleColor === undefined) circleColor = "#FF0000";
    if(ptNum == 0) return;

    var filledTrackNum = 0;
    var semi_filled_num = 0;
    for(var t=0; t<this.circles_in_track.length; t++){
        if(this.circles_in_track[t]<ptNum) {
            filledTrackNum = t+1;
        }
    }
    if(filledTrackNum){
        semi_filled_num = ptNum - this.circles_in_track[filledTrackNum-1];
    }else{
        semi_filled_num = ptNum;
    }
    var each_l = 20;//radian length between each circle
    var ball;
    var trackNum = filledTrackNum + 1;
    for(var i=0; i<trackNum; i++){//each track
        var r = i*30+45;
        if (r > this.radius) break;//do not draw beyond the radar area

        var l_length_quarter = r*Math.PI/2;
        var circe_num = Math.floor(l_length_quarter/each_l);
        if(semi_filled_num && i == trackNum-1){//draw last track with remaining point
            circe_num = semi_filled_num;
        }
        //console.log("circe_num: "+circe_num);
        for(var j=0; j<circe_num; j++){
            var n = each_l*(j+1)/r - 0.05 + offsetRadian;
            var x = r*Math.cos(n);
            var y = r*Math.sin(n);
            ball = new Ball(8,circleColor, "#666666");
            ball.x = x;
            ball.y = y;
            //console.log("n, x, y: "+n+","+x+","+y);
            ball.draw(this.ctx);
        }
    }
};


RadarChart.prototype.__shadeColor = function(color, percent){
    var R = parseInt(color.substring(1,3),16);
    var G = parseInt(color.substring(3,5),16);
    var B = parseInt(color.substring(5,7),16);

    R = parseInt(R * (100 + percent) / 100);
    G = parseInt(G * (100 + percent) / 100);
    B = parseInt(B * (100 + percent) / 100);

    R = (R<255)?R:255;
    G = (G<255)?G:255;
    B = (B<255)?B:255;

    var RR = ((R.toString(16).length==1)?"0"+R.toString(16):R.toString(16));
    var GG = ((G.toString(16).length==1)?"0"+G.toString(16):G.toString(16));
    var BB = ((B.toString(16).length==1)?"0"+B.toString(16):B.toString(16));

    return "#"+RR+GG+BB;
};

RadarChart.prototype.addTarget = function(target) {
    var max = 104;
    this.targets.push(target);
    if(this.targets.length > max) this.targets.splice(0, 1);
};

RadarChart.prototype.removeTarget = function(tid) {
    for(var i=0; i<this.targets.length; i++){
        if(this.targets[i]['id'] == tid) {
            this.targets.splice(i, 1);
            break;
        }
    }
};

RadarChart.prototype.draw = function (ctx) {
    
    ctx.save();
    
    ctx.clearRect(0, 0, this.radius, this.radius);//clear bottom right
    ctx.clearRect(0, 0, this.radius, -this.radius);//clear top right
    ctx.clearRect(0, 0, -this.radius, this.radius);//clear bottom left
    ctx.clearRect(0, 0, -this.radius, -this.radius);//clear top left
    ctx.rotate(0);//reset context

    //draw black background
    ctx.arc(0, 0, this.radius, 0, (Math.PI * 2), true);
    ctx.fillStyle = "#000000";
    ctx.fill();

    //draw tracks
    var trackNum = Math.floor(this.radius/30);
    ctx.beginPath();
    for(var t = 0; t<trackNum; t++){
        ctx.arc(0, 0, 30+t*30, 0, (Math.PI * 2), true);
    }
    ctx.strokeStyle = "#333333";
    ctx.stroke();

    //draw axis
    ctx.beginPath();
	ctx.moveTo(-this.radius, 0);
	ctx.lineTo(this.radius, 0);
    ctx.moveTo(0, -this.radius);
    ctx.lineTo(0, this.radius);
	ctx.closePath();
	ctx.stroke();

    //draw text: Alert(red), Crit(orange), Error(yellow), Warn(blue)
    ctx.font = "bold 12px sans-serif";
    ctx.fillStyle = this.colors[0];
    ctx.fillText("Alert", 4, 12);//4th quadrant
    ctx.fillStyle = this.colors[1];
    ctx.fillText("Crit", -30, 12);//3th quadrant
    ctx.fillStyle = this.colors[2];
    ctx.fillText("Error", -30, -4);//2th quadrant
    ctx.fillStyle = this.colors[3];
    ctx.fillText("Warn", 4, -4);//1th quadrant

    this.__drawTargets();//draw the scanned targets

    //draw scanning pointer
    //*** rotate the pointer every time draw ***
    this.angle += this.speed;
    ctx.rotate(this.angle);
    var r = trackNum*30;
    for(var i = 0; i< 17; i++){//small sectors to composite the large arc
	    var color = "#00FF00";
	    ctx.beginPath();
	    //x, y, radius, start_angle, end_angle, anti-clockwise
	    ctx.arc(0, 0, r, 0, -Math.PI/72, true);
	    ctx.lineTo(0, 0);//up side
	    ctx.lineTo(r, 0);//down side
	    ctx.fillStyle = this.__shadeColor(color, -6*i);
	    ctx.fill();

	    ctx.rotate(-Math.PI/72+Math.PI/180);//draw next small sector
    }

    ctx.restore();

};//end of draw


function Ball (radius, color, borderColor) {
  if (radius === undefined) { radius = 40; }
  if (color === undefined) { color = "#ff0000"; }
  this.x = 0;
  this.y = 0;
  this.radius = radius;
  this.rotation = 0;
  this.scaleX = 1;
  this.scaleY = 1;
  this.color = utils.parseColor(color);
  this.borderColor = borderColor;
  this.lineWidth = 1;
}

Ball.prototype.draw = function (context) {
  context.save();
  context.translate(this.x, this.y);
  context.rotate(this.rotation);
  context.scale(this.scaleX, this.scaleY);
  
  context.strokeStyle = this.borderColor;
  context.lineWidth = this.lineWidth;
  context.fillStyle = this.color;
  context.beginPath();
  //x, y, radius, start_angle, end_angle, anti-clockwise
  context.arc(0, 0, this.radius, 0, (Math.PI * 2), true);
  context.closePath();
  context.fill();
  if (this.lineWidth > 0) {
    context.stroke();
  }

  context.restore();
};

function Line (beginX,beginY,endX,endY, color) {
	this.beginX=beginX;
	this.beginY=beginY;
	this.endX=endX;
	this.endY=endY;
	this.lineCap='round';
	this.color = color;	
}

Line.prototype.draw = function (context) {
	context.save();
	context.translate(this.x, this.y);  
  
	context.lineWidth = 2;  
	context.beginPath();
  
	context.moveTo(this.beginX, this.beginY);
	context.lineTo(this.endX, this.endY);

	context.closePath();
	context.strokeStyle=this.color; 
	context.lineCap=this.lineCap; // square round butt
	context.stroke();
  
  	context.restore();
};

function JSAnimationEngine (canvas) {
	window.JSEngineChildren = [];
	window.JSEngineFlag = true;
    window.JSEngineCounter = -1;
    window.lowcpu = false;
	window.JSEngineContext = canvas.getContext('2d');
	window.JSEngineEnterframe = function enterFrame () {

		if(!this.JSEngineFlag) return;
		window.requestAnimationFrame(JSEngineEnterframe, canvas);//request to redraw

		this.JSEngineCounter += 1;

        if(window.lowcpu){//slowdown the draw frequency to obtain a better performance
            if(this.JSEngineCounter % 4) return;
        }
		this.JSEngineContext.clearRect(0, 0, canvas.width, canvas.height);//***clear all before redraw...
		for(var i in this.JSEngineChildren){
			this.JSEngineChildren[i].draw(this.JSEngineContext);
		}

	};//end of enterframe

}//end of JSAnimationEngine

JSAnimationEngine.prototype.addChild = function (child) {
	window.JSEngineChildren.push(child);
};

JSAnimationEngine.prototype.run = function (lowcpu) {
    window.JSEngineFlag = true;
    if(lowcpu) window.lowcpu = true;
    window.JSEngineEnterframe();
};

JSAnimationEngine.prototype.stop = function () {
	window.JSEngineFlag = false;
};

/**
 * Normalize the browser animation API across implementations. This requests
 * the browser to schedule a repaint of the window for the next animation frame.
 * Checks for cross-browser support, and, failing to find it, falls back to setTimeout.
 * @param {function}    callback  Function to call when it's time to update your animation for the next repaint.
 * @param {HTMLElement} element   Optional parameter specifying the element that visually bounds the entire animation.
 * @return {number} Animation frame request.
 */
if (!window.requestAnimationFrame) {
  window.requestAnimationFrame = (window.webkitRequestAnimationFrame ||
                                  window.mozRequestAnimationFrame ||
                                  window.msRequestAnimationFrame ||
                                  window.oRequestAnimationFrame ||
                                  function (callback) {
                                    return window.setTimeout(callback, 17 /*~ 1000/60*/);
                                  });
}

/**
 * ERRATA: 'cancelRequestAnimationFrame' renamed to 'cancelAnimationFrame' to reflect an update to the W3C Animation-Timing Spec.
 *
 * Cancels an animation frame request.
 * Checks for cross-browser support, falls back to clearTimeout.
 * @param {number}  Animation frame request.
 */
if (!window.cancelAnimationFrame) {
  window.cancelAnimationFrame = (window.cancelRequestAnimationFrame ||
                                 window.webkitCancelAnimationFrame || window.webkitCancelRequestAnimationFrame ||
                                 window.mozCancelAnimationFrame || window.mozCancelRequestAnimationFrame ||
                                 window.msCancelAnimationFrame || window.msCancelRequestAnimationFrame ||
                                 window.oCancelAnimationFrame || window.oCancelRequestAnimationFrame ||
                                 window.clearTimeout);
}

/* Object that contains our utility functions.
 * Attached to the window object which acts as the global namespace.
 */
window.utils = {};

/**
 * Keeps track of the current mouse position, relative to an element.
 * @param {HTMLElement} element
 * @return {object} Contains properties: x, y, event
 */
window.utils.captureMouse = function (element) {
  var mouse = {x: 0, y: 0, event: null},
      body_scrollLeft = document.body.scrollLeft,
      element_scrollLeft = document.documentElement.scrollLeft,
      body_scrollTop = document.body.scrollTop,
      element_scrollTop = document.documentElement.scrollTop,
      offsetLeft = element.offsetLeft,
      offsetTop = element.offsetTop;
  
  element.addEventListener('mousemove', function (event) {
    var x, y;
    
    if (event.pageX || event.pageY) {
      x = event.pageX;
      y = event.pageY;
    } else {
      x = event.clientX + body_scrollLeft + element_scrollLeft;
      y = event.clientY + body_scrollTop + element_scrollTop;
    }
    x -= offsetLeft;
    y -= offsetTop;
    
    mouse.x = x;
    mouse.y = y;
    mouse.event = event;
  }, false);
  
  return mouse;
};

/**
 * Keeps track of the current (first) touch position, relative to an element.
 * @param {HTMLElement} element
 * @return {object} Contains properties: x, y, isPressed, event
 */
window.utils.captureTouch = function (element) {
  var touch = {x: null, y: null, isPressed: false, event: null},
      body_scrollLeft = document.body.scrollLeft,
      element_scrollLeft = document.documentElement.scrollLeft,
      body_scrollTop = document.body.scrollTop,
      element_scrollTop = document.documentElement.scrollTop,
      offsetLeft = element.offsetLeft,
      offsetTop = element.offsetTop;

  element.addEventListener('touchstart', function (event) {
    touch.isPressed = true;
    touch.event = event;
  }, false);

  element.addEventListener('touchend', function (event) {
    touch.isPressed = false;
    touch.x = null;
    touch.y = null;
    touch.event = event;
  }, false);
  
  element.addEventListener('touchmove', function (event) {
    var x, y,
        touch_event = event.touches[0]; //first touch
    
    if (touch_event.pageX || touch_event.pageY) {
      x = touch_event.pageX;
      y = touch_event.pageY;
    } else {
      x = touch_event.clientX + body_scrollLeft + element_scrollLeft;
      y = touch_event.clientY + body_scrollTop + element_scrollTop;
    }
    x -= offsetLeft;
    y -= offsetTop;
    
    touch.x = x;
    touch.y = y;
    touch.event = event;
  }, false);
  
  return touch;
};

/**
 * Returns a color in the format: '#RRGGBB', or as a hex number if specified.
 * @param {number|string} color
 * @param {boolean=}      toNumber=false  Return color as a hex number.
 * @return {string|number}
 */
window.utils.parseColor = function (color, toNumber) {
  if (toNumber === true) {
    if (typeof color === 'number') {
      return (color | 0); //chop off decimal
    }
    if (typeof color === 'string' && color[0] === '#') {
      color = color.slice(1);
    }
    return window.parseInt(color, 16);
  } else {
    if (typeof color === 'number') {
      color = '#' + ('00000' + (color | 0).toString(16)).substr(-6); //pad
    }
    return color;
  }
};

/**
 * Converts a color to the RGB string format: 'rgb(r,g,b)' or 'rgba(r,g,b,a)'
 * @param {number|string} color
 * @param {number}        alpha
 * @return {string}
 */
window.utils.colorToRGB = function (color, alpha) {
  //number in octal format or string prefixed with #
  if (typeof color === 'string' && color[0] === '#') {
    color = window.parseInt(color.slice(1), 16);
  }
  alpha = (alpha === undefined) ? 1 : alpha;
  //parse hex values
  var r = color >> 16 & 0xff,
      g = color >> 8 & 0xff,
      b = color & 0xff,
      a = (alpha < 0) ? 0 : ((alpha > 1) ? 1 : alpha);
  //only use 'rgba' if needed
  if (a === 1) {
    return "rgb("+ r +","+ g +","+ b +")";
  } else {
    return "rgba("+ r +","+ g +","+ b +","+ a +")";
  }
};

/**
 * Determine if a rectangle contains the coordinates (x,y) within it's boundaries.
 * @param {object}  rect  Object with properties: x, y, width, height.
 * @param {number}  x     Coordinate position x.
 * @param {number}  y     Coordinate position y.
 * @return {boolean}
 */
window.utils.containsPoint = function (rect, x, y) {
  return !(x < rect.x ||
           x > rect.x + rect.width ||
           y < rect.y ||
           y > rect.y + rect.height);
};

/**
 * Determine if two rectangles overlap.
 * @param {object}  rectA Object with properties: x, y, width, height.
 * @param {object}  rectB Object with properties: x, y, width, height.
 * @return {boolean}
 */
window.utils.intersects = function (rectA, rectB) {
  return !(rectA.x + rectA.width < rectB.x ||
           rectB.x + rectB.width < rectA.x ||
           rectA.y + rectA.height < rectB.y ||
           rectB.y + rectB.height < rectA.y);
};
