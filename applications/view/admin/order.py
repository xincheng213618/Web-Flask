from flask import Blueprint, request, render_template,jsonify,escape


from applications.models import GridUser,RegisterInfo,Gridorder
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
    legal_address =str_escape(request.args.get("legal_address", type=str))
    email_address =str_escape(request.args.get("email_address", type=str))
    contact_number=str_escape(request.args.get("contact_number", type=str))
    user_class =str_escape(request.args.get("user_class", type=int))

    mf = ModelFilter()
    if name:
        mf.contains(field_name="name", value=name)
    if legal_address:
        mf.contains(field_name="legal_address", value=legal_address)
    if email_address:
        mf.contains(field_name="email_address", value=email_address)
    if contact_number:
        mf.contains(field_name="contact_number", value=contact_number)
    if user_class:
        mf.exact(field_name="user_class", value=user_class)
    # orm查询
    # 使用分页获取data需要.items
    query = GridUser.query.filter(mf.get_filter(GridUser)).layui_paginate()
    count = query.total
    # "普通用户" if i[5] == 0 else "高级用户" if i[5] == 1 else "钻石用户"
    return table_api(
        data=[{
            'id': user.id,
            'name': user.name,
            'legal_address': user.legal_address,
            'email_address': user.email_address,
            'contact_number': user.contact_number,
            'user_class': "普通用户" if user.user_class  == 0 else "高级用户" if user.user_class == 1 else "钻石用户",
            'create_date': user.create_date,
        } for user in query],
        count=query.total)
    # 返回api
    return table_api(data=model_to_dicts(schema=GridUserOutSchema, data=mail.items), count=count)


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
