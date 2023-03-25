from flask import Blueprint, request, render_template,jsonify,escape

from applications.models import GridUser,RegisterInfo,GridVendor
from flask import Blueprint, render_template, request, current_app
from flask_login import current_user
from flask_mail import Message
from applications.common.curd import model_to_dicts
from applications.common.helper import ModelFilter
from applications.common.utils.http import table_api, fail_api, success_api
from applications.common.utils.rights import authorize
from applications.common.utils.validate import str_escape
from applications.extensions import db, flask_mail
from applications.models import Mail
from applications.schemas import GridUserOutSchema,RegisterInfoOutSchema,GridVendorOutSchema
from applications.common import curd

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
    # 获取请求参数
    name =str_escape(request.args.get("vendor_name", type=str))
    address =str_escape(request.args.get("address", type=str))
    contact_number =str_escape(request.args.get("contact_number", type=str))

    mf = ModelFilter()
    if name:
        mf.contains(field_name="name", value=name)
    if address:
        mf.contains(field_name="address", value=address)
    if contact_number:
        mf.contains(field_name="contact_number", value=contact_number)

    # orm查询
    # 使用分页获取data需要.items
    query = GridVendor.query.filter(mf.get_filter(GridVendor)).layui_paginate()
    count = query.total
    # "普通用户" if i[5] == 0 else "高级用户" if i[5] == 1 else "钻石用户"
    return table_api(
        data=[{
            'id': user.id,
            'name': user.name,
            'address': user.address,
            'contact_number': user.contact_number,
            'create_date': user.create_date
        } for user in query],
        count=query.total)
    return table_api(data=model_to_dicts(schema=GridUserOutSchema, data=mail.items), count=count)



@vendor.post('/save')
def save():
    req_json = request.json
    name = str_escape(req_json.get("name"))
    address = str_escape(req_json.get('address'))
    contact_number = str_escape(req_json.get('contact_number'))
    item = GridVendor(name=name, address=address, contact_number=contact_number)
    db.session.add(item)
    db.session.commit()
    return success_api(msg="增加成功")



@vendor.get('/edit/<int:id>')
def edit(id):
    item = curd.get_one_by_id(GridVendor, id)
    return render_template('admin/module/edit.html',vendor = item)

@vendor.get('/info/<int:id>')
def info(id):
    vendor = curd.get_one_by_id(GridVendor, id)
    vendor={}
    vendor['id'] =vendor.id
    vendor['name'] = vendor.name
    vendor['address'] = vendor.address
    vendor['contact_number'] = vendor.contact_number

    res =RegisterInfo.query.filter_by(vendor_id=vendor.id).all()

    vendor['sninfo'] =model_to_dicts(schema=RegisterInfoOutSchema, data=res)
    return render_template('admin/module/info.html',vendor = vendor)



@vendor.delete('/remove/<int:id>')
@authorize("admin:vendor:remove")
def delete(id):
    res = GridVendor.query.filter_by(id=id).delete()
    db.session.commit()
    if not res:
        return fail_api(msg="删除失败")
    return success_api(msg="删除成功")


@vendor.delete('/batchRemove')
@authorize("admin:vendor:remove")
def batch_remove():
    ids = request.form.getlist('ids[]')
    for id in ids:
        res = GridVendor.query.filter_by(id=id).delete()
        db.session.commit()
    return success_api(msg="批量删除成功")


