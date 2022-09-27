#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 9/21/21 11:40 PM
# @Author : Archer
# @File : mining.py
# @desc :
"""

from mine.block import *


class Mining(object):
    def __init__(self):
        self.target = None
        self.rewards = None
        self.block_header = None
        self.block = None
        self.coinbase = None
        self.txs = None
        pass

    def cal_dif(self, nBits):
        exponents = int(nBits / 0x1000000)
        exp = 64 - exponents * 2
        coefficient = hex(nBits % 0x1000000)[2:].zfill(6)
        target = exp * '0' + coefficient + (64 - 6 - exp) * '0'
        self.target = target

    def mining(self):
        new_block = Block().construct()
        self.cal_dif(new_block.block_header.nBits)
        CON.acquire()

        global THREAD_Pow
        THREAD_Pow = threading.Thread(target=pow_task, name='thread_db')
        QUEUE.put(new_block)
        QUEUE.put(self.target)
        CON.release()
        THREAD_Pow.start()
        THREAD_Pow.join()

        CON.acquire()
        new_block = QUEUE.get()
        CON.release()
        self.block = new_block

        print('\n\n               mining success!!!')
        print(self.__repr__())
        data = {'block_hash': new_block.block_hash,
                'block_height': new_block.block_header.block_height,
                'block_head': new_block.block_header.get_raw(),
                'block_tx_count': encode_varint(new_block.tx_count),
                'block_body': ''.join(new_block.block_body)}

        storeDB(data, 0)
        self.block.coinbase.store_in_database('1')
        self.block.change_tx_if_use()
        self.block.clear_store_utxos()
        return self

    def __repr__(self):
        return '                <block_height>: {block_height} \n' \
               '                <block_hash>: {block_hash} \n' \
               '                <block_reward>: {block_reward} \n' \
               '                <block_gas_fee>: {gas_fee} \n\n'.format(
            block_height=self.block.block_header.block_height, block_hash=self.block.block_hash, block_reward=6,
            gas_fee=self.block.gas_fee)



def pow_task():
    CON.acquire()
    new_block = QUEUE.get()
    target = QUEUE.get()
    CON.release()
    block_hash_ = format_data(double_sha256(new_block.block_header.get_raw()))
    while int(block_hash_, 16) > int(target, 16):
        # print(block_hash_)
        new_block.block_header = new_block.cal()
        block_hash_ = double_sha256(new_block.block_header.get_raw())
    new_block.block_hash = block_hash_
    CON.acquire()
    QUEUE.put(new_block)
    CON.release()