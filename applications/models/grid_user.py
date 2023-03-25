import datetime
from applications.extensions import db


class GridUser(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='用户编号')
    name = db.Column(db.String(30), comment='用户名')
    legal_address = db.Column(db.String(255), comment='注册地址')
    email_address = db.Column(db.String(255), comment='注册邮件')
    contact_number = db.Column(db.String(25), comment='联系电话')
    user_class = db.Column(db.Integer,default=0, comment='联系电话')
    create_date = db.Column(db.DateTime, default=datetime.datetime.now, comment='创建时间')


class GridVendor(db.Model):
    __tablename__ = 'vendor'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='用户编号')
    name = db.Column(db.String(255), comment='name')
    address = db.Column(db.String(255), comment='address')
    contact_number = db.Column(db.String(15), comment='contact_number')
    create_date = db.Column(db.DateTime, default=datetime.datetime.now, comment='创建时间')



class GridSn(db.Model):
    __tablename__ = 'serial-number'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='用户编号')
    sn = db.Column(db.String(24), comment='name')
    vendor_id = db.Column(db.Integer, comment='vendor_id')
    module_id = db.Column(db.Integer, comment='module_id')
    effect_months =db.Column(db.DateTime, comment='module_id')
    create_date = db.Column(db.DateTime, default=datetime.datetime.now, comment='创建时间')

class Gridmodule(db.Model):
    __tablename__ = 'charging-module'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='用户编号')
    name = db.Column(db.String(30), comment='name')
    code = db.Column(db.Integer, comment='code')
    download_address = db.Column(db.Integer, comment='download_address')
    renewal_type =db.Column(db.DateTime, comment='renewal_type')
    create_date = db.Column(db.DateTime, default=datetime.datetime.now, comment='创建时间')

class Gridorder(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='用户编号')
    user_id = db.Column(db.Integer, comment='user_id')
    serial_id = db.Column(db.Integer, comment='serial_id')
    payment = db.Column(db.Integer, comment='payment')
    effect_date = db.Column(db.DateTime, comment='effect_date')
    expire_date = db.Column(db.DateTime, comment='expire_date')
    create_date = db.Column(db.DateTime, default=datetime.datetime.now, comment='创建时间')