from flask import Blueprint, request, render_template,jsonify,escape


from applications.models import GridUser,RegisterInfo,Gridorder,GridSn,Gridregion,GridVendor
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
            'vendor': (lambda x: "无" if x is None else x.name)(curd.get_one_by_id(GridVendor, item.user_id)),
            'user': "未使用",
            'serial':(lambda x: "无" if x is None else x.sn)(curd.get_one_by_id(GridSn, item.serial_id)),
            'payment':str(item.payment) +"￥",
            'create_date': item.create_date.strftime( '%Y-%m-%d %H:%M:%S'),
        } for item in query],
        count=query.total)



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
