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
from applications.models import  GridSn,Gridmodule,GridVendor

serial = Blueprint('serial', __name__, url_prefix='/serial')

# 用户管理
@serial.get('/')
@authorize("admin:serial:main")
def main():
    return render_template('admin/serial/main.html')
# 用户增加

@serial.get('/data')
@authorize("admin:serial:main")
def data():
    # 获取请求参数
    sn =str_escape(request.args.get("serial_name", type=str))
    module_name =str_escape(request.args.get("module_name", type=str))
    vendor_name =str_escape(request.args.get("vendor_name", type=str))
    mf = ModelFilter()
    if sn:
        sn= sn.strip().replace("-", "")
        mf.contains(field_name="name", value=sn)
    if module_name:
        mf.contains(field_name="module_name", value=module_name)
    if vendor_name:
        mf.contains(field_name="module_name", value=vendor_name)
    # orm查询
    # 使用分页获取data需要.items
    query = GridSn.query.filter(mf.get_filter(GridSn)).layui_paginate()
    count = query.total
    # "普通用户" if i[5] == 0 else "高级用户" if i[5] == 1 else "钻石用户"
    return table_api(
        data=[{
            'id': item.id,
            'sn': item.sn,
            'vendor': curd.get_one_by_id(GridVendor, item.vendor_id).name,
            'moudle': curd.get_one_by_id(Gridmodule, item.module_id).name,
            'effect_months': item.effect_months,
            'create_date': item.create_date,
        } for item in query],
        count=query.total)

@serial.get('/add')
@authorize("admin:serial:add")
def add():
    return render_template('admin/serial/add.html')
@serial.post('/save')
@authorize("admin:serial:add")
def save():
    req_json = request.json
    sn = str_escape(req_json.get("sn"))
    module_name = str_escape(req_json.get('module_name'))
    vendor_name = str_escape(req_json.get('vendor_name'))
    item = GridSn(sn=sn, module_name=module_name, vendor_name=vendor_name)
    db.session.add(item)
    db.session.commit()
    return success_api(msg="增加成功")

@serial.get('/edit/<int:id>')
@authorize("admin:serial:edit")
def edit(id):
    item = curd.get_one_by_id(GridSn, id)
    return render_template('admin/serial/edit.html',serial = item)




@serial.get('/info/<int:id>')
@authorize("admin:serial:main")
def info(id):
    return render_template('admin/serial/info.html')

@serial.delete('/remove/<int:id>')
@authorize("admin:serial:remove")
def delete(id):
    res = GridSn.query.filter_by(id=id).delete()
    db.session.commit()
    if not res:
        return fail_api(msg="删除失败")
    return success_api(msg="删除成功")



# 批量删除
@serial.delete('/batchRemove')
@authorize("admin:serial:remove")
def batch_remove():
    ids = request.form.getlist('ids[]')
    for id in ids:
        res = GridSn.query.filter_by(id=id).delete()
        db.session.commit()
    return success_api(msg="批量删除成功")

