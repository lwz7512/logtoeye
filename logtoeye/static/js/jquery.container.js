/**
 * Created with PyCharm.
 * User: lwz
 * Date: 5/15/13
 * Time: 10:05 PM
 */


/**
 * general html container in oop style based on jquery.js
 * @param w the container width like: 100px, or 90%;
 * @param h the container height like: 100px, or 90%;
 * @constructor
 *
 * Usage:
 *
 *  var row = new JQBox("99%", "100px");
    row.addClass("row-box");
    row.append("hello world");
    row.appendTo("body");
    //$("body").append(row.element);
    row.id = 'first_dyna_row';
    console.log("the row id: "+row.id);

 * class name definition of row-box:
    *   .row-box {
            border: 1px solid #ccc;
            border-radius: 10px;
            background-color: #f00;
            padding: 4px; margin: 2px;
        }
 *
 */
function JQBox(w, h){
    this.__container = $("<div/>");
    this.__container.css('width', w);
    this.__container.css('height', h);
    this.element = this.__container.get(0);

    this.__defineGetter__('id', function(){
        return this.__container.attr('id');
    });
    this.__defineSetter__('id', function(v){
       this.__container.attr('id', v);
    });
}
JQBox.prototype.css = function(style, value){
    this.__container.css(style, value);
};
JQBox.prototype.addClass = function(className){
    this.__container.addClass(className);
};
JQBox.prototype.removeClass = function(className){
    this.__container.removeClass(className);
};
JQBox.prototype.appendTo = function(parent){
    this.__container.appendTo(parent);
};
JQBox.prototype.append = function(child){
    this.__container.append(child);
};
JQBox.prototype.addChild = function(child){
    this.__container.append(child);
};
JQBox.prototype.clone = function(){
    return this.__container.clone();
};


/**
 * panel component based on jquery-ui.css
 * @param title
 * @param w
 * @param h
 * @constructor
 *
 * Usage:
 *
 *  var widget = new JQWidget('Sample Panel', '300px', '200px');
    widget.appendTo("body");
    widget.addChild("hello panel!");

 */
function JQWidget(title, w, h){
    JQBox.apply(this, [w, h]);

    //reference jquery-ui.css class name...
    this.addClass('ui-widget ui-widget-content ui-corner-all');
    this.css('position', 'relative');
    this.css('font-size', '12px');

    var title_bar = $("<div/>");
    //reference jquery-ui.css class name...
    title_bar.addClass('ui-widget-header ui-corner-top ui-helper-clearfix');
    title_bar.css('padding', '.3em .2em .2em .3em');
    title_bar.css('position', 'relative');
    title_bar.css('border-left', '0 none');
    title_bar.css('border-right', '0 none');
    title_bar.css('border-top', '0 none');

    var title_span = $("<span/>").append(title);
    title_span.css('float', 'left');
    title_span.css('margin', '.1em 0 .2em');
    title_span.appendTo(title_bar);

    this.addChild(title_bar);
}
JQWidget.prototype = JQBox.prototype;
