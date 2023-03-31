from main import *
import pymysql
import time

from flask import Blueprint, request, render_template, jsonify, escape
from applications.models import GridUser, RegisterInfo, GridVendor, Gridregion, GridSn,Gridmodule,Gridorder
from flask import Blueprint, render_template, request, current_app,redirect
from flask_login import current_user
from flask_mail import Message
from applications.common.curd import model_to_dicts
from applications.common.helper import ModelFilter
from applications.common.utils.http import table_api, fail_api, success_api
from applications.common.utils.rights import authorize
from applications.common.utils.validate import str_escape
from applications.extensions import db, flask_mail
from applications.models import Mail
from applications.schemas import GridUserOutSchema, RegisterInfoOutSchema, GridVendorOutSchema
from applications.common import curd


@app.route('/generateSNCode', methods=['get'])
def generateSNCode():
    query = Gridmodule.query.filter().all()
    modules = [{
        'id': item.id,
        'title': item.name,
    } for item in query]

    query = GridVendor.query.filter().all()
    vendors = [{
        'id': item.id,
        'title': item.name,
    } for item in query]


    return render_template("generateSNCode.html",vendors =vendors,modules=modules)


from werkzeug.routing import BaseConverter
class RegexConverter(BaseConverter):
    def __init__(self, url_map, *args):
        super(RegexConverter, self).__init__(url_map)
        self.url = url_map
        self.regex = args[0]   # 正则的匹配规则

    def to_python(self, value):
        return value
app.url_map.converters['reg'] = RegexConverter   # 注册url转换类
@app.route('/email_captcha_Vaild/<reg(".*?"):captcha>', methods=['get'])
def email_captcha_Vaild1(captcha):
    print(captcha)
    email = request.args.get('email')
    if not email:
        resu = {'code': 1, 'message':"请输入email"}
        return jsonify(resu)
    if captcha == util.redistaic.GetValue(email):
        resu = {'code': 0, 'message':"验证通过"}
        return jsonify(resu)
    else:
        resu = {'code': 1, 'message':"您输入的验证码有误"}
        return jsonify(resu)

@app.route('/email_captcha_Vaild', methods=['post'])
def email_captcha_Vaild():
    email = request.values.get('email')
    captcha = request.values.get('captcha')
    if captcha == util.redistaic.GetValue(email):
        resu = {'code': 0, 'message':"验证通过"}
        return jsonify(resu)
    else:
        resu = {'code': 1, 'message':"您输入的验证码有误"}
        return jsonify(resu)





@app.route('/getModule', methods=['get'])
def GetModule():
    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT, use_unicode=True)
    cursor = db.cursor()
    sql = "SELECT `name`,`code` FROM `grid`.`charging-module`"
    num = cursor.execute(sql)
    module = cursor.fetchall()
    modulelist = []
    for row in module:
        modulelist.append(row[0]);
    resu = {'state': 0, 'message': '', 'list': modulelist}
    return jsonify(resu)
import random, string

@app.route("/GeneraSNCode", methods=['post'])
def GeneraSNCode():
    vendor_id = request.values.get('vendor_id')
    module_id = request.values.get('module_id')
    if not vendor_id or not module_id:
        resu = {'state': 1, 'message': '参数不能存在空值'}
        return jsonify(resu)

    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT,
                         use_unicode=True)
    cursor = db.cursor()


    sn = ''.join(random.sample(string.ascii_letters + string.digits, 24)).upper()
    expire_date = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime("2050-01-01", "%Y-%m-%d"))
    create_date =time.strftime("%Y-%m-%d %H:%M:%S", time.localtime());
    sql = "INSERT INTO `grid`.`serial-number` (`sn`, `vendor_id`, `module_id`, `effect_months`,`create_date` ) VALUES ('%s', %s, %s, '%s','%s')" % (
    sn, vendor_id, module_id,expire_date,create_date );
    print(sql)
    num = cursor.execute(sql);
    db.commit()
    print(sn)
    pattern = re.compile('.{6}')
    sn = '-'.join(pattern.findall(sn))

    resu = {'state': 0, 'message': '', 'sn': sn}
    return jsonify(resu)


@app.route('/addSNCode', methods=['post'])
def addSNCode():
    sn = request.values.get('sn')
    print(sn)
    if not sn:
        resu = {'state': 1, 'message': '参数不能存在空值'}
        return jsonify(resu)
    if not checkSN(sn):
        resu = {'state': 1, 'message': '序列号参数异常'}
        return jsonify(resu)
    sn = sn.strip().replace("-", "")
    try:
        db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT,
                             use_unicode=True)
        cursor = db.cursor()
        create_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        sql = "INSERT INTO `grid`.`serial-number` (`sn`, `vendor_id`, `module_id`, `effect_months`, `create_date`) VALUES ('%s', %s, %s,'%s', '%s')" % (
        sn, 11, 11, create_date, create_date)
        print(sql)
        aa = cursor.execute(sql)
        db.commit()
        print(aa)
        if (aa == 0):
            resu = {'state': 0, 'message': '注册成功'}
            return jsonify(resu)  # 将字典转换为json串, json是字符串
        resu = {'state': 0, 'message': '注册成功'}
    except Exception:
        resu = {'state': 1, 'message': "数据库连接失败"}
    return jsonify(resu)  # 将字典转换为json串, json是字符串

