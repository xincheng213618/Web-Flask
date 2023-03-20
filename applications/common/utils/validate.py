# xss过滤
from flask import abort, make_response, jsonify, escape


def str_escape(s):
    if not s:
        return None
    return str(escape(s))


def check_data(schema, data):
    errors = schema.validate(data)
    for k, v in errors.items():
        for i in v:
            # print("{}{}".format(k, i))
            msg = "{}{}".format(k, i)
    if errors:
        abort(make_response(jsonify(result=False, msg=msg), 200))
