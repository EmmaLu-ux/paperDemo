#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 9/22/21 12:03 AM
# @Author : Archer
# @File : trade.py
# @desc :
"""
from tools.jsonOp import json2file, file2json, path_create
from transaction_file.transaction import *
from user.user import *
from tools.schnorrRing import *


# from config.thread_config import *

class Trading(object):
    def __init__(self, user=None):
        self.user = user
        pass

    def Trading(self, user):
        self.user = user

        # print('1. normal_transaction')
        # print('2. create_contract')
        # print('3. invoke_contract')
        # version = int(input('please input your choice number: '))
        # version = 2
        # if version == 1:
        #     self.nomarl_transaction()
        # elif version == 2:
        #     self.create_contract()
        # elif version == 3:
        #     self.invoke_contract()

    def init_data(self, hash_code='', prev_state='', func_number=0, args='',
                  domain_name='', domain_name_ip='', file_path=''):
        data = {'hash_code': hash_code,
                'prev_state': prev_state,
                'func_number': func_number,
                'args': args,
                'domain_name': domain_name,
                'domain_name_ip': domain_name_ip,
                'file_path': file_path}
        return data

    def nomarl_transaction(self, to, value):
        version = 1
        # to = input('please input the receiver:')
        # value = int(input('please input the trade value:'))

        # to = 'a4b157e680d00f77a385e422f591d1aae3c7be3e6e2ba954abac53ce4a2803813d57a368ddb2e69f02afe8724e3351fdc105236d639eab44c733cee0814c1b90'
        # value = 10

        data = self.init_data()

        tx_raw = Transaction().construct(version=version, from_=self.user.pk, to=to, value=value,
                                         data=data, signature='', nonce=self.user.nonce).get_raw()
        print('tx_raw')
        print(tx_raw)

        signature = self.user.sign(tx_raw)
        tx = Transaction().construct(version=version, from_=self.user.pk, to=to, value=value,
                                     data=data, signature=signature, nonce=self.user.nonce)
        self.user.nonce += 1
        print('signature')
        print(signature)
        print('pk')
        print(self.user.pk)
        return tx
        # tx.store_in_database('0')
        # m = '<tx: ' + tx.tx_hash + ' store successfully\n from you to ' + to + '\n value: ' + str(value) + '>'
        # LOGGER.info(m)

    def create_contract(self):
        # hash_code = double_sha256('contract')
        hash_code = '413791f5a8fb4acff5b710b798e2b636b17d500f4c7596603805face9128e0a8'
        data = self.init_data(hash_code=hash_code, prev_state='0' * 64)
        value = 0
        to = ''
        version = 2
        self.user.nonce += 1
        tx_raw = Transaction().construct(version=version, from_=self.user.pk, to=to, value=value,
                                         data=data, signature='', nonce=self.user.nonce).get_raw()
        signature = self.user.sign(tx_raw)
        tx = Transaction().construct(version=version, from_=self.user.pk, to=to, value=value,
                                     data=data, signature=signature, nonce=self.user.nonce)

        tx.store_in_database('0')
        addr = tx.tx_hash
        m = '<tx: ' + tx.tx_hash + ' store successfully\n you have created the contract on ' + str(addr) + '>'
        # print_success(m)
        dir_ = '/transaction_file/revoke_contract_log/' + str(addr)
        path_create(dir_)

        return tx

    def invoke_contract(self, args):
        version = 3
        # to = input('please input the contract address: ')
        # print('1: create')
        # print('2: commit')
        # print('3: reveal')
        # print('4: finalize')
        # print('5: update')
        # print('6: transfer')
        # to = 'e3c4f4972a5049a633f30cf77a857c3e5140f1523480f3ae39325129682757f9'

        # func_choice = int(input('please input the function number: '))
        func_choice = args['func_choice']
        # func_choice = 3
        if func_choice == 0:
            data = self.invoke_create(args)
        elif func_choice == 1:
            data = self.invoke_commit(args)
        elif func_choice == 2:
            data = self.invoke_reveal(args)
        elif func_choice == 3:
            data = self.invoke_finalize(args)
        elif func_choice == 4:
            data = self.invoke_update(args)
        elif func_choice == 5:
            data = self.invoke_transfer(args)
        elif func_choice == 6:
            data = self.invoke_receiver(args)
        elif func_choice == 7:
            data = self.invoke_renewal(args)
        tx_raw = Transaction().construct(version=version, from_=self.user.pk, to=args['to'], value=0,
                                         data=data, signature='', nonce=self.user.nonce).get_raw()
        signature = self.user.sign(tx_raw)
        tx = Transaction().construct(version=version, from_=self.user.pk, to=args['to'], value=0,
                                     data=data, signature=signature, nonce=self.user.nonce)
        m = '<tx: ' + tx.tx_hash + ' store successfully >'
        LOGGER.info(m)
        tx.store_in_database('0')
        return tx

        #

    def invoke_create(self, args):
        to = args['to']
        t1 = args['t1']
        t2 = args['t2']
        domain_name = args['domain_name']
        signature = self.user.sign(domain_name)
        args_addr = self.user.pk
        args = {'t1': t1,
                't2': t2,
                'domain_name': domain_name,
                'signature': signature}
        json_data = {'invoke_create': args}
        dir_path = '/transaction_file/revoke_contract_log/' + to
        path_create(dir_path)
        path = '/transaction_file/revoke_contract_log/' + to + '/' + args_addr + '.json'

        json2file(path, json_data)
        LOGGER.info(str(json_data) + ' store in ' + args_addr + '.json')
        data = self.init_data(func_number=0, args=args_addr, file_path=path)
        return data

    def invoke_commit(self, args):
        '''

        :param to:  contract_addr
        :param bidding_price: bidding price
        :return:
        '''
        to = args['to']
        bidding_price = args['bidding_price']
        file_path = '/contract/log/' + to + '.json'
        con_prev_state = file2json(file_path)
        con_prev_state_hash = double_sha256(str(con_prev_state))

        pk = self.user.pk

        data = getsk(self.user.token, bidding_price)
        pk = data[0]
        sk = data[1]
        funds = data[2]
        c_r = data[3]
        m = 'ZJGSUSCIE'
        ecdsa_sig = self.user.sign(m)
        schnorr_sig = schnorrSign(m, sk)
        ring_sign_info_1 = ringScheme(funds[1])
        ring_sign_info_2 = ringScheme(funds[2])
        zkp_args = {'pk': pk,
                    'fund0': funds[0],
                    'fund1': funds[1],
                    'fund2': funds[2],
                    'schnorr_sig': schnorr_sig,
                    'ring_sign_info_1': ring_sign_info_1,
                    'ring_sign_info_2': ring_sign_info_2
                    }
        # zkp_args = [pk, schnorr_sig, ring_sign_info_1, ring_sign_info_2]
        domain_name = con_prev_state['domain_name']

        args = {'pk': self.user.pk,
                'funds': [fund['fund'] for fund in funds[1]],
                'sig': ecdsa_sig,
                'zkp': zkp_args}
        args_addr = self.user.pk

        path = '/transaction_file/revoke_contract_log/' + to + '/' + args_addr + '.json'
        json_data = file2json(path)
        json_data['invoke_commit'] = args
        json2file(path, json_data)
        LOGGER.info(str(json_data) + ' store in ' + args_addr + '.json')
        self.user.aution_info[domain_name] = {'pk': pk,
                                              'bidding_price': bidding_price,
                                              'sk': sk,
                                              'funds': funds,
                                              'c_r': c_r[1],
                                              'schnorr_sig': schnorr_sig,
                                              'ring_sign_info_1': ring_sign_info_1,
                                              'ring_sign_info_2': ring_sign_info_2}
        self.user.store()
        data = self.init_data(prev_state=con_prev_state_hash, func_number=1, args=args_addr, file_path=path)
        return data

    def invoke_reveal(self, args):
        to = args['to']
        args_addr = self.user.pk
        file_path = '/contract/log/' + to + '.json'
        con_prev_state = file2json(file_path)
        con_prev_state_hash = double_sha256(str(con_prev_state))
        domain_name = con_prev_state['domain_name']
        args = {'pk': self.user.pk,
                'c_r': self.user.aution_info[domain_name]['c_r']}
        path = '/transaction_file/revoke_contract_log/' + to + '/' + args_addr + '.json'
        json_data = file2json(path)
        json_data['invoke_reveal'] = args
        json2file(path, json_data)
        data = self.init_data(prev_state=con_prev_state_hash, func_number=2, args=args_addr, file_path=path)
        return data

    def invoke_finalize(self, args):
        to = args['to']
        args_addr = self.user.pk
        file_path = '/contract/log' + to + '.json'
        con_prev_state = file2json(file_path)
        con_prev_state_hash = double_sha256(str(con_prev_state))
        data = self.init_data(prev_state=con_prev_state_hash, func_number=3, args=args_addr)
        return data

    def invoke_update(self, args):
        """
        :param args:  { 'to' : contract_addr,
                        'domain_name': domain_name,
                        'ip': ip,
                        'signature': signature
                        }
        :return:
        """
        args_addr = self.user.pk
        to = args['to']
        file_dir_path = '/transaction_file/revoke_contract_log/' + to
        path_create(file_dir_path)
        args_ = {'invoke_update': args}
        path = '/transaction_file/revoke_contract_log/' + to + '/' + args_addr + '.json'
        json2file(path, args_)
        data = self.init_data(func_number=4, args=args_addr, file_path=path)
        return data

    def invoke_transfer(self, args):
        args_addr = self.user.pk
        to = args['to']
        file_dir_path = '/transaction_file/revoke_contract_log/' + to
        path_create(file_dir_path)
        file_path = '/transaction_file/revoke_contract_log/' + to + '/' + args_addr + '.json'
        args_ = {'invoke_transfer': args}
        json2file(file_path, args_)
        data = self.init_data(func_number=5, args=args_addr, file_path=file_path)
        return data

    def invoke_receiver(self, args):
        transfer_value = args['value']

        args_addr = self.user.pk
        to = args['to']
        file_path = '/transaction_file/revoke_contract_log/' + to + '/' + args_addr + '.json'

        pk = args['pk2']
        zkp_args = self.create_zkp(pk, transfer_value)
        args['zkp'] = zkp_args
        args_ = {'invoke_receiver': args}
        json2file(file_path, args_)
        data = self.init_data(func_number=6, args=args_addr, file_path=file_path)
        return data

    def invoke_renewal(self, args):
        args_addr = self.user.pk
        value = args['value']
        zkp_args = self.create_zkp(args['pk2'], value)
        args['zkp'] = zkp_args

        to = args['to']
        file_dir_path = '/transaction_file/revoke_contract_log/' + to
        path_create(file_dir_path)
        file_path = '/transaction_file/revoke_contract_log/' + to + '/' + args_addr + '.json'
        args_ = {'invoke_renewal': args}
        json2file(file_path, args_)
        data = self.init_data(func_number=7, args=args_addr, file_path=file_path)
        return data

    def create_zkp(self, use_pk, value):
        data = {'pk': use_pk}
        event = construct_message(data=data, index=13)
        event.wait()
        user_data = DB_ANSWER_QUEUE.get()

        data = getsk(user_data['value'], value)
        pk = data[0]
        sk = data[1]
        funds = data[2]
        c_r = data[3]
        m = 'ZJGSUSCIE'
        ecdsa_sig = self.user.sign(m)
        schnorr_sig = schnorrSign(m, sk)
        ring_sign_info_1 = ringScheme(funds[1])
        ring_sign_info_2 = ringScheme(funds[2])
        zkp_args = {'pk': pk,
                    'fund0': funds[0],
                    'fund1': funds[1],
                    'fund2': funds[2],
                    'schnorr_sig': schnorr_sig,
                    'ring_sign_info_1': ring_sign_info_1,
                    'ring_sign_info_2': ring_sign_info_2
                    }
        # zkp_args = [pk, schnorr_sig, ring_sign_info_1, ring_sign_info_2]
        return zkp_args


if __name__ == '__main__':
    username = 'root'
    password = 'abc123'
    user = User().user(username=username, password=password)
    Trading().trading(user)
