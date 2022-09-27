#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 10/10/21 7:52 PM
# @Author : Archer
# @File : test.py
# @desc :
"""
from mine.block import Block
from transaction_file.trade import Trading
from transaction_file.transaction_args import invoke_update_args, invoke_transfer_args, invoke_receiver_args, \
    invoke_renewal_args, invoke_create_args, invoke_commit_args, invoke_reveal_args, invoke_finalize_args
from user.user import User
from config.thread_config import *


def pack_block():
    block = Block().construct()
    block.store_in_database()


def deploy(t):
    # deploy contract
    t.create_contract()


def update_test(contract_addr, t):
    domain_name = 'http://test.com'
    ip = '127.0.0.1:1234'
    to = contract_addr
    args = invoke_update_args(domain_name=domain_name, to=to, user=t.user, ip=ip)
    t.invoke_contract(args)


def transfer_test(contract_addr, t):
    to = contract_addr
    domain_name = 'http://test.com'
    pk2 = 'b9db5af0b4d9dd98b01f6b56de2596aef09409ea693d913230cbdb7847029583a7f0c0dd6b0adca6f9b943d4bb5d6982e94e323f5f501f06ad4fea0fcdd12ac4'
    args = invoke_transfer_args(user=t.user, pk2=pk2, to=to, domain_name=domain_name, value=5)
    t.invoke_contract(args)


def receiver_test(contract_addr, t):
    to = contract_addr
    domain_name = 'http://test.com'
    args = invoke_receiver_args(to=to, user=t.user, domain_name=domain_name, value=5)
    t.invoke_contract(args)


def renewal_test(contract_addr, t):
    to = contract_addr
    domain_name = 'http://test.com'
    pk1 = 'b9db5af0b4d9dd98b01f6b56de2596aef09409ea693d913230cbdb7847029583a7f0c0dd6b0adca6f9b943d4bb5d6982e94e323f5f501f06ad4fea0fcdd12ac4'
    args = invoke_renewal_args(to=to, user=t.user, domain_name=domain_name, value=5, pk1=pk1)
    t.invoke_contract(args)


def create_test(contract_addr, t):
    to = contract_addr
    t1 = 123
    t2 = 123456
    domain_name = 'http://test.com'
    args = invoke_create_args(to=to, t1=t1, t2=t2, domain_name=domain_name)
    t.invoke_contract(args)


def commit_test(contract_addr, t, bidding_price):
    to = contract_addr
    args = invoke_commit_args(to=to, bidding_price=bidding_price)
    t.invoke_contract(args)


def reveal_test(contract_addr, t):
    to = contract_addr
    args = invoke_reveal_args(to=to)
    t.invoke_contract(args)


def finalize_test(contract_addr, t):
    to = contract_addr
    args = invoke_finalize_args(to=to)
    t.invoke_contract(args)


username = 'root'
password = 'abc123'
user = User().user(username=username, password=password)
root = Trading(user)

username = 'archer'
password = 'abc123'
user = User().user(username=username, password=password)
archer = Trading(user)

username = 'mike'
password = 'abc123'
user = User().user(username=username, password=password)
mike = Trading(user)

username = 'alice'
password = 'abc123'
user = User().user(username=username, password=password)
alice = Trading(user)

# deploy(archer)
# pack_block()
contract_addr = '3d2fb0dfdb0af233e92b2cd05ebc8ccd85b62dccfd8c35bc66cd257c28d09f71create'

# update_test(contract_addr, user, t)

# transfer_test(contract_addr, t)
# pack_block()


# receiver_test(contract_addr, archer)
# pack_block()

# renewal_test(contract_addr, t)
# pack_block()

create_test(contract_addr, root)
pack_block()

commit_test(contract_addr, archer, 7)
commit_test(contract_addr, mike, 6)
commit_test(contract_addr, alice, 5)
pack_block()


reveal_test(contract_addr, archer)
reveal_test(contract_addr, mike)
reveal_test(contract_addr, alice)
pack_block()

finalize_test(contract_addr, root)
pack_block()