# -*- coding: utf-8 -*-
'''
查询，复杂查询，推理
'''
from operator import add, or_
from functools import partial
from collections import deque

from knowGraf1_2.Constant import *


def query(db, con1, rel, con2):
    """
    三元组的查询
    :param db: <class 'DB'>
    :param con1:
    :param rel:
    :param con2:
    con1, rel, con2 为 NULL或者 str
    :return:
    """

    count = (con1, rel, con2).count(NULL)
    # 无NULL
    if count == 0:
        doc = db.find_con_by_id(con1)
        if doc and con2 in doc[rel]:
            return True
        else:
            return False
    # 两个 NULL
    elif count == 2:
        con = con1 if con1 != NULL else con2
        return db.find_con_by_id(con)
    # 一个 NULL
    else:
        # 查关系
        if rel == NULL:
            doc = db.find_con_by_id(con1)
            return set(k for k, v in doc.items() if con2 in v)
        # 找概念
        if con1 != NULL:
            return set(db.find_con_by_id(con1)[rel])
        else:
            # 这里有bug 特殊关系不能反转 先不做处理了
            return set(db.find_con_by_id(con2)[getInverseRel(rel)])



class InferenceMachine:
    """推理机 多重查询的核心类"""
    def __init__(self, DBName, triples, known={}):
        """
        :param triples(带查询的三元组):  list/tuple ([A1,ID1.ID2] , [B2,ID3,B3],...)
        :param konwn (三元组中的已知量): dict
        """
        self.DB = DB(DBName)
        self.triples = triples
        # 初始化变量字典
        self.varDict = {ele: [NULL] for triple in triples for ele in triple if ele.istitle()}
        # 将已知量代入
        for k, v in known.items():
            self.varDict[k] = set(v)

        self.valList = list(self.varDict.keys())
        self.actions = []
        self.query = partial(query, self.DB)

    def create_unknown_triples(self, triple):
        '''得到三元组未知量的个数 以及由已知量和未知量组成的新三元组'''
        c1, r, c2 = [list(self.varDict.get(ele, [ele])) for ele in triple]
        # if three unknown or only rel konwn
        if not (c1[0] or r[0] or c2[0]) or (not c1[0] and r[0] and not c2[0]):
            return 3
        # if all known
        if c1[0] and r[0] and c2[0]:
            return 0
        else:
            triples =  [(eleC1, eleR, eleC2) for eleC1 in c1
                                             for eleR in r
                                             for eleC2 in c2]
            return triples

    def find_all_value(self):
        """找到三元组所有的值"""
        triples = deque(self.triples)
        while triples:
            triple = triples.popleft()
            unknown_triples = self.create_unknown_triples(triple)
            if unknown_triples == 3:
                triples.append(triple)
            elif unknown_triples == 0:
                continue
            else:
                # 索引： 变量名

                valInd = {ind: triple[ind] for ind, val in enumerate(unknown_triples[0]) if val == NULL}
                if len(valInd) == 2:
                    con, rel = set(), set()
                    for unknown_triple in unknown_triples:
                        doc = self.query(*unknown_triple)
                        con |= set(doc.keys())
                        rel |= set(reduce(add, doc.values()))
                    self.varDict[valInd.pop(1)] = rel
                    self.varDict[list(valInd.values())[0]] = con
                else:
                    self.varDict[list(valInd.values())[0]] = reduce(or_,
                                                                    [self.query(*triple) for triple in
                                                                     unknown_triples])

    def find_action(self, varDict, valList, action={}):
        '''得到所有的解'''
        # 如果变量字典为空 验证action
        if not varDict:
            if self.validation_action(action):
                self.actions.append(action)
        else:
            for val in varDict.pop(valList[0]):
                self.find_action(dict(varDict), valList[1:], dict(action, **{valList[0]: val}))

    def validation_action(self, action):
        '''验证解是否正确'''
        for triple in self.triples:
            # 将已知的变量代入到三元组中
            triple = [action.get(ele, ele) for ele in triple]
            if not self.query(*triple):
                return False
        else:
            return True

    def exec(self):
        '''启动函数'''
        self.find_all_value()
        self.find_action(dict(self.varDict), list(self.valList))
        return self.actions

if __name__ == '__main__':
    pass

