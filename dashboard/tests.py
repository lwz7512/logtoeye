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
from bson.code import Code



class MongoDBTest(TestCase):

    def setUp(self):
        # prepare...
        client = MongoClient()
        self.db = client['mgdbtest']
        self.raw_visits = self.db['raw_visits']
        self.raw_visits.remove()

    def test_access_count_by_client(self):
        res_3 = {'name': 'mock.access.192.168.0.104', 'value': 0.1, 'resource': '/blog/2',
                 'timestamp': time.time()-24*60*60-1, 'original': '127.0.0.1', 'server_name': 'runbytech.com'}
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
        print obj['statusCode'], obj['countryName'], obj['cityName']

    def test_last7day_access_count_by_client(self):
        res_0 = {'name': 'mock.access.192.168.0.104', 'value': 0.1, 'resource': '/blog/2',
                 'timestamp': time.time()-8*24*60*60, 'original': '127.0.0.1', 'server_name': 'localhost'}
        res_1 = {'name': 'mock.access.192.168.0.104', 'value': 0.1, 'resource': '/blog/2',
                 'timestamp': time.time()-46*60*60, 'original': '127.0.0.1', 'server_name': 'localhost'}
        res_2 = {'name': 'mock.access.192.168.0.104', 'value': 0.1, 'resource': '/blog/2',
                 'timestamp': time.time()-47*60*60, 'original': '127.0.0.1', 'server_name': 'localhost'}
        res_3 = {'name': 'mock.access.192.168.0.104', 'value': 0.1, 'resource': '/blog/2',
                 'timestamp': time.time()-48*60*60, 'original': '192.168.0.101', 'server_name': 'localhost'}
        res_4 = {'name': 'mock.access.192.168.0.104', 'value': 0.2, 'resource': '/',
                 'timestamp': time.time()-24*60*60, 'original': '192.168.0.101', 'server_name': 'localhost'}
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
        self.raw_visits.map_reduce(mapper, reducer, "daily_visitors", query=last7day)  # save to daily_visitors collection
        print "-------------- daily_visitors ----------------------"
        for doc in self.db["daily_visitors"].find():
            print doc
        maper_2 = Code("""
                    function() {
                      emit(this['_id']['day'], {count: 1});
                    }
                    """)
        self.db["daily_visitors"].map_reduce(maper_2, reducer, "daily_visitors_unique")
        print "---------- print daily_visitors_unique -------------"
        for doc in self.db["daily_visitors_unique"].find():
            print doc['_id'].strftime("%Y-%m-%d"), doc['value']['count']