__author__ = 'lwz'

# filter the threshold value by each metric...


class NginxRequestTimeFilter(object):

    def init(self):
        pass

    def filter(self, metric):
        print 'to filter the metric in NginxRequestFilter...'



filters = [NginxRequestTimeFilter]