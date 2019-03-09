# -*- coding: utf-8 -*-
"""
 : 知识图谱的构建
 : 用于概念/实例 关系/属性的 增删改
"""
# import my model
from knowGraf1_2.Constant import *


# import other model
import sys
from operator import add
from functools import reduce, partial

from pymongo import ReturnDocument
from pymongo import UpdateOne, DeleteOne
from collections import deque

sys.setrecursionlimit(10000000) # 设置最大递归数

def pull_rel_vals(cid, doc):
    '''
    断开概念的所有逆连接
    :param cid:
    :param doc:
    :return:
    '''
    req = []
    for rel, vals in doc.items():
        _rel = getInverseRel(rel)
        req += [UpdateOne({ID: val}, {PULL: {_rel: cid}}) for val in vals]
    return req



class KG(DB):
    """
    构建知识图谱的核心类
    """
    def __init__(self, DBName):
        super().__init__(DBName=DBName)

    def update_and_rtn_child(self, id, update, return_document=ReturnDocument.BEFORE):
        """

        :param id:
        :param update:
        :return [child1, child2 ...]:
        """
        projection = {ID: False, CHILDEREN: True}
        children = self.CONDATA.find_one_and_update({ID: id}, update=update, projection=projection, return_document=return_document)
        return children[CHILDEREN] if children else []

    def update_and_rtn_rels(self, id, update, return_document=ReturnDocument.BEFORE):
        """

        :param id:
        :param update:
        :return {rel： con}:
        """
        projection = {ID: False, CHILDEREN: False, PARENTS: False, ATTR: False, CSYN: False, ESYN: False}
        rels = self.CONDATA.find_one_and_update({ID: id}, update=update,
                                                          projection=projection,
                                                          return_document=return_document)
        return Doc(rels) if rels else Doc()

    def del_child_and_rtn_rels(self, id, child):
        return self.update_and_rtn_rels(id, {PULL: {CHILDEREN: child}})

    def add_child_and_rtn_rels(self, id, child):
        return self.update_and_rtn_rels(id, {ADD: {CHILDEREN: child}})

    def set_domains(self, con1, rel, con2, op):
        """
        关系增加/删除定义域
        :parelam
        """
        self.RELDATA.update_one({ID: rel}, {op: {DOMAINS: [con1, con2]}})

        _rel = getInverseRel(rel)
        self.RELDATA.update_one({ID: _rel}, {op: {DOMAINS: [con2, con1]}})

    def upd_conn_one(self, con1, rel, con2, op):
        """改变概念/实例中关系（继承的）的指向性 只生成参数"""
        return [UpdateOne({ID: con1}, {op: {rel: con2}}),
                UpdateOne({ID: con2}, {op: {getInverseRel(rel): con1}})]

    def upd_conn(self, triples, ops):
        """改变概念/实例中关系（继承的）的指向性 执行"""
        update = reduce(add, (self.upd_conn_one(*(triple+[op])) for triple, op in zip(triples, ops)))
        self.CONDATA.bulk_write(update)

    def conn_con(self, con1, rel, con2, op):
        """给子概念添加/删除关系"""
        conChild = self.update_and_rtn_child(con1, {op: {rel: [con2]}})
        if conChild:
            cons = deque(conChild)
            while cons:
                con = cons.popleft()
                cons += self.update_and_rtn_child(con, {op: {rel: []}})

    def conn_cons(self, con1, rel, con2, op):
        """
        两个概念之间建立(添加)/删除连接(关系)
        :param triple:
        """
        # 删除/建立 域
        self.set_domains(con1, rel, con2, op)
        # 删除/添加概念的关系
        self.conn_con(con1, rel, con2, op)
        _rel = getInverseRel(rel)
        self.conn_con(con2, _rel, con1, op)

    def upd_con_name(self, id, newName):
        self.CONDATA.update_one({ID: id}, {BUILD: {CSYN: newName}})
        self.CONTERM.update_one({ID: id}, {BUILD: {TERM: newName}})

    def upd_rel_name(self, id, newName):
        _newName, _id =  [name + '逆' for name in newName], getInverseRel(id)
        self.RELTERM.update_one({ID: id}, {BUILD: {TERM: newName}})
        self.RELTERM.update_one({ID: _id}, {BUILD: {TERM: _newName}})
        self.RELDATA.update_one({ID: id}, {BUILD: {CSYN: newName}})
        self.RELDATA.update_one({ID: _id}, {BUILD: {CSYN: _newName}})

    def create_rel_doc(self, name, attr):
        """添加单个
        :return data term rtn"""
        id = getID(attr)
        _id = getInverseRel(id)
        _name = name + '逆'
        return ([{ID: id, ATTR: [attr], CSYN: [name], GLOSS: []}, {ID: _id, ATTR: [attr], CSYN: [_name], GLOSS: []}],# data
                [{ID: id, TERM: [name]}, {ID: _id, TERM: [_name]}],        # term
                [{'id': id, 'name': name}, {'id': _id, 'name': _name}])  # rtn

    def add_rel(self, names, attrs):
        """
        创建关系的文档
        :param names 名字列表,attrs 属性列表:
        :return [{'id': id, 'name': name}]
        """
        datas, terms, rtns = [], [], []
        for name, attr in zip(names, attrs):
            data, term, rtn = self.create_rel_doc(name, attr)
            datas += data
            terms += term
            rtns += rtn

        if datas:
            self.RELDATA.insert(datas)
        if terms:
            self.RELTERM.insert(terms)
        return rtns

    def del_rel(self, id):
        '''
        删除关系 ：删除文档，删除所有该域概连接
        :param id:
        '''
        # 删关系并返回概念的域

        domians = Doc(self.RELDATA.find_one_and_delete({ID: id}, projection={ID: False, DOMAINS: True}))[DOMAINS]
        _id = getInverseRel(id)
        if domians:  # 如果域存在
            self.conn_cons(domians[0], id, domians[1], DEL)  # 删除连接
        self.RELDATA.bulk_write([DeleteOne({ID: _id})])
        self.RELTERM.bulk_write([DeleteOne({ID: _id}), DeleteOne({ID: id})])

    def add_rule(self, name, unkonwn, body):
        """
        添加 规则
        :param name: str
        :param unkonwn: ['A', 'B']
        :param body: [["A", "-1000000000000001495", "C"], ["B", "-1000000000000001495", "C"]]
        :return:
        """
        data = {ID: getID(RULE), CSYN: [name], ATTR: [RULE]}
        data[UNKNOWN] = unkonwn
        data[BODY] = body
        term = {ID: data[ID], TERM: data[CSYN]}

        self.RELTERM.insert(term)
        self.RELDATA.insert(data)

        return [{'id': term[ID], 'name': term[TERM]}]

    def del_rule(self, id):
        """删除规则"""
        self.RELDATA.delete_one({ID: id})
        self.RELTERM.delete_one({ID: id})

    def create_con_doc(self, name, attr):
        """创建概念/实例的文档"""
        id = getID(attr)
        return ({ID: id, ATTR: [attr], CSYN: [name],  ESYN: [], PARENTS: [], GLOSS: []},# data
                {ID: id, TERM: [name]},                                   # term
                {'id': id, 'name': name})                               # rtn

    def add_con_or_ins(self, names, attrs):
        """添加概念/实例"""
        datas, terms, rtns = [], [], []
        for name, attr in zip(names, attrs):
            data, term, rtn = self.create_con_doc(name, attr)
            datas.append(data)
            terms.append(term)
            rtns.append(rtn)
        self.CONTERM.insert(terms)
        self.CONDATA.insert(datas)
        return rtns

    def del_one_ins(self, id):
        condata = []
        projection = {ID: False, ATTR: False, CSYN: False, ESYN: False}  # 只返回关系值
        doc = Doc(self.CONDATA.find_one_and_delete({ID: id}, projection=projection))
        condata += [UpdateOne({ID: par}, {PULL: {CHILDEREN: id}}) for par in doc.pop(PARENTS, [])]
        condata += pull_rel_vals(id, doc)
        return condata

    def del_ins(self, ids):
        """
        删除实例
        :param ids: [id1, id2, ...]
        :return:
        """
        self.CONTERM.bulk_write([DeleteOne({ID: id}) for id in ids])
        self.CONDATA.bulk_write(reduce(add, [self.del_one_ins(id) for id in ids]))

    def del_con_and_rtn_subcon(self, id, ancestorRels):
        """
        删除一个概念
        :param id:
        :param ancestorRels:
        :return bulk for condata and bulk for conterm: [DeleteOne, ...] , [DeleteOne, ...]
        """
        condata, conterm = [DeleteOne({ID: id})], [DeleteOne({ID: id})]
        doc = self.find_con_by_id(id, CSYN, ESYN, PARENTS)
        children = doc.pop(CHILDEREN, [])
        attribute = doc.pop(ATTR)[0]
        if attribute == CON:
            # 对于继承关系逆使用PULL
            condata += pull_rel_vals(id, {rel: doc.pop(rel, []) for rel in ancestorRels})
            # 删除 连接
            for rel, con2, in doc.items():
                self.conn_cons(id, rel, con2, DEL)
        else:
            condata.append(UpdateOne({ID: id}, {DEL: dict({PARENTS: 1}, **{rel: 1 for rel in ancestorRels})}))

        return condata, conterm, children

    def del_one_con(self, id, ancestorRels):
        """删除单个概念"""
        condata, conterm = [DeleteOne({ID: id})], [DeleteOne({ID: id})]
        doc = self.find_con_by_id(id, CSYN, ESYN, PARENTS)
        children = doc.pop(CHILDEREN, [])
        # 继承关系用pull
        condata += pull_rel_vals(id, {rel: doc.pop(rel, []) for rel in ancestorRels})
        # 删除所有的个性关系
        for rel, con2 in doc.items():
            self.conn_cons(id, rel, con2, DEL)
        # 对子概念断继承
        condata += [UpdateOne({ID: children}, {PULL: {PARENTS: id}}) for child in children]

        return condata, conterm, []

    def del_con(self, id, isDelSubCon=True):
        """
        删除 概念及其子概念
        概念的父概念的逆关系 → pull_rel_vals
        概念及子概念的关系 → upd_conn_one
        实例的关系 → DEL
        :return:
        """
        # 得到父概念
        parId = self.find_con_by_id({ID: id}, CSYN, ESYN, CHILDEREN, ATTR).get(PARENTS, [None])[0]
        if parId:
            rels = tuple(self.update_and_rtn_rels(parId, update={PULL: {CHILDEREN: id}}).keys())
        else:
            rels = tuple()

        # 各个操作表参数
        condata, conterm = [], []
        conDeque = deque([id])

        # 只删除还是也删除子概念
        if isDelSubCon:
            del_func = self.del_con_and_rtn_subcon
        else:
            del_func = self.del_one_con

        while conDeque:

            data, term, children = del_func(conDeque.popleft(), ancestorRels=rels)
            condata += data
            conterm += term
            if children:
                conDeque += children

        if condata:
            self.CONDATA.bulk_write(condata)
        if conterm:
            self.CONTERM.bulk_write(conterm)

    def add_child(self, par, child):
        """
        给概念添加子概念
        :param par:
        :param child:
        :return:
        """
        # 父概念添加子概念 并返回自己的所有关系
        rels = tuple(self.update_and_rtn_rels(par, update={ADD: {CHILDEREN: child}}).keys())
        if rels:
            rels = dict(zip(rels, [[]]*len(rels)))
            # 子概念添加父概念,继承关系，并返回自己的所有孩子。
            # ！！ parent -> addToSet rels -> set
            children = self.update_and_rtn_child(child, {BUILD: rels, ADD: {PARENTS: par}})
            if children:
                # 所有孩子都继承关系
                children = deque(children)
                while children:
                    children += self.update_and_rtn_child(children.popleft(), {BUILD: rels})
        else:
            self.CONDATA.update_one({ID: child}, {ADD: {PARENTS: par}})

    def break_inherit(self, id, rels):
        """断开概念的关系"""
        projection = {ID: False, CSYN: False, ESYN: False, ATTR: False, PARENTS: False}
        # 概念的普通关系和
        doc = Doc(self.CONDATA.find_one_and_update({ID: id}, {DEL: rels},
                                                       projection=projection,
                                                       return_document=ReturnDocument.BEFORE))

        condata = pull_rel_vals(id, {k: doc[k] for k in rels.keys()})
        return condata, doc[CHILDEREN]

    def del_child(self, par, child):
        """
        删除子概念
        :param par:
        :param child:
        :return:
        """
        rels = tuple(self.update_and_rtn_rels(par, update={PULL: {CHILDEREN: child}}).keys())
        if rels:
            rels = dict(zip(rels, [[]]*len(rels)))
            condata = [UpdateOne({ID: child}, {PULL: {PARENTS: par}})]
            # 断关系 得到 child的子概念
            cons = deque([child])
            while cons:
                data, children = self.break_inherit(cons.popleft(), rels)
                condata += data
                cons += children
            if condata:
                self.CONDATA.bulk_write(condata)
        else:
            self.CONDATA.update_one({ID: child}, {PULL: {PARENTS: par}})

    def upd_con_attr(self, con, attr):
        """更新概念/实例 属性"""
        self.CONDATA.update_one({ID: con}, {BUILD: {ATTR: [attr]}})

    def upd_rel_attr(self, rel, attr):
        """更新 关系/属性 的属性"""
        self.RELDATA.update_one({ID: rel}, {BUILD: {ATTR: [attr]}})
        _rel = getInverseRel(rel)
        self.RELDATA.update_one({ID: _rel}, {BUILD: {ATTR: [attr]}})


    def upd_con_gloss(self, con, content):
        self.CONDATA.update_one({ID: con}, {BUILD: {GLOSS: [content]}})

    def upd_rel_gloss(self, con, content):
        self.RELDATA.update_one({ID: con}, {BUILD: {GLOSS: [content]}})



if __name__ == '__main__':
   kg = KG('BDNAME')
   print(kg.update_and_rtn_child("100000000006124", {PULL: {PARENTS: 1}}))

