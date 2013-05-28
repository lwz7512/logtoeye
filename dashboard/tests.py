"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import time

from django.test import TestCase
from pymongo import MongoClient


class MongoDBTest(TestCase):

    def setUp(self):
        # prepare...
        client = MongoClient()
        self.db = client['mgdbtest']

    def test_access_count_by_client(self):
        self.raw_visits = self.db['raw_visits']
        res_1 = {'name': 'mock.access.192.168.0.104', 'value': 0.1, 'resource': '/',
                 'timestamp': time.time()*1000, 'original': '127.0.0.1', 'sever_name': 'localhost'}
        self.raw_visits.insert([res_1])