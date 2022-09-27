#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 11/17/21 5:55 AM
# @Author : Archer
# @File : dir_test.py
# @desc :
"""

import os


def path_create(relative_path):
    pwd = os.getcwd()[:]
    new_absolute_path = pwd+'/'
    relative_path = relative_path[2:]
    while len(relative_path) != 0:
        new_absolute_path = new_absolute_path + relative_path[:relative_path.find('/')] + '/'
        if not os.path.exists(new_absolute_path):
            os.makedirs(new_absolute_path)
        relative_path = relative_path[relative_path.find('/')+1:]


if __name__ == '__main__':
    relative_path = './test0/test1/'
    path_create(relative_path)
