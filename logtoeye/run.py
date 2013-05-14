#!/usr/bin/env python
# ------------ a startup-script for this django project run in SocketIOServer --------
# ------------ created at 2013/04/27 --------------------

__author__ = 'lwz'

import os
import sys
from gevent import monkey
from socketio.server import SocketIOServer
from nswsgihandler import NSWSGIHandler, LogSocketIOHandler

monkey.patch_all(thread=False)

PORT = 9000
PID_FILE = 'sio.pid'
PID = None


def remember():
    # remember me to report self status to dashboard
    f = open(PID_FILE, 'w')
    global PID
    PID = str(os.getpid())
    f.write(PID)
    f.flush()
    f.close()


def ready():
    global PORT
    # ADD PORT PARAM IN sys.arg
    if len(sys.argv) > 1:
        PORT = int(sys.argv[1])

    try:
        import settings
    except ImportError:
        error_info = "Error: Can't find the file 'settings.py' in the directory containing %r. " \
                     "It appears you've customized things.\nYou'll have to run django-admin.py, " \
                     "passing it your settings module.\n(If the file settings.py does indeed exist, " \
                     "it's causing an ImportError somehow.)\n" % __file__
        sys.stderr.write(error_info)
        sys.exit(1)
    else:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


def go():

    # must import namespace class here after os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    from namespaces import SimplePushNS, RootNamespace
    # Dummy request object to maintain state between Namespace initialization.
    # just for ChatNamespace share data
    request = {'self_reported': False, 'pid': PID}
    # here can assign several namespaces pair by key:value
    application = NSWSGIHandler({'': RootNamespace, '/simplepush': SimplePushNS}, request)
    sio = SocketIOServer(('0.0.0.0', PORT), application, resource="socket.io", log=None)
    # log_file="request.log", handler_class=LogSocketIOHandler,)  # JUST WRITE ACCESS LOG TO FILE
    print 'SocketIOServer Listening on http://0.0.0.0:%s and on port 10843 (flash policy server)' % PORT
    print 'PID is: %s' % PID
    try:
        sio.serve_forever()
    except KeyboardInterrupt:
        sio.stop()
        print ' >>> SocketIO Server Stopped!'


if __name__ == '__main__':
    remember()
    ready()
    go()