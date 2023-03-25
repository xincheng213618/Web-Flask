from applications.extensions import ma
from marshmallow import fields

class GridUserOutSchema(ma.Schema):
    id = fields.Integer()
    name = fields.Str()
    legal_address = fields.Str()
    email_address = fields.Str()
    contact_number = fields.Str()
    user_class = fields.Integer()
    create_date = fields.DateTime()

class RegisterInfoOutSchema(ma.Schema):
    id = fields.Integer()
    user_id = fields.Str()
    equip_identify = fields.Str()
    mac_address = fields.Str()
    sn = fields.Str()
    create_date = fields.DateTime()

class GridVendorOutSchema(ma.Schema):
    id = fields.Integer()
    name = fields.Str()
    address = fields.Str()
    contact_number = fields.Str()
    create_date = fields.DateTime()

class GridSnOutSchema(ma.Schema):
    id = fields.Integer()
    sn = fields.Str()
    vendor_id = fields.Integer()
    module_id = fields.Integer()
    effect_months = fields.DateTime()
    create_date = fields.DateTime()

class GridmoduleOutSchema(ma.Schema):
    id = fields.Integer()
    name = fields.Str()
    code =fields.Str()
    download_address = fields.Str()
    renewal_type =fields.Integer()
    create_date = fields.DateTime()
