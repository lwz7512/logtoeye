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

window.onload = init;

function init(){
    //cache all the widget here
    $.widgets = {};

    var grid = createNginxUrlGrid("#west-grid");
    register_widget('nginx.access.*', grid);

    var radar = createRadarChart('canvas');
    register_widget('nginx.error.*', radar);

    var plot_sio = createTimeSeries("#sio-chart-placeholder");
    register_widget('sio.cputime.minute', plot_sio);

    var plot_ngx = createTimeSeries("#nginx-chart-placeholder");
    register_widget('nginx.cputime.minute', plot_ngx);

    connect_to_sio();

}//end of init


function register_widget(name, wgt_obj){
    $.widgets[name] = wgt_obj;
}


function get_widget(name){
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
            {name:'value',index:'value', width:80, align:"right", sorttype:"float"},
            {name:'timestamp',index:'timestamp', width:100, align:"right", sortable:false},
            {name:'original',index:'original', width:150,align:"center",sortable:false}
        ],
        rowNum:10,
        hidegrid: false, //hide the fold button in title-bar
        caption: "Nginx URL Request Time Display"
    });//end of jqgrid init

}//end of createGrid

function createRadarChart(canvas){
    var canvas = document.getElementById(canvas);
    var engine = new JSAnimationEngine(canvas);
    var radar = new RadarChart(canvas, canvas.height/2);
    engine.addChild(radar);
    engine.run();
    //TODO, ...
    engine.stop();

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
                        font: {
                            color: "#FFFFFF"
                        }
                    }
                  };
    return $.plot(div, [], options);

}


function randomData(){
    var d2 = [];
    var localNow = new Date();
    var utcOffsetMiliSec = localNow.getTimezoneOffset()*60*1000;
    localNow.setTime(localNow.getTime()-utcOffsetMiliSec);//to utc time
    for(var i = 0; i<60; i++){
        var passedMinutes = localNow.getTime() - i*60*1000;
        d2.push([passedMinutes, i*Math.random()]);
    }
    return d2;
}


function connect_to_sio(){
    //connect to sio sever...
    socket = io.connect("/simplepush");//connect to SimpleNamespace

    if(!socket) return;

    socket.on('connect', function () {
        console.log('Connected to the server!');
    });

    socket.on('_res', function (msgs) {//listening resource event to show in the top-left grid
        var json_obj;
        var grid = get_widget('nginx.access.*');
        for (var i in msgs) {
            //console.log(msgs[i])
            json_obj = JSON.parse(msgs[i]);
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
    var orig_pts;
    var merged;
    var rendered_plot;
    var orig_plot = get_widget(msg.name);
    if(orig_plot){
        trace('to update chart with: ');
        //trace(json_obj);
        orig_pts = orig_plot.getData()[0].data;
        //render line chart again to create new x-axis
        rendered_plot = createTimeSeries(orig_plot.getPlaceholder());
        register_widget(msg.name, rendered_plot);//save again

        merged = merge(orig_pts, [msg.timestamp, msg.value]);
        rendered_plot.setData([merged]);
        rendered_plot.setupGrid();
        rendered_plot.draw();
    }else{
        console.warn('unknown msg type: '+msg.name);
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
    console.log(obj);
}

$(window).bind("beforeunload", function() {
    socket.disconnect();
});

$(window).bind("resize", function() {
    if(grid) {
        grid.setGridWidth(document.body.clientWidth*0.54, true);
    }
});