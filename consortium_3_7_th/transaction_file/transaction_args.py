#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 3/2/22 6:41 PM
# @Author : Archer
# @File : transaction_args.py
# @desc :
"""
from tools.pointsMul import scalar_mult_g


def invoke_create_args(to, t1, t2, domain_name):
    args = {'func_choice': 0,
            'to': to,
            't1': t1,
            't2': t2,
            'domain_name': domain_name}
    return args


def invoke_commit_args(to, bidding_price):
    args = {'func_choice': 1,
            'to': to,
            'bidding_price': bidding_price}
    return args


def invoke_reveal_args(to):
    args = {'func_choice': 2,
            'to': to}
    return args


def invoke_finalize_args(to):
    args = {'func_choice': 3,
            'to': to}
    return args


def invoke_update_args(user, to, domain_name, ip):
    signature = user.sign(domain_name)
    args = {'func_choice': 4,
            'pk': user.pk,
            'to': to,
            'domain_name': domain_name,
            'ip': ip,
            'signature': signature
            }
    return args


def invoke_transfer_args(user, to, domain_name, pk2, value, end_time):
    enc_fund = scalar_mult_g(value)
    args = {'func_choice': 5,
            'to': to,
            'pk1': user.pk,
            'domain_name': domain_name,
            'signature': user.sign(domain_name),
            'pk2': pk2,
            'funds': enc_fund,
            'end_time': end_time
            }
    return args


def invoke_receiver_args(to, user, domain_name, value):
    enc_fund = scalar_mult_g(value)

    args = {'func_choice': 6,
            'to': to,
            'domain_name': domain_name,
            'pk2': user.pk,
            'funds': enc_fund,
            'value': value,
            }
    return args


def invoke_renewal_args(to, pk1, user, domain_name, value):
    enc_fund = scalar_mult_g(value)
    args = {'func_choice': 7,
            'to': to,
            'pk1': pk1,
            'pk2': user.pk,
            'domain_name': domain_name,
            'signature': user.sign(domain_name),
            'funds': enc_fund,
            'value': value,
            }
    return args


if __name__ == '__main__':
    print('hello world')
