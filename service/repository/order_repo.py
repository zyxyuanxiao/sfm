#!/usr/bin/env python
# encoding: utf-8

"""
@version: v1.0
@author: suyuan
@license: 
@contact: suyuan@gmail.com
@site: https://github.com/su6838354/sfm
@software: PyCharm
@file: order_repo.py
@time: 16/11/3 上午11:50
"""

from service.repository.base_repo import BaseRepo
from service.repository.base_repo import transaction
from constant import *
from tornado.concurrent import run_on_executor


class OrderRepo(BaseRepo):
    TABLE_NAME = 'sfm_order'

    def insert(self, order_id, ship_amount, sku_amount, credit_amount, pay_amount, sku_count, user_id, address_id,
               user_note, card_id):
        sql = """
            insert into {} set order_id=%s, state=0, ctime=%s, utime=%s, overtime=%s,
            ship_amount=%s, sku_amount=%s, credit_amount=%s, pay_amount=%s, user_id=%s, address_id=%s, status=1, user_note=%s, credit_card_id=%s
        """.format(self.TABLE_NAME)
        lastrowid = self.db.execute_lastrowid(sql, order_id, time.time(), time.time(),
                                              time.time() + CONST_ORDER_OVER_DURATION,
                                              ship_amount, sku_amount, credit_amount, pay_amount, user_id, address_id,
                                              user_note, card_id)
        return lastrowid

    @run_on_executor
    def select_by_user_id_state(self, user_id, state, page, count):
        sql = """
            select * from {} where user_id=%s and status=1 and state=%s order by ctime desc limit %s,%s
        """.format(self.TABLE_NAME)
        res = self.db.query(sql, user_id, state, (page-1)*count, count)

        sql = """
            select 1 from {} where user_id=%s and status=1 and state=%s
        """.format(self.TABLE_NAME)
        total = self.db.execute_rowcount(sql, user_id, state)
        return res, total

    @run_on_executor
    def select_by_user_id_all(self, user_id, page, count):
        sql = """
            select * from {} where user_id=%s and status=1 order by ctime desc limit %s,%s
        """.format(self.TABLE_NAME)
        res = self.db.query(sql, user_id, (page-1)*count, count)

        sql = """
            select 1 from {} where user_id=%s and status=1
        """.format(self.TABLE_NAME)
        total = self.db.execute_rowcount(sql, user_id)
        return res, total

    @run_on_executor
    def select_for_pay(self, user_id, order_id):
        """订单未超时, 订单属于用户, 订单未支付状态 state=0"""
        sql = """
            select * from {} where user_id=%s and order_id=%s and overtime>%s and state=0
        """.format(self.TABLE_NAME)
        res = self.db.get(sql, user_id, order_id, time.time())
        return res

    @run_on_executor
    def delete_order(self, order_id):
        sql = """
            update {} set status=0 WHERE order_id=%s
        """.format(self.TABLE_NAME)
        res = self.db.execute_lastrowid(sql, order_id)
        return res

    @run_on_executor
    def update_state_1(self, order_id):
        """
        付款,回调
        :param order_id:
        :return:
        """
        sql = """
            update {} set state=1 where order_id=%s
        """.format(self.TABLE_NAME)
        res = self.db.execute_lastrowid(sql, order_id)
        return res

    @run_on_executor
    def update_state_2(self, order_id, logistics_id):
        """
        发货
        :param order_id:
        :return:
        """
        sql = """
            update {} set state=2, logistics_id=%s where order_id=%s and state=1
        """.format(self.TABLE_NAME)
        res = self.db.execute_rowcount(sql, logistics_id, order_id)
        return res

    @run_on_executor
    def update_state_3(self, order_id):
        """
        确认收货
        :param order_id:
        :return:
        """
        sql = """
            update {} set state=3 where order_id=%s and state=2
        """.format(self.TABLE_NAME)
        res = self.db.execute_lastrowid(sql, order_id)
        return res

    @run_on_executor
    def update_state_4(self, order_id, reason):
        """
        取消订单
        :param order_id:
        :param reason:
        :return:
        """
        sql = """
            update {} set state=4, reason=%s WHERE order_id=%s and state=0
        """.format(self.TABLE_NAME)
        res = self.db.execute_rowcount(sql, reason, order_id)
        return res

    @run_on_executor
    def update_state_5(self, order_id, reason):
        """
        订单过期
        :param order_id:
        :param reason:
        :return:
        """
        sql = """
            update {} set state=5 WHERE order_id=%s and state=0
        """.format(self.TABLE_NAME)
        res = self.db.execute_lastrowid(sql, reason, order_id)
        return res

    @run_on_executor
    def select_by_order_id(self, order_id):
        sql = """
            select * from {} where order_id=%s
        """.format(self.TABLE_NAME)
        res = self.db.get(sql, order_id)
        return res

    @run_on_executor
    def select_by_order_id_user_id(self, order_id, user_id):
        sql = """
            select * from {} where order_id=%s AND user_id=%s
        """.format(self.TABLE_NAME)
        res = self.db.get(sql, order_id, user_id)
        return res

    @run_on_executor
    def select_by_credit_card_id(self, credit_id):
        sql = """
            select * from {} where credit_card_id=%s and state=1
        """.format(self.TABLE_NAME)
        res = self.db.query(sql, credit_id)
        return res

    @run_on_executor
    def select_for_background(self, u_id, u_mobile, order_id, state, ctime_st, ctime_ed, page, count):
        sql = """
            select user_tb.*, order_tb.* from sfm_user as user_tb JOIN sfm_order as order_tb on user_tb.id=order_tb.user_id
            where user_tb.id like %s and user_tb.mobile like %s
            and order_tb.id like %s and order_tb.ctime>%s and order_tb.ctime<%s and order_state=%s
            order by order_tb.ctime desc limit %s, %s
        """
        res = self.db.query(sql, u_id, u_mobile, order_id, ctime_st, ctime_ed, state, (page-1)*count, count)
        sql = """
            select 1 from sfm_user as user_tb JOIN sfm_order as order_tb on user_tb.id=order_tb.user_id
            where user_tb.id like %s and user_tb.mobile like %s
            and order_tb.id like %s and order_tb.ctime>%s and order_tb.ctime<%s and order_state=%s
        """
        total = self.db.execute_rowcount(sql, u_id, u_mobile, order_id, ctime_st, ctime_ed, state,)
        return res, total

    @run_on_executor
    def select_for_background_all(self, u_id, u_mobile, order_id, ctime_st, ctime_ed, page, count):
        sql = """
            select user_tb.*, order_tb.* from sfm_user as user_tb JOIN sfm_order as order_tb on user_tb.id=order_tb.user_id
            where user_tb.id like %s and user_tb.mobile like %s
            and order_tb.id like %s and order_tb.ctime>%s and order_tb.ctime<%s
            order by order_tb.ctime desc limit %s, %s
        """
        u_id = '%' + u_id + '%'
        u_mobile = '%' + u_mobile + '%'
        order_id = '%' + order_id + '%'
        res = self.db.query(sql, u_id, u_mobile, order_id, ctime_st, ctime_ed, (page-1)*count, count)
        sql = """
            select 1 from sfm_user as user_tb JOIN sfm_order as order_tb on user_tb.id=order_tb.user_id
            where user_tb.id like %s and user_tb.mobile like %s
            and order_tb.id like %s and order_tb.ctime>%s and order_tb.ctime<%s
        """
        total = self.db.execute_rowcount(sql, u_id, u_mobile, order_id, ctime_st, ctime_ed)
        return res, total


    def test(self):
        with transaction() as trans:
            sql = "select * from {} where id=1 for update".format(self.TABLE_NAME)
            res = self.db.get(sql)
            return res
