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
    create_at = db.Column(db.DateTime, default=datetime.datetime.now, comment='创建时间')