from flask import Blueprint, request, render_template, jsonify, escape
import datetime
from applications.models import GridUser, RegisterInfo, GridVendor, Gridregion, GridSn,Gridmodule
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
from applications.schemas import GridUserOutSchema, RegisterInfoOutSchema, GridVendorOutSchema
from applications.common import curd

vendor = Blueprint('vendor', __name__, url_prefix='/vendor')


# 用户管理
@vendor.get('/')
@authorize("admin:vendor:mian")
def main():
    return render_template('admin/vendor/main.html')

@vendor.get('/data')
@authorize("admin:vendor:mian")
def data():
    # 获取请求参数
    name = str_escape(request.args.get("vendor_name", type=str))
    address = str_escape(request.args.get("address", type=str))
    contact_number = str_escape(request.args.get("contact_number", type=str))

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
            'id': vendor.id,
            'name': vendor.name,
            'address': vendor.address,
            'contact_number': vendor.contact_number,
            'create_date': vendor.create_date,
            'region': curd.get_one_by_id(Gridregion, vendor.region_id).name
        } for vendor in query],
        count=query.total)


@vendor.get('/add')
@authorize("admin:vendor:add")
def add():
    query = Gridregion.query.filter().all()
    regions = [{
        'id': item.id,
        'title': item.name,
    } for item in query]
    return render_template('admin/vendor/add.html', regions=regions)


@vendor.post('/save')
@authorize("admin:vendor:add")
def save():
    req_json = request.json
    name = str_escape(req_json.get("name"))
    address = str_escape(req_json.get('address'))
    contact_number = str_escape(req_json.get('contact_number'))
    region_id = req_json.get('region_id')

    item = GridVendor(name=name, address=address, contact_number=contact_number, region_id=region_id)
    db.session.add(item)
    db.session.commit()
    return success_api(msg="增加成功")


@vendor.get('/edit/<int:id>')
@authorize("admin:vendor:edit")
def edit(id):
    item = curd.get_one_by_id(GridVendor, id)
    query = Gridregion.query.filter().all()
    regions = [{
        'id': item.id,
        'title': item.name,
    } for item in query]

    return render_template('admin/vendor/edit.html', vendor=item,regions=regions)

@vendor.put('/update')
@authorize("admin:vendor:edit", log=True)
def update():
    req_json = request.json
    id = str_escape(req_json.get("id"))
    name = str_escape(req_json.get('name'))
    contact_number = str_escape(req_json.get('contact_number'))
    address = str_escape(req_json.get('address'))
    GridVendor.query.filter_by(id=id).update(
        {'name': name, 'contact_number': contact_number, 'address': address})
    db.session.commit()
    return success_api(msg="更新成功")

@vendor.get('/info/<int:id>')
@authorize("admin:vendor:main")
def info(id):
    item = curd.get_one_by_id(GridVendor, id)
    vendor = {}
    vendor['id'] = item.id
    vendor['name'] = item.name
    vendor['address'] = item.address
    vendor['contact_number'] = item.contact_number
    vendor['region'] = curd.get_one_by_id(Gridregion, item.region_id).name

    query = GridSn.query.filter_by(vendor_id=item.id).all()

    vendor['sninfo'] = [{
            'id': item.id,
            'sn': item.sn,
            'vendor': curd.get_one_by_id(GridVendor, item.vendor_id).name,
            'moudle': curd.get_one_by_id(Gridmodule, item.module_id).name,
            'effect_months': item.effect_months,
            'create_date': item.create_date,
        } for item in query]

    query = Gridregion.query.filter().all()

    regions = [{
        'id': item.id,
        'title': item.name,
    } for item in query]
    return render_template('admin/vendor/info.html', vendor=vendor,regions =regions)


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
