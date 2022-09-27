#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 3/5/22 11:14 PM
# @Author : Archer
# @File : data_cal.py
# @desc :
"""
import sys

from tools.jsonOp import file2json, json2file

sys.path.append('../')


if __name__ == '__main__':
    path = '/z_test_data/cost_time.json'
    data = file2json(path)
    for item in data:
        data[item]['average'] = (data[item]['end'] - data[item]['start'])/50.0

    json2file(path, data)