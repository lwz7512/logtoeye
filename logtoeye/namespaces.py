__author__ = 'lwz'

import logging
import time
import settings
from json import dumps, loads
from pymongo import MongoClient
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
        self.init_db()
        self.app_filters = []
        self.find_app_filters()

    def init_db(self):
        client = MongoClient()
        self.db = client['logtoeye']

    def find_app_filters(self):
        not_djgo_apps = [app for app in settings.INSTALLED_APPS if app.startswith('django') is not True]
        for app in not_djgo_apps:
            try:
                # from parent dir to import
                filters_module = __import__('%s.filters' % app, fromlist=['filters'], level=1)
                app_filters_cls = getattr(filters_module, 'filters')
                # cache all the filters in list
                [self.app_filters.append(flt()) for flt in app_filters_cls]
            except ImportError:
                self.logger.warning('Can not import filters module from : %s' % app)

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
                      'timestamp': timestamp,}
            # send to browser
            self.broadcast_event('_pfm', [dumps(metric)])
            # save in db
            self.on_pfm([dumps(metric)])
            time.sleep(60)  # have a rest for one minute

    def recv_disconnect(self):
        self.disconnect(silent=True)
        self.log('client has disconnected !')

    # receive the message use send method...
    def recv_message(self, message):
        self.broadcast_event('announcement', message)
        self.log("Server received: %s" % message)

    def log(self, message):
        self.logger.info("[{0}] {1}".format(self.socket.sessid, message))

    def on_alert(self, payloads):
        deserialized_metrics = [loads(metric_str) for metric_str in payloads]
        for metric in deserialized_metrics:
            metric_name = '.'.join(metric['name'].split('.')[:2])
            collection = self.db[metric_name]
            collection.insert(metric)
            for flt_inst in self.app_filters:
                if metric_name == flt_inst.name:
                    flt_inst.filter(metric)

        self.log('receive alert...then announce to browser!')
        # send to browser
        self.broadcast_event('_alert', payloads)

    def on_res(self, payloads):
        deserialized_metrics = [loads(metric_str) for metric_str in payloads]
        for metric in deserialized_metrics:
            metric_name = '.'.join(metric['name'].split('.')[:2])
            collection = self.db[metric_name]
            collection.insert(metric)
            for flt_inst in self.app_filters:
                if metric_name == flt_inst.name:
                    flt_inst.filter(metric)

        self.log('receive res...then announce to browser!')
        # send to browser
        self.broadcast_event('_res', payloads)

    def on_pfm(self, payloads):
        deserialized_metrics = [loads(metric_str) for metric_str in payloads]
        for metric in deserialized_metrics:
            metric_name = '.'.join(metric['name'].split('.')[:2])
            collection = self.db[metric_name]
            collection.insert(metric)
            for flt_inst in self.app_filters:
                if metric_name == flt_inst.name:
                    flt_inst.filter(metric)

        self.log('receive pfm...then announce to browser!')
        # send to browser
        self.broadcast_event('_pfm', payloads)