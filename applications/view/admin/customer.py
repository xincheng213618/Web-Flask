from flask import Blueprint, request, render_template,jsonify,escape


customer = Blueprint('customer', __name__, url_prefix='/customer')

# 用户管理
@customer.get('/')

def main():
    return render_template('admin/customer/main.html')
# 用户增加
@customer.get('/add')
def add():
    return render_template('admin/customer/add.html')

import pymysql
from util.sql import *
@customer.get('/data')
def data():
    page = request.args.get('page', type=int)
    limit = request.args.get('limit', type=int)
    customer_name =escape(request.args.get("customer_name"))
    if not page:
        page = 1
    if not limit:
        limit = 10
    if not customer_name or customer_name=="None":
        customer_name =""

    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT,
                         use_unicode=True)
    cursor = db.cursor()
    sql  ="SELECT * FROM `grid`.`user` WHERE name LIKE '%s' LIMIT  %s,%s"%(str("%"+customer_name +"%"),limit*(page-1),limit)
    print(sql)
    aa = cursor.execute(sql)

    res =cursor.fetchall()
    data = []
    for i in res:
        customer={}
        customer['id'] =i[0]
        customer['name'] =i[1]
        customer['legal_address'] =i[2]
        customer['email_address'] =i[3]
        customer['contact_number'] =i[4]
        customer['user_class'] = "普通用户" if i[5]==0 else "高级用户" if i[5]==1 else  "钻石"

        data.append(customer)

    sql ="SELECT COUNT(*) FROM `grid`.`user`"
    cursor.execute(sql)
    count =cursor.fetchall()

    resu = {'code': 0, 'message': '', 'data': data, 'count': count[0][0], 'limit': limit}
    return jsonify(resu);

def str_escape(s):
    if not s:
        return None
    return str(escape(s))
@customer.post('/save')
def save():
    req_json = request.json
    name = str_escape(req_json.get("name"))
    address = str_escape(req_json.get('address'))
    contact_number = str_escape(req_json.get('contact_number'))

    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT,
                         use_unicode=True)
    cursor = db.cursor()
    sql  ="INSERT INTO `grid`.`customer` (`name`, `address`, `contact_number`) VALUES ('%s', '%s', '%s')"%(name,address,contact_number)
    aa = cursor.execute(sql)
    db.commit()
    return jsonify(success=True, msg="增加成功")


@customer.get('/edit/<int:id>')
def edit(id):
    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT,
                         use_unicode=True)
    cursor = db.cursor()
    sql  ="SELECT * FROM `grid`.`user` where `id`= '%s'"%(id)
    aa = cursor.execute(sql)
    list =cursor.fetchall()
    customer={}
    customer['id'] = list[0][0]
    customer['name'] = list[0][1]
    customer['legal_address'] = list[0][2]
    customer['email_address'] = list[0][3]
    customer['contact_number'] = list[0][3]
    return render_template('admin/customer/edit.html',customer = customer)


@customer.get('/info/<int:id>')
def info(id):
    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT,
                         use_unicode=True)
    cursor = db.cursor()
    sql  ="SELECT * FROM `grid`.`user` where `id`= '%s'"%(id)
    aa = cursor.execute(sql)
    list =cursor.fetchall()
    customer={}
    customer['id'] = list[0][0]
    customer['name'] = list[0][1]
    customer['legal_address'] = list[0][2]
    customer['email_address'] = list[0][3]
    customer['contact_number'] = list[0][3]

    sql  ="SELECT * FROM `grid`.`register-info` where `user_id`= '%s'"%(id)
    aa = cursor.execute(sql)
    lists =cursor.fetchall()
    sninfo =[]
    for list in lists:
        sn = {}
        sn['mac'] = list[3]
        sn['sn'] = list[4]
        sn['create_date'] = list[5]
        sninfo.append(sn)
    customer['sninfo'] =sninfo

    return render_template('admin/customer/info.html',customer = customer)

# 删除用户
@customer.delete('/remove/<int:id>')
def delete(id):
    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT, use_unicode=True)
    cursor = db.cursor()
    sql = "DELETE FROM `grid`.`user` WHERE `id` = %s" % (id)
    print(sql)
    aa = cursor.execute(sql)
    db.commit()
    if aa == 0:
        return jsonify(success=False, msg="删除失败")
    return jsonify(success=True, msg="删除成功")


@customer.delete('/batchRemove')
def batch_remove():
    ids = request.form.getlist('ids[]')
    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT, use_unicode=True)
    cursor = db.cursor()

    for id in ids:
        sql = "DELETE FROM `grid`.`user` WHERE `id` = %s" % (id)
        aa = cursor.execute(sql)
        if (aa==0):
            return jsonify(success=False, msg="删除失败")
    db.commit()
    return jsonify(success=True, msg="删除成功")

