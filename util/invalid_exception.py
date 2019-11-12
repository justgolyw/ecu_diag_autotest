#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Author : yangwei.li
@Create date : 2019-11-12
@FileName : invalid_exception.py
"""

class InvalidException(BaseException):

    def __init__(self, msg="raise s selfException"):
        print(msg)
