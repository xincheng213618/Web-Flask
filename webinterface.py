from main import *
from flask import render_template,request,jsonify,redirect
import pymysql

@app.route('/generateSNCode', methods=['get'])
def generateSNCode():
    return render_template("generateSNCode.html")



from werkzeug.routing import BaseConverter
class RegexConverter(BaseConverter):
    def __init__(self, url_map, *args):
        super(RegexConverter, self).__init__(url_map)
        self.url = url_map
        self.regex = args[0]   # 正则的匹配规则

    def to_python(self, value):
        return value
app.url_map.converters['reg'] = RegexConverter   # 注册url转换类
@app.route('/email_captcha_Vaild/<reg(".*?"):captcha>', methods=['get'])
def email_captcha_Vaild1(captcha):
    print(captcha)
    email = request.args.get('email')
    if not email:
        resu = {'code': 1, 'message':"请输入email"}
        return jsonify(resu)
    if captcha == util.redistaic.GetValue(email):
        resu = {'code': 0, 'message':"验证通过"}
        return jsonify(resu)
    else:
        resu = {'code': 1, 'message':"您输入的验证码有误"}
        return jsonify(resu)

@app.route('/email_captcha_Vaild', methods=['post'])
def email_captcha_Vaild():
    email = request.values.get('email')
    captcha = request.values.get('captcha')
    if captcha == util.redistaic.GetValue(email):
        resu = {'code': 0, 'message':"验证通过"}
        return jsonify(resu)
    else:
        resu = {'code': 1, 'message':"您输入的验证码有误"}
        return jsonify(resu)





@app.route('/getModule', methods=['get'])
def GetModule():
    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT, use_unicode=True)
    cursor = db.cursor()
    sql = "SELECT `name`,`code` FROM `grid`.`charging-module`"
    num = cursor.execute(sql)
    module = cursor.fetchall()
    modulelist = []
    for row in module:
        modulelist.append(row[0]);
    resu = {'state': 0, 'message': '', 'list': modulelist}
    return jsonify(resu)
import random, string

@app.route("/GeneraSNCode", methods=['post'])
def GeneraSNCode():
    vendor = request.values.get('vendor')
    moudle = request.values.get('moudle')

    if not vendor:
        resu = {'state': 1, 'message': '参数不能存在空值'}
        return jsonify(resu)

    db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT,
                         use_unicode=True)
    cursor = db.cursor()
    sql = "SELECT `id`,`name` FROM `grid`.`vendor` WHERE `name` = '%s'" % (vendor);
    num = cursor.execute(sql);
    if (num == 0):
        resu = {'state': 1, 'message': '找不到供应商，请重新输入或者注册'}
        return jsonify(resu)

    vendor_id = cursor.fetchall()[0][0]
    sn = ''.join(random.sample(string.ascii_letters + string.digits, 24)).upper()

    sql = "SELECT `id`,`name` FROM `grid`.`charging-module` WHERE `name` = '%s'" % (moudle);
    num = cursor.execute(sql);
    if (num == 0):
        resu = {'state': 1, 'message': '找不到供应商，请重新输入或者注册'}
        return jsonify(resu)

    module_id = cursor.fetchall()[0][0]

    if (module_id==0):
        expire_date = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime("2050-01-01", "%Y-%m-%d"))
    expire_date = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime("2050-01-01", "%Y-%m-%d"))
    create_date =time.strftime("%Y-%m-%d %H:%M:%S", time.localtime());
    sql = "INSERT INTO `grid`.`serial-number` (`sn`, `vendor_id`, `module_id`, `effect_months`,`create_date` ) VALUES ('%s', %s, %s, '%s','%s')" % (
    sn, vendor_id, module_id,expire_date,create_date );
    print(sql)
    num = cursor.execute(sql);
    db.commit()
    print(sn)
    pattern = re.compile('.{6}')
    sn = '-'.join(pattern.findall(sn))
    # smtpdemo.receivers =["114803203@qq.com"]
    resu = {'state': 0, 'message': '', 'sn': sn}
    return jsonify(resu)


@app.route('/addSNCode', methods=['post'])
def addSNCode():
    sn = request.values.get('sn')
    print(sn)
    if not sn:
        resu = {'state': 1, 'message': '参数不能存在空值'}
        return jsonify(resu)
    if not checkSN(sn):
        resu = {'state': 1, 'message': '序列号参数异常'}
        return jsonify(resu)
    sn = sn.strip().replace("-", "")
    try:
        db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT,
                             use_unicode=True)
        cursor = db.cursor()
        create_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        sql = "INSERT INTO `grid`.`serial-number` (`sn`, `vendor_id`, `module_id`, `effect_months`, `create_date`) VALUES ('%s', %s, %s,'%s', '%s')" % (
        sn, 11, 11, create_date, create_date)
        print(sql)
        aa = cursor.execute(sql)
        db.commit()
        print(aa)
        if (aa == 0):
            resu = {'state': 0, 'message': '注册成功'}
            return jsonify(resu)  # 将字典转换为json串, json是字符串
        resu = {'state': 0, 'message': '注册成功'}
    except Exception:
        resu = {'state': 1, 'message': "数据库连接失败"}
    return jsonify(resu)  # 将字典转换为json串, json是字符串

