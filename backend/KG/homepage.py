from flask import Flask,request,render_template,redirect
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask import jsonify
from flask import request

import KG_test

app = Flask(__name__)
manager = Manager(app)
start_info = {}


def load_start_info():
    global start_info
    with open('starter_info.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            data = line.strip().split(':')
            k = data[0]
            v = data[1].split()
            start_info.update({k: v})


@app.route('/')
def index():
    return render_template('starter.html', info=start_info)


@app.route('/search/', methods=['POST'])
def search():
    """

    Argument:
        - keyword: customer's target word.

    Return:
        -info: info is str which your API return.

    """
    info = KG_test.db_fun(request.values['p'])
    return info


if __name__ == "__main__":
    load_start_info()
    print(start_info)
    manager.run()