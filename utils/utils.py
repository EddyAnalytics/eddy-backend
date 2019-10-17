from django.contrib import admin
from django_mysql.models import JSONField
from graphene import Scalar, JSONString
from graphene_django.converter import convert_django_field
from graphql.language import ast


class IntID(Scalar):
    @staticmethod
    def serialize(value):
        return int(value)

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.IntValue):
            return int(node.value)

    @staticmethod
    def parse_value(value):
        return int(value)


@convert_django_field.register(JSONField)
def convert_mysql_json_field_to_graphene_json_string(field, registry=None):
    return JSONString(description=field.help_text, required=not field.null)


class ReadOnlyIdAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
