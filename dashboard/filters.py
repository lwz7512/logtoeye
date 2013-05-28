__author__ = 'lwz'

# filter the threshold value by each metric...


class NginxRequestTimeFilter(object):

    def __init__(self):
        self.name = 'nginx.access'

    def filter(self, metric):
        print 'to filter the metric in NginxRequestFilter...'


class SIOCPUTimeFilter(object):

    def __init__(self):
        self.name = 'sio.cputime'

    def filter(self, metric):
        print 'to filter the metric in SIOCPUTimeFilter...'


filters = [NginxRequestTimeFilter, SIOCPUTimeFilter]