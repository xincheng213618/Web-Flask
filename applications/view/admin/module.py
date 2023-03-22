from flask import Blueprint, request, render_template,jsonify,escape


module = Blueprint('module', __name__, url_prefix='/module')

# 用户管理
@module.get('/')
def main():
    return render_template('admin/module/main.html')
# 用户增加
@module.get('/add')
def add():
    return render_template('admin/module/add.html')




import pymysql
from util.sql import *
@module.get('/data')
def data():
    page = request.args.get('page', type=int)
    limit = request.args.get('limit', type=int)
    module_name =escape(request.args.get("module_name"))
    if not page:
        page = 1
    if not limit:
        limit = 10
    if not module_name or module_name=="None":
        module_name =""

    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT,
                         use_unicode=True)
    cursor = db.cursor()
    sql = "SELECT * FROM `grid`.`charging-module` WHERE name LIKE '%s' LIMIT  %s,%s" % (
    str("%" + module_name + "%"), limit * (page - 1), limit)
    print(sql)
    aa = cursor.execute(sql)

    res =cursor.fetchall()
    data = []
    for i in res:
        module={}
        module['id'] =i[0]
        module['name'] =i[1]
        module['code'] =i[2]
        module['download_address'] =i[3]
        module['renewal_type'] =i[4]
        data.append(module)

    sql ="SELECT COUNT(*) FROM `grid`.`charging-module`"
    cursor.execute(sql)
    count =cursor.fetchall()
    resu = {'code': 0, 'message': '', 'data': data, 'count': count[0][0], 'limit': limit}
    return jsonify(resu);

def str_escape(s):
    if not s:
        return None
    return str(escape(s))
@module.post('/save')
def save():
    req_json = request.json
    name = str_escape(req_json.get("name"))
    address = str_escape(req_json.get('address'))
    contact_number = str_escape(req_json.get('contact_number'))

    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT,
                         use_unicode=True)
    cursor = db.cursor()
    sql  ="INSERT INTO `grid`.`charging-module` (`name`, `address`, `contact_number`) VALUES ('%s', '%s', '%s')"%(name,address,contact_number)
    aa = cursor.execute(sql)
    db.commit()
    return jsonify(success=True, msg="增加成功")


@module.get('/edit/<int:id>')
def edit(id):
    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT,
                         use_unicode=True)
    cursor = db.cursor()
    sql  ="SELECT * FROM `grid`.`charging-module` where `id`= '%s'"%(id)
    aa = cursor.execute(sql)
    list =cursor.fetchall()
    module={}
    module['id'] = list[0][0]
    module['name'] = list[0][1]
    module['address'] = list[0][2]
    module['contact_number'] = list[0][3]

    return render_template('admin/module/edit.html',module = module)

@module.get('/info/<int:id>')
def info(id):
    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT,
                         use_unicode=True)
    cursor = db.cursor()
    sql  ="SELECT * FROM `grid`.`charging-module` where `id`= '%s'"%(id)
    aa = cursor.execute(sql)
    list =cursor.fetchall()
    module={}
    module['id'] = list[0][0]
    module['name'] = list[0][1]
    module['address'] = list[0][2]
    module['contact_number'] = list[0][3]


    sql  ="SELECT * FROM `grid`.`serial-number` where `module_id`= '%s'"%(id)
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
    module['sninfo'] =sninfo

    return render_template('admin/module/info.html',module = module)

@module.delete('/remove/<int:id>')
def delete(id):
    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT, use_unicode=True)
    cursor = db.cursor()
    sql = "DELETE FROM `grid`.`charging-module` WHERE `id` = %s" % (id)
    print(sql)
    aa = cursor.execute(sql)
    db.commit()
    if aa == 0:
        return jsonify(success=False, msg="删除失败")
    return jsonify(success=True, msg="删除成功")



# 批量删除
@module.delete('/batchRemove')
def batch_remove():
    ids = request.form.getlist('ids[]')
    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT, use_unicode=True)
    cursor = db.cursor()

    for id in ids:
        sql = "DELETE FROM `grid`.`charging-module` WHERE `id` = %s" % (id)
        aa = cursor.execute(sql)
        if (aa==0):
            return jsonify(success=False, msg="删除失败")
    db.commit()
    return jsonify(success=True, msg="删除成功")

