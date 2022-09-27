#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 11/7/21 5:43 AM
# @Author : Archer
# @File : block_parse.py
# @desc :
"""
import threading

from config.config import DB_QUEST_QUEUE, DB_TH_EVENT, DB_ANSWER_QUEUE, LOGGER
from contract.contract import Contract
from database.database_message_create import construct_message
from mine.block import BlockHead
from parse.block_head_parse import BlockHeadParse
from parse.transaction_parse import TransactionParse
from tools.jsonOp import file2json, json2file
from tools.utils import *


class BlockParse(object):

    def __init__(self, magic_number=0x47535858, block_size=None, tx_count=None, coninbase=None, txs=None):
        self.magic_number = magic_number
        self.block_size = block_size
        self.tx_root = None
        self.state_root = None
        self.block_height = None
        self.block_head = None
        self.block_body = None
        self.tx_count = tx_count
        self.block_hash = None
        self.txs = []
        self.txs_raw = {}
        self.raw_data = None

    def tx_merkle_construct(self):
        childs = []
        for tx in self.txs:
            childs.append(self.txs_raw[tx.tx_hash])
        if len(childs) == 0:
            childs = ['zjgsu-scie']
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
        event = construct_message(data=None, index=4)
        event.wait()
        result = DB_ANSWER_QUEUE.get()
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

    def parse(self, block_head_raw, tx_hash_list):
        block_head_ = BlockHeadParse().parser(block_head_raw)
        if tx_hash_list[0] != 'zjgsu-scie':
            self.get_tx(tx_hash_list)

        self.tx_merkle_construct()
        self.state_merkle_construct()

        event = construct_message(data=None, index=7)
        event.wait()
        pre_block = DB_ANSWER_QUEUE.get()
        # pre_block = DBOperation(None, 7)

        self.block_height = pre_block['block_height'] + 1

        self.block_head = BlockHead().construct(tx_root=self.tx_root,
                                                state_root=self.state_root,
                                                prev_block_hash=pre_block['block_hash'],
                                                block_height=self.block_height,
                                                timestamp=block_head_.timestamp)

        self.block_hash = double_sha256(self.block_head.raw_data)
        assert self.block_hash == block_head_.block_hash
        return self
        # DBOperation(tx_raw, 9)

    def get_tx(self, tx_hash_list):
        for tx_hash in tx_hash_list:
            data = {'tx_hash': tx_hash}
            event = construct_message(data=data, index=18)
            event.wait()
            tx_raw = DB_ANSWER_QUEUE.get()

            tx = TransactionParse().parse(tx_raw)
            self.txs.append(tx)
            self.txs_raw[tx_hash] = tx_raw


            if tx.version == 1:
                self.update_user_info(tx)
            elif tx.version == 2:
                self.create_contract(tx)
            elif tx.version == 3:
                self.invoke_contact(tx)
                pass
            data = {'tx_hash':tx_hash}

            event = construct_message(data=data, index=9)
            event.wait()
            DB_ANSWER_QUEUE.get()
        return

    def update_user_info(self, tx):
        tx_info = {'from_': tx.from_,
                   'value': tx.value,
                   'to': tx.to,
                   'nonce': tx.nonce}
        data = {'pk': tx_info['from_']}
        event = construct_message(data=data, index=13)
        event.wait()
        user_from = DB_ANSWER_QUEUE.get()
        # user_from = DBOperation(data, 13)

        data = {'pk': tx_info['to']}
        event = construct_message(data=data, index=13)
        event.wait()
        user_to = DB_ANSWER_QUEUE.get()
        # user_to = DBOperation(data, 13)

        user_from['value'] -= tx_info['value']
        user_from['nonce'] += 1
        user_to['value'] += tx_info['value']

        event = construct_message(data=user_to, index=14)
        event.wait()
        DB_ANSWER_QUEUE.get()
        # DBOperation(user_to, 14)

        event = construct_message(data=user_from, index=14)
        event.wait()
        DB_ANSWER_QUEUE.get()
        # DBOperation(user_from, 14)

    def create_contract(self, tx):
        tx_info = {'from_': tx.from_,
                   'value': tx.value,
                   'to': tx.to,
                   'data': tx.data,
                   'nonce': tx.nonce}

        data = {'pk': tx_info['from_']}

        event = construct_message(data=data, index=13)
        event.wait()
        user_from = DB_ANSWER_QUEUE.get()
        # user_from = DBOperation(data, 13)

        user_from['nonce'] += 1
        # update user_info
        event = construct_message(data=user_from, index=14)
        event.wait()
        DB_ANSWER_QUEUE.get()
        # DBOperation(user_from, 14)

        # creat contract addr
        addr = double_sha256(tx.from_ + tx.data['hash_code'])
        data = {
            'addr': addr,
            'owner': tx.from_,
            'enc_fund': 0,
            'hash_code': tx.data['hash_code']
        }
        event = construct_message(data=data, index=10)
        event.wait()
        DB_ANSWER_QUEUE.get()
        # DBOperation(data, 10)
        m = 'the contract store successfully!'
        LOGGER.info(m)

    def store_in_json_file(self):
        file_name = '/p2p/tx.json'
        testdata = file2json(file_name)
        print(testdata)
        block_data = {'block_height': self.block_height,
                      'block_size': self.block_size,
                      'block_head': self.block_head.raw_data,
                      'tx_hash_list': [tx.tx_hash for tx in self.txs]}
        data = {'m_type': 'block',
                'm_owner': None,
                'm_file': None,
                'm_hash': self.block_hash,
                'm_data': block_data}
        testdata['data'].append(data)
        print(testdata)
        json2file(data=testdata, relative_path=file_name)

    def store_in_database(self):
        data = {'block_height': self.block_height,
                 'block_hash': self.block_hash,
                 'block_magic_number': '58585347',
                 'block_size': self.block_size,
                 'block_head': self.block_head.raw_data,
                 'block_body': self.block_body}
        event = construct_message(data=data, index=6)
        event.wait()
        DB_ANSWER_QUEUE.get()
        # DBOperation(data, 6)

    def invoke_contact(self, tx):
        args_addr = tx.data['args_addr']
        file_path = '/transaction_file/revoke_contract_log/' + tx.to + '/' + args_addr + '.json'
        args_data = file2json(file_path)
        if tx.data['func_number'] == 0:
            t1 = args_data['invoke_create']['t1']
            t2 = args_data['invoke_create']['t2']
            domain_name = args_data['invoke_create']['domain_name']
            signature = args_data['invoke_create']['signature']
            con = Contract().create(t1=t1, t2=t2, domain_name=domain_name, signature=signature, contract_addr=tx.to)
            pass
        elif tx.data['func_number'] == 1:
            pk = args_data['invoke_commit']['pk']
            funds = args_data['invoke_commit']['funds']
            signature = args_data['invoke_commit']['sig']
            zkp = args_data['invoke_commit']['zkp']
            con = Contract().commit(pk=pk, funds=funds, sig=signature, zkp_args=zkp, contract_addr=tx.to)

        elif tx.data['func_number'] == 2:
            pk = args_data['invoke_reveal']['pk']
            c_r = args_data['invoke_reveal']['c_r']
            con = Contract().reveal(pk=pk, c_r_list=c_r, contract_addr=tx.to)
            pass

        elif tx.data['func_number'] == 3:
            con = Contract().finalize(contract_addr=tx.to)
        elif tx.data['func_number'] == 4:
            pk = args_data['invoke_update']['pk']
            domain_name = args_data['invoke_update']['domain_name']
            ip = args_data['invoke_update']['ip']
            sig = args_data['invoke_update']['signature']

            con = Contract().update(pk=pk, domain_name=domain_name, ip=ip, sig=sig, contract_addr=tx.to)

        elif tx.data['func_number'] == 5:
            pk1 = args_data['invoke_transfer']['pk1']
            pk2 = args_data['invoke_transfer']['pk2']
            domain_name = args_data['invoke_transfer']['domain_name']

            sig = args_data['invoke_transfer']['signature']
            funds = args_data['invoke_transfer']['funds']
            end_time = args_data['invoke_transfer']['end_time']
            con = Contract().transfer(pk1=pk1, domain_name=domain_name, pk2=pk2, sig=sig, funds=funds,
                                      end_time=end_time,
                                      contract_addr=tx.to)

        elif tx.data['func_number'] == 6:
            pk2 = args_data['invoke_receiver']['pk2']
            domain_name = args_data['invoke_receiver']['domain_name']
            funds = args_data['invoke_receiver']['funds']
            zkp = args_data['invoke_receiver']['zkp']
            con = Contract().receiver(domain_name=domain_name, pk2=pk2, funds=funds, zkp_args=zkp, contract_addr=tx.to)

        elif tx.data['func_number'] == 7:
            pk1 = args_data['invoke_renewal']['pk1']
            pk2 = args_data['invoke_renewal']['pk2']
            domain_name = args_data['invoke_renewal']['domain_name']
            funds = args_data['invoke_renewal']['funds']
            sig = args_data['invoke_renewal']['signature']
            zkp = args_data['invoke_renewal']['zkp']

            con = Contract().renewal(pk1=pk1, pk2=pk2, domain_name=domain_name, funds=funds, zkp_args=zkp, sig=sig,
                                     contract_addr=tx.to)

            pass

        # args_addr = tx.data['args_addr']
        # file_path = '/transaction_file/revoke_contract_log/' + tx.to + '/' + args_addr + '.json'
        # args_data = file2json(file_path)
        # if tx.data['func_number'] == 0:
        #     t1 = args_data['invoke_create']['t1']
        #     t2 = args_data['invoke_create']['t2']
        #     domain_name = args_data['invoke_create']['domain_name']
        #     signature = args_data['invoke_create']['signature']
        #     con = Contract().create(t1=t1, t2=t2, domain_name=domain_name, signature=signature, contract_addr=tx.to)
        #     pass
        # elif tx.data['func_number'] == 1:
        #     pk = args_data['invoke_commit']['pk']
        #     funds = args_data['invoke_commit']['funds']
        #     signature = args_data['invoke_commit']['sig']
        #     zkp = args_data['invoke_commit']['zkp']
        #     con = Contract().commit(pk=pk, funds=funds, sig=signature, zkp_args=zkp, contract_addr=tx.to)
        #
        # elif tx.data['func_number'] == 2:
        #     pk = args_data['invoke_reveal']['pk']
        #     c_r = args_data['invoke_reveal']['c_r']
        #     con = Contract().reveal(pk=pk, c_r_list=c_r, contract_addr=tx.to)
        #     pass
        # elif tx.data['func_number'] == 3:
        #     con = Contract().finalize(contract_addr=tx.to)
        #
        # elif tx.data['func_number'] == 4:
        #     pk = args_data['invoke_update']['pk']
        #     domain_name = args_data['invoke_update']['domain_name']
        #     ip = args_data['invoke_update']['ip']
        #     sig = args_data['invoke_update']['signature']
        #
        #     con = Contract().update(pk=pk, domain_name=domain_name, ip=ip, sig=sig, contract_addr=tx.to)
        # elif tx.data['func_number'] == 5:
        #     pk1 = args_data['invoke_transfer']['pk1']
        #     pk2 = args_data['invoke_transfer']['pk2']
        #     domain_name = args_data['invoke_transfer']['domain_name']
        #
        #     sig = args_data['invoke_transfer']['signature']
        #     funds = args_data['invoke_transfer']['funds']
        #     con = Contract().transfer(pk1=pk1, domain_name=domain_name, pk2=pk2, sig=sig, funds=funds,
        #                               contract_addr=tx.to)
        # elif tx.data['func_number'] == 6:
        #     pk2 = args_data['invoke_receiver']['pk2']
        #     domain_name = args_data['invoke_receiver']['domain_name']
        #     funds = args_data['invoke_receiver']['funds']
        #     con = Contract().receiver(domain_name=domain_name, pk2=pk2, funds=funds, contract_addr=tx.to)
        #
        # elif tx.data['func_number'] == 7:
        #     pk1 = args_data['invoke_renewal']['pk1']
        #     pk2 = args_data['invoke_renewal']['pk2']
        #     domain_name = args_data['invoke_renewal']['domain_name']
        #     funds = args_data['invoke_renewal']['funds']
        #     sig = args_data['invoke_renewal']['signature']
        #     con = Contract().renewal(pk1=pk1, pk2=pk2, domain_name=domain_name, funds=funds, contract_addr=tx.to,
        #                              sig=sig)


if __name__ == '__main__':
    assert (1 == 2)
