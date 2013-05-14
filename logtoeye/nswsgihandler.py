__author__ = 'lwz'
# ----------- namespaced WSGIHandler used by socketio server --------
# ----------- 2013/05/01 -----------
import os
from socketio import socketio_manage
from socketio.handler import SocketIOHandler
from django.core.handlers.wsgi import WSGIHandler


class NSWSGIHandler(WSGIHandler):
    """
    enhanced WSGIHandler that use namespace dict used by SocketIOServer
    """
    def __init__(self, namespace_dict, request=None):
        super(NSWSGIHandler, self).__init__()
        self.namespace_dict = namespace_dict
        self.request = request

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO'].strip('/')
        # print 'request: %s' % path

        # serve favicon file...
        if path == 'favicon.ico':
            start_response('200 OK', [('Content-Type', "image/x-icon")])
            abspath = 'static/images/%s' % path
            return [open(abspath).read()]

        if path.startswith('static/'):  # host the root app static files
            try:
                # use the relative path of this file in the static dirs
                # 2013/05/02
                data = open(path).read()
            except IOError:
                print 'Not found: %s' % path
                return self.not_found(start_response)

            if path.endswith(".jpg"):
                content_type = "image/jpeg"
            elif path.endswith(".png"):
                content_type = "image/png"
            elif path.endswith(".js"):
                content_type = "text/javascript"
            elif path.endswith(".css"):
                content_type = "text/css"
            elif path.endswith(".swf"):
                content_type = "application/x-shockwave-flash"
            else:
                content_type = "text/html"

            start_response('200 OK', [('Content-Type', content_type)])
            return [data]

        if path.startswith("socket.io"):  # host the socket.io request
            socketio_manage(environ, self.namespace_dict, self.request)
        else:
            response = super(NSWSGIHandler, self).__call__(environ, start_response)
            # print 'wsgi return: %s' % response.serialize()
            return response  # host the django request

    def not_found(self, start_response):
        start_response('404 Not Found', [])
        return ['<h1>Not Found</h1>']


class LogSocketIOHandler(SocketIOHandler):

    def log_request(self):
        log = self.server.log
        if log:
            log.write(self.format_request() + '\n')
            log.flush()  # WRITE THE BUFFER TO FILE...