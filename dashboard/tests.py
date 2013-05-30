"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import time
import urllib2
import json

from django.test import TestCase

from pymongo import MongoClient
from pymongo import DESCENDING
from pymongo import ASCENDING
from bson.code import Code


class MongoDBTest(TestCase):

    def setUp(self):
        client = MongoClient()
        self.db = client['mgdbtest']
        self.raw_visits = self.db['raw_visits']
        self.raw_visits.remove()
        self.raw_alerts = self.db['raw_alerts']
        self.raw_alerts.remove()
        self.raw_pfms = self.db['raw_pfms']
        self.raw_pfms.remove()

    def test_access_count_by_client(self):
        res_3 = {'name': 'mock.access.192.168.0.104', 'value': 0.1, 'resource': '/blog/2',
                 'timestamp': time.time()-24*60*60, 'original': '127.0.0.1', 'server_name': 'runbytech.com'}
        res_4 = {'name': 'mock.access.192.168.0.104', 'value': 0.2, 'resource': '/',
                 'timestamp': time.time(), 'original': '123.125.114.144', 'server_name': 'logtoeye.com'}
        res_5 = {'name': 'mock.access.192.168.0.104', 'value': 0.2, 'resource': '/',
                 'timestamp': time.time(), 'original': '180.149.134.18', 'server_name': 'logtoeye.com'}
        self.raw_visits.insert([res_3, res_4, res_5])

        self.raw_visits.ensure_index([('timestamp', DESCENDING)])
        condition = {"server_name": "logtoeye.com", "timestamp": {"$gt": time.time()-24*60*60}}
        clients = self.raw_visits.find(condition).distinct("original")
        print "unique client: ", clients

    def test_top_region_by_client(self):
        ips = ['180.149.134.18', '123.125.114.144', '163.177.65.160'
               '173.194.72.138', '82.94.164.162', '204.232.175.90']
        key = "9730aa0c8b5c67b560947f664bf9c4f5128a3b81b0ff6f3f0f16dca1bea46fcb"
        ip = "124.193.192.36"
        ip_query_url = "http://api.ipinfodb.com/v3/ip-city/?key=%s&ip=%s&format=json" % (key, ip)
        print ip_query_url
        result = urllib2.urlopen(ip_query_url)
        obj = json.load(result)
        print obj['statusCode'], ',', obj['countryName'], ',', obj['cityName']

    def test_last7day_access_count_by_client(self):
        # one week ago
        res_0 = {'name': 'mock.access.192.168.0.104', 'value': 0.1, 'resource': '/blog/2',
                 'timestamp': time.time()-8*24*60*60, 'original': '127.0.0.1', 'server_name': 'localhost'}
        # yesterday
        res_1 = {'name': 'mock.access.192.168.0.104', 'value': 0.1, 'resource': '/blog/2',
                 'timestamp': time.time()-46*60*60, 'original': '127.0.0.1', 'server_name': 'localhost'}
        res_2 = {'name': 'mock.access.192.168.0.104', 'value': 0.1, 'resource': '/blog/2',
                 'timestamp': time.time()-47*60*60, 'original': '127.0.0.1', 'server_name': 'localhost'}
        res_3 = {'name': 'mock.access.192.168.0.104', 'value': 0.1, 'resource': '/blog/2',
                 'timestamp': time.time()-48*60*60, 'original': '192.168.0.101', 'server_name': 'localhost'}
        # last day
        res_4 = {'name': 'mock.access.192.168.0.104', 'value': 0.2, 'resource': '/',
                 'timestamp': time.time()-24*60*60, 'original': '192.168.0.101', 'server_name': 'localhost'}
        # today
        res_5 = {'name': 'mock.access.192.168.0.104', 'value': 0.2, 'resource': '/',
                 'timestamp': time.time(), 'original': '192.168.0.101', 'server_name': 'logtoeye.com'}
        self.raw_visits.insert([res_0, res_1, res_2, res_3, res_4, res_5])

        mapper = Code("""
                     function () {
                         var d = new Date();
                         d.setTime(this.timestamp*1000);
                         d.setHours(8,0,0,0);//add timezone offset
                         emit({day: d, original: this.original}, {count: 1});
                     }
                    """)
        reducer = Code("""
                     function(key, values) {
                          var count = 0;
                          values.forEach(function(v) {
                            count += v['count'];
                          });
                          return {count: count};
                        }
                     """)
        last7day = {'timestamp': {'$gt': time.time()-7*24*60*60}}
        # aggregate once
        self.raw_visits.map_reduce(mapper, reducer, "daily_visitors", query=last7day)  # save to daily_visitors collection
        print "-------------- daily_visitors ----------------------"
        for doc in self.db["daily_visitors"].find():
            print doc
        maper_twice = Code("""
                    function() {
                      emit(this['_id']['day'], {count: 1});
                    }
                    """)
        # aggregate twice
        self.db["daily_visitors"].map_reduce(maper_twice, reducer, "daily_visitors_unique")
        print "---------- print daily_visitors_unique -------------"
        for doc in self.db["daily_visitors_unique"].find():
            print doc['_id'].strftime("%Y-%m-%d"), ',', doc['value']['count']

    def test_last_day_top10_url_visited(self):
        res_0 = {'name': 'mock.access.192.168.0.104', 'value': 0.1, 'resource': '/blog/2',
                 'timestamp': time.time()-24*60*60, 'original': '127.0.0.1', 'server_name': 'localhost'}
        res_1 = {'name': 'mock.access.192.168.0.104', 'value': 0.1, 'resource': '/blog/2',
                 'timestamp': time.time(), 'original': '192.168.0.103', 'server_name': 'localhost'}
        res_2 = {'name': 'mock.access.192.168.0.104', 'value': 0.1, 'resource': '/blog/2',
                 'timestamp': time.time(), 'original': '192.168.0.102', 'server_name': 'localhost'}
        res_3 = {'name': 'mock.access.192.168.0.104', 'value': 0.1, 'resource': '/blog/2',
                 'timestamp': time.time(), 'original': '192.168.0.101', 'server_name': 'localhost'}
        res_4 = {'name': 'mock.access.192.168.0.104', 'value': 0.2, 'resource': '/',
                 'timestamp': time.time(), 'original': '192.168.0.101', 'server_name': 'localhost'}
        res_5 = {'name': 'mock.access.192.168.0.104', 'value': 0.2, 'resource': '/',
                 'timestamp': time.time(), 'original': '192.168.0.101', 'server_name': 'logtoeye.com'}
        self.raw_visits.insert([res_0, res_1, res_2, res_3, res_4, res_5])

        mapper = Code("""
                    function(){
                        emit(this.resource, { count : 1 });
                    }
                    """)
        reducer = Code("""
                     function(key, values) {
                          var count = 0;
                          values.forEach(function(v) {
                            count += v['count'];
                          });
                          return {count: count};
                        }
                     """)
        query = {'timestamp': {"$gt": time.time()-24*60*60}, 'server_name': 'localhost'}
        self.raw_visits.map_reduce(mapper, reducer, "url_rank", query=query)
        results = self.db["url_rank"].find().sort("value", DESCENDING)
        for doc in results:
            # print doc
            print doc['_id'], ',', doc['value']['count']

    def test_last_day_top10_request_length(self):
        res_0 = {'name': 'mock.access.192.168.0.104', 'value': 0.1, 'resource': '/blog/2',
                 'timestamp': time.time()-24*60*60, 'original': '127.0.0.1', 'server_name': 'localhost'}
        res_1 = {'name': 'mock.access.192.168.0.104', 'value': 0.1, 'resource': '/blog/1',
                 'timestamp': time.time()-1, 'original': '192.168.0.103', 'server_name': 'localhost'}
        res_2 = {'name': 'mock.access.192.168.0.104', 'value': 0.2, 'resource': '/blog/2',
                 'timestamp': time.time()-2, 'original': '192.168.0.102', 'server_name': 'localhost'}
        res_3 = {'name': 'mock.access.192.168.0.104', 'value': 0.3, 'resource': '/blog/3',
                 'timestamp': time.time()-3, 'original': '192.168.0.101', 'server_name': 'localhost'}
        res_4 = {'name': 'mock.access.192.168.0.104', 'value': 0.01, 'resource': '/',
                 'timestamp': time.time()-4, 'original': '192.168.0.101', 'server_name': 'localhost'}
        res_5 = {'name': 'mock.access.192.168.0.104', 'value': 0.01, 'resource': '/',
                 'timestamp': time.time(), 'original': '192.168.0.101', 'server_name': 'logtoeye.com'}
        self.raw_visits.insert([res_0, res_1, res_2, res_3, res_4, res_5])

        self.raw_visits.ensure_index([('timestamp', DESCENDING)])
        condition = {"server_name": "localhost", "timestamp": {"$gt": time.time()-24*60*60}}
        fields = {'_id': False, 'resource': True, 'value': True, 'server_name': True}
        visits = self.raw_visits.find(spec=condition, fields=fields, limit=3, sort=[{'value', DESCENDING}])
        for doc in visits:
            print doc

    def test_last_day_alert_volume(self):
        alt_1 = {'name': 'mock.alert.localhost', 'level': 1, 'message': 'alert description in simple format',
                 'cause': 'related info about the alert...', 'timestamp': time.time()-24*60*60,
                 'original': 'the invoker for this alert...', 'server_name': 'localhost'}
        alt_2 = {'name': 'mock.alert.192.168.0.101', 'level': 1, 'message': 'alert description in simple format',
                 'cause': 'related info about the alert...', 'timestamp': time.time(),
                 'original': 'the invoker for this alert...', 'server_name': '192.168.0.101'}
        alt_3 = {'name': 'mock.alert.localhost', 'level': 1, 'message': 'alert description in simple format',
                 'cause': 'related info about the alert...', 'timestamp': time.time(),
                 'original': 'the invoker for this alert...', 'server_name': 'localhost'}
        alt_4 = {'name': 'mock.alert.localhost', 'level': 1, 'message': 'alert description in simple format',
                 'cause': 'related info about the alert...', 'timestamp': time.time(),
                 'original': 'the invoker for this alert...', 'server_name': 'localhost'}
        self.raw_alerts.insert([alt_1, alt_2, alt_3, alt_4])

        condition = {"server_name": "localhost", "timestamp": {"$gt": time.time()-24*60*60}}
        alerts_total_last_day = self.raw_alerts.find(condition).count()
        print "alert last day: ", alerts_total_last_day
        self.assertEqual(alerts_total_last_day, 2)

    def test_last_day_alert_by_level(self):
        alt_1 = {'name': 'mock.alert.localhost', 'level': 1, 'message': 'alert description in simple format',
                 'cause': 'related info about the alert...', 'timestamp': time.time(),
                 'original': 'the invoker for this alert...', 'server_name': 'localhost'}
        alt_2 = {'name': 'mock.alert.localhost', 'level': 1, 'message': 'alert description in simple format',
                 'cause': 'related info about the alert...', 'timestamp': time.time(),
                 'original': 'the invoker for this alert...', 'server_name': 'localhost'}
        alt_3 = {'name': 'mock.alert.localhost', 'level': 2, 'message': 'alert description in simple format',
                 'cause': 'related info about the alert...', 'timestamp': time.time(),
                 'original': 'the invoker for this alert...', 'server_name': 'localhost'}
        alt_4 = {'name': 'mock.alert.localhost', 'level': 3, 'message': 'alert description in simple format',
                 'cause': 'related info about the alert...', 'timestamp': time.time(),
                 'original': 'the invoker for this alert...', 'server_name': 'localhost'}
        self.raw_alerts.insert([alt_1, alt_2, alt_3, alt_4])

        mapper = Code("""
                    function(){
                        emit(this.level, { count : 1 });
                    }
                    """)
        reducer = Code("""
                     function(key, values) {
                          var count = 0;
                          values.forEach(function(v) {
                            count += v['count'];
                          });
                          return {count: count};
                        }
                     """)
        query = {'timestamp': {"$gt": time.time()-24*60*60}, 'server_name': 'localhost'}
        self.raw_alerts.map_reduce(mapper, reducer, "alt_group", query=query)
        results = self.db["alt_group"].find()
        for doc in results:
            print doc

    def test_last_day_alert_unprocessed(self):  # status: -1
        alt_1 = {'name': 'mock.alert.localhost', 'level': 1, 'message': 'alert description in simple format',
                 'cause': 'related info about the alert...', 'timestamp': time.time(), 'status': 0,
                 'original': 'the invoker for this alert...', 'server_name': 'localhost'}
        alt_2 = {'name': 'mock.alert.localhost', 'level': 1, 'message': 'alert description in simple format',
                 'cause': 'related info about the alert...', 'timestamp': time.time(), 'status': -1,
                 'original': 'the invoker for this alert...', 'server_name': 'localhost'}
        alt_3 = {'name': 'mock.alert.localhost', 'level': 2, 'message': 'alert description in simple format',
                 'cause': 'related info about the alert...', 'timestamp': time.time(), 'status': -1,
                 'original': 'the invoker for this alert...', 'server_name': 'localhost'}
        alt_4 = {'name': 'mock.alert.localhost', 'level': 3, 'message': 'alert description in simple format',
                 'cause': 'related info about the alert...', 'timestamp': time.time(), 'status': 1,
                 'original': 'the invoker for this alert...', 'server_name': 'localhost'}
        self.raw_alerts.insert([alt_1, alt_2, alt_3, alt_4])

        mapper = Code("""
                    function(){
                        emit(this.level, { count : 1 });
                    }
                    """)
        reducer = Code("""
                     function(key, values) {
                          var count = 0;
                          values.forEach(function(v) {
                            count += v['count'];
                          });
                          return {count: count};
                        }
                     """)
        query = {'timestamp': {"$gt": time.time()-24*60*60}, 'server_name': 'localhost', 'status': -1}
        self.raw_alerts.map_reduce(mapper, reducer, "alt_group_unprocessed", query=query)
        results = self.db["alt_group_unprocessed"].find()
        for doc in results:
            print doc

    def test_last_day_top10_alert_occurrence(self):  # group by title
        alt_1 = {'name': 'mock.alert.localhost', 'level': 1, 'message': 'alert description in simple format',
                 'cause': 'related info about the alert...', 'timestamp': time.time(), 'status': 0,
                 'original': 'the invoker for this alert...', 'server_name': 'localhost',
                 'title': 'mock alert in localhost for IOException'}
        alt_2 = {'name': 'mock.alert.localhost', 'level': 1, 'message': 'alert description in simple format',
                 'cause': 'related info about the alert...', 'timestamp': time.time(), 'status': -1,
                 'original': 'the invoker for this alert...', 'server_name': 'localhost',
                 'title': 'mock alert in localhost for IOException'}
        alt_3 = {'name': 'mock.alert.localhost', 'level': 2, 'message': 'alert description in simple format',
                 'cause': 'related info about the alert...', 'timestamp': time.time(), 'status': 0,
                 'original': 'the invoker for this alert...', 'server_name': 'localhost',
                 'title': 'mock alert in localhost for IOException'}
        alt_4 = {'name': 'mock.crit.localhost', 'level': 3, 'message': 'alert description in simple format',
                 'cause': 'related info about the alert...', 'timestamp': time.time(), 'status': 1,
                 'original': 'the invoker for this alert...', 'server_name': 'localhost',
                 'title': 'mock alert in localhost for APPException'}
        alt_5 = {'name': 'mock.crit.localhost', 'level': 2, 'message': 'alert description in simple format',
                 'cause': 'related info about the alert...', 'timestamp': time.time(), 'status': -1,
                 'original': 'the invoker for this alert...', 'server_name': 'localhost',
                 'title': 'mock alert in localhost for APPException'}
        alt_6 = {'name': 'mock.error.localhost', 'level': 3, 'message': 'alert description in simple format',
                 'cause': 'related info about the alert...', 'timestamp': time.time(), 'status': 1,
                 'original': 'the invoker for this alert...', 'server_name': 'localhost',
                 'title': 'mock alert in localhost for UNKOWNException'}
        self.raw_alerts.insert([alt_1, alt_2, alt_3, alt_4, alt_5, alt_6])

        mapper = Code("""
                    function(){
                        emit(this.title, { count : 1 });
                    }
                    """)
        reducer = Code("""
                     function(key, values) {
                          var count = 0;
                          values.forEach(function(v) {
                            count += v['count'];
                          });
                          return {count: count};
                     }
                     """)
        query = {'timestamp': {"$gt": time.time()-24*60*60}, 'server_name': 'localhost'}
        self.raw_alerts.map_reduce(mapper, reducer, "alt_occurrence", query=query)
        results = self.db["alt_occurrence"].find().sort("value", DESCENDING).limit(10)
        for doc in results:
            print self.raw_alerts.find_one({'title': doc['_id']})
            print doc

    def test_nginx_cpu_avg(self):
        pfm_1 = {'name': 'nginx.cputime.localhost', 'value': 1,
                 'timestamp': time.time()-1*60*60, 'server_name': 'localhost'}
        pfm_2 = {'name': 'nginx.cputime.localhost', 'value': 2,
                 'timestamp': time.time()-2*60*60, 'server_name': 'localhost'}
        pfm_3 = {'name': 'nginx.cputime.localhost', 'value': 1,
                 'timestamp': time.time()-3*60*60, 'server_name': 'localhost'}
        self.raw_pfms.insert([pfm_1, pfm_2, pfm_3])

        self.raw_pfms.ensure_index([('timestamp', DESCENDING)])
        query = {'timestamp': {"$gt": time.time()-24*60*60}, 'server_name': 'localhost'}
        reducer = Code("""
                     function(doc, out) {
                        out.count++;
                        out.total += parseFloat(doc.value); //use 'value' field to calculate
                     }
                     """)
        finalizer = Code("""
                        function(out) {
                            out.avg = out.total / out.count;
                        }
                        """)
        result = self.raw_pfms.group(
            key=None,  # group use
            condition=query,
            initial={'count': 0, 'total': 0},
            reduce=reducer,
            finalize=finalizer,)
        formatted = round(result[0]['avg'], 2)
        print 'is it string? ', isinstance(formatted, basestring)
        print 'is it number? ', isinstance(formatted, (int, long, float, complex))
        print 'nginx cpu-time avg: ', formatted
        print 'result: ', result

    def test_nginx_cpu_last_day(self):
        pfm_1 = {'name': 'nginx.cputime.localhost', 'value': 1,
                 'timestamp': time.time()-2*60*60, 'server_name': 'localhost'}
        pfm_2 = {'name': 'nginx.cputime.localhost', 'value': 2,
                 'timestamp': time.time()-1*60*60, 'server_name': 'localhost'}
        pfm_3 = {'name': 'nginx.cputime.localhost', 'value': 1,
                 'timestamp': time.time()-3*60*60, 'server_name': 'localhost'}
        self.raw_pfms.insert([pfm_1, pfm_2, pfm_3])

        self.raw_pfms.ensure_index([('timestamp', DESCENDING)])
        query = {'timestamp': {"$gt": time.time()-24*60*60}, 'server_name': 'localhost'}
        results = self.raw_pfms.find(spec=query, fields={'_id': False}).sort('timestamp', ASCENDING)
        for doc in results:
            print doc

    def test_sio_cpu_avg(self):
        pfm_1 = {'name': 'sio.cputime.localhost', 'value': 1,
                 'timestamp': time.time()-1*60*60, 'server_name': 'localhost'}
        pfm_2 = {'name': 'sio.cputime.localhost', 'value': 2,
                 'timestamp': time.time()-2*60*60, 'server_name': 'localhost'}
        pfm_3 = {'name': 'sio.cputime.localhost', 'value': 1,
                 'timestamp': time.time()-3*60*60, 'server_name': 'localhost'}
        self.raw_pfms.insert([pfm_1, pfm_2, pfm_3])

        self.raw_pfms.ensure_index([('timestamp', DESCENDING)])
        query = {'timestamp': {"$gt": time.time()-24*60*60}, 'server_name': 'localhost'}
        reducer = Code("""
                     function(doc, out) {
                        out.count++;
                        out.total += parseFloat(doc.value); //use 'value' field to calculate
                     }
                     """)
        finalizer = Code("""
                        function(out) {
                            out.avg = out.total / out.count;
                        }
                        """)
        result = self.raw_pfms.group(
            key=None,  # group use
            condition=query,
            initial={'count': 0, 'total': 0},
            reduce=reducer,
            finalize=finalizer,)
        formatted = round(result[0]['avg'], 2)
        print 'is it string? ', isinstance(formatted, basestring)
        print 'is it number? ', isinstance(formatted, (int, long, float, complex))
        print 'sio cpu-time avg: ', formatted
        print 'result: ', result

    def test_sio_cpu_last_day(self):
        pfm_1 = {'name': 'sio.cputime.localhost', 'value': 1,
                 'timestamp': time.time()-2*60*60, 'server_name': 'localhost'}
        pfm_2 = {'name': 'sio.cputime.localhost', 'value': 2,
                 'timestamp': time.time()-1*60*60, 'server_name': 'localhost'}
        pfm_3 = {'name': 'sio.cputime.localhost', 'value': 1,
                 'timestamp': time.time()-3*60*60, 'server_name': 'localhost'}
        self.raw_pfms.insert([pfm_1, pfm_2, pfm_3])

        self.raw_pfms.ensure_index([('timestamp', DESCENDING)])
        query = {'timestamp': {"$gt": time.time()-24*60*60}, 'server_name': 'localhost'}
        results = self.raw_pfms.find(spec=query, fields={'_id': False}).sort('timestamp', ASCENDING)
        for doc in results:
            print doc
