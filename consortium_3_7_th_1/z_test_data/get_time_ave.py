#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 5/6/22 9:34 PM
# @Author : Archer
# @File : get_time_ave.py
# @desc :
"""
key_counts = {'create':10,
              'commit':10,
              'reveal':10,
              'finalize':10,
              'update':50,
              'transfer':50,
              'receiver':50,
              'renewal':50}

import json

def test():
    with open("./cost_time.json", 'r') as load_f:
        cost_time = json.load(load_f)

    with open("./time_ave.json", 'r') as load_f:
        time_ave = json.load(load_f)
        load_f.close()
    #
    # cost_time = json.load()
    # time_ave = json.load("./time_ave.json")
    for key in key_counts:
        count = key_counts[key]
        time = cost_time[key]['end'] - cost_time[key]['start']
        ave_time = time/count
        time_ave[key] = ave_time
    with open("./time_ave.json", 'w') as load_f:
        json.dump(time_ave, load_f)
        load_f.close()
    print(time_ave)

if __name__ == '__main__':
    test()