from flask import Blueprint, request, render_template,jsonify,escape


vendor = Blueprint('vendor', __name__, url_prefix='/vendor')

# 用户管理
@vendor.get('/')
def main():
    return render_template('admin/vendor/main.html')
# 用户增加
@vendor.get('/add')
def add():
    return render_template('admin/vendor/add.html')

import pymysql
from util.sql import *

@vendor.get('/data')
def data():
    page = request.args.get('page', type=int)
    limit = request.args.get('limit', type=int)
    vendor_name =escape(request.args.get("vendor_name"))
    if not page:
        page = 1
    if not limit:
        limit = 10
    if not vendor_name or vendor_name=="None":
        vendor_name =""

    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT,
                         use_unicode=True)
    cursor = db.cursor()
    sql = "SELECT * FROM `grid`.`vendor` WHERE name LIKE '%s' LIMIT  %s,%s" % (
    str("%" + vendor_name + "%"), limit * (page - 1), limit)
    print(sql)
    aa = cursor.execute(sql)

    res =cursor.fetchall()
    data = []
    for i in res:
        vendor={}
        vendor['id'] =i[0]
        vendor['name'] =i[1]
        vendor['address'] =i[2]
        vendor['contact_number'] =i[3]
        data.append(vendor)

    sql ="SELECT COUNT(*) FROM `grid`.`vendor`"
    cursor.execute(sql)
    count =cursor.fetchall()

    resu = {'code': 0, 'message': '', 'data': data, 'count': count[0][0], 'limit': limit}
    return jsonify(resu);

def str_escape(s):
    if not s:
        return None
    return str(escape(s))
@vendor.post('/save')
def save():
    req_json = request.json
    name = str_escape(req_json.get("name"))
    address = str_escape(req_json.get('address'))
    contact_number = str_escape(req_json.get('contact_number'))

    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT,
                         use_unicode=True)
    cursor = db.cursor()
    sql  ="INSERT INTO `grid`.`vendor` (`name`, `address`, `contact_number`) VALUES ('%s', '%s', '%s')"%(name,address,contact_number)
    aa = cursor.execute(sql)
    db.commit()
    return jsonify(success=True, msg="增加成功")


@vendor.get('/edit/<int:id>')
def edit(id):
    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT,
                         use_unicode=True)
    cursor = db.cursor()
    sql  ="SELECT * FROM `grid`.`vendor` where `id`= '%s'"%(id)
    aa = cursor.execute(sql)
    list =cursor.fetchall()
    vendor={}
    vendor['id'] = list[0][0]
    vendor['name'] = list[0][1]
    vendor['address'] = list[0][2]
    vendor['contact_number'] = list[0][3]

    return render_template('admin/vendor/edit.html',vendor = vendor)

@vendor.get('/info/<int:id>')
def info(id):
    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT,
                         use_unicode=True)
    cursor = db.cursor()
    sql  ="SELECT * FROM `grid`.`vendor` where `id`= '%s'"%(id)
    aa = cursor.execute(sql)
    list =cursor.fetchall()
    vendor={}
    vendor['id'] = list[0][0]
    vendor['name'] = list[0][1]
    vendor['address'] = list[0][2]
    vendor['contact_number'] = list[0][3]


    sql  ="SELECT * FROM `grid`.`serial-number` where `vendor_id`= '%s'"%(id)
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
    vendor['sninfo'] =sninfo

    return render_template('admin/vendor/info.html',vendor = vendor)

@vendor.delete('/remove/<int:id>')
def delete(id):
    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT, use_unicode=True)
    cursor = db.cursor()
    sql = "DELETE FROM `grid`.`vendor` WHERE `id` = %s" % (id)
    print(sql)
    aa = cursor.execute(sql)
    db.commit()
    if aa == 0:
        return jsonify(success=False, msg="删除失败")
    return jsonify(success=True, msg="删除成功")



# 批量删除
@vendor.delete('/batchRemove')
def batch_remove():
    ids = request.form.getlist('ids[]')
    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT, use_unicode=True)
    cursor = db.cursor()

    for id in ids:
        sql = "DELETE FROM `grid`.`vendor` WHERE `id` = %s" % (id)
        aa = cursor.execute(sql)
        if (aa==0):
            return jsonify(success=False, msg="删除失败")
    db.commit()
    return jsonify(success=True, msg="删除成功")

