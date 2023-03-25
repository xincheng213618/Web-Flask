import datetime
from applications.extensions import db


class RegisterInfo(db.Model):
    __tablename__ = 'register-info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='用户编号')
    user_id = db.Column(db.Integer, comment='user_id')
    equip_identify = db.Column(db.String(50), comment='')
    mac_address = db.Column(db.String(20), comment='')
    sn = db.Column(db.String(255), comment='')
    create_date = db.Column(db.DateTime, default=datetime.datetime.now, comment='创建时间')