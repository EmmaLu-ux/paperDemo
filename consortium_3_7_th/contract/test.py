#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 11/6/21 5:30 AM
# @Author : Archer
# @File : test.py
# @desc :
"""
import json


def data2json():
    data = {
        't1': 'abc',
        't2': 123,
        't3': 1.22
    }
    with open("./test.json", "w") as f:
        json.dump(data, f)
    print("done")


def json2data():
    with open("./test.json", 'r') as load_f:
        load_dict = json.load(load_f)
        print(load_dict)


if __name__ == '__main__':
    # data2json()
    # json2data()
    a = '123'
    data = {'1': a}
    print(data)
    a = 456
    print(data)
