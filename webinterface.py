from main import *
import pymysql
import time

from flask import Blueprint, request, render_template, jsonify, escape, send_from_directory
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
from applications.extensions import db

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


import random, string
@app.route("/GeneraSNCode", methods=['post'])
def GeneraSNCode():
    vendor_id = request.values.get('vendor_id')
    module_id = request.values.get('module_id')
    if not vendor_id or not module_id:
        resu = {'state': 1, 'message': '参数不能存在空值'}
        return jsonify(resu)


    sn = ''.join(random.sample(string.ascii_letters + string.digits, 24)).upper()
    print("生成序列号" +sn)
    expire_date = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime("2050-01-01", "%Y-%m-%d"))
    create_date =time.strftime("%Y-%m-%d %H:%M:%S", time.localtime());

    item = GridSn(sn=sn,vendor_id =vendor_id,module_id= module_id,effect_months =expire_date,create_date =create_date)
    db.session.add(item)
    db.session.commit()
    serial =GridSn.query.filter_by(sn=sn).first()
    item = Gridorder(user_id=vendor_id, serial_id=serial.id, payment=0, effect_date=expire_date, expire_date=expire_date)
    db.session.add(item)
    db.session.commit()

    resu = {'state': 0, 'message': '', 'sn': '-'.join(re.compile('.{6}').findall(sn))}
    return jsonify(resu)


