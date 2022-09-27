#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 11/20/21 7:50 AM
# @Author : Archer
# @File : contract_.py
# @desc :
"""
import json
import os
import time

from config.config import LOGGER
from database.DatabaseOperation import DBOperation
from tools.ecdsa_signature import verify


class Contract_(object):

    def __init__(self):
        self.addr = None
        self.domain_name = None
        self.owner_pk = None
        self.receiver_pk = None
        self.funds = None
        self.data = None

    def transfer(self, pk1, domain_name, pk2, signature, funds, contract_addr):
        self.addr = contract_addr
        data = {'domain_name': domain_name}

        self.owner_pk = pk1
        self.receiver_pk = pk2
        self.domain_name = domain_name
        self.funds = funds

        nowtime = time.time()
        nowtime = 0
        data = {'domain_name': self.data['domain_name']}
        domain_info = DBOperation(data, 11)
        if nowtime < int(domain_info['expirat']):
            if verify(m=self.domain_name, signature=signature, verify_key=domain_info['owner']):
                DBOperation(data, 16)
            else:
                m = 'transfer phase signature check failed!'
                LOGGER.info(m)
        else:
            m = self.domain_name + 'had expired!'
            LOGGER.info(m)
        self.data = {
            'owner_pk': self.owner_pk,
            'receiver_pk': self.receiver_pk,
            'funds': self.funds
        }
        self.data2file_json()

    def receiver(self, pk2, funds, zkp_args):
        if self.zkp():
            # reduce receiver fund
            # add transfer fund
            # transfer domain_name
            pass
        return

    def zkp(self):
        return True


    def data2file_json(self):
        pwd = os.getcwd()
        pwd = pwd[:pwd.rfind('/')]
        file_name = pwd + '/contract/log_1/' + self.addr + '.json'
        with open(file_name, 'w') as f:
            json.dump(self.data, f)
        print("done")

    def file_json2data(self):
        pwd = os.getcwd()
        pwd = pwd[:pwd.rfind('/')]
        file_name = pwd + '/contract/log_1/' + self.addr + '.json'
        with open(file_name, 'r') as load_f:
            self.data = json.load(load_f)
            self.owner = self.data['owner']
            self.bidder = self.data['bidder']
            self.t1 = self.data['t1']
            self.t2 = self.data['t2']
            self.domain_name = self.data['domain_name']




if __name__ == '__main__':
    print('hello world')
