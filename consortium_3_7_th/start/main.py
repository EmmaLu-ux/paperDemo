#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 11/20/21 6:10 PM
# @Author : Archer
# @File : main.py
# @desc :
"""
from mine.block import Block
from transaction_file.trade import Trading
from user.user import User
from config.thread_config import *

def func(user):
    while True:
        print('1. pack block')
        print('2. trade')
        print('3. logout')
        choice = int(input('please input your choice number: '))
        if choice == 1:
            block = Block().construct()
            block.store_in_database()
            pass
        elif choice == 2:
            Trading().trading(user)
            pass
        elif choice == 3:
            username = input('please input your username: ')
            password = input('please input your password: ')
            user = User().user(username=username, password=password)
            user.__repr__()
        else:
            print('invalid choice number.\n')

def login():
    username = input('please input your username: ')
    password = input('please input your password: ')
    user = User().user(username=username, password=password)
    user.__repr__()
    func(user)


if __name__ == '__main__':
    login()