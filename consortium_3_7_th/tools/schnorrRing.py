#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
# @Time : 11/12/21 12:33 AM
# @Author : Archer
# @File : test.py
# @desc :
"""
from config.config import *
import secrets
from tools.pointsMul import *
from tools.utils import sha256


def generate_random():
    secret_generator = secrets.SystemRandom()
    k = secret_generator.randint(1, int(ecc_table['p'], base=16))
    k = (k ^ secret_generator.randint(1, int(ecc_table['p'], base=16))) % int(ecc_table['p'], base=16)
    return k


def generate_h():
    point_g = strToPoints(ecc_table['g'])
    k = generate_random()
    point_h = scalar_mult(k, point_g)
    point_h = pointsToStr(point_h)
    ecc_table['h'] = point_h


def getsk(token, bidding_price):
    a = bidding_price
    b = token - a
    l = L_MAX
    r_1 = generate_random()
    r_s_2 = [generate_random() for i in range(0, l)]
    r_s_3 = [generate_random() for i in range(0, l)]
    g = strToPoints(ecc_table['g'])
    h = strToPoints(ecc_table['h'])
    n = int(ecc_table['n'], 16)
    x_g = scalar_mult(token, g)
    r_1_h = scalar_mult(r_1, h)
    fund1 = point_add(x_g, r_1_h)
    a_b = bin(a)[2:].rjust(l, '0')
    b_b = bin(b)[2:].rjust(l, '0')

    fund2 = []
    fund3 = []
    for i in range(0, l):
        r_ = r_s_2[i]
        value = pow(2, i)
        e = value * int(a_b[l - i - 1])
        r_s_2[i] = [e, r_]
        fund_ = point_add(scalar_mult(e, g), scalar_mult(r_, h))
        data = {'bit_value': int(a_b[l - i - 1]),
                'fund': fund_,
                'r': r_,
                'value': value
                }
        fund2.append(data)

    for i in range(0, l):
        r_ = r_s_3[i]
        value = pow(2, i)
        e = value * int(b_b[l - i - 1])
        r_s_3[i] = [e, r_]
        fund_ = point_add(scalar_mult(e, g), scalar_mult(r_, h))
        data = {'bit_value': int(b_b[l - i - 1]),
                'fund': fund_,
                'r': r_,
                'value': value
                }
        fund3.append(data)

    s_2 = None
    s_3 = None
    for i in range(0, l):
        s_2 = point_add(s_2, fund2[i]['fund'])
        s_3 = point_add(s_3, fund3[i]['fund'])

    s_all = point_add(s_2, s_3)
    sk = (r_1 - sum([r_s[1] for r_s in r_s_2]) - sum([r_s[1] for r_s in r_s_3])) % n
    s_all_re = point_neg(s_all)
    pk = point_add(fund1, s_all_re)
    pk_ = scalar_mult(sk, h)
    assert pk == pk_

    funds = [fund1, fund2, fund3]
    r_s = [r_1, r_s_2, r_s_3]
    data = [pk, sk, funds, r_s]
    return data


def schnorrSign(m, sk):
    n = int(ecc_table['n'], 16)
    h = strToPoints(ecc_table['h'])
    r = generate_random()
    R = scalar_mult(r, h)
    alpha = sha256(m + pointsToStr(R))
    delta = (sk * int(alpha, 16) + r) % n
    return (alpha, delta)


def schnorrVerify(m, sig, pk):
    n = int(ecc_table['n'], 16)
    h = strToPoints(ecc_table['h'])
    alpha = sig[0]
    delta = sig[1]
    delta_h = scalar_mult(delta, h)
    alpha_pk = scalar_mult(int(alpha, 16), pk)
    re_alpha_pk = point_neg(alpha_pk)
    R_ = point_add(delta_h, re_alpha_pk)
    alpha_ = sha256(m + pointsToStr(R_))
    if alpha == alpha_:
        # print('schnorrVerify success')
        return True
    else:
        return False



def ringSign(k, L, m, sk):
    n = int(ecc_table['n'], 16)
    h = strToPoints(ecc_table['h'])
    L_string = ''.join(str(L))
    if k == 0:
        a = generate_random()
        c_1 = sha256(L_string + m + pointsToStr(scalar_mult(a, h)))
        s_1 = generate_random()
        s_1_h = scalar_mult(s_1, h)
        c_1_L1 = scalar_mult(int(c_1, 16), L[1])
        temp = point_add(s_1_h, c_1_L1)
        c_0 = sha256(L_string + m + pointsToStr(temp))
        s_0 = (a - sk * int(c_0, 16)) % n
        return (c_0, s_0, s_1)
    else:
        a = generate_random()
        c_0 = sha256(L_string + m + pointsToStr(scalar_mult(a, h)))
        s_0 = generate_random()
        s_0_h = scalar_mult(s_0, h)
        c_0_L1 = scalar_mult(int(c_0, 16), L[0])
        temp = point_add(s_0_h, c_0_L1)
        c_1 = sha256(L_string + m + pointsToStr(temp))
        s_1 = (a - sk * int(c_1, 16)) % n
        return (c_0, s_0, s_1)


def ringVerify(m, sig, L):
    n = int(ecc_table['n'], 16)
    h = strToPoints(ecc_table['h'])
    L_string = ''.join(str(L))
    c_0 = sig[0]
    s_0 = sig[1]
    s_1 = sig[2]
    s_0_h = scalar_mult(s_0, h)
    c_0_L0 = scalar_mult(int(c_0, 16), L[0])
    e_0 = point_add(s_0_h, c_0_L0)
    c_1 = sha256(L_string + m + pointsToStr(e_0))

    s_1_h = scalar_mult(s_1, h)
    c_1_L1 = scalar_mult(int(c_1, 16), L[1])
    e_1 = point_add(s_1_h, c_1_L1)
    cal_c_0 = sha256(L_string + m + pointsToStr(e_1))
    if c_0 == cal_c_0:
        # print('ringVerify success')
        return True
    else:
        return False



def ringScheme(funds):
    ring_sign_info = []
    for fund in funds:
        n = int(ecc_table['n'], 16)
        h = strToPoints(ecc_table['h'])
        g = strToPoints(ecc_table['g'])
        sk = fund['r']
        value = fund['value']
        pk_1 = fund['fund']
        value_g = scalar_mult(value, g)
        re_value_g = point_neg(value_g)
        pk_2 = point_add(fund['fund'], re_value_g)
        # pk_2 = fund['fund'] * gmpy2.invert(pow(g_, value), p) % p
        L = [pk_1, pk_2]
        m = 'ZJGSUSCIE'
        sig = ringSign(fund['bit_value'], L, m,  sk)
        data = {'L': L,
                'm': m,
                'sk': sk,
                'sig': sig}
        ring_sign_info.append(data)
        # ringVerify(m, sig, L)
    return ring_sign_info


if __name__ == '__main__':
    x = 5
    token = 2
    data = getsk(x, token)
    pk = data[0]
    sk = data[1]
    funds = data[2]
    r_s = data[3]
    m = 'hello'
    sig = schnorrSign(m, sk)
    schnorrVerify(m, sig, pk)
    ringScheme(funds[1])
    # ringScheme(funds[1])
