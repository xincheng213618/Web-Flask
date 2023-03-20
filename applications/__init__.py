import os
import flask
from applications.extensions import init_plugs
from applications.view import init_view
from applications.common.script import init_script
from applications.extensions import db
from applications.configs import config
def create_app(app,config_name=None):

    if not config_name:
        # 尝试从本地环境中读取
        config_name = os.getenv('FLASK_CONFIG', 'development')

    # 引入数据库配置
    app.config.from_object(config[config_name])

    # 注册各种插件
    init_plugs(app)

    # 注册路由
    init_view(app)

    # 注册命令
    init_script(app)
    return app

def add_app(app):
    init_plugs(app)
    init_view(app)
    init_script(app)



