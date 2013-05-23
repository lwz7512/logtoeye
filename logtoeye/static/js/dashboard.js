/**
 * Created with PyCharm.
 * User: lwz
 * Date: 5/9/13
 * Time: 1:07 PM
 * To change this template use File | Settings | File Templates.
 */

WEB_SOCKET_SWF_LOCATION = "/static/flashsocket/WebSocketMain.swf";
WEB_SOCKET_DEBUG = true;

// socket.io specific code, connect to a namespace(endpoint)
var socket;
var DEBUG = true;

window.onload = init;


function init(){

    $(function(){$('*[title]').monnaTip();});

    build_widget_grid();

    var grid = createNginxUrlGrid("#resource-grid");
    register_widget('nginx.access.*', grid);

    var radar = createRadarChart('canvas');
    register_widget('nginx.error.*', radar);
    radar.list = new UList("#radar-list-placeholder");

    //FIXME, JUST FOR TEST...
    var now = new Date();
    var last_minute = now.getTime() - 60000;
    var llast_minute = now.getTime() - 2*60000;
    var lllast_minute = now.getTime() - 3*60000;
    var altObj_1 = {'id': "1",'name': 'ngnix.error.localhost', 'level': 'error', 'timestamp': now.getTime(), 'message': 'error details...'};
    var altObj_2 = {'id': "2",'name': 'ngnix.alert.localhost', 'level': 'alert', 'timestamp': last_minute, 'message': 'alert details...'};
    var altObj_3 = {'id': "3",'name': 'ngnix.crit.localhost', 'level': 'crit', 'timestamp': llast_minute, 'message': 'crit details...'};
    var altObj_4 = {'id': "4",'name': 'ngnix.warn.localhost', 'level': 'warn', 'timestamp': lllast_minute, 'message': 'warn details...'};
    radar.targets = [altObj_1, altObj_2, altObj_3, altObj_4];

    var plot_sio = createTimeSeries("#sio-chart-placeholder");
    register_widget('sio.cputime.minute', plot_sio);

    var plot_ngx = createTimeSeries("#nginx-chart-placeholder");
    register_widget('nginx.cputime.minute', plot_ngx);

    connect_to_sio();

}//end of init

//TODO, BUILD UI WITH JQUERY.CONTAINER ...
function build_widget_grid(){

    var secondRow_leftCell = new Cell('54.4%', '99%', 'left', false);
    var secondRow_rightCell = new Cell('44.6%', '99%', 'right', false);
    var thirdRow_leftCell = new Cell('54.4%', '99%', 'left', false);
    var thirdRow_rightCell = new Cell('44.6%', '99%', 'right', false);

    var secondRow = new JQBox('99%', '300px');
    secondRow.id = "second-row";
    secondRow.css('margin', '2px');
    secondRow.insertAfter($("#header"));
    secondRow.addChild(secondRow_leftCell);
    secondRow.addChild(secondRow_rightCell);

    var thirdRow = new JQBox('99%', '300px');
    thirdRow.id = "third-row";
    thirdRow.css('margin', '2px');
    thirdRow.insertAfter(secondRow);
    thirdRow.addChild(thirdRow_leftCell);
    thirdRow.addChild(thirdRow_rightCell);


    secondRow_leftCell.addChild("<table id='resource-grid'></table>");// top left data grid
    var radar_widget = new JQWidget('Alert Scanning Radar', '100%', '100%');
    radar_widget.addChild("<canvas id='canvas' width='270' height='270'/>");// top right radar
    var radar_list_box = new Cell('47%', '90%', 'right', false);// alert message list
    radar_list_box.id = "radar-list-placeholder";
    radar_list_box.css('overflow', 'hidden');//clip the content
    radar_widget.addChild(radar_list_box);
    secondRow_rightCell.addChild(radar_widget);

    var sio_widget = new JQWidget('SocketIO server CPU time', '100%', '100%');
    var chart_sio = new JQBox('100%', '92%');// sio chart
    chart_sio.id = "sio-chart-placeholder";
    chart_sio.css('font-size', '14px').css('line-height', '1.2em');
    sio_widget.addChild(chart_sio);
    thirdRow_leftCell.addChild(sio_widget);

    var nginx_widget = new JQWidget('Nginx server CPU time', '100%', '100%');
    var chart_nginx = new JQBox('100%', '92%');// nginx chart
    chart_nginx.id = "nginx-chart-placeholder";
    chart_nginx.css('font-size', '14px').css('line-height', '1.2em');
    nginx_widget.addChild(chart_nginx);
    thirdRow_rightCell.addChild(nginx_widget);

}

function register_widget(name, wgt_obj){
    if(!$.widgets) $.widgets = {};
    $.widgets[name] = wgt_obj;
}


function get_widget(name){
    if(!$.widgets) $.widgets = {};
    return $.widgets[name];
}


function createNginxUrlGrid(div){

    //create jqGrid...
    var offset = 26;//for chrome, 2013/05/08 by lwz
    var userAgentVar = navigator.userAgent;
    if (userAgentVar.indexOf("Firefox") != "-1"){
        offset = 0;
    }

    return $(div).jqGrid({//create push message grid
        height: 250,
        autowidth: true,
        datatype: "json",
        scrollOffset: offset,//Monkey Patch here set the value, so the horizontal scrollbar disappeared!
        colNames:['Name','Url', 'Value', 'Timestamp','Original'],
        colModel:[
            {name:'name',index:'name', width:150, align:"right", sortable:false},
            {name:'resource',index:'resource', width:150, align:"right", sortable:false},
            {name:'value',index:'value', width:100, align:"right", sorttype:"float"},
            {name:'timestamp',index:'timestamp', width:100, align:"right", sortable:false},
            {name:'original',index:'original', width:130,align:"center",sortable:false}
        ],
        rowNum:10,
        hidegrid: false, //hide the fold button in title-bar
        caption: "Nginx URL Request Time Display"
    });//end of jqgrid init

}//end of createGrid

function createRadarChart(canvas){
    var element = document.getElementById(canvas);
    var engine = new JSAnimationEngine(element);
    var radar = new RadarChart(element, element.height/2);
    engine.addChild(radar);
    engine.run(true);
    //engine.stop();

    return radar;
}


/**
 * create one series line chart
 * @param div
 * @returns {*}
 */
function createTimeSeries(div){
    var oneHourAgo = 60*60*1000;
    var localNow = new Date();
    var utcOffsetMiliSec = localNow.getTimezoneOffset()*60*1000;
    localNow.setTime(localNow.getTime()-utcOffsetMiliSec);//to utc time
    var options = {
                    series: {
                        lines: {
                            lineWidth: 1
                        },
                        shadowSize: 0	// Drawing is faster without shadows
                    },
                    grid: {
                        backgroundColor: { colors: ["#00f", "#000"] }
                    },
                    xaxis: {
                        font: {
                            color: "#FFFFFF"
                        },
                        mode: "time",
                        minTickSize: [1, "minute"],
                        twelveHourClock: true,
                        timeformat: "%H:%M",
                        min: localNow-oneHourAgo,
					    max: localNow
                    },
                    yaxis: {
                        min: 0,
                        max: 100,
                        font: {
                            color: "#FFFFFF"
                        }
                    }
                  };
    var plot = $.plot(div, [], options);
    plot.setData([[]]);//blank chart draw axis first...
    plot.setupGrid();
    plot.draw();

    return plot;
}


function connect_to_sio(){
    //connect to sio sever...
    socket = io.connect("/simplepush");//connect to SimpleNamespace

    if(!socket) return;

    socket.on('connect', function () {
        trace('Connected to the server!');
    });

    var cellBackgroundBy = function(value, max){
        var percent = value*100/max;
        var div = "<div style='width:"+percent+"px; height:20px; padding:6px 4px 0px 4px;";
        div += " background-image:url(/static/images/px.png); background-repeat:repeat-x;'>";
        div += value+"</div>";
        return div;
    };

    socket.on('_res', function (msgs) {//listening resource event to show in the top-left grid
        var json_obj;
        var grid = get_widget('nginx.access.*');
        for (var i in msgs) {
            //console.log(msgs[i])
            json_obj = JSON.parse(msgs[i]);
            if (json_obj['max']){//has max value, then to draw percent bar in value cell
                var html_cell = cellBackgroundBy(json_obj["value"], json_obj["max"]);
                trace(html_cell);
                json_obj["value"] = html_cell;
            }
            grid.addRowData(json_obj.id, json_obj, 'first');
        }
        var rowIds = grid.getDataIDs();
        //FIXME, max display row number is: 10
        if(rowIds.length>10){
            grid.delRowData(rowIds[rowIds.length-1]);//remove the foremost row;
        }
    });

    socket.on('_alert', function (msgs) {//listening alert event to show in radar chart
        //TODO, DISPLAY IN RADAR CHART...
        var radar = get_widget('nginx.error.*');

    });

    socket.on('_pfm', function (msgs) {//listening performance event to show in line chart
        for(var i in msgs){
            var json_obj = JSON.parse(msgs[i]);
            updateTimeSeries(json_obj);
        }
    });

}//end of connect_to_sio

/**
 * update the line chart with received message...
 * supposed one series only in each plot, so easy to get the showed data points
 *
 * @param msg
 */
function updateTimeSeries(msg) {
    msg.timestamp = localToUTC(msg.timestamp);
    var first_series_pts;
    var merged;
    var rendered_plot;
    var orig_plot = get_widget(msg.name);
    if(orig_plot){
        trace('to update chart with: ');
        trace(msg);
        if(orig_plot.getData().length){
            first_series_pts = orig_plot.getData()[0].data;//get the first series only
        }else{
            first_series_pts = [];
        }
        //render line chart again to create new x-axis
        rendered_plot = createTimeSeries(orig_plot.getPlaceholder());
        register_widget(msg.name, rendered_plot);//save again

        merged = merge(first_series_pts, [msg.timestamp, msg.value]);
        rendered_plot.setData([merged]);
        rendered_plot.setupGrid();
        rendered_plot.draw();
    }else{
        warn('unknown msg type: '+msg.name);
    }

}//end of re-render line chart with coming data


/**
 * only keep one hour data, so beyond 30 will remove the foremost point
 * @param original
 * @param pt
 */
function merge(original, pt){
    original.splice(0, 0, pt);//insert to the first
    if(original.length>60){
        original.pop();
    }

    return original;
}


function localToUTC(localSecond){
    var localNow = new Date();
    var utcOffsetMiliSec = localNow.getTimezoneOffset()*60*1000;
    localNow.setTime(localSecond*1000-utcOffsetMiliSec);//to utc time
    return localNow.getTime();
}


function trace(obj){
    if(!DEBUG) return;
    console.log(obj);
}


function warn(obj){
    if(!DEBUG) return;
    console.warn(obj);
}


$(window).bind("beforeunload", function() {
    socket.disconnect();
});

$(window).bind("resize", function() {
    var grid = get_widget('nginx.access.*');
    if(grid) {
        grid.setGridWidth(document.body.clientWidth*0.54, true);
    }
});