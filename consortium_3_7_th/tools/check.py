#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 10/20/21 1:29 AM
# @Author : Archer
# @File : check.py
# @desc :
"""
import secrets
from gmpy2 import *

def getRandomNumber(n):
    number = secrets.randbits(n)
    return number

def int2bit(n):
    bitString = bin(n).replace('0b', '')
    return bitString


if __name__ == '__main__':
    g = getRandomNumber(160)
    h = getRandomNumber(160)
