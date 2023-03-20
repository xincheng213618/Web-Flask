from flask import Blueprint, request, render_template,jsonify,escape


order = Blueprint('order', __name__, url_prefix='/order')

# 订单管理
@order.get('/')

def main():
    return render_template('admin/order/main.html')
# 用户增加
@order.get('/add')
def add():
    return render_template('admin/order/add.html')

import pymysql
from util.sql import *
@order.get('/data')
def data():
    page = request.args.get('page', type=int)
    limit = request.args.get('limit', type=int)
    order_name =escape(request.args.get("order_name"))
    if not page:
        page = 1
    if not limit:
        limit = 10
    if not order_name or order_name=="None":
        order_name =""

    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT,
                         use_unicode=True)
    cursor = db.cursor()
    # sql  ="SELECT * FROM `grid`.`order` WHERE name LIKE '%s' LIMIT  %s,%s"%(str("%"+order_name +"%"),limit*(page-1),limit)
    # print(sql)
    # aa = cursor.execute(sql)
    #
    # res =cursor.fetchall()
    res =[]
    data = []
    for i in res:
        order={}
        order['id'] =i[0]
        order['name'] =i[1]
        order['address'] =i[2]
        order['contact_number'] =i[3]
        data.append(order)

    sql ="SELECT COUNT(*) FROM `grid`.`order`"
    cursor.execute(sql)
    count =cursor.fetchall()

    resu = {'code': 0, 'message': '', 'data': data, 'count': count[0][0], 'limit': limit}
    return jsonify(resu);

def str_escape(s):
    if not s:
        return None
    return str(escape(s))
@order.post('/save')
def save():
    req_json = request.json
    name = str_escape(req_json.get("name"))
    address = str_escape(req_json.get('address'))
    contact_number = str_escape(req_json.get('contact_number'))

    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT,
                         use_unicode=True)
    cursor = db.cursor()
    sql  ="INSERT INTO `grid`.`order` (`name`, `address`, `contact_number`) VALUES ('%s', '%s', '%s')"%(name,address,contact_number)
    aa = cursor.execute(sql)
    db.commit()
    return jsonify(success=True, msg="增加成功")


@order.get('/edit/<int:id>')
def edit(id):
    # db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT,
    #                      use_unicode=True)
    # cursor = db.cursor()
    # sql  ="INSERT INTO `grid`.`order` (`name`, `address`, `contact_number`) VALUES ('%s', '%s', '%s')"%(name,address,contact_number)
    # aa = cursor.execute(sql)
    return render_template('admin/user/edit.html')


@order.delete('/remove/<int:id>')
def delete(id):
    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT, use_unicode=True)
    cursor = db.cursor()
    sql = "DELETE FROM `grid`.`order` WHERE `id` = %s" % (id)
    print(sql)
    aa = cursor.execute(sql)
    db.commit()
    if aa == 0:
        return jsonify(success=False, msg="删除失败")
    return jsonify(success=True, msg="删除成功")
#
# # 删除用户
# @order.delete('/remove/<int:id>')
# def delete(id):
#     res = Mail.query.filter_by(id=id).delete()
#     if not res:
#         return fail_api(msg="删除失败")
#     db.session.commit()
#     return success_api(msg="删除成功")
#
#
# # 批量删除
# @order.delete('/batchRemove')
# def batch_remove():
#     ids = request.form.getlist('ids[]')
#     for id in ids:
#         res = Mail.query.filter_by(id=id).delete()
#         if not res:
#             return fail_api(msg="批量删除失败")
#     db.session.commit()
#     return success_api(msg="批量删除成功")
#
