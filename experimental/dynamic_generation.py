import re

import graphene
from django.db import models
from graphene import Scalar
from graphene_django import DjangoObjectType
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


# convert a snake case string to a camel case string
def camel_to_snake(string):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


# convert a snake case string to a camel case string
def snake_to_camel(string):
    return ''.join(x.capitalize() or '_' for x in string.split('_'))


def fields_to_arguments(fields):
    django_type_to_graphene_type = {
        models.IntegerField: graphene.Int,
        models.CharField: graphene.String,
        models.DateTimeField: graphene.DateTime,
        models.BooleanField: graphene.Boolean,
        models.EmailField: graphene.String,  # TODO maybe change e-mail field graphene type
    }

    arguments = dict()
    for field in fields:
        if isinstance(field, models.AutoField):
            pass
        elif isinstance(field, models.OneToOneField):
            arguments[field.name + '_id'] = IntID()
        elif isinstance(field, models.ForeignKey):
            arguments[field.name + '_id'] = IntID()
        else:
            arguments[field.name] = django_type_to_graphene_type[type(field)]()

    return arguments


# dynamically generate *Type classes (DebeziumConnectorType, DebeziumConnectorConfigType)
def model_to_type_(model):
    meta = type(
        'Meta',
        (),
        {'model': model}
    )

    type_ = type(
        model.__name__ + 'Type',
        (DjangoObjectType,),
        {'Meta': meta}
    )

    return type_


# factory for resolve methods for * Queries
def resolve_factory(model):
    def resolve(root, info, **kwargs):
        id = kwargs.get('id')

        if id is None:
            return None

        target = model.objects.get(pk=id)

        if target is None:
            return None

        return target

    return resolve


# factory for resolve_all methods for all* Queries
def resolve_all_factory(model):
    def resolve_all(root, info, **kwargs):
        target = model.objects.all()

        return target

    return resolve_all


# dynamically generate *Query classes (DebeziumConnectorQuery, DebeziumConnectorConfigQuery)
def model_to_query(model, type_):
    query = type(
        model.__name__ + 'Query',
        (graphene.ObjectType,),
        {camel_to_snake(model.__name__): graphene.Field(type_, id=IntID()),
         'resolve_' + camel_to_snake(model.__name__): resolve_factory(model),
         'all_' + camel_to_snake(model.__name__): graphene.List(type_),
         'resolve_all_' + camel_to_snake(model.__name__): resolve_all_factory(model)},
    )

    return query


# factory for mutate methods for Create* mutations
def mutate_factory_create(model, arguments):
    @classmethod
    def mutate(cls, root, info, **kwargs):
        target = model()

        for argument_name, argument_type in arguments.__dict__.items():
            if argument_name in kwargs.keys():
                if argument_type == IntID:
                    foreign = model.objects.get(pk=kwargs.get(argument_name))
                    setattr(target, argument_name, foreign)
                else:
                    setattr(target, argument_name, kwargs.get(argument_name))

        target.save()
        return cls(**{camel_to_snake(model.__name__): target})

    return mutate


# dynamically generate Create* classes (CreateDebeziumConnector, CreateDebeziumConnectorConfig)
def model_to_create(model, type_):
    arguments = type(
        'Arguments',
        (),
        fields_to_arguments(model._meta.fields)
    )

    create = type(
        'Create' + model.__name__,
        (graphene.Mutation,),
        {'Arguments': arguments,
         camel_to_snake(model.__name__): graphene.Field(type_),
         'mutate': mutate_factory_create(model, arguments)}
    )

    return create


# factory for mutate methods for Update* mutations
def mutate_factory_update(model, arguments):
    @classmethod
    def mutate(cls, root, info, **kwargs):
        id = kwargs.get('id')

        if id is None:
            return None

        target = model.objects.get(pk=id)

        if target is None:
            return None

        for argument_name, argument_type in arguments.__dict__.items():
            if argument_name in kwargs.keys():
                if argument_type == IntID:
                    foreign = model.objects.get(pk=kwargs.get(argument_name))
                    setattr(target, argument_name, foreign)
                else:
                    setattr(target, argument_name, kwargs.get(argument_name))

        target.save()
        return cls(**{camel_to_snake(model.__name__): target})

    return mutate


# dynamically generate Update* classes (UpdateDebeziumConnector, UpdateDebeziumConnectorConfig)
def model_to_update(model, type_):
    arguments = type(
        'Arguments',
        (),
        fields_to_arguments(model._meta.fields)
    )

    setattr(arguments, 'id', IntID())

    update = type(
        'Update' + model.__name__,
        (graphene.Mutation,),
        {'Arguments': arguments,
         camel_to_snake(model.__name__): graphene.Field(type_),
         'mutate': mutate_factory_update(model, arguments)}
    )

    return update


# factory for mutate methods for Delete* mutations
def mutate_factory_delete(model, arguments):
    @classmethod
    def mutate(cls, root, info, **kwargs):
        id = kwargs.get('id')

        if id is None:
            return None

        target = model.objects.get(pk=id)

        if target is None:
            return None

        target.delete()
        return cls(**{camel_to_snake(model.__name__): None})

    return mutate

# dynamically generate Delete* classes (DeleteDebeziumConnector, DeleteDebeziumConnectorConfig)
def model_to_delete(model, type_):
    arguments = type(
        'Arguments',
        (),
        {}
    )

    setattr(arguments, 'id', IntID())

    delete = type(
        'Delete' + model.__name__,
        (graphene.Mutation,),
        {'Arguments': arguments, camel_to_snake(model.__name__): graphene.Field(type_),
         'mutate': mutate_factory_delete(model, arguments)}
    )

    return delete


# dynamically generate *Mutation classes (DebeziumConnectorMutation, DebeziumConnectorConfigMutation)
def model_to_mutation(model, type_):
    create = model_to_create(model, type_)
    update = model_to_update(model, type_)
    delete = model_to_delete(model, type_)
    mutation = type(
        model.__name__ + 'Mutation',
        (object,),
        {
            camel_to_snake(create.__name__): create.Field(),
            camel_to_snake(update.__name__): update.Field(),
            camel_to_snake(delete.__name__): delete.Field()
        }
    )

    return mutation
