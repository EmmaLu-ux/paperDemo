#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 11/25/21 5:40 PM
# @Author : Archer
# @File : getTestData.py
# @desc :
"""
from config.config import NODE, NODE_INFO
from mine.block import Block
from p2p.message_construct import tx_broad_message, pre_prepare_message, commit_message, prepare_message
from tools.jsonOp import json2file, file2json
from config.thread_config import *
from transaction_file.trade import Trading
from user.user import User


def contract_create(path):
    data = []
    username = 'root'
    password = 'abc123'
    user = User().user(username=username, password=password)
    trade = Trading(user=user)
    args = {'func_choice': 0,
            'to': '09b3c2f25c070578976c4befb0f3359c50f4710dea07f22243b3a0e7ddb8c562',
            't1': 123,
            't2': 123456,
            'domain_name': 'http://test.com',}
    tx = trade.invoke_contract(args=args)
    tx.store_in_database()
    message = tx_broad_message(tx)
    data.append(message)
    json2file(path, data)
    print('success')



def broadcast_test(path):
    message = file2json(path)
    NODE.send_to_nodes(message)

def block(path):
    block = Block().construct()
    m_hash = block.block_hash
    block_head = block.block_head.raw_data
    block_tx_hash_list = [tx.tx_hash for tx in block.txs]
    if len(block_tx_hash_list) == 0:
        block_tx_hash_list.append('zjgsu-scie')
    leader_node = NODE_INFO
    sequence_number = 1
    data = []
    pre_prepare = pre_prepare_message(block_head=block_head, m_hash=m_hash, block_tx_hash_list=block_tx_hash_list, leader_node=leader_node, sequence_number=sequence_number)
    data.append(pre_prepare)

    prepare = prepare_message(m_hash=m_hash, leader_node=leader_node, sequence_number=sequence_number)
    data.append(prepare)

    commit = commit_message(m_hash=m_hash, leader_node=leader_node, sequence_number=sequence_number)
    data.append(commit)
    json2file(path, data)

    # block.store_in_database()


def create_contract_account():
    username = 'mike'
    password = 'abc123'
    user = User().user(username=username, password=password)
    trade = Trading(user=user)
    to = ""
    tx = trade.create_contract()
    a = 1


if __name__ == '__main__':
    path = "/test_data/tx.json"
    contract_create(path)
    path = "/test_data/block.json"
    block(path)


