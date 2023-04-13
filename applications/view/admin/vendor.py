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

import  datetime
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

import re
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

    pattern = re.compile('.{6}')
    vendor['sninfo'] = [{
            'id': item.id,
            'sn': '-'.join(pattern.findall(item.sn)),
            'vendor': curd.get_one_by_id(GridVendor, item.vendor_id).name,
            'moudle': curd.get_one_by_id(Gridmodule, item.module_id).name,
            'effect_months': item.effect_months.strftime( '%Y-%m-%d %H:%M:%S') ,
            'create_date': item.create_date.strftime( '%Y-%m-%d %H:%M:%S') ,
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



import os
from flask import Flask, Response,make_response

from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from urllib.parse import quote
import time
import numpy as np
import codecs
from applications.common.utils import mail

from flask_apscheduler import APScheduler
from applications.extensions.init_apscheduler import scheduler

from main import app
from sqlalchemy import create_engine

@scheduler.task('interval', id='11444445', seconds=30)
def Sendstatistics():
    id =1
    with app.app_context():
        db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT, use_unicode=True)
        cursor = db.cursor()
        sql = "SELECT `serial-number`.vendor_id, COUNT( DISTINCT `register-info`.sn) AS activated_sn_count FROM `serial-number` LEFT JOIN `register-info` ON `serial-number`.sn = `register-info`.sn GROUP BY `serial-number`.vendor_id"
        print(sql)
        aa = cursor.execute(sql)
        bb = cursor.fetchall();
        vendorcontent =""
        alllincense = 0
        allactivate = 0
        for item in bb:
            id = item[0]
            vendor = curd.get_one_by_id(GridVendor, id)
            if not vendor:
                break;
            query = GridSn.query.filter_by(vendor_id=id).all()
            alllincense +=len(query)
            allactivate +=item[1]

            vendorcontent +=vendor.name +"\n\r    "
            vendorcontent +="目前发放license总数：" + str(len(query)) + "个\n\r   <br>   "
            vendorcontent +="激活了：" + str(item[1]) + "个\n\r     <br> "
            vendorcontent += "总金额：" + " 0.00￥ " + "\n\r   <br>   "

        content = "Grid4月报：" + "\n\r  <br> "
        content += "目前发放license总数：" + str(alllincense) + "个，\n\r  <br> "
        content += "激活了：" + str(allactivate) + "个\n\r  <br> "
        content += "总金额：" +" 0.00￥ "+"\n\r  <br> "
        content += vendorcontent

        content +="<table><tr><th>代理商</th><th>发放Lincense数量</th><th>激活数量</th></tr><tr><td>代理商A</td><td>11</td><td>2</td></tr><tr><td>代理商B</td><td>$19.99</td><td>This is an even better product!</td></tr></table>";

        print("run")
        message = Message(subject="Grid统计数据",sender=('南京理工计算成像研究院有限公司', '1791746286@qq.com'), recipients="1791746286@qq.com".split(";"), html=content)
        message.attach("统计数据.pdf", "application/pdf", getreportpdf_content(1))
        mail.send_mail(message)

import pymysql
HOST = 'xc213618.ddns.me'
USER = 'root'
PASSWD = 'xincheng'
DB = 'grid'
PORT = 3306
CHARSET = 'utf8'
@vendor.get('/downloadreport')
@authorize("admin:vendor:report")
def report():
    # scheduler.add_job(id ="11444441", func=Sendstatistics, trigger='cron', second='*/30')
    id = str_escape(request.args.get("id", type=str))

    # uploads = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    # return send_from_directory(directory =uploads, path='back.pdf',mimetype = 'application/pdf')
    # with open(uploads +'\\back.pdf', 'rb') as f:
    #     file_content = f.read()
    # response = make_response(file_content)


    # 将PDF内容写入响应对象并返回
    response = make_response(getreportpdf_content(id))

    response.headers['Content-Disposition'] = "attachment; filename* = UTF-8''" + quote(
        vendor.name +"_" + str(int(time.time())) + ".pdf")
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.mimetype = 'application/pdf'
    return response

def getreportpdf_content(id):

    vendor = curd.get_one_by_id(GridVendor,id)
    if not vendor:
        return fail_api(msg="找不到对映的代理商信息")

    query = GridSn.query.filter_by(vendor_id = id).all()
    buffer = BytesIO()

    data= [[
            item.id,
            '-'.join(re.compile('.{6}').findall(item.sn)),
            curd.get_one_by_id(Gridmodule, item.module_id).name,
            item.effect_months.strftime( '%Y-%m-%d %H:%M:%S') ,
            item.create_date.strftime( '%Y-%m-%d %H:%M:%S') ,
        ] for item in query]
    header =["名称","sn","name","effect_months","create_date"]

    data.insert(0,header)

    # 创建PDF文档对象并设置元信息
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    pdf.title = "My PDF Report"

    pdfmetrics.registerFont(TTFont('SimSun', os.getcwd()+ '\\static\\fonts\\'+'SimSun.ttf'))

    stylesheet = getSampleStyleSheet()

    stylesheet.add(ParagraphStyle(fontName='SimSun', name='Song', leading=20, fontSize=12))  # 自己增加新注册的字体

    title = '<font size="20"><b>         Grid代理商报表 \n\r</b><b>序列号信息</b></font>'
    centered_title = Paragraph(title, stylesheet['Song'])
    pdf_elements = [centered_title, Spacer(10, 5)]

    # 创建表格对象并设置样式
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'SimSun'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'SimSun'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))

    # 将表格对象添加到PDF文档中并关闭
    pdf_elements.append(table)
    pdf.build(pdf_elements)
    pdf_content = buffer.getvalue()
    buffer.close()
    return pdf_content