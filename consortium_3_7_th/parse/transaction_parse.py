#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 11/7/21 5:55 AM
# @Author : Archer
# @File : transaction_parse.py
# @desc :
"""
from tools.utils import *
from user.user import *
from database.database_message_create import construct_message

class TransactionParse(object):
    def __init__(self):

        self.version = None
        self.from_ = None
        self.to = None
        self.value = None
        self.data = {
            'hash_code': None,  # no use?
            'prev_state': None,
            'func_number': None,
            'args_addr': None,
            'domain_name': None,
            'domain_name_ip': None,
            'file_path': None,
        }
        self.signature = None
        self.nonce = None
        self.raw_data = None
        self.tx_hash = None
        self.data_raw = None
        self.signature_data = None
        self.size = None

    def parse(self, raw_data):
        self.raw_data = raw_data
        self.size = len(raw_data)
        offset = 0
        self.tx_hash = double_sha256(raw_data)
        self.version = decode_uint32(raw_data[offset: offset + 8])
        offset += 8
        self.from_ = format_data(raw_data[offset: offset + 128])
        offset += 128

        to_len, size = decode_varint(raw_data[offset:])
        offset += size
        self.to = format_data(raw_data[offset: offset + to_len])
        offset += to_len

        self.value = decode_uint64(raw_data[offset: offset + 16])
        offset += 16

        data_len, size_ = decode_varint(raw_data[offset:])
        offset += size_
        self.data_parse(format_data(raw_data[offset: offset + data_len]))
        offset += data_len
        self.signature_data = raw_data[:offset] + raw_data[offset + 128:]
        self.signature = format_data(raw_data[offset: offset + 128])
        offset += 128

        self.nonce = decode_uint32(raw_data[offset: offset + 8])
        offset += 8


        return self

    def signature_verify(self):
        if not verify(m=self.signature_data, signature=self.signature, verify_key=self.from_):
            return False
        return True

    def check_if_stored(self):
        """

        :return: True: tx had been stored
                 False: tx does not be stored
        """
        data = {'tx_hash': self.tx_hash}
        event = construct_message(data, index=20)
        event.wait()
        return DB_ANSWER_QUEUE.get()



    def data_parse(self, raw_data):
        offset = 0
        keys = ['hash_code', 'prev_state', 'func_number', 'args_addr', 'domain_name', 'domain_name_ip']
        for key in keys:
            if key == 'func_number':
                a = raw_data[offset:]
                self.data[key], size = decode_varint(raw_data[offset:])
                offset += size
            else:
                len_, size = decode_varint(raw_data[offset:])
                offset += size
                self.data[key] = format_data(raw_data[offset: offset + len_])
                offset += len_
        if self.version == 2:
            self.data['file_path'] = None
        elif self.version == 3:
            self.data['file_path'] = '/transaction_file/revoke_contract_log/' + self.to + '/' + self.from_ + '.json'

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


        event = construct_message(data=data, index=2)
        event.wait()
        DB_ANSWER_QUEUE.get()
        # DBOperation(data, 2)


        data = {'tx_hash': self.tx_hash,
                'raw_data': self.raw_data,
                'if_pack': if_pack}
        event = construct_message(data=data, index=3)
        event.wait()
        DB_ANSWER_QUEUE.get()
        # DBOperation(data, 3)


if __name__ == '__main__':
    a = '123'
    b = a[0:0]
    print(b)
