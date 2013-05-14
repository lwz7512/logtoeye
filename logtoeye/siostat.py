# created at 2013/05/14
__author__ = 'lwz'

import time


def collect(pid):
    # print 'Collecting sio server cpu usage...'

    pre_sio = __get_sio_time(pid)
    pre_total = __get_total_time()
    time.sleep(1)  # sleep for update
    pst_sio = __get_sio_time(pid)
    pst_total = __get_total_time()

    sio_cpu_diff = sum(pst_sio) - sum(pre_sio)
    total_diff = (pst_total[0]+pst_total[2]) - (pre_total[0]+pre_total[2])

    sio_cpu_percent = sio_cpu_diff*100.00/total_diff
    total_cpu_percent = (pst_total[0]+pst_total[2])*100/sum(pst_total)
    # print 'sio_cpu_percent: %s' % sio_cpu_diff
    # print 'total cpu percent: %s' % total_cpu_percent

    return sio_cpu_percent


def __get_sio_time(pid):
    child_proc_file = open('/proc/%s/stat' % pid, "r")  # use first work process for sample
    child_field_pre = child_proc_file.readline().split(' ')
    child_proc_file.close()
    return int(child_field_pre[13]), int(child_field_pre[14])  # usertime, systemtime


def __get_total_time():
    statFile = open('/proc/stat', "r")
    times = statFile.readline().split(" ")[2:6]  # user, nice, system, idle
    for i in range(len(times)):
        times[i] = int(times[i])
    statFile.close()
    return times