import flask
from flask import Blueprint, request, render_template,jsonify
import re,pymysql,json
import time

HOST = 'xc213618.ddns.me'
USER = 'root'
PASSWD = 'xincheng'
DB = 'grid'
PORT = 3306
CHARSET = 'utf8'

# 创建一个服务，把当前这个python文件当做一个服务
app = flask.Flask(__name__)
@app.route('/register', methods=['post'])
def register():
    user_id = 1
    sn = request.values.get('sn')
    register_info = request.values.get('register-info')
    mac_address = request.values.get('mac-address')
    equip_identify = request.values.get('equip-identify')

    if not sn or not mac_address or not register_info:
        resu = {'state': 1, 'message': '参数不能存在空值'}
        return jsonify(resu)
    if not checkSN(sn):
        resu = {'state': 1, 'message': '序列号参数异常'}
        return jsonify(resu)
    if not checkMac(mac_address):
        resu = {'state': 1, 'message': 'Mac地址参数异常'}
        return jsonify(resu)

    sn = sn.strip().replace("-", "")
    mac_address = mac_address.strip().replace("-", "").replace(":", "").replace(".", "")

    if register_info:
        register_info = json.loads(register_info)
        name = register_info["name"]
        if not name:
            resu = {'state': 1, 'message': '用户名为空'}
            return jsonify(resu)
        legal_address = register_info["legal_address"]
        if not legal_address:
            resu = {'state': 1, 'message': '注册地址为空'}
            return jsonify(resu)
        email_address = register_info["email_address"]
        if not email_address:
            resu = {'state': 1, 'message': '注册邮件地址为空'}
            return jsonify(resu)
        contact_number = register_info["contact_number"]
        if not email_address:
            resu = {'state': 1, 'message': '联系电话为空'}
            return jsonify(resu)


        try:
            db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT,
                                 use_unicode=True)
            cursor = db.cursor()

            try:
                sql = "SELECT * FROM  `user` WHERE `name` = '%s'" % (name);
                num = cursor.execute(sql)
                result = cursor.fetchall();
                if num == 0:
                    print("找不到用户信息，现在重新插入用户信息")
                    sql = "INSERT INTO `user` (name, legal_address, email_address, contact_number,user_class) \
                           VALUES ('%s', '%s', '%s','%s',0)" % \
                          (name, legal_address, email_address, contact_number)
                    num = cursor.execute(sql)
                    db.commit()

                    sql = "SELECT * FROM  `user` WHERE `name` = '%s'" % (name);
                    num = cursor.execute(sql)
                    result = cursor.fetchall();
                    print(result)
                    user_id = result[0][0]
                    db.commit()
                else:
                    user_id = result[0][0]

            except Exception as e:
                print(e.args)
                resu = {'state': 1, 'message': "用戶信息格式不正确，请检查register_info"}
                return jsonify(resu)  # 将字典转换为json串, json是字符串

            sql = "SELECT * FROM  `serial-number` WHERE `sn` = '%s'" % (sn.strip().replace("-", ""));
            print(sql)
            aa = cursor.execute(sql)
            if (aa == 0):
                resu = {'state': 1, 'message': "该序列号无效"}
                return jsonify(resu)  # 将字典转换为json串, json是字符串

            sql = "SELECT * FROM  `register-info` WHERE `sn` = '%s'" % (sn);
            print(sql)
            aa = cursor.execute(sql)
            if (aa != 0):
                bb = cursor.fetchall();
                print(bb[0])
                if bb[0][3] != mac_address and bb[0][1] == user_id:
                    resu = {'state': 1, 'message': "该用户已经注册过，是否重新注册到新设备？"}
                    return jsonify(resu)  # 将字典转换为json串, json是字符串
                else:
                    resu = {'state': 1, 'message': "该序列号已经注册"}
                    return jsonify(resu)  # 将字典转换为json串, json是字符串

            sql = "SELECT * FROM  `register-info` WHERE `mac_address` = '%s'" % (mac_address);
            num = cursor.execute(sql)

            create_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            sql = "INSERT INTO `register-info` (user_id, equip_identify, mac_address, sn,create_date) \
                   VALUES (%s, '%s', '%s','%s','%s')" % \
                  (user_id, equip_identify, mac_address, sn, create_date)
            print(sql)
            num = cursor.execute(sql)
            db.commit()

            resu = {'state': 0, 'message': "注册成功", 'user-class': 0, 'feature-list': [{"Moudlue": "基础版本"}]}
            return jsonify(resu)  # 将字典转换为json串, json是字符串
        except Exception as e:
            resu = {'state': 1, 'message': e.args}
            return jsonify(resu)  # 将字典转换为json串, json是字符串
    else:
        resu = {'state': 1, 'message': '参数不能为空！'}

        return jsonify(resu)

def returnMsg(Msg=""):
    if not Msg or Msg == "":
        return jsonify({'state': 0, 'message': ''})
    Msg =str(Msg)
    return jsonify("{'state': 1, 'message': "+Msg+"}")
@app.route('/unregister', methods=['post'])
def unregister():
    sn = request.values.get('sn')
    register_info = request.values.get('register-info')
    mac_address = request.values.get('mac-address')
    equip_identify = request.values.get('equip-identify')

    if not sn or not mac_address or not register_info:
        resu = {'state': 1, 'message': '参数不能存在空值'}
        return jsonify(resu)
    if not checkSN(sn):
        resu = {'state': 1, 'message': '序列号参数异常'}
        return jsonify(resu)
    if not checkMac(mac_address):
        resu = {'state': 1, 'message': 'Mac地址参数异常'}
        return jsonify(resu)

    sn = sn.strip().replace("-", "")
    mac_address = mac_address.strip().replace("-", "").replace(":", "").replace(".", "")

    try:
        db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT, use_unicode=True)
        cursor = db.cursor()

        try:
            register_info = json.loads(register_info)
            name = register_info["name"]
            legal_address = register_info["legal_address"]
            email_address = register_info["email_address"]
            contact_number = register_info["contact_number"]
            sql = "SELECT * FROM  `user` WHERE `name` = '%s'" % (name);
            num = cursor.execute(sql)
            result = cursor.fetchall();
            if num == 0:
                resu = {'state': 1, 'message': "找不到用户信息"}
                return jsonify(resu)  # 将字典转换为json串, json是字符串
            else:
                user_id = result[0][0]
        except:
            resu = {'state': 1, 'message': "用戶信息格式不正确，请检查register_info"}
            return jsonify(resu)  # 将字典转换为json串, json是字符串

        sql = "SELECT * FROM `grid`.`register-info` WHERE `sn` = '%s'" % (sn)
        num = cursor.execute(sql)
        if num == 0:
            resu = {'state': 1, 'message': "找不到已经注册的序列号"}
            return jsonify(resu)  # 将字典转换为json串, json是字符串
        else:
            result = cursor.fetchall()
            print(result[0])
            id = result[0][1]
            if id != user_id:
                resu = {'state': 1, 'message': "用户信息和已注册的用户信息不匹配"}
                return jsonify(resu)  # 将字典转换为json串, json是字符串

        sql = "DELETE FROM  `register-info` WHERE `sn` = '%s'" % (sn);
        num = cursor.execute(sql)

        db.commit()
        if (num != 0):
            resu = {'state': 0, 'message': "取消注册成功"}
            return jsonify(resu)  # 将字典转换为json串, json是字符串
        else:
            resu = {'state': 1, 'message': "找不到序列号"}
            return jsonify(resu)  # 将字典转换为json串, json是字符串

        sql = "DELETE FROM  `register-info` WHERE `mac_address` = '%s'" % (mac_address);
        print(sql)
        aa = cursor.execute(sql)
        db.commit()
        if (aa == 0):

            resu = {'state': 1, 'message': "找不到已经注册的信息", }
            return jsonify(resu)  # 将字典转换为json串, json是字符串
        else:
            resu = {'state': 0, 'message': "取消注册成功", }
            return jsonify(resu)  # 将字典转换为json串, json是字符串
    except:
        resu = {'state': 1, 'message': "数据库连接失败"}
        return jsonify(resu)  # 将字典转换为json串, json是字符串



def checkSN(sn):
    sn = sn.strip().replace("-", "")
    print(sn, len(sn))
    if len(sn) == 24 and re.match(r"^[A-Za-z0-9]+$", sn):
        return True
    return False



def checkMac(mac):
    mac = mac.strip().replace("-", "").replace(":", "").replace(".", "")
    return re.match(r"^\s*([0-9a-fA-F]{2,2}){5,5}[0-9a-fA-F]{2,2}\s*$", mac)


@app.route('/checkregister', methods=['post'])
def checkregister():
    sn = request.values.get('sn')
    macstrings = request.values.get('mac-array')

    if not sn or not macstrings:
        resu = {'state': 1, 'message': '参数不能存在空值'}
        return jsonify(resu)
    if not checkSN(sn):
        resu = {'state': 1, 'message': '序列号参数异常'}
        return jsonify(resu)

    sn = sn.strip().replace("-", "")
    macs = macstrings.split(";")
    print(macstrings)
    checkmacis = False
    for mac in macs:
        if checkMac(mac):
            checkmacis = True
            break
    if not checkmacis:
        resu = {'state': 1, 'message': 'Mac地址参数异常'}
        return jsonify(resu)

    try:
        db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT, use_unicode=True)
        cursor = db.cursor()
        sql = "SELECT * FROM  `register-info` WHERE `sn` = '%s'" % (sn)
        print(sql)
        aa = cursor.execute(sql)
        print(aa)
        if (aa == 0):
            resu = {'state': 1, 'message': '找不到注册信息'}
            return jsonify(resu)  # 将字典转换为json串, json是字符串
        for row in cursor.fetchall():
            print(row[3])
            for mac in macs:
                if (row[3].strip().replace("-", "").replace(":", "").replace(".", "") == mac.strip().replace("-",
                                                                                                             "").replace(
                        ":", "").replace(".", "")):
                    resu = {'state': 0, 'message': '0'}
                    return jsonify(resu)  # 将字典转换为json串, json是字符串
        resu = {'state': 1, 'message': '当前序列号已注册到其他机器'}
        db.commit()
    except Exception as e:
        print(e.args)
        resu = {'state': 1, 'message': "数据库连接失败"}
    return jsonify(resu)  # 将字典转换为json串, json是字符串

@app.route('/checkregisterdata', methods=['post'])
def checkregisterdata():
    sn = request.values.get('sn')
    if not sn:
        resu = {'state': 1, 'message': '参数不能存在空值'}
        return jsonify(resu)
    if not checkSN(sn):
        resu = {'state': 1, 'message': '序列号参数异常'}
        return jsonify(resu)
    try:
        db = pymysql.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, charset=CHARSET, port=PORT, use_unicode=True)
        cursor = db.cursor()
        sql = "SELECT * FROM `grid`.`serial-number` WHERE `sn` = '%s'" % (sn)
        print(sql)
        aa = cursor.execute(sql)
        if (aa == 0):
            resu = {'state': 1, 'message': '找不到注册信息'}
            return jsonify(resu)  # 将字典转换为json串, json是字符
        else:
            res = cursor.fetchall()
            resu = {'state': 0, 'message': '0','sn':res[0][1],'effect_months': res[0][4]}
            return jsonify(resu)  # 将字典转换为json串, json是字符串
    except Exception:
        resu = {'state': 1, 'message': "数据库连接失败"}
    return jsonify(resu)  # 将字典转换为json串, json是字符串



