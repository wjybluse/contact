# -*- coding: utf-8 -*-
__author__ = 'wan'
import ConfigParser
import uuid


class ConfigUtil():
    def __init__(self, path):
        self.path = path

    def db_conf(self):
        cfg = ConfigParser.ConfigParser()
        cfg.read(self.path)
        ret = dict()
        for key in cfg.options("db"):
            ret[key] = cfg.get("db", key)
        return ret


def general_uid():
    return uuid.uuid4()
