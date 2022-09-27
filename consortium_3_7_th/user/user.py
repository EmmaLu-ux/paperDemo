#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 11/3/21 6:55 AM
# @Author : Archer
# @File : User.py
# @desc :
"""
import json

from database.DatabaseOperation import *
from database.database_message_create import construct_message
from tools.ecdsa_signature import *


class User(object):
    def __init__(self):
        self.username = None
        self.password = None
        self.sk = None
        self.pk = None
        self.token = None
        self.encfund = None
        self.nonce = None
        self.change_height = None
        self.aution_info = {}

    def user(self, username=None, password=None):
        data = {'username': username,
                'password': password}
        event = construct_message(data=data, index=1)
        event.wait()
        userInfo = DB_ANSWER_QUEUE.get()

        # userInfo = DBOperation(data, 1)
        if userInfo is None:
            return None
        self.username = userInfo['username']
        self.password = userInfo['password']
        self.sk = userInfo['sk']
        self.pk = userInfo['pk']
        self.token = int(userInfo['token'])
        self.enc_fund = userInfo['enc_fund']
        self.nonce = int(userInfo['nonce'])
        self.change_height = userInfo['change_height']
        self.load()
        return self

    def sign(self, message):
        signature = sign(self.sk, message)
        return signature

    def verify(self, message, signature, pk):
        vk = VerifyingKey.from_string(bytes.fromhex(pk), curve=SECP256k1)
        return vk.verify(bytes.fromhex(signature), bytes(message, 'utf-8'))

    def __repr__(self):
        print('\n==============================================')
        print('                account info')
        print('                username:', self.username)
        print('                token:', self.token)
        print('                nonce:', self.nonce)
        print('==============================================\n')

    def store(self):
        pwd = os.getcwd()
        pwd = pwd[:pwd.rfind('/')]
        file_name = pwd + '/user/log/' + self.username + '.json'
        with open(file_name, 'w') as f:
            json.dump(self.aution_info, f)
        print("done")

    def load(self):
        pwd = os.getcwd()
        pwd = pwd[:pwd.rfind('/')]
        file_name = pwd + '/user/log/' + self.username + '.json'
        with open(file_name, 'r') as load_f:
            self.aution_info = json.load(load_f)


# if __name__ == '__main__':
#     user = User().user('archer', 'abc123')
#     user.__repr__()