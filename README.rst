Logtoeye - Your viewport for service and files!
=====================================
 Logtoeye is a realtime data visualization platform based on django/socket.io/gevent-socketio,
 it's dashboard can display metric/non-metric data instantly pushed from various socket.io client.

Sigh...
-------------------------------------
this project is in sleep status for a long time, and no plan to restart!
And, the original design is not good to mix django server and socketio server.
So, if possible to restart it, be sure to separate the two!
2013/08/25

Why?
-------------------------------------
 For the most of existing software and tools in monitoring the service and log files has several problems below:

 - too big in size and try to including as many as possible functionality;
 - complex config and not easy to started quickly;
 - user interface may not configurable, beautiful, concise;
 - data visualization may not be real time;
 - the architecture lack adequate flexibility, or not a open/plugins design;

Features
-------------------------------------
 * Distributed collect agent for log file and system performance;
 * Plug-ins architecture for metric/non-metric data collecting;
 * Customizable dashboard interface with different html widget(line-chart/radar-chart/data-grid);
 * Realtime data display in browser using emerging pushing technology;
 * Full stack means of alert notification: browser/desktop/mobile by message or email;
 * Open source project and open architecture, so easily to integrate 3rd part plugins;

Usage
-------------------------------------
 start server: ::

    ~$ cd logtoeye
    .../logtoeye$ python run.py

 visit dashboard: ::

    http://localhost:9000/dashboard

Dependency
-------------------------------------
 * gevent: https://pypi.python.org/pypi/gevent/0.13.8
 * gevent-socketio: https://pypi.python.org/pypi/gevent-socketio/0.3.5-rc2
 * django: https://pypi.python.org/pypi/Django/1.5.1
 * mongoDB: http://www.mongodb.org/
 * pymongo: https://pypi.python.org/pypi/pymongo/2.5.1
 * WebElements: http://www.webelements.in/Home

Roadmap
-------------------------------------
 version 0.1 include:

 * stand-alone dashboard;
 * QQ email;
 * chrome desktop notification;
 * html report;

 version 0.2 include:

 * integrated with graphite;
 * android client to show alert;
 * desktop client in AIR app;
