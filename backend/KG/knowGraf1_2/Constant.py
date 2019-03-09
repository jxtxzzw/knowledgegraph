# -*- coding: utf-8 -*-
'''
知识图谱
'''


import os, re
from pymongo import MongoClient
from functools import  reduce, partial
from operator import add, or_

SERVICE = MongoClient('localhost', 27017)
USER = os.path.join(os.path.split(__file__)[0], 'user.txt')

try:
    with open(USER, 'r', encoding='utf-8') as f:
        IDPOINTER = eval(f.read())
except ImportError:
    IDPOINTER = {"rel": 100000000,
                 "con": 100000000000000,
                 "ins": 100000000000000000,
                 "attr": 1000000000000000000,
                 "rule": 10000000000000000000}



'''---------------------------------常量---------------------------'''

ADD = '$addToSet'  # 添加键值
PULL = '$pull'     # 移除值
DEL = '$unset'    # 删除键
BUILD = '$set'       # 设置键

ID = '_id'
PARENTS = 'parents' # 父概念
CHILDEREN = 'child' # 子概念
DOMAINS = 'domains'   # 定义域
ATTR = 'attr'  # 属性
CSYN = 'csyn'
ESYN = 'esyn'
GLOSS = 'gloss'  # 文档注释

TERM = 'term'    # term表
DATA = 'data'    # data表

CON = 'con'      # 概念
INS = 'ins'      # 实例
REL = 'rel'      # 关系
RULE = 'rule'  # 规则

UNKNOWN = 'unknown'
BODY = 'body'
NULL = 0


DELDOMAINS = []   # 删除定义域时传入的定义域



DELSUB = 100   # 删除所有子概念
DELONE = 101   # 只删除关系对

# 重新定义字典类 使得当keyerror 返回值 []
class Doc(dict):
    def __missing__(self, key):
        return []

PARTTEN = re.compile(r'[^()]+')

class DB:

    __slots__ = ['db', 'CONTERM', 'CONDATA', 'RELTERM', 'RELDATA']

    def __init__(self, DBName):
        self.db = SERVICE[DBName]
        self.CONTERM = self.db.ConTerm
        self.CONDATA = self.db.ConData
        self.RELTERM = self.db.RelTerm
        self.RELDATA = self.db.RelData


    def find_rel_by_id(self, id_, *noRtn):
        doc = self.RELDATA.find_one({ID: id_}, projection=dict({i: False for i in noRtn}, **{ID: False}))
        return Doc(doc) if doc else Doc()

    def find_con_by_id(self, id_, *noRtn):
        """
        find_con_by_id('234234324', CSYN, CHILD, PARENT)
        查询 id为234234324的概念， 不返回 CSYN, CHILD, PARENT；
        :param id_: 
        :param noRtn: 
        :return: 
        """
        doc = self.CONDATA.find_one({ID: id_}, projection=dict({i: False for i in noRtn}, **{ID: False}))
        return Doc(doc) if doc else Doc()

    def cid2name(self, id_):
        doc = self.CONTERM.find_one({ID: id_}, projection={ID: False, TERM: True})
        return doc[TERM] if doc else []

    def rid2name(self, id_):
        doc = self.RELTERM.find_one({ID: id_}, projection={ID: False, TERM: True})
        return doc[TERM] if doc else []

    def cname2id(self, name):
        ids = tuple(self.CONTERM.find({TERM: name}, projection={ID: True}))
        if ids:
            return [id_[ID] for id_ in ids]
        else:
            return []

    def rname2id(self, name):
        ids = tuple(self.RELTERM.find({TERM: name}, projection={ID: True}))
        if ids:
            return [id_[ID] for id_ in ids]
        else:
            return []



    def delete_all(self):
        for col in (self.RELTERM, self.RELDATA, self.CONTERM, self.CONDATA):
            col.drop()

def del_all(db):
    '''删除库'''
    for col in (db.CONDATA, db.CONTERM, db.RELDATA, db.RELTERM):
        col.drop()

def getID(mode):
    # 返回id(字符串类型) 并 对应值+1
    global IDPOINTER

    id = IDPOINTER[mode]
    IDPOINTER[mode] = id + 1
    with open(USER, 'w') as f:
        f.write(str(IDPOINTER))

    return str(id)

def getInverseRel(id):
    '''得到逆关系'''
    return id[1:] if id[0] == '-' else '-'+id




if __name__ == '__main__':

    db = DB('homeWorkDb')
    print(db.cname2id('C语言结构'))
    print(db.find_rel_by_id('parents'))
    pass

