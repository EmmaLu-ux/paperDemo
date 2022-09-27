#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 9/21/21 11:12 PM
# @Author : Archer
# @File : transaction.py
# @desc :
"""
import threading

from config.config import DB_QUEST_QUEUE, DB_TH_EVENT, DB_ANSWER_QUEUE
from tools.utils import *

from database.DatabaseOperation import DBOperation


class Transaction(object):
    def __init__(self):
        self.version = None
        self.from_ = None
        self.to = None
        self.value = None
        self.data = None
        self.nonce = None
        self.signature = None
        self.raw_data = None
        self.tx_hash = None
        self.data_raw = None

    def construct(self, version=None, from_=None, to=None, value=None, data=None, signature=None, nonce=None):
        self.version = version  # 1: receiver is external account 2: receiver is contract
        self.from_ = from_
        self.to = to
        self.value = value
        self.data = data
        self.signature = signature
        self.nonce = nonce
        self.raw_data = self.get_raw()
        self.tx_hash = double_sha256(self.raw_data)
        return self

    def check_transaction_construct(self):
        pass

    def get_raw(self):
        self.data_raw = self.get_data_raw()
        raw = ''
        raw += str(encode_uint32(self.version))

        raw += format_data(self.from_)

        len_data = len(format_data(self.to))
        raw += str(encode_varint(len_data))
        raw += format_data(self.to)

        raw += str(encode_uint64(self.value))

        len_data = len(format_data(self.data_raw))
        raw += str(encode_varint(len_data))
        raw += format_hash(self.data_raw)
        raw += format_data(self.signature)

        raw += str(encode_uint32(self.nonce))
        return raw

    def get_data_raw(self):
        data = self.data
        data_raw = ''
        len_data = len(format_data(data['hash_code']))
        data_raw += str(encode_varint(len_data))
        data_raw += format_data(data['hash_code'])

        len_data = len(format_data(data['prev_state']))
        data_raw += str(encode_varint(len_data))
        data_raw += format_data(data['prev_state'])

        data_raw += str(encode_varint(data['func_number']))

        len_data = len(format_data(data['args']))
        data_raw += str(encode_varint(len_data))
        data_raw += format_data(data['args'])


        len_data = len(format_data(data['domain_name']))
        data_raw += str(encode_varint(len_data))
        data_raw += format_data(data['domain_name'])

        len_data = len(format_data(data['domain_name_ip']))
        data_raw += str(encode_varint(len_data))
        data_raw += format_data(data['domain_name_ip'])
        return data_raw

    def store_in_database(self, if_pack='0'):
        data = {
            'tx_hash': self.tx_hash,
            'tx_version': self.version,
            'tx_from': self.from_,
            'tx_to': self.to,
            'tx_value': self.value,
            'tx_data': self.data_raw,
            'tx_signature': self.signature,
            'tx_nonce': self.nonce,
            'if_pack': if_pack
        }

        event = threading.Event()
        data_ = (data, 2, event)
        DB_QUEST_QUEUE.put(data_)
        DB_TH_EVENT.set()
        event.wait()
        DB_ANSWER_QUEUE.get()
        # DBOperation(data, 2)

        data = {'tx_hash': self.tx_hash,
                'raw_data': self.raw_data,
                'if_pack': if_pack}

        event = threading.Event()
        data_ = (data, 3, event)
        DB_QUEST_QUEUE.put(data_)
        DB_TH_EVENT.set()
        event.wait()
        DB_ANSWER_QUEUE.get()
        # DBOperation(data, 3)





    # def __repr__(self):
    #     print("<tx>:\n")
    #     return
