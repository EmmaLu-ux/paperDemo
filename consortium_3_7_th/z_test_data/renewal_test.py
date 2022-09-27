#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 3/4/22 12:51 AM
# @Author : Archer
# @File : update_test.py
# @desc :
"""
import time
import sys
sys.path.append('../')
from transaction_file.transaction_args import invoke_create_args, invoke_update_args, invoke_renewal_args
from config.config import NODE_INFO, NODE, TEST_KEY, DEMO_AMOUNT
from mine.block import Block
from p2p.message_construct import pre_prepare_message, tx_broad_message
from tools.jsonOp import file2json, json2file
from transaction_file.trade import Trading
from user.user import User
from config.thread_config import *


def renewal_test(contract_addr, t, i):
    to = contract_addr
    domain_name = 'http://test' + str(i) + '.com'

    args = invoke_renewal_args(to=to, user=t.user, domain_name=domain_name, value=5, pk1=t.user.pk)
    tx = t.invoke_contract(args)
    message = tx_broad_message(tx)
    NODE.send_to_nodes(message)
    a = 1


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
    time_[TEST_KEY] = {'start': start}
    json2file(cost_time, time_)
    for i in range(0, DEMO_AMOUNT):
        contract_addr = contract_list[i]
        renewal_test(contract_addr, root, i)
        pack_block()
