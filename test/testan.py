# -*- coding: utf-8 -*-
__author__ = 'wan'


def out(arg1, arg2):
    def xx(fn):
        print(arg1 + arg2)
        print "hahha"
        return fn

    return xx


@out("haode", "nimei")
def wode(params):
    print(params)
    print("nihao")


if __name__ == '__main__':
    wode(1234)