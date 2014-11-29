# -*- coding: utf-8 -*-
__author__ = 'wan'
import pymongo

from tools.conf import ConfigUtil

DEFAULT_SE = ['_user', 'phone', 'email']


class DBServer():
    def __init__(self, path, collections):
        db_conf = ConfigUtil(path).db_conf()
        self.client = pymongo.MongoClient("mongodb://{0}:{1}".format(db_conf['host'], db_conf['port']))
        self.db = self.client[collections]
        if len(db_conf['username']) > 0 and len(db_conf['password']) > 0:
            self.db.authenticate(db_conf['username'], password=db_conf['password'])

    def query(self, **kwargs):
        users = []
        for user in self.db.users.find(kwargs):
            user.pop("_id")
            users.append(user)
        users.sort(key=lambda item: item['datetime'] if 'datetime' in item else -1, reverse=True)
        return users

    def insert(self, **kwargs):
        self.validate(**kwargs)
        data = {}
        for key, val in kwargs.items():
            data[key] = val[0]
        self.db.users.insert(data)

    def validate(self, **kwargs):
        for key, val in kwargs.items():
            if key not in DEFAULT_SE:
                continue
            user = self.db.users.find_one({key: val[0]})
            if user:
                raise ValueError("The phone was sign up!please sign in")


    def remove(self, **kwargs):
        return self.db.users.remove(kwargs)

    def update(self, condition, **kwargs):
        user = self.db.users.find_one(condition)
        if user:
            data = combine_data(user, kwargs)
            self.db.users.update(condition, data)
            return
        raise ValueError('The use does not exist')

    def find_all(self):
        users = []
        for user in self.db.users.find():
            user.pop("_id")
            users.append(user)
        users.sort(key=lambda item: item['datetime'] if 'datetime' in item else -1, reverse=True)
        return users

    def close(self):
        self.client.close()


def combine_data(user, option):
    for k, val in option.items():
        user[k] = val
    return user
