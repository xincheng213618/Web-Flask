from applications.extensions import ma
from marshmallow import fields

class GridUserOutSchema(ma.Schema):
    id = fields.Integer()
    name = fields.Str()
    legal_address = fields.Str()
    email_address = fields.Str()
    contact_number = fields.Str()
    user_class = fields.Integer()
    create_at = fields.DateTime()


