# -*- coding: utf-8 -*-
__author__ = 'wan'
import logging


class User(object):
    def __init__(self):
        pass

    @classmethod
    def covert(cls, **kwargs):
        user = cls()
        for key, value in kwargs.items():
            if 'submit' in key:
                continue
            if isinstance(value, list):
                value = value[0]
            setattr(user, str(key), value)
        return user

    @classmethod
    def find_user(cls, db, **kwargs):
        """
        :rtype : User
        """
        user = db.query(**kwargs)
        if len(user) <= 0:
            return None
        logging.info("Find the users %s", str(user))
        return cls.covert(**user[0])

    @classmethod
    def find_all(cls, db):
        users = []
        for user in db.find_all():
            users.append(cls.covert(user))
        logging.info("Find the users %s", str(user))
        return users

    @classmethod
    def find_by_condition(cls, db, **kwargs):
        return db.query(**kwargs)
