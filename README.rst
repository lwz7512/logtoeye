Logtoeye
=====================================
Logtoeye is a realtime data visualization platform based on django/socket.io/gevent-socketio,
it's dashboard can display metric/non-metric data instantly pushed from various socket.io client.

Features
-------------------------------------
 * Distributed collect agent for log file and system performance;
 * Plug-ins architecture for metric/non-metric data collecting;
 * Customizable dashboard interface with different html widget(line-chart/radar-chart/data-grid);
 * Realtime data display in browser using emerging pushing technology;
 * Full stack means of alert notification: browser/desktop/mobile by message or email;
 * Open source project and open architecture, so easily to integrate 3rd part plugins;

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
