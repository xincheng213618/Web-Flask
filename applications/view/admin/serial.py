from flask import Blueprint, request, render_template,jsonify,escape


serial = Blueprint('serial', __name__, url_prefix='/serial')

# 用户管理
@serial.get('/')
def main():
    return render_template('admin/serial/main.html')
# 用户增加
@serial.get('/add')
def add():
    return render_template('admin/serial/add.html')

import pymysql
from util.sql import *

@serial.get('/data')
def data():
    page = request.args.get('page', type=int)
    limit = request.args.get('limit', type=int)
    serial_name =escape(request.args.get("serial_name"))
    if not page:
        page = 1
    if not limit:
        limit = 10
    if not serial_name or serial_name=="None":
        serial_name =""

    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT,
                         use_unicode=True)
    cursor = db.cursor()
    sql = "SELECT * FROM `grid`.`serial-number` WHERE sn LIKE '%s' LIMIT  %s,%s" % (
    str("%" + serial_name + "%"), limit * (page - 1), limit)
    print(sql)
    aa = cursor.execute(sql)
    res =cursor.fetchall()
    data = []
    for i in res:
        serial={}
        serial['id'] =i[0]
        serial['sn'] =i[1]
        serial['vendor'] ="代理商A"
        serial['moudle'] ="基础版"
        data.append(serial)

    resu = {'code': 0, 'message': '', 'data': data, 'count': aa, 'limit': limit}
    return jsonify(resu);

def str_escape(s):
    if not s:
        return None
    return str(escape(s))
@serial.post('/save')
def save():
    req_json = request.json
    name = str_escape(req_json.get("name"))
    address = str_escape(req_json.get('address'))
    contact_number = str_escape(req_json.get('contact_number'))

    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT,
                         use_unicode=True)
    cursor = db.cursor()
    sql  ="INSERT INTO `grid`.`serial` (`name`, `address`, `contact_number`) VALUES ('%s', '%s', '%s')"%(name,address,contact_number)
    aa = cursor.execute(sql)
    db.commit()
    return jsonify(success=True, msg="增加成功")


@serial.get('/edit/<int:id>')
def edit(id):
    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT,
                         use_unicode=True)
    cursor = db.cursor()
    sql  ="SELECT * FROM `grid`.`serial` where `id`= '%s'"%(id)
    aa = cursor.execute(sql)
    list =cursor.fetchall()
    serial={}
    serial['id'] = list[0][0]
    serial['name'] = list[0][1]
    serial['address'] = list[0][2]
    serial['contact_number'] = list[0][3]

    return render_template('admin/serial/edit.html',serial = serial)

@serial.get('/info/<int:id>')
def info(id):
    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT,
                         use_unicode=True)
    cursor = db.cursor()
    sql  ="SELECT * FROM `grid`.`serial` where `id`= '%s'"%(id)
    aa = cursor.execute(sql)
    list =cursor.fetchall()
    serial={}
    serial['id'] = list[0][0]
    serial['name'] = list[0][1]
    serial['address'] = list[0][2]
    serial['contact_number'] = list[0][3]


    sql  ="SELECT * FROM `grid`.`serial-number` where `serial_id`= '%s'"%(id)
    aa = cursor.execute(sql)
    lists =cursor.fetchall()
    sninfo =[]
    for list in lists:
        sn = {}
        sn['id'] = list[0]
        sn['sn'] = list[1]
        sn['module_id'] = list[3]
        sn['effect_months'] = list[1]
        sn['create_date'] = list[4]
        sninfo.append(sn)
    serial['sninfo'] =sninfo

    return render_template('admin/serial/info.html',serial = serial)

@serial.delete('/remove/<int:id>')
def delete(id):
    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT, use_unicode=True)
    cursor = db.cursor()
    sql = "DELETE FROM `grid`.`serial` WHERE `id` = %s" % (id)
    print(sql)
    aa = cursor.execute(sql)
    db.commit()
    if aa == 0:
        return jsonify(success=False, msg="删除失败")
    return jsonify(success=True, msg="删除成功")



# 批量删除
@serial.delete('/batchRemove')
def batch_remove():
    ids = request.form.getlist('ids[]')
    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT, use_unicode=True)
    cursor = db.cursor()

    for id in ids:
        sql = "DELETE FROM `grid`.`serial` WHERE `id` = %s" % (id)
        aa = cursor.execute(sql)
        if (aa==0):
            return jsonify(success=False, msg="删除失败")
    db.commit()
    return jsonify(success=True, msg="删除成功")

