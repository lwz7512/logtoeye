/**
 * Created with PyCharm.
 * User: lwz
 * Date: 5/22/13
 * Time: 10:58 PM
 * To change this template use File | Settings | File Templates.
 */

/**
 * juqerylized ul/li component...
 * @param parent, the jquery container to hold the ul/li
 * @constructor
 */
function UList(parent){
    this.ul = $("<ul/>");
    this.ul.css({padding: 0, margin: 0});
    this.ul.appendTo(parent);
    this.colors = {'alert': '#FF0000', 'crit': '#FFB90F', 'error': '#FFFF00', 'warn': '#0000FF'};

    this.highliteItems = function(items){
        this.ul.empty();

        //hide the showed tooltip
        var tooltip = $("p.tip");
        if(tooltip) tooltip.hide().empty().css({top: 0, left: 0} );

        for(var i=0; i<items.length; i++){
            this.ul.append(this.__createLi(items[i]));
        }
    };

    this.__createLi = function(obj){
        var li = $("<li/>");
        li.css('list-style-type', 'none');
        li.css('margin', '4px');
        li.css('font-size', '14px');
        li.css('color', this.colors[obj['level']]);

        li.attr('title', obj['message']);
        li.append(obj['name']);

        return li;
    }

}//end of ulist