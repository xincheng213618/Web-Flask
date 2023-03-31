from flask import Blueprint, request, render_template,jsonify,escape

from applications.models import GridUser,RegisterInfo,Gridregion
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
from applications.schemas import GridUserOutSchema,RegisterInfoOutSchema
from applications.common import curd

region = Blueprint('region', __name__, url_prefix='/region')

@region.get('/data')
def data():
    # 获取请求参数
    name =str_escape(request.args.get("region_name", type=str))
    mf = ModelFilter()
    if name:
        mf.contains(field_name="name", value=name)

    # orm查询
    # 使用分页获取data需要.items
    query = Gridregion.query.filter(mf.get_filter(Gridregion)).layui_paginate()

    return table_api(
        data=[{
            'id ': item.id,
            'name': item.name,
        } for item in query],
        count=query.total)
@region.get('/add')
@authorize("admin:region:add")
def add():
    return render_template('admin/region/add.html')

@region.post('/save')
@authorize("admin:region:add")
def save():
    req_json = request.json
    name = str_escape(req_json.get("name"))
    address = str_escape(req_json.get('address'))
    contact_number = str_escape(req_json.get('contact_number'))
    item = Gridregion(name=name, address=address, contact_number=contact_number)
    db.session.add(item)
    db.session.commit()
    return success_api(msg="增加成功")

@region.get('/edit/<int:id>')
@authorize("admin:region:edit")
def edit(id):
    item = curd.get_one_by_id(Gridregion, id)
    return render_template('admin/module/edit.html',region = item)

@region.get('/info/<int:id>')
@authorize("admin:region:main")
def info(id):
    region = curd.get_one_by_id(Gridregion, id)
    region={}
    region['id'] =region.id
    region['name'] = region.name
    region['address'] = region.address
    region['contact_number'] = region.contact_number

    res =RegisterInfo.query.filter_by(region_id=region.id).all()

    region['sninfo'] =model_to_dicts(schema=RegisterInfoOutSchema, data=res)
    return render_template('admin/module/info.html',region = region)



@region.delete('/remove/<int:id>')
@authorize("admin:region:remove")
def delete(id):
    res = Gridregion.query.filter_by(id=id).delete()
    db.session.commit()
    if not res:
        return fail_api(msg="删除失败")
    return success_api(msg="删除成功")


@region.delete('/batchRemove')
@authorize("admin:region:remove")
def batch_remove():
    ids = request.form.getlist('ids[]')
    for id in ids:
        res = Gridregion.query.filter_by(id=id).delete()
        db.session.commit()
    return success_api(msg="批量删除成功")


