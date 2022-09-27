#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 10/21/21 7:00 PM
# @Author : Archer
# @File : create.py
# @desc :
"""
import json
import time
from database.DatabaseOperation import *
from tools.ecdsa_signature import verify
from tools.pointsMul import point_add, point_neg, scalar_mult, pointsToStr, scalar_mult_g
from tools.schnorrRing import schnorrVerify, ringVerify
from database.database_message_create import construct_message

# from tools.elgamalring import *
from tools.utils import double_sha256


class Contract(object):
    def __init__(self):
        self.data = None
        self.t1 = None
        self.t2 = None
        self.owner = None
        self.bidder = {}
        self.addr = None
        self.zkp_dict = {}
        self.funds_list = {}
        self.winner = None
        self.receiver_ = None
        self.transfer_ = None
        self.domain_info = None
        self.domain_name = None

    def create(self, t1, t2, domain_name, signature, contract_addr):
        self.addr = contract_addr
        if t1 >= t2:
            return False
        # now_time = time.time()
        now_time = 0
        # shortest_time = 3600 * 24 * 3
        shortest_time = 0
        if t1 - now_time < shortest_time:
            return False
        if t2 - now_time < shortest_time * 2:
            return False

        data = {'domain_name': domain_name}
        event = construct_message(data=data, index=11)
        event.wait()
        domain_info = DB_ANSWER_QUEUE.get()

        # a new domain name will be auctioned
        if domain_info is None and signature is None:
            self.owner = None
            self.bidder = {}
            self.data = {'owner': self.owner,
                         'bidder': self.bidder,
                         't1': t1,
                         't2': t2,
                         'domain_name': domain_name,
                         'domain_info': domain_info,
                         'signature': signature,
                         'addr': self.addr,
                         'zkp_dict': self.zkp_dict}
            self.data2file()
            return True

        if domain_info is None:
            return False
        # check if the domain being auctioned
        if domain_info['state'] == '1':
            m_ = domain_name + ' state is 1'
            LOGGER.error(m_)
            return False
        # check if user have the domain
        if not verify(m=domain_info['domain_name'], signature=signature, verify_key=domain_info['owner']):
            m_ = 'signature verify failed!'
            LOGGER.error(m_)
            return False
        data = {'pk': domain_info['owner']}
        event = construct_message(data=data, index=13)
        event.wait()
        self.owner = DB_ANSWER_QUEUE.get()

        # self.owner = DBOperation(data, 13)
        self.bidder = {}
        hash_code = double_sha256('contract')

        self.data = {'owner': self.owner,
                     'bidder': self.bidder,
                     't1': t1,
                     't2': t2,
                     'domain_name': domain_name,
                     'domain_info': domain_info,
                     'signature': signature,
                     'addr': self.addr,
                     'zkp_dict': self.zkp_dict}
        # set domain name state
        data = {'domain_name': domain_info['domain_name'],
                'domain_state': 1}
        event = construct_message(data=data, index=12)
        event.wait()
        DB_ANSWER_QUEUE.get()
        # DBOperation(data_, 12)
        m = domain_info['domain_name'] + 'is being auctioned at ' + self.addr
        LOGGER.info(m)
        self.data2file()
        return True

    def commit(self, pk, funds, sig, zkp_args, contract_addr):
        self.addr = contract_addr
        self.file2data()
        if pk not in self.bidder:
            now_time = time.time()
            now_time = 0
            if now_time <= self.t1:
                m = 'ZJGSUSCIE'
                if verify(m, sig, pk):
                    if self.ZKP(zkp_args):
                        self.bidder[pk] = {'c_r_list': None,
                                           'funds': funds,
                                           'bidd_value': None}
                        self.zkp_dict[pk] = zkp_args
                        self.bidding_lock(funds=funds, bidder_pk=pk, contract_addr=contract_addr)
                        m = 'you have commit the bid!'
                        LOGGER.info(m)
                        self.data['zkp_dict'] = self.zkp_dict
                        self.data['bidder'] = self.bidder
                        self.data2file()
                    else:
                        return 0
            else:
                m = 'you fail to committ the bid!'
                LOGGER.info(m)
        else:
            m = 'you had committed the bid!'
            LOGGER.info(m)

    def reveal(self, pk, c_r_list, contract_addr):
        self.addr = contract_addr
        self.file2data()
        if pk in self.bidder:
            funds = self.bidder[pk]
            now_time = time.time()
            now_time = 0
            if now_time <= self.t2:
                l = L_MAX
                g = FUND_G
                h = FUND_H
                for i in range(0, l):
                    fund_ = list(point_add(scalar_mult(c_r_list[i][0], g), scalar_mult(c_r_list[i][1], h)))
                    if fund_ != funds['funds'][i]:
                        m = 'you fail to reveal the funds'
                        LOGGER.info(m)
                        return False
                bid_value = sum([c[0] for c in c_r_list])
                self.bidder[pk]['c_r_list'] = c_r_list
                self.bidder[pk]['bid_value'] = bid_value
                self.data2file()
            else:
                m = 'you have exceeded the deadline of reveal time!'
                LOGGER.info(m)
                return False
        else:
            m = 'you not join the bid!'
            LOGGER.info(m)
        return True

    def finalize(self, contract_addr):
        self.addr = contract_addr
        self.file2data()
        now_time = time.time()
        now_time = 123456789123
        if now_time < self.t2:
            return False

        data = {'domain_name': self.domain_name}
        event = construct_message(data=data, index=11)
        event.wait()
        domain_info = DB_ANSWER_QUEUE.get()

        if domain_info['state'] == '0':  # state should be 1
            return False

        second_high_price = None
        winner_pk = None
        for user_pk in self.bidder:
            if self.bidder[user_pk]['bid_value'] is None:
                data = {'pk': user_pk}
                event = construct_message(data=data, index=17)
                event.wait()
                DB_ANSWER_QUEUE.get()

                # DBOperation(data, 17)
                m = user_pk + 'has been punished'
                LOGGER.info(m)
                pass
            if winner_pk is None:
                second_high_price = self.bidder[user_pk]['bid_value']
                winner_pk = user_pk
            if self.bidder[user_pk]['bid_value'] > self.bidder[winner_pk]['bid_value']:
                second_high_price = self.bidder[winner_pk]['bid_value']
                winner_pk = user_pk

        data = {'addr': contract_addr}
        event = construct_message(data=data, index=21)
        event.wait()
        contract_enc_funds = DB_ANSWER_QUEUE.get()
        contract_enc_funds = strToPoints(contract_enc_funds)
        for bidder_pk in self.bidder:
            if bidder_pk != winner_pk:
                # unlock bidding
                contract_enc_funds = self.bidding_unlock(bidder_pk=bidder_pk, contract_enc_funds=contract_enc_funds,
                                                         funds=self.bidder[bidder_pk]['funds'])

        self.winner = winner_pk
        if self.owner is not None:
            data = {'pk': self.owner['pk']}
            event = construct_message(data=data, index=13)
            event.wait()
            owner_info = DB_ANSWER_QUEUE.get()
            g = ecc_table['g']
            g = strToPoints(g)

            enc_bidding = scalar_mult(second_high_price, g)
            owner_info['enc_fund'] = point_add(strToPoints(owner_info['enc_fund']), enc_bidding)
            data = {'user_pk': owner_info['pk'],
                    'enc_fund': pointsToStr(owner_info['enc_fund'])}
            event = construct_message(data=data, index=22)
            event.wait()
            DB_ANSWER_QUEUE.get()

        data = {'contract_addr': contract_addr,
                'enc_fund': 0}
        event = construct_message(data=data, index=23)
        event.wait()
        DB_ANSWER_QUEUE.get()

        data = {
            'domain_name': self.data['domain_name'],
            'user_pk': winner_pk,
        }

        event = construct_message(data=data, index=15)
        event.wait()
        DB_ANSWER_QUEUE.get()
        # DBOperation(data, 15)

        # change domain name owner

        pass

    def update(self, pk, domain_name, ip, sig, contract_addr):
        now_time = time.time()
        data = {'domain_name': domain_name}
        event = construct_message(data=data, index=11)
        event.wait()
        domain_info = DB_ANSWER_QUEUE.get()
        if int(domain_info['expiration']) <= now_time:
            return False
        if domain_info['owner'] != pk:
            return False
        if not verify(domain_name, sig, pk):
            return False

        data = {
            'domain_name': domain_name,
            'ip': ip
        }
        event = construct_message(data=data, index=19)
        event.wait()
        DB_ANSWER_QUEUE.get()
        return True

    def transfer(self, pk1, domain_name, sig, pk2, funds, end_time, contract_addr):
        self.addr = contract_addr
        # self.data2file()
        now_time = time.time()
        shortest_time = 0
        if end_time - now_time < shortest_time:
            return False

        data = {'domain_name': domain_name}
        event = construct_message(data=data, index=11)
        event.wait()
        domain_info = DB_ANSWER_QUEUE.get()

        if domain_info['state'] == '1':
            return False
        if int(domain_info['expiration']) <= now_time:
            return False
        if not verify(domain_name, sig, pk1):
            return False
        # set state = 1
        data = {'domain_name': domain_name,
                'domain_state': 1}
        event = construct_message(data=data, index=12)
        event.wait()
        DB_ANSWER_QUEUE.get()
        self.owner = None
        self.bidder = None
        # t1 means end time
        self.t1 = end_time
        self.t2 = None
        self.domain_name = domain_name
        self.data = {'transfer': pk1,
                     'receiver': pk2,
                     'transfer_funds': funds,
                     'domain_name': domain_name,
                     'owner': self.owner,
                     'bidder': self.bidder,
                     't1': self.t1,
                     't2': self.t2,
                     'domain_info': domain_info,
                     }
        self.data2file()

    def receiver(self, domain_name, pk2, funds, zkp_args, contract_addr):

        self.addr = contract_addr
        self.file2data()
        now_time = time.time()

        # time out
        if self.data['t1'] < now_time:
            # set stat = 0
            data = {'domain_name': domain_name,
                    'user_pk': pk2}
            event = construct_message(data=data, index=15)
            event.wait()
            DB_ANSWER_QUEUE.get()
            return False

        if pk2 != self.data['receiver']:
            return False
        if self.data['transfer_funds'] != funds:
            return False
        if not self.ZKP(zkp_args):
            print_error("receiver zkp check failed")
            return False

        data = {'pk': self.data['transfer']}
        event = construct_message(data=data, index=13)
        event.wait()
        transfer_info = DB_ANSWER_QUEUE.get()

        data = {'pk': pk2}
        event = construct_message(data=data, index=13)
        event.wait()
        receiver_info = DB_ANSWER_QUEUE.get()

        transfer_info['enc_fund'] = point_add(strToPoints(transfer_info['enc_fund']), funds)
        data = {'user_pk': transfer_info['pk'],
                'enc_fund': pointsToStr(transfer_info['enc_fund'])}
        event = construct_message(data=data, index=22)
        event.wait()
        DB_ANSWER_QUEUE.get()

        receiver_info['enc_fund'] = point_add(strToPoints(receiver_info['enc_fund']), point_neg(funds))
        data = {'user_pk': receiver_info['pk'],
                'enc_fund': pointsToStr(transfer_info['enc_fund'])}
        event = construct_message(data=data, index=22)
        event.wait()
        DB_ANSWER_QUEUE.get()

        # set the domain_name owner
        data = {'domain_name': domain_name,
                'user_pk': pk2}
        event = construct_message(data=data, index=15)
        event.wait()
        DB_ANSWER_QUEUE.get()

        # set stat = 0
        data = {'domain_name': domain_name,
                'user_pk': pk2}
        event = construct_message(data=data, index=15)
        event.wait()
        DB_ANSWER_QUEUE.get()
        pass

    def renewal(self, pk1, pk2, sig, domain_name, funds, zkp_args, contract_addr):
        now_time = time.time()
        data = {'domain_name': domain_name}
        event = construct_message(data=data, index=11)
        event.wait()
        domain_info = DB_ANSWER_QUEUE.get()
        if int(domain_info['expiration']) <= now_time:
            return False
        if domain_info['owner'] != pk1:
            return False
        if not verify(domain_name, sig, pk2):
            return False

        if not self.ZKP(zkp_args):
            print_error("renewal zkp check failed")
            return False

        # pk2 will give the money
        data = {'pk': pk2}
        event = construct_message(data=data, index=13)
        event.wait()
        renewer_info = DB_ANSWER_QUEUE.get()

        renewer_info['enc_fund'] = point_add(strToPoints(renewer_info['enc_fund']), point_neg(funds))
        data = {'user_pk': renewer_info['pk'],
                'enc_fund': pointsToStr(renewer_info['enc_fund'])}
        event = construct_message(data=data, index=22)
        event.wait()
        DB_ANSWER_QUEUE.get()
        # no check funds

        domain_info['expiration'] = int(domain_info['expiration'])
        domain_info['expiration'] += 60 * 24 * 30
        data = {
            'domain_name': domain_name,
            'expiration': domain_info['expiration']
        }
        event = construct_message(data=data, index=24)
        event.wait()
        DB_ANSWER_QUEUE.get()
        return True

    def ZKP(self, zkp_args):
        m = 'ZJGSUSCIE'
        # check
        fund1 = zkp_args['fund0']
        fund2 = zkp_args['fund1']
        fund3 = zkp_args['fund2']
        schnorr_pk = zkp_args['pk']
        s_2 = None
        s_3 = None
        l = L_MAX
        for i in range(0, l):
            s_2 = point_add(s_2, fund2[i]['fund'])
            s_3 = point_add(s_3, fund3[i]['fund'])
        s_all = point_add(s_2, s_3)
        s_all_re = point_neg(s_all)
        schnorr_pk_ = list(point_add(fund1, s_all_re))
        if schnorr_pk != schnorr_pk_:
            LOGGER.info('schnorr scheme pk check failed!')
        if not schnorrVerify(m=m, sig=zkp_args['schnorr_sig'], pk=schnorr_pk):
            LOGGER.info('schorr signature verify failed!')
            return False

        for fund in zkp_args['ring_sign_info_1']:
            sig = fund['sig']
            L = [tuple(f) for f in fund['L']]
            m = fund['m']
            if not ringVerify(m=m, sig=sig, L=L):
                LOGGER.info('ring signature 1 verify failed!')
                return False

        for fund in zkp_args['ring_sign_info_2']:
            sig = fund['sig']
            L = [tuple(f) for f in fund['L']]
            m = fund['m']
            if not ringVerify(m, sig, L):
                LOGGER.info('ring signature 2 verify failed!')
                return False
        return True

    def bidding_lock(self, funds, bidder_pk, contract_addr):
        data = {'pk': bidder_pk}
        event = construct_message(data=data, index=13)
        event.wait()
        user_info = DB_ANSWER_QUEUE.get()
        data = {'addr': contract_addr}
        event = construct_message(data=data, index=21)
        event.wait()
        contract_enc_funds = DB_ANSWER_QUEUE.get()
        if contract_enc_funds != '0':
            contract_enc_funds = strToPoints(contract_enc_funds)
        else:
            contract_enc_funds = 0
        for i in range(0, len(funds)):
            if contract_enc_funds == 0 and i == 0:
                contract_enc_funds = funds[i]
                continue
            else:
                # contract_addr store bidding fund
                contract_enc_funds = point_add(contract_enc_funds, funds[i])
                # lock bidder's bidding fund
                user_info['enc_fund'] = point_add(contract_enc_funds, point_neg(funds[i]))

        data = {'user_pk': bidder_pk,
                'enc_fund': pointsToStr(user_info['enc_fund'])}
        event = construct_message(data=data, index=22)
        event.wait()
        DB_ANSWER_QUEUE.get()

        data = {'contract_addr': contract_addr,
                'enc_fund': pointsToStr(contract_enc_funds)}
        event = construct_message(data=data, index=23)
        event.wait()
        DB_ANSWER_QUEUE.get()

    def bidding_unlock(self, funds, bidder_pk, contract_enc_funds):
        data = {'pk': bidder_pk}
        event = construct_message(data=data, index=13)
        event.wait()
        user_info = DB_ANSWER_QUEUE.get()
        user_info['enc_fund'] = strToPoints(user_info['enc_fund'])
        for i in range(0, len(funds)):
            # contract_addr store bidding fund

            user_info['enc_fund'] = point_add(user_info['enc_fund'], funds[i])
            # lock bidder's bidding fund

            contract_enc_funds = point_add(contract_enc_funds, point_neg(funds[i]))

        data = {'user_pk': bidder_pk,
                'enc_fund': pointsToStr(user_info['enc_fund'])}
        event = construct_message(data=data, index=22)
        event.wait()
        DB_ANSWER_QUEUE.get()
        return contract_enc_funds

    def data2file(self):
        pwd = os.getcwd()
        pwd = pwd[:pwd.rfind('/')]
        file_name = pwd + '/contract/log/' + self.addr + '.json'
        with open(file_name, 'w') as f:
            json.dump(self.data, f)
        print("done")

    def file2data(self):
        pwd = os.getcwd()
        pwd = pwd[:pwd.rfind('/')]
        file_name = pwd + '/contract/log/' + self.addr + '.json'
        with open(file_name, 'r') as load_f:
            self.data = json.load(load_f)

            self.owner = self.data['owner']
            self.bidder = self.data['bidder']
            self.t1 = self.data['t1']
            self.t2 = self.data['t2']
            if 'domain_name' in self.data:
                self.domain_name = self.data['domain_name']
            if 'domain_info' in self.data:
                self.domain_info = self.data['domain_info']
