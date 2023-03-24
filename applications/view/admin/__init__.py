from flask import Flask

from applications.view.admin.admin_log import admin_log
from applications.view.admin.dict import admin_dict
from applications.view.admin.index import admin_bp
from applications.view.admin.file import admin_file
from applications.view.admin.power import admin_power
from applications.view.admin.role import admin_role
from applications.view.admin.user import admin_user
from applications.view.admin.monitor import admin_monitor_bp
from applications.view.admin.task import admin_task
from applications.view.admin.mail import admin_mail
from applications.view.admin.customer import customer
from applications.view.admin.vendor import vendor
from applications.view.admin.order import order
from applications.view.admin.module import module
from applications.view.admin.serial import serial


def register_admin_views(app: Flask):
    app.register_blueprint(admin_bp)
    app.register_blueprint(admin_user)
    app.register_blueprint(admin_file)
    app.register_blueprint(admin_monitor_bp)
    app.register_blueprint(admin_log)
    app.register_blueprint(admin_power)
    app.register_blueprint(admin_role)
    app.register_blueprint(admin_dict)
    app.register_blueprint(admin_task)
    app.register_blueprint(admin_mail)
    app.register_blueprint(customer)
    app.register_blueprint(vendor)
    app.register_blueprint(order)
    app.register_blueprint(module)
    app.register_blueprint(serial)

