import re

import graphene
from django.db import models
from graphene import Scalar
from graphene_django import DjangoObjectType
from graphql.language import ast

import authentication.models
from authentication.exceptions import UserNotAuthenticatedException, UserNotAuthorizedException


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
        elif isinstance(field, models.OneToOneRel):
            # reverse of self
            arguments[field.name + '_id'] = IntID()
        elif isinstance(field, models.ForeignKey):
            # reverse of ManyToOneRel
            arguments[field.name + '_id'] = IntID()
        elif isinstance(field, models.ManyToOneRel):
            # reverse of ForeignKey
            arguments[field.name + '_ids'] = graphene.List(IntID)
        elif isinstance(field, models.ManyToManyField):
            # Mostly for user groups and permissions (django stuff not our own stuff)
            arguments[field.name + '_ids'] = graphene.List(IntID)
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
        {'Meta': meta, 'id': IntID()}
    )

    return type_


# factory for resolve methods for * Queries
def resolve_factory(model):
    def resolve(root, info, **kwargs):
        if not isinstance(info.context.user, authentication.models.User):
            raise UserNotAuthenticatedException()

        if model.requires_superuser and not info.context.user.is_superuser:
            raise UserNotAuthorizedException()

        id = kwargs.get('id')

        if id is None:
            return None

        target = model.objects.get(pk=id)

        if target is None:
            return None

        if not info.context.user.is_superuser:
            if model == authentication.models.User:
                if target != info.context.user:
                    return None
            else:
                if target.user != info.context.user:
                    return None

        return target

    return resolve


# factory for resolve_all methods for all* Queries
def resolve_all_factory(model):
    def resolve_all(root, info, **kwargs):
        if not isinstance(info.context.user, authentication.models.User):
            raise UserNotAuthenticatedException()

        if model.requires_superuser and not info.context.user.is_superuser:
            raise UserNotAuthorizedException()

        if model == authentication.models.User:
            targets = [info.context.user]
        else:
            if not info.context.user.is_superuser:
                targets = model.objects.filter(user=info.context.user)
            else:
                targets = model.objects.all()

        return targets

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
        if not isinstance(info.context.user, authentication.models.User):
            raise UserNotAuthenticatedException()

        if model.requires_superuser and not info.context.user.is_superuser:
            raise UserNotAuthorizedException()

        target = model()

        if model != authentication.models.User:
            target.user = info.context.user

        for argument_name, argument_type in arguments.__dict__.items():
            if argument_name in kwargs.keys():
                if argument_name == 'password':
                    target.set_password(kwargs.get(argument_name))
                elif argument_type == IntID:
                    foreign = model.objects.get(pk=kwargs.get(argument_name))
                    setattr(target, argument_name, foreign)
                elif argument_type == graphene.List(IntID):
                    foreigns = model.objects.filter(id__in=kwargs.get(argument_name))
                    setattr(target, argument_name, foreigns)
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
        fields_to_arguments(model._meta.get_fields())
    )

    if hasattr(arguments, 'user_id'):
        delattr(arguments, 'user_id')

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
        if not isinstance(info.context.user, authentication.models.User):
            raise UserNotAuthenticatedException()

        if model.requires_superuser and not info.context.user.is_superuser:
            raise UserNotAuthorizedException()

        id = kwargs.get('id')

        if id is None:
            return None

        target = model.objects.get(pk=id)

        if target is None:
            return None

        if not info.context.user.is_superuser:
            if model == authentication.models.User:
                if target != info.context.user:
                    return None
            else:
                if target.user != info.context.user:
                    return None

        for argument_name, argument_type in arguments.__dict__.items():
            if argument_name in kwargs.keys():
                if argument_name == 'password':
                    target.set_password(kwargs.get(argument_name))
                elif argument_type == IntID:
                    foreign = model.objects.get(pk=kwargs.get(argument_name))
                    setattr(target, argument_name, foreign)
                elif argument_type == graphene.List(IntID):
                    foreigns = model.objects.filter(id__in=kwargs.get(argument_name))
                    setattr(target, argument_name, foreigns)
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
        fields_to_arguments(model._meta.get_fields())
    )

    setattr(arguments, 'id', IntID())

    if hasattr(arguments, 'user_id'):
        delattr(arguments, 'user_id')

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
        if not isinstance(info.context.user, authentication.models.User):
            raise UserNotAuthenticatedException()

        if model.requires_superuser and not info.context.user.is_superuser:
            raise UserNotAuthorizedException()

        id = kwargs.get('id')

        if id is None:
            return None

        target = model.objects.get(pk=id)

        if target is None:
            return None

        if not info.context.user.is_superuser:
            if model == authentication.models.User:
                if target != info.context.user:
                    return None
            else:
                if target.user != info.context.user:
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

    if hasattr(arguments, 'user_id'):
        delattr(arguments, 'user_id')

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
