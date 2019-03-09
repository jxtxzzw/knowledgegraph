from knowGraf1_2.Interpreter import Interpreter
DBNAME = "disease"


key_str = "肺炎"
complier = Interpreter(DBNAME, key_str)
fun, args = complier.query_to_triples(key_str)
res, re_str = complier.run()
print(res, re_str)