#!/usr/bin/env python
# encoding: utf-8

"""
@version: v1.0
@author: suyuan
@license: 
@contact: suyuan@gmail.com
@site: https://github.com/su6838354/sfm
@software: PyCharm
@file: repos.py
@time: 16/10/13 下午2:23
"""

from user_repo import UserRepo
from address_repo import AddressRepo
from cart_repo import CartRepo
from external_repo import ExternalRepo
from order_repo import OrderRepo
from sku_order_repo import SkuOrderRepo

from conn import sms_redis, celery_redis, mongo_db




class Repos(object):
    _user_repo = UserRepo()
    _address_repo = AddressRepo()
    _cart_repo = CartRepo()
    _external_repo = ExternalRepo()
    _order_repo = OrderRepo()
    _sku_order_repo = SkuOrderRepo()

    _sms_redis = sms_redis
    _celery_redis = celery_redis

    _mongodb = mongo_db

    @property
    def user_repo(self):
        return self._user_repo

    @property
    def sms_redis(self):
        return self._sms_redis

    @property
    def celery_redis(self):
        return self._celery_redis

    @property
    def address_repo(self):
        return self._address_repo

    @property
    def cart_repo(self):
        return self._cart_repo

    @property
    def expernal_repo(self):
        return self._external_repo

    @property
    def order_repo(self):
        return self._order_repo

    @property
    def sku_order_repo(self):
        return self._sku_order_repo

    @property
    def order_mongodb(self):
        return self._mongodb.order
