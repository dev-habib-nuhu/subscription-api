from marshmallow import Schema, fields, validate


class PlanSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    description = fields.Str()
    price = fields.Float(required=True, validate=validate.Range(min=0))
    duration_in_days = fields.Int(required=True, validate=validate.Range(min=1))


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    created_at = fields.DateTime(dump_only=True, format="iso")

    class Meta:
        datetimeformat = "%Y-%m-%dT%H:%M:%S"
        ordered = True


class SubscriptionSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    plan_id = fields.Int(required=True)
    start_date = fields.DateTime(dump_only=True, format="iso")
    end_date = fields.DateTime(dump_only=True, format="iso")
    is_active = fields.Boolean(dump_only=True)
    auto_renew = fields.Boolean()
    created_at = fields.DateTime(dump_only=True, format="iso")
    plan = fields.Nested(PlanSchema, dump_only=True)

    class Meta:
        datetimeformat = "%Y-%m-%dT%H:%M:%S"
        ordered = True


plan_schema = PlanSchema()
plan_list_schema = PlanSchema(many=True)

user_schema = UserSchema()

subscription_schema = SubscriptionSchema()
subscription_list_schema = SubscriptionSchema(many=True)
