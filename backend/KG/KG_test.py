from knowGraf1_2.Interpreter import Interpreter
from knowGraf1_2.Constant import DB
import json
import pymongo


DBNAME = 'SanGuo'

def db_build():
    DB(DBNAME).delete_all()
    with open('all.txt', mode='r', encoding='utf-8') as code:
        lines = code.readlines()
        for line in lines:
            key_str = line.strip()
            #complier = Interpreter(DBNAME, code.read().split('//')[0])
            complier = Interpreter(DBNAME, key_str)
            res = complier.run()

            # print('code run end ,res is ')
            #
            # for i in res:
            #     print(i)

def db_fun(key_str):
    col = ["ConTerm", 'ConData', 'RelTerm', 'RelData']
    info_dict = {}
    if 'add' in key_str:
        key_str = key_str.replace('add','+')
    if 'minus' in key_str:
        key_str = key_str.replace('minus','-')
    if (key_str[:6] == "import"):
        data = eval(key_str[6:])
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient[DBNAME]
        for name in col:
            mydb[name].drop()
        for x in data:
            mydb[x[0]].insert_one(eval(x[1]))
        info_dict.update({'result':'success'})
        json_data = json.dumps(info_dict)
        return json_data

    complier = Interpreter(DBNAME, key_str)
    fun,args = complier.query_to_triples(key_str)
    res, re_str = complier.run()

    if '=' in key_str:
        info_dict['result'] = re_str
    elif key_str == "export":
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient[DBNAME]
        ret = []
        for name in col:
            mycol = mydb[name]
            for x in mycol.find():
                ret.append([name, str(x)])
        info_dict.update({'result': str(ret)})
    else:
        for res_ in res:
            if type(res_) == list:
                re_list = []
                for v in res_:
                    if type(v) == dict:
                        re_list.append(v['csyn'][0])
                info_dict.update({'result':re_list})
            if type(res_) == str:
                if args.count(0) > 1:
                    info = res_[res_.find('{'):]
                    info = eval(info)
                    for k, v in info.items():
                        v_new = []
                        if len(v) > 0:
                            for item in v:
                                if len(item) > 0:
                                    v_new.append(item[0])
                        if len(v_new) > 0:
                            if type(k) != str:
                                k_new = k[0]
                            else:
                                k_new = k
                            info_dict.update({k_new: v_new})
                else:
                    info = res_[res_.find('['):]
                    info = eval(info)
                    info_dict = {}
                    v_list = []
                    for re in info:
                        v_list.append(re[0])
                    info_dict.update({'result': v_list})
    json_data = json.dumps(info_dict)
    return json_data

if __name__ == '__main__':
    db_build()
