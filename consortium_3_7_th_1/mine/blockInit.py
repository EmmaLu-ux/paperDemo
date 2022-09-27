#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 10/21/21 8:50 PM
# @Author : Archer
# @File : blockInit.py
# @desc :
"""
import time

from transaction_file.transaction import *


class BlockHeader(object):
    """
    version                          4
    prev_block_hash                  32
    merkle_root_hash                 32
    time                             4
    nBits                            4
    nonce                            4
    """

    def __init__(self, version=0, prev_block_hash='0' * 64, tx_root='0' * 64, state_root='0' * 64, nBits=0x1d00ffff,
                 nonce=0, ):
        self.version = version
        self.block_height = 0
        self.prev_block_hash = prev_block_hash
        self.tx_root = tx_root
        self.state_root = state_root
        self.timestamp = int(time.time())
        self.raw_data = None

    def construct(self, version=0, prev_block_hash='0' * 64, tx_root='0' * 64, state_root='0' * 64, block_height=0):
        self.version = version
        self.prev_block_hash = prev_block_hash
        self.tx_root = tx_root
        self.state_root = state_root
        self.timestamp = int(time.time())
        self.block_height = block_height  # get from table
        self.raw_data = self.get_raw()
        return self

    def get_raw(self):
        raw = ''
        raw += str(encode_uint32(self.version))
        raw += str(encode_uint32(self.block_height))
        raw += format_data(self.prev_block_hash)
        raw += format_data(self.tx_root)
        raw += format_data(self.state_root)
        raw += str(encode_uint32(self.timestamp))
        return raw


class Block(object):
    """
    magic_number                     4
    block_size                       4
    block_header                     80
    tx_count                         varies
    txs                              varies
    """

    def __init__(self, magic_number=0xd9b4bef9, block_size=None, tx_count=None):
        self.magic_number = magic_number
        self.block_size = block_size
        self.tx_root = None
        self.state_root = None
        self.block_height = None
        self.block_header = None
        self.block_body = None
        self.tx_count = tx_count
        self.block_hash = None
        self.txs = []
        self.txs_raw = []
        self.raw_data = None

    def tx_merkle_construct(self):
        childs = ['zjgsu-scie-archer']
        parents = []
        childs = self.check_2(childs)
        for i in range(0, len(childs), 2):
            result = double_sha256(childs[i] + childs[i + 1])
            parents.append(result)

        while len(parents) != 1:
            childs = parents
            parents = []
            childs = self.check_2(childs)
            for i in range(0, len(childs), 2):
                result = double_sha256(childs[i].encode() + childs[i + 1])
                parents.append(result)
        self.tx_root = parents[0]

    def state_merkle_construct(self):
        childs = self.get_external_account()
        parents = []
        childs = self.check_2(childs)
        for i in range(0, len(childs), 2):
            result = double_sha256(childs[i] + childs[i + 1])
            parents.append(result)

        while len(parents) != 1:
            childs = parents
            parents = []
            childs = self.check_2(childs)
            for i in range(0, len(childs), 2):
                result = double_sha256(childs[i] + childs[i + 1])
                parents.append(result)
        self.state_root = parents[0]

    def get_external_account(self):
        result = DBOperation(None, 4)
        user_info = [user[0] + user[1] + user[2] for user in result]
        return user_info

    def check_2(self, txs):
        """
        :param txs:
        :return:
        """
        len_txs = len(txs)
        if len_txs % 2 == 1:
            txs.append(txs[len_txs - 1])
        return txs

    def construct(self):
        self.tx_merkle_construct()
        self.state_merkle_construct()
        self.block_header = BlockHeader().construct(tx_root=self.tx_root, state_root=self.state_root)
        self.block_hash = double_sha256(self.block_header.raw_data)
        self.block_height = self.block_header.block_height
        description = 'zjgsu-scie-archer'
        self.block_body = description
        self.raw_data = self.get_raw()
        return self

    def store_in_database(self):

        data = {'block_height': self.block_height,
                'block_hash': self.block_hash,
                'block_magic_number': '58585347',
                'block_size': self.block_size,
                'block_head': self.block_header.raw_data,
                'block_body': self.block_body}
        DBOperation(data, 6)

    def get_raw(self):
        raw = ''
        raw += self.block_header.raw_data
        raw += self.block_body

        self.block_size = len(raw)
        raw = '58585347' + encode_varint(self.block_size) + raw
        return raw


if __name__ == '__main__':
    initblock = Block().construct()
    initblock.store_in_database()
