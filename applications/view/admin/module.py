from flask import Blueprint, request, render_template,jsonify
from applications.models import Gridmodule,RegisterInfo
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

module = Blueprint('module', __name__, url_prefix='/module')

# 用户管理
@module.get('/')
@authorize("admin:module:main")
def main():
    return render_template('admin/module/main.html')


@module.get('/data')
@authorize("admin:module:main")
def data():
    # 获取请求参数
    name =str_escape(request.args.get("module_name", type=str))
    code =str_escape(request.args.get("code", type=str))
    download_address =str_escape(request.args.get("download_address", type=str))
    renewal_type=str_escape(request.args.get("renewal_type", type=str))
    user_class =str_escape(request.args.get("user_class", type=int))


    mf = ModelFilter()
    if name:
        mf.contains(field_name="name", value=name)
    if code:
        mf.contains(field_name="code", value=code)
    if download_address:
        mf.contains(field_name="download_address", value=download_address)
    if renewal_type:
        mf.exact(field_name="renewal_type", value=renewal_type)
    # orm查询
    # 使用分页获取data需要.items
    query = Gridmodule.query.filter(mf.get_filter(Gridmodule)).layui_paginate()
    count = query.total
    # "普通用户" if i[5] == 0 else "高级用户" if i[5] == 1 else "钻石用户"
    return table_api(
        data=[{
            'id': item.id,
            'name': item.name,
            'code': item.code,
            'download_address': item.download_address,
            'renewal_type':  "无" if item.renewal_type  == 0 else "月" if item.renewal_type == 1 else "季" if item.renewal_type == 2 else "年",
            'create_date': item.create_date,
        } for item in query],
        count=query.total)
    # 返回api
    return table_api(data=model_to_dicts(schema=GridmoduleOutSchema, data=mail.items), count=count)
@module.get('/add')
@authorize("admin:module:add")
def add():
    return render_template('admin/module/add.html')

@module.post('/save')
@authorize("admin:module:add")
def save():
    req_json = request.json
    name = str_escape(req_json.get("name"))
    code = str_escape(req_json.get('code'))
    download_address = str_escape(req_json.get('download_address'))
    renewal_type = str_escape(req_json.get('renewal_type'))
    moudle = Gridmodule(name=name, code=code, download_address=download_address,renewal_type =0)
    db.session.add(moudle)
    db.session.commit()
    return success_api(msg="增加成功")


@module.get('/edit/<int:id>')
@authorize("admin:module:edit")
def edit(id):
    gridmodule = curd.get_one_by_id(Gridmodule, id)
    return render_template('admin/module/edit.html',module = gridmodule)


@module.get('/info/<int:id>')
@authorize("admin:module:main")
def info(id):
    module = curd.get_one_by_id(Gridmodule, id)
    module={}
    module['id'] =module.id
    module['name'] = module.name
    module['code'] = module.code
    module['download_address'] = module.download_address
    module['renewal_type'] = module.renewal_type
    module['create_date'] = module.create_date

    mf = ModelFilter()
    mf.exact('user_id',module.id)

    res =RegisterInfo.query.filter_by(module_id=module.id).all()

    module['sninfo'] =model_to_dicts(schema=RegisterInfoOutSchema, data=res)
    return render_template('admin/module/info.html',module = module)

# 删除用户
@module.delete('/remove/<int:id>')
@authorize("admin:module:remove")
def delete(id):
    res = Gridmodule.query.filter_by(id=id).delete()
    db.session.commit()
    if not res:
        return fail_api(msg="删除失败")
    return success_api(msg="删除成功")


@module.delete('/batchRemove')
@authorize("admin:module:remove")
def batch_remove():
    ids = request.form.getlist('ids[]')
    for id in ids:
        res = Gridmodule.query.filter_by(id=id).delete()
        db.session.commit()
    return success_api(msg="批量删除成功")





