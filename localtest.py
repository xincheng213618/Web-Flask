from flask_login import current_user,login_required

from main import *
from applications import create_app
from util import smtp
def send(email):
    receivers = email
    headers ="Grid统计数据"
    content ="统计数据\n\r"
    content +="新增客户：2人\n\r"
    content +="新增代理商：1位, xxxxx,xxxxx\n\r"
    content +="新发放序列号：18个，xxxxx,xxxx,xxxx\n\r"
    code, msg = smtp.sendmail(headers,content)

if __name__ == '__main__':
    app.config['MAX_CONTENT_LENGTH'] = 160 * 1000 * 1000
    create_app(app)
    app.run(debug=True, port=18888, host='0.0.0.0');

