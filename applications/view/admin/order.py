from flask import Blueprint, request, render_template,jsonify,escape


from applications.models import GridUser,RegisterInfo,Gridorder,GridSn
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
order = Blueprint('order', __name__, url_prefix='/order')

# 订单管理
@order.get('/')
@authorize("admin:order:main")
def main():
    return render_template('admin/order/main.html')
# 用户增加


@order.get('/data')
@authorize("admin:order:main")
def data():
    # 获取请求参数
    name =str_escape(request.args.get("customer_name", type=str))
    mf = ModelFilter()
    if name:
        mf.contains(field_name="name", value=name)

    query = Gridorder.query.filter(mf.get_filter(Gridorder)).layui_paginate()
    return table_api(
        data=[{
            'id': item.id,
            'user': curd.get_one_by_id(GridUser, item.user_id).name,
            'serial': curd.get_one_by_id(GridSn, item.serial_id).sn,
            'create_date': item.create_date,
        } for item in query],
        count=query.total)


@order.get('/add')
@authorize("admin:order:add")
def add():
    return render_template('admin/order/add.html')
@order.post('/save')
@authorize("admin:order:add")
def save():
    req_json = request.json
    user_id = str_escape(req_json.get("user_id"))
    serial_id = str_escape(req_json.get('serial_id'))
    payment = str_escape(req_json.get('payment'))
    effect_date = str_escape(req_json.get('effect_date'))
    expire_date = str_escape(req_json.get('expire_date'))

    item = Gridorder(user_id=user_id, serial_id=serial_id, payment=payment,effect_date =effect_date,expire_date =expire_date)
    db.session.add(item)
    db.session.commit()
    return success_api(msg="增加成功")

@order.get('/edit/<int:id>')
@authorize("admin:order:edit")
def edit(id):
    item = curd.get_one_by_id(Gridorder, id)
    return render_template('admin/module/edit.html',order = item)



#
@order.delete('/remove/<int:id>')
@authorize("admin:order:remove")
def delete(id):
    res = Gridorder.query.filter_by(id=id).delete()
    db.session.commit()
    if not res:
        return fail_api(msg="删除失败")
    return success_api(msg="删除成功")


@order.delete('/batchRemove')
@authorize("admin:vendor:remove")
def batch_remove():
    ids = request.form.getlist('ids[]')
    for id in ids:
        res = Gridorder.query.filter_by(id=id).delete()
        db.session.commit()
    return success_api(msg="批量删除成功")
