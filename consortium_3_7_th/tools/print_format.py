#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 11/5/21 1:12 AM
# @Author : Archer
# @File : print_format.py
# @desc :
"""

def print_success(m):
    print('\033[0;32m%s\033[0m' % m)


def print_error(m):
    print('\033[0;31m%s\033[0m' % m)

if __name__ == '__main__':
    print_success('abc')
    print_error('abc')