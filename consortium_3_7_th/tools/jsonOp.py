#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 11/13/21 12:26 AM
# @Author : Archer
# @File : jsonOp.py
# @desc :
"""
import json
import os
from config.config import COMMON_PATH


def path_create(path):
    dir_path = COMMON_PATH + path
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def file2json(relative_path):
    file_path = COMMON_PATH + relative_path
    data = None
    try:

        with open(file_path, 'r') as load_f:
            data = json.load(load_f)
    except IOError:

        # LOGGER.error('open' + relative_path+' failed')
        return {}
    else:
        return data


def json2file(relative_path, data):
    file_path = COMMON_PATH + relative_path
    with open(file_path, 'w+') as f:
        json.dump(data, f)
        f.close()
    print("done")


if __name__ == '__main__':
    addr = '123'
    data = {'hhh': 123}
    re = ''
    json2file(addr, data)
