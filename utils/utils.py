from graphene import Scalar
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
