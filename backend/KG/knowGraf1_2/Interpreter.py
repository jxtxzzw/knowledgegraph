# -*- coding: utf-8 -*-
'''
 ** version 0.0.2
 ** w 语言解释器
    简介：
        -w语言 -> 底层的API
        -可以通过简单的语句实现对知识库的增删改查，查询，推理
 ** 添加/删除文档
 **     -概念/实例/关系/属性 +=/-= &xxx/xxx/(xxx xxx xxx xxx)/xxx xxx xxx
 **     -规则 += (A.规则名.B :- A.R1.C B.R2.C)
 **     -规则 -= xxx
 ** note:
 **     -x1.x2 语义为 x1的 x2
 ** 添加/删除孩子
 **     -x1.child  +=/-= x2
 **     -x1.ins +=/-= x2
 ** 建立连接
 **     -x1.r1 +/- x2
 ** 增加/删除关系值
 **     -x1.r1 +=/-= x2
 ** 修改term的性质
 **     -xxx.attr = 实例/关系
 **     -xxx.attr = 属性/关系
 ** 修改term的gloss
 **     -xxx.gloss = xxxx
 ** 设置term的名字
 **     -xxx.name = &xxx/xxx/(xxx xxx xxx xxx)/xxx xxx xxx
 ** 添加/删除term的名字
 **     -xxx.name +=/-= &xxx/xxx/(xxx xxx xxx xxx)/xxx xxx xxx
 ** 添加变量
 **     -&xxx = xxx/xxx xxx xxx/(xxx xxx xxx)
 ** 三元组查询
 **     -xxx
 **     -xxx.xxx
 **     -xxx.?.xxx
 **     -?.xxx.xxx
 **     -xxx.xxx.xxx
 ** 特殊的简单查询
 **     -概念/实例/关系/属性/规则
 **     -xxx.child/attr/parent

 **  复杂查询
 **     -(x1.r1.x2 x2.r2.x3 ... )
 **  规则推理
 **     -x2.rule.x1
 **
 **
'''
# import module
from knowGraf1_2.Build import KG
from knowGraf1_2.Query import query, InferenceMachine
from knowGraf1_2.Constant import (DB, PARTTEN, CON, INS, RULE, REL,
                                  ATTR, BUILD, PULL, DEL, ADD, NULL,
                                  CHILDEREN, PARENTS, ID, BODY, UNKNOWN,
                                  CSYN, ESYN, GLOSS)



import re
from functools import reduce
from operator import add
from collections import deque, Iterable



KEYWORD = ('概念', '实例', '关系', '属性', '规则', 'name', ATTR, 'child', 'ins', GLOSS)
SPECIALREL = (CHILDEREN, PARENTS, ATTR, CSYN, ESYN, GLOSS)

SPECIALCON = (CON, ATTR, REL, INS, RULE)


SPLIT = ' '
CONTERM, RELTERM = 'ConTerm', 'RelTerm'
CommentSymbol = '#'


P_OP = re.compile(r'(\+=)|(-=)|(=)|(\+)|(-)')
P_KW = re.compile(r'(\.child)|(\.name)|(\.性质)|(\.ins)|(\.)|'
                  r'(实例)|(概念)|(关系)|(属性)|(规则)|(&)')

zhPattern = re.compile(u'[\u4e00-\u9fa5]+')

is_chinese = lambda term: bool(zhPattern.findall(term))
is_unknown = lambda term: re.sub(r'([\d]+)', '', term).isupper()


# 移除已存在的概念
def pull_exist_term(db, prop):
    def decorator(func):
        if prop in ['con', 'attr']:
            get_id = db.cname2id
        else:
            get_id = db.rname2id

        def wrapper(terms):
            terms = [term for term in terms if not get_id(term)]
            return func(terms)

        return wrapper

    return decorator

def matching(content, split=SPLIT):
    '''
    str : ( xxx ,  xxx  ...)/xxx -> list : [xxx,xxx]/[xxx]
    :return list or str:
    '''

    if not split or split not in content:
        return [content.strip().lstrip('(').rstrip(')')]

    for res in PARTTEN.findall(content):
        # 如果不是空格 那么就是匹配到的内容
        if not res.isspace():
            return [i.strip() for i in res.split(split) if (not i.isspace() and i)]

def get_kw(seq):
    """得到序列中的关键字"""
    res = P_KW.search(seq)
    return res.group() if res else '.'

def get_op(seq):
    """得到序列中的操作符"""
    res = P_OP.search(seq)
    return res.group() if res else ''




class Interpreter:
    """处理语言的核心类"""
    __slots__ = ('DB', 'KG', 'seqs', 'varSpace', 'funcMap', 'dbName')



    def __init__(self, DBName, sequences):
        self.DB = DB(DBName)
        self.KG = KG(DBName)
        self.dbName = DBName
        self.seqs = sequences.split('\n')
        self.varSpace = {}  # 变量空间

        self.funcMap = {
            "概念": self.find_all_con,
            "实例": self.find_all_ins,
            "属性": self.find_all_attr,
            "关系": self.find_all_rel,
            "规则": self.find_all_rule,
            '概念-=': self.del_con,
            '概念+=': self.add_con,
            '实例-=': self.del_ins,
            '实例+=': self.add_ins,
            '关系-=': self.del_rel,
            '关系+=': self.add_rel,
            '属性-=': self.del_attr,
            '属性+=': self.add_attr,
            '规则-=': self.del_rule,
            '规则+=': self.add_rule,
            ATTR+'=': self.upd_property,
            GLOSS+'=':self.upd_term_glosee,
            'child-=': self.del_child,
            'child+=': self.add_child,
            'ins-=': self.del_child,
            'ins+=': self.add_child,
            'name+=': self.add_name,
            'name-=': self.del_name,
            'name=': self.set_name,
            '+': self.create_conn,
            '-': self.break_conn,
            '-=': self.pull_rel_value,
            '+=': self.add_rel_value,
            '&=': self.add_var,
            'query': self.query,
            'multiple_queries': self.multiple_queries,
             'reasoning': self.reasoning
        }



    def parse_parms(self, parms):
        '''
        用于参数解析 预处理
        :param param  str:(x1,x2,x3)/x1/var
        :return list :
        '''
        if self.varSpace.get(parms):
            return self.varSpace[parms]
        else:
            return matching(parms)

    def parse_left(self, left):
        """解析序列的左侧"""

        left, *right = left.split('.')
        left = left.replace(' ', '')
        left = left.strip()
        if right:
            right = right[0].strip()

        if left in KEYWORD:
            keyWord, arg = left, []
        elif right in KEYWORD:
            keyWord, arg = right, self.parse_parms(left)
        elif '&' in left:
            varName = left.strip()
            keyWord, arg = '&', [varName]
        else:
            keyWord, arg = '', [self.parse_parms(left), self.parse_parms(right)]

        return keyWord, arg

    def parse_right(self, right):
        """解析序列的右侧"""
        if ':-' in right:
            return matching(right, None)[0]
        else:
            return self.parse_parms(right.strip())

    def query_to_triples(self, seq):
        """解析查询的参数"""
        if seq.count('.') == 0:
            func, arg = 'query', [seq.strip(), NULL, NULL]
        elif seq.count('.') == 1:

            func, arg = 'query', [i.strip() for i in seq.split('.')] + [NULL]
        else:

            arg = [(NULL if '?' in i else i.strip()) for i in seq.split('.')]

            if arg[1] != NULL and arg[1] not in SPECIALREL:
                relId = arg[1] = self.get_rel_id(arg[1])
                relAttr = self.DB.find_rel_by_id(relId)[ATTR][0]
                func = 'query' if relAttr != RULE else 'reasoning'
            else:
                func = 'query'
        return func, arg

    def parse_query_sequence(self, seq):
        """解析查询语句
        return 'query'/'multiple_queries'/'reasoning' and arg
        """
        func, arg = None, []
        # 特殊查询
        if seq in KEYWORD[:4]:
            func = seq
        # 多重查询
        elif seq.count('.') > 2:
            func = 'multiple_queries'
            arg = self.get_rule_body(seq)
        # 简单查询 / 推理
        else:
            func, arg = self.query_to_triples(seq)

        return func, arg

    def parse(self, seq):
        """解析语句
        return func arg"""
        op = get_op(seq)
        # 构建
        if op:
            left, right = seq.split(op)
            keyWord, leftArg = self.parse_left(left)
            rightArg = self.parse_right(right)

            arg = leftArg + [rightArg]
        # 查询
        else:
            keyWord, arg = self.parse_query_sequence(seq.strip())

        print('this seq keyword is {}, arg is{}'.format(keyWord + op, arg))
        return self.funcMap[keyWord + op], arg

    def exec(self, func, args):
        """执行单条语句"""
        return func(*args)

    def can_exec(self, seq):
        """判断语句是否可执行"""
        return seq and CommentSymbol not in seq

    def run(self):
        count = 0
        rtn = []
        re_str = ''
        for seq in self.seqs:
            if self.can_exec(seq):
                func, arg = self.parse(seq)
                res = self.exec(func, arg)


                re_str = 'No.{} seq is {} , res is {} \n\n '.format(count, seq, res)
                count += 1
                if not isinstance(res, str) or 'query' in res:
                    rtn.append(res)
        return rtn, re_str

    def get_con_id(self, name):
        """得到概念的id"""
        if name == NULL or (is_unknown(name) and (not is_chinese(name))) or name in SPECIALCON or name.isdigit():
            id_ = name
        else:
            id_ = self.DB.cname2id(name)
            id_ = id_[0] if id_ else None

        return id_

    def get_rel_id(self, name):
        """得到关系的id"""
        if name == NULL or (is_unknown(name) and (not is_chinese(name))) or name in SPECIALREL or name[1:].isdigit():
            id_ = name
        else:
            id_ = self.DB.rname2id(name)
            id_ = id_[0] if id_ else None

        return id_

    def get_triple_id(self, con1, rel, con2):
        """得到 三元组中每一元的id"""
        con1Id = self.get_con_id(con1)
        relId = self.get_rel_id(rel)
        con2Id = self.get_con_id(con2)
        return [con1Id, relId, con2Id]

    def creat_all_triple(self, con1s, rels, con2s):
        """从概念列表，关系列表，中创建所有的三元组"""
        return [self.get_triple_id(con1, rel, con2)
                         for con1 in con1s
                         for rel in rels
                         for con2 in con2s]

    def get_rule_body(self, body):
        """得到规则体"""

        body = deque(body.split('.'))
        res = []
        while body:
            con1 = body.popleft().strip()
            rel = body.popleft().strip()
            con2, *nextCon = [i.strip() for i in body.popleft().split(' ') if i]
            res.append([con1, rel, con2])
            if nextCon and not nextCon[0].isspace():
                body.appendleft(nextCon[0])
        return res


    # funcMap function

    def add_con(self, cons):
        '''增加概念 cons type is token ,Three forms [xxx,xxx]/xxx/var'''
        cons = [con for con in cons if not self.DB.cname2id(con)]
        return self.KG.add_con_or_ins(cons, [CON]*len(cons))

    def add_ins(self, inss):
        '''增加实例 inss type is token ,Three forms [xxx,xxx]/xxx/var'''
        inss = [ins for ins in inss if not self.DB.cname2id(ins)]
        return self.KG.add_con_or_ins(inss, [INS] * len(inss))

    def add_attr(self, attrs):
        '''增加属性 attrs type is token ,Three forms [xxx,xxx]/xxx/var'''
        attrs = [attr for attr in attrs if not self.DB.rname2id(attr)]
        return self.KG.add_rel(attrs, [ATTR] * len(attrs))

    def add_rel(self, rels):
        '''增加关系 rels type is token ,Three forms [xxx,xxx]/xxx/var'''
        rels = [rel for rel in rels if not self.DB.rname2id(rel)]
        return self.KG.add_rel(rels, [REL] * len(rels))


    def add_rule(self, rule):
        '''增加规则 rule type is token '''

        head, body = rule.split(':-')
        unknown1, name, unknown2 = head.split('.')
        unknown = [unknown1.strip(), unknown2.strip()]
        # res = matching(body, None)
        body = self.get_rule_body(body)

        # name -> id
        body = [self.get_triple_id(*triple) for triple in body]
        return self.KG.add_rule(name, unknown, body)

    def del_con(self, cons):
        """删除概念"""
        consId = [self.get_con_id(con) for con in cons]
        for conId in consId:
            self.KG.del_con(conId)
        return 'del con : {} ok'.format(cons)

    def del_ins(self, inss):
        """删除 实例   """
        inssId = [self.get_con_id(ins) for ins in inss]
        self.KG.del_ins(inssId)
        return 'del ins: {} ok'.format(inss)

    def del_attr(self, attrs):
        """删除 属性"""
        attrsId = [self.get_rel_id(attr) for attr in attrs]
        for attrId in attrsId:
            self.KG.del_rel(attrId)
        return 'del attr: {} ok'.format(attrs)

    def del_rel(self, rels):
        '''删除关系 '''
        relsId = [self.get_rel_id(rel) for rel in rels]
        for rel in relsId:
            self.KG.del_rel(rel)
        return 'del rel: {} ok '.format(rels)

    def del_rule(self, rules):
        '''删除规则'''
        rulesId = [self.get_rel_id(rule) for rule in rules]
        for rel in rulesId:
            self.KG.del_rel(rel)
        return 'del rule: {} ok '.format(rules)



    def create_conn(self, con1, rel, con2):
        """创建概念之间的连接"""
        tripleId = self.get_triple_id(con1[0], rel[0], con2[0])

        tripleId.append(BUILD)
        self.KG.conn_cons(*tripleId)
        return 'create {rel} between {con1} and {con2} is ok '.format(rel=rel, con1=con1, con2=con2)

    def break_conn(self, con1, rel, con2):
        """断开概念之间的连接"""
        tripleId = self.get_triple_id(con1[0], rel[0], con2[0])
        tripleId.append(DEL)
        self.KG.conn_cons(*tripleId)
        return 'break {rel} between {con1} and {con2} is ok '.format(rel=rel, con1=con1, con2=con2)

    def add_rel_value(self, con1s, rels, con2s):
        """增加关系值"""
        triplesId = self.creat_all_triple(con1s, rels, con2s)
        self.KG.upd_conn(triplesId, [ADD]*len(triplesId))
        return 'add {rel} between {con1} and {con2} is ok '.format(rel=rels, con1=con1s, con2=con2s)

    def pull_rel_value(self, con1s, rels, con2s):
        """删除关系值"""
        triplesId = self.creat_all_triple(con1s, rels, con2s)
        self.KG.upd_conn(triplesId, [PULL]*len(triplesId))
        return 'pull {rel} between {con1} and {con2} is ok '.format(rel=rels, con1=con1s, con2=con2s)


    def add_child(self, parent, children):
        """添加子节点"""
        parentId = self.get_con_id(parent)
        for child in children:
            child = self.get_con_id(child)
            self.KG.add_child(parentId, child)

        return '{parent} add child :{children} is ok '.format(parent=parent, children=children)

    def del_child(self, parent, children):
        """删除子节点"""
        parent = self.get_con_id(parent)
        for child in children:
            child = self.get_con_id(child)
            self.KG.del_child(parent, child)
        return '{parent} del child :{children} is ok '.format(parent=parent, children=children)

    def set_name(self, term, newNames):
        """设置条目的名字"""
        termId = self.get_con_id(term)
        if termId:
            id_ = termId
            self.KG.upd_con_name(id_, newNames)
        else:
            id_ = self.get_rel_id(term)
            self.KG.upd_rel_name(id_, newNames)

        return 'set {term} name is {newNams} is ok'.format(term=term, newNams=newNames)

    def add_name(self, term, newNames):
        """增加概念的名字"""
        termId = self.get_con_id(term)
        if termId:
            oldNames = self.DB.cid2name(termId)
            self.KG.upd_con_name(termId, list(set(oldNames) | set(newNames)))
        else:
            termId = self.get_rel_id(term)
            oldNames = self.DB.rid2name(termId)
            self.KG.upd_rel_name(termId, list(set(oldNames) | set(newNames)))

        return 'add {term} name is {newNams} is ok'.format(term=term, newNams=newNames)

    def del_name(self, term, newNames):
        """删除概念的名字"""
        termId = self.get_con_id(term)
        if termId:
            oldNames = self.DB.cid2name(termId)
            self.KG.upd_con_name(termId, list(set(oldNames) - set(newNames)))
        else:
            termId = self.get_rel_id(term)
            oldNames = self.DB.rid2name(termId)
            self.KG.upd_rel_name(termId, list(set(oldNames) - set(newNames)))
        return 'add {term} name is {newNams} is ok'.format(term=term, newNams=newNames)


    def upd_property(self, term, updprop):
        """更新概念/实例 关系/属性 的属性"""
        updprop = updprop[0]
        map_ = {'实例': INS, '概念': CON, '关系': REL, '属性': ATTR}
        if updprop in ['实例', '概念']:
            find_id, upd_func = self.get_con_id, self.KG.upd_con_attr
        else:
            find_id, upd_func = self.get_rel_id, self.KG.upd_rel_attr

        id_ = find_id(term)
        upd_func(id_, map_[updprop])

        return 'set {term} property is {prop} ok'.format(term=term, prop=updprop)

    def upd_term_glosee(self, term, gloss):
        """修改术语的注释"""
        _id = self.get_con_id(term)
        if _id:
            self.KG.upd_con_gloss(_id, gloss[0])
            return 'upd con gloss ok, con is {}, gloss is {}'.format(term, gloss[0])
        _id = self.get_rel_id(term)
        if _id:
            self.KG.upd_rel_gloss(_id, gloss[0])
            return 'upd rel gloss ok, con is {}, gloss is {}'.format(term, gloss[0])

        return 'id error'



    def add_var(self, varName, varValue):
        """添加变量"""
        self.varSpace[varName] = varValue
        return 'add var: {var} value: {value}'.format(var=varName, value=varValue)

    def query(self, *triple):
        """查询：简单查询"""
        # ->id
        triple = self.get_triple_id(*triple)

        res = query(self.DB, *triple)
        if isinstance(res, bool):
            res = 'query is ok , res is {}'.format(res)
        elif isinstance(res, (list, set, tuple)):
            find_name = self.DB.rid2name if triple[1] == NULL else self.DB.cid2name

            res = 'query is ok , res is {}'.format([find_name(i) or [i]
                                                    for i in res])
        else:
            find_rel_name = self.DB.rid2name
            find_con_name = self.DB.cid2name
            res = 'query is ok , res is {}'.format(
                {(tuple(find_rel_name(rel)) if rel not in SPECIALREL else rel):
                            [(find_con_name(con) if rel not in (CSYN, ESYN, ATTR) else [con]) for con in cons]
                  for rel, cons in res.items()}
            )

        return res

    def multiple_queries(self, *triples):
        """多重查询"""
        triples = [self.get_triple_id(*triple) for triple in triples]
        actions = InferenceMachine(self.dbName, triples).exec()
        # 建立属性索引
        attrIndex = {REL: [], CON: []}
        for triple in triples:
            con1, rel, con2 = triple
            if is_unknown(con1):
                attrIndex[CON].append(con1)
            if is_unknown(rel):
                attrIndex[REL].append(rel)
            if is_unknown(con2):
                attrIndex[CON].append(con2)

        res = []
        for actionId in actions:
            actionName = {}
            for unk, val in actionId.items():
                if unk in attrIndex[CON]:
                    actionName[unk] = self.DB.cid2name(val)
                else:
                    actionName[unk] = self.DB.rid2name(val)
            res.append(actionName)

        return res


    def reasoning(self, c1, rule, c2):
        """推理"""
        ruleDoc = self.DB.find_rel_by_id(rule)
        # 规则体 未知量
        body, unknown = ruleDoc[BODY], ruleDoc[UNKNOWN]
        # 已知量
        known = {}

        if not is_unknown(c1):
            known[unknown[0]] = [self.get_con_id(i) for i in self.parse_parms(c1)]
        if not is_unknown(c2):
            known[unknown[1]] = [self.get_rel_id(i) for i in self.parse_parms(c1)]

        actions = InferenceMachine(self.dbName, body, known).exec()


        if is_unknown(c1):
            return [self.DB.cid2name(con) for con in set([action[c1] for action in actions if action.get(c1)])]
        elif is_unknown(c2):
            return [self.DB.cid2name(con) for con in set([action[c2] for action in actions if action.get(c2)])]
        else:
            return bool(actions)

    def find_all_term(self, collection, term):
        """找到所有的term"""
        res = collection.find({ATTR: term}, projection={ID: True, CSYN: True})
        return list(res)

    def find_all_con(self):
        """找到所有的概念"""
        return self.find_all_term(self.DB.CONDATA, CON)

    def find_all_ins(self):
        """找到所有的实例"""
        return self.find_all_term(self.DB.CONDATA, INS)

    def find_all_rel(self):
        """找到所有的关系"""
        return self.find_all_term(self.DB.RELDATA, REL)

    def find_all_attr(self):
        """找到所有的属性"""
        return self.find_all_term(self.DB.RELDATA, ATTR)

    def find_all_rule(self):
        """找到所有的规则"""
        return self.find_all_term(self.DB.RELDATA, RULE)

if __name__ == '__main__':
    zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
    print(zhPattern.findall('打打'))


    # res = ii.run()

