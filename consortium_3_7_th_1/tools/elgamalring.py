#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/11/2 18:02
# @Author  : archer
# @File    : test.py
# @Software: PyCharm

import random
import math
import gmpy2
from tools.utils import *

def init():
    g = random.randint(1, 10)
    h = random.randint(1, 10)
    return g, h


def int2bit(num):
    result = bin(num)
    return result


def getFund(token, g, h):
    r = random.random()
    fund = pow(g, token) * pow(h, r)
    return fund, r


def getsk(x, token, g, h, p):

    a = token
    b = x - a
    l = 10
    r_1 = random.randint(1, 5)
    r_2 = [random.randint(1, 5) for i in range(0, l)]
    r_3 = [random.randint(1, 5) for i in range(0, l)]
    fund1 = pow(g, x) * pow(h, r_1) % p

    a_b = bin(a)[2:].rjust(l, '0')
    b_b = bin(b)[2:].rjust(l, '0')

    fund2 = []
    fund3 = []
    for i in range(0, l):
        r_ = r_2[i]
        value = pow(2, i)
        e = value*int(a_b[l-i-1])
        fund_ = pow(g, e, p) * pow(h, r_, p) % p
        data = {'bit_value': int(a_b[l-i-1]),
                'fund': fund_,
                'r': r_,
                'value': value
                }
        fund2.append(data)

    for i in range(0, l):
        r_ = r_3[i]
        value = pow(2, i)
        e = value*int(b_b[l-i-1])
        fund_ = pow(g, e, p) * pow(h, r_, p) % p
        data = {'bit_value': int(b_b[l-i-1]),
                'fund': fund_,
                'r': r_,
                'value': value
                }
        fund3.append(data)

    s = 1
    for i in range(0, l):
        s = s * fund2[i]['fund'] * fund3[i]['fund'] % p

    sk = (r_1 - sum(r_2) - sum(r_3)) % (p-1)
    pk = gmpy2.invert(s, p)*fund1%p

    funds = [fund1, fund2, fund3]
    r_s = [r_1, r_2, r_3]
    data = [pk , sk, funds, r_s]
    return data


def elgamaSign(sk, m, g, p):
    k = random.randint(2, p - 2)
    while math.gcd(k, p-1) != 1:
        k = random.randint(2, p - 2)
    r = gmpy2.powmod(g, k, p)

    # s = ((int(sha256(m), 16) - sk*r) * gmpy2.invert(k, p)) % p
    s = (1 - sk*r) * gmpy2.invert(k, p-1) % (p-1)
    while s == 0:
        k = random.randint(2, p - 2)
        while math.gcd(k, p - 1) != 1:
            k = random.randint(2, p - 2)
        r = gmpy2.powmod(g, k, p)
        s = (1 - sk * r) * gmpy2.invert(k, p-1) % (p-1)
    return (r, s)


def elgamaVerify(pk , m, sig, g, p):
    r = sig[0]
    s = sig[1]

    # sig_ = gmpy2.powmod(g, int(sha256(m), 16), p)
    sig_ = gmpy2.powmod(g, 1, p)
    cal_sig = gmpy2.powmod(pk, r, p) * gmpy2.powmod(r, s, p) % p
    if sig_ == cal_sig:
        return True
    return False

def ringSign(k, L, m, g, p, sk):
    L_string = ''.join(str(L))
    if k == 0:
        a = random.randint(0, p-1)

        c_1 = sha256(L_string + m + str(pow(g, a, p)))
        s_1 = random.randint(0, p-1)
        temp = pow(g, s_1, p) * pow(L[1], int(c_1, 16), p) % p
        c_0 = sha256(L_string+m+str(temp))
        s_0 = (a - sk*int(c_0, 16)) % (p -1)
        return (c_0, s_0, s_1)
    else :
        a = random.randint(0, p-1)
        c_0 = sha256(L_string + m + str(pow(g, a, p)))
        s_0 = random.randint(0, p-1)
        temp = pow(g, s_0, p) * pow(L[0], int(c_0, 16), p) % p
        c_1 = sha256(L_string + m + str(temp))
        s_1 = (a - sk * int(c_1, 16)) % (p - 1)
        return (c_0, s_0, s_1)

def ringVerify(m, sig, g, p, L):
    L_string = ''.join(str(L))
    c_0 = sig[0]
    s_0 = sig[1]
    s_1 = sig[2]
    e_0 = pow(g, s_0, p) * pow(L[0], int(c_0, 16), p) % p
    c_1 = int(sha256(L_string + m + str(e_0)), 16)

    e_1 = pow(g, s_1, p) * pow(L[1], c_1, p) % p
    cal_c_0 = sha256(L_string + m + str(e_1))
    assert(c_0 == cal_c_0)
    print('verify success')


def ringScheme(funds, g, p, g_):
    for fund in funds:
        sk = fund['r']
        value = fund['value']
        pk_1 = fund['fund']
        pk_2 = fund['fund'] * gmpy2.invert(pow(g_, value), p) % p
        L = [pk_1, pk_2]
        m = 'hello'
        pk_ = pow(h, sk, p)
        sig = ringSign(fund['bit_value'], L,m, g, p, sk)
        ringVerify(m, sig, g, p, L)

if __name__ == '__main__':
    p = gmpy2.next_prime(10)
    g, h = 5, 7
    x = 8
    token = 3
    data = getsk(x, token, g,h, p)
    pk = data[0]
    sk = data[1]
    funds = data[2]
    r_s = data[3]
    m = 'hello'
    signature = elgamaSign(sk, m, h, p)
    elgamaVerify(pk, m, signature, h, p)
    fund1 = funds[0]
    fund2 = funds[1]
    fund3 = funds[2]
    ringScheme(fund2, h, p, g)
    ringScheme(fund3, h, p, g)



