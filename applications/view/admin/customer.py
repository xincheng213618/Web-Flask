
from applications.models import GridUser,RegisterInfo
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


customer = Blueprint('customer', __name__, url_prefix='/customer')

# 用户管理
@customer.get('/')
@authorize("admin:customer:main")
def main():
    return render_template('admin/customer/main.html')
@customer.get('/data')
@authorize("admin:customer:main")
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
@customer.get('/add')
@authorize("admin:customer:add")
def add():
    return render_template('admin/customer/add.html')
@customer.post('/save')
@authorize("admin:customer:add")
def save():
    req_json = request.json
    name = str_escape(req_json.get("name"))
    legal_address = str_escape(req_json.get('legal_address'))
    email_address = str_escape(req_json.get('email_address'))
    user = GridUser(name=name, legal_address=legal_address, email_address=email_address)
    db.session.add(user)
    db.session.commit()
    return success_api(msg="增加成功")


@customer.get('/edit/<int:id>')
@authorize("admin:customer:edit", log=True)
def edit(id):
    gridUser = curd.get_one_by_id(GridUser, id)
    return render_template('admin/customer/edit.html',customer = gridUser)
@customer.put('/update')
@authorize("admin:customer:edit", log=True)
def update():
    req_json = request.json
    id = request.json.get("userId")
    data = {
        "name": str_escape(req_json.get("name")),
        "contact_number": str_escape(req_json.get("contact_number")),
        "email_address": str_escape(req_json.get("email_address")),
        "legal_address": str_escape(req_json.get("legal_address")),
    }
    res = GridUser.query.filter_by(id=id).update(data)
    db.session.commit()
    if not res:
        return fail_api(msg="更新权限失败")
    return success_api(msg="更新权限成功")


@customer.get('/info/<int:id>')
@authorize("admin:customer:main")
def info(id):
    gridUser = curd.get_one_by_id(GridUser, id)
    customer={}
    customer['id'] =gridUser.id
    customer['name'] = gridUser.name
    customer['legal_address'] = gridUser.legal_address
    customer['email_address'] = gridUser.email_address
    customer['contact_number'] = gridUser.contact_number

    mf = ModelFilter()
    mf.exact('user_id',gridUser.id)

    res =RegisterInfo.query.filter_by(user_id=gridUser.id).all()

    customer['sninfo'] =model_to_dicts(schema=RegisterInfoOutSchema, data=res)
    return render_template('admin/customer/info.html',customer = customer)

# 删除用户
@customer.delete('/remove/<int:id>')
@authorize("admin:customer:remove")
def delete(id):
    res = GridUser.query.filter_by(id=id).delete()
    db.session.commit()
    if not res:
        return fail_api(msg="删除失败")
    return success_api(msg="删除成功")


@customer.delete('/batchRemove')
@authorize("admin:customer:remove")
def batch_remove():
    ids = request.form.getlist('ids[]')
    for id in ids:
        res = GridUser.query.filter_by(id=id).delete()
        db.session.commit()
    return success_api(msg="批量删除成功")

