__author__ = 'lwz'

import logging
import time
from json import dumps

from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin
from siostat import collect


# @namespace('')
class RootNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):

    def initialize(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("socketio.rootns")  # use logger defined in settings.LOGGING
        self.log("RootNamespace session started")

    def recv_connect(self):
        pass

    def log(self, message):
        self.logger.info(message)

    def recv_disconnect(self):
        self.disconnect(silent=True)
        self.log('client has disconnected !')

    def recv_message(self, message):
        self.broadcast_event('announcement', message)
        self.log("RootNamespace recv_message: %s" % message)


# @namespace('/simplepush')
class SimplePushNS(BaseNamespace, RoomsMixin, BroadcastMixin):

    def initialize(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("socketio.simplepush")  # use logger defined in settings.LOGGING
        self.log("ChatNamespace session started")

    def recv_connect(self):
        if self.request['self_reported']:  # use the shared value to avoid repeated spawn...
            return
        self.spawn(self.collect_status)  # create a child process
        self.request['self_reported'] = True
        self.log("*** ChatNamespace SPAWNED SELF REPORT TASK ***")

    def collect_status(self):
        while True:
            cpu_percent = collect(self.request['pid'])
            timestamp = time.time()
            metric = {'name': 'sio.cputime.minute',
                      'type': 'pfm',
                      'value': cpu_percent,
                      'timestamp': timestamp,
                      'id': str(timestamp)}
            # send to browser
            self.broadcast_event('_pfm', [dumps(metric)])
            time.sleep(60)  # have a rest for one minute

    def recv_disconnect(self):
        self.disconnect(silent=True)
        self.request['self_reported'] = False
        self.log('client has disconnected !')

    # receive the message use send method...
    def recv_message(self, message):
        self.broadcast_event('announcement', message)
        self.log("Server received: %s" % message)

    def log(self, message):
        self.logger.info("[{0}] {1}".format(self.socket.sessid, message))

    def on_alert(self, payload):
        # TODO, SAVE TO MANGODB FOR REPORT GENERATION...

        # TODO, ADD FILTERS: DO SOMETHING BY SOME THRESHOLD VALUE...

        self.log('receive alert...then announce to browser!')
        # send to browser
        self.broadcast_event('_alert', payload)

    def on_res(self, payload):
        # TODO, SAVE TO MANGODB FOR REPORT GENERATION...

        # TODO, ADD FILTERS: DO SOMETHING BY SOME THRESHOLD VALUE...

        self.log('receive res...then announce to browser!')
        # send to browser
        self.broadcast_event('_res', payload)

    def on_pfm(self, payload):
        # TODO, SAVE TO MANGODB FOR REPORT GENERATION...

        # TODO, ADD FILTERS: DO SOMETHING BY SOME THRESHOLD VALUE...

        self.log('receive pfm...then announce to browser!')
        # send to browser
        self.broadcast_event('_pfm', payload)