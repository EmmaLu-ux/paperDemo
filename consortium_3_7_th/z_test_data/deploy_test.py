#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 3/3/22 6:29 PM
# @Author : Archer
# @File : create_test.py
# @desc :
"""
import time
import sys
sys.path.append('../')

from mine.block import Block
from p2p.message_construct import pre_prepare_message, prepare_message, commit_message, tx_broad_message
from tools.jsonOp import json2file, file2json
from transaction_file.trade import Trading
from user.user import User
from config.config import *
from config.thread_config import *


def deploy(user):
    # deploy contract

    contract_list = []
    for i in range(0, 50):
        contract = user.create_contract()
        contract.store_in_database()
        message = tx_broad_message(contract)
        NODE.send_to_nodes(message)
        contract_list.append(contract.tx_hash)
    return contract_list


def pack_block():
    block = Block().construct()
    block.store_in_database()

    m_hash = block.block_hash
    block_head = block.block_head.raw_data
    block_tx_hash_list = [tx.tx_hash for tx in block.txs]
    if len(block_tx_hash_list) == 0:
        block_tx_hash_list.append('zjgsu-scie')
    leader_node = NODE_INFO
    sequence_number = 1

    pre_prepare = pre_prepare_message(block_head=block_head, m_hash=m_hash, block_tx_hash_list=block_tx_hash_list,
                                      leader_node=leader_node, sequence_number=sequence_number)
    print('send message')
    NODE.send_to_nodes(pre_prepare)
    a = 1



if __name__ == '__main__':
    path = '/z_test_data/contract.json'
    contract_list = file2json(path)

    username = 'root'
    password = 'abc123'
    user = User().user(username=username, password=password)
    root = Trading(user)
    cost_time = '/z_test_data/cost_time.json'
    time_ = file2json(cost_time)
    start = int(round(time.time() * 1000))
    time_['deploy'] = {'start': start}
    json2file(cost_time, time_)

    pack_block()

    json2file(path, contract_list)
