import re

import graphene
from django.db import models
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField


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
            arguments[field.name + '_id'] = graphene.ID()
        elif isinstance(field, models.ForeignKey):
            arguments[field.name + '_id'] = graphene.ID()
        else:
            arguments[field.name] = django_type_to_graphene_type[type(field)]()

    return arguments


# dynamically generate *Node classes (DebeziumConnectorNode, DebeziumConnectorConfigNode)
def model_to_node(model):
    meta = type(
        'Meta',
        (),
        {'model': model, 'fields': '__all__', 'filter_fields': '__all__', 'interfaces': (graphene.relay.Node,)}
    )

    node = type(
        model.__name__ + 'Node',
        (DjangoObjectType,),
        {'Meta': meta}
    )

    return node


# dynamically generate *Query classes (DebeziumConnectorQuery, DebeziumConnectorConfigQuery)
def model_to_query(model, node):
    query = type(
        model.__name__ + 'Query',
        (graphene.ObjectType,),
        {camel_to_snake(model.__name__): graphene.Node.Field(node),
         'all_' + camel_to_snake(model.__name__): DjangoFilterConnectionField(node)}
    )

    return query


# factory for mutate methods for Create* mutations
def mutate_factory_create(model, arguments):
    @classmethod
    def mutate(cls, root, info, **kwargs):
        target = model()
        for argument_name, argument_type in arguments.__dict__.items():
            if argument_name in kwargs.keys():
                if argument_type == graphene.ID:
                    foreign = graphene.relay.Node.get_node_from_global_id(info, kwargs.get(argument_name))
                    setattr(target, argument_name, foreign)
                else:
                    setattr(target, argument_name, kwargs.get(argument_name))
        target.save()
        return cls(**{camel_to_snake(model.__name__): target})

    return mutate


# dynamically generate Create* classes (CreateDebeziumConnector, CreateDebeziumConnectorConfig)
def model_to_create(model, node):
    arguments = type(
        'Arguments',
        (),
        fields_to_arguments(model._meta.fields)
    )

    create = type(
        'Create' + model.__name__,
        (graphene.Mutation,),
        {'Arguments': arguments, camel_to_snake(model.__name__): graphene.Field(node),
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

        target = graphene.relay.Node.get_node_from_global_id(info, id)

        if target is None:
            return None

        for argument_name, argument_type in arguments.__dict__.items():
            if argument_name in kwargs.keys():
                if argument_type == graphene.ID:
                    foreign = graphene.relay.Node.get_node_from_global_id(info, kwargs.get(argument_name))
                    setattr(target, argument_name, foreign)
                else:
                    setattr(target, argument_name, kwargs.get(argument_name))
        target.save()
        return cls(**{camel_to_snake(model.__name__): target})

    return mutate


# dynamically generate Update* classes (CreateDebeziumConnector, CreateDebeziumConnectorConfig)
def model_to_update(model, node):
    arguments = type(
        'Arguments',
        (),
        fields_to_arguments(model._meta.fields)
    )

    setattr(arguments, 'id', graphene.ID())

    update = type(
        'Update' + model.__name__,
        (graphene.Mutation,),
        {'Arguments': arguments, camel_to_snake(model.__name__): graphene.Field(node),
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

        target = graphene.relay.Node.get_node_from_global_id(info, id)

        if target is None:
            return None

        target.delete()
        return cls(**{camel_to_snake(model.__name__): target})

    return mutate


def model_to_delete(model, node):
    arguments = type(
        'Arguments',
        (),
        {}
    )

    setattr(arguments, 'id', graphene.ID())

    delete = type(
        'Delete' + model.__name__,
        (graphene.Mutation,),
        {'Arguments': arguments, camel_to_snake(model.__name__): graphene.Field(node),
         'mutate': mutate_factory_delete(model, arguments)}
    )

    return delete


# dynamically generate *Mutation classes (DebeziumConnectorMutation, DebeziumConnectorConfigMutation)
def model_to_mutation(model, node):
    create = model_to_create(model, node)
    update = model_to_update(model, node)
    delete = model_to_delete(model, node)
    mutation = type(
        model.__name__ + 'Mutation',
        (object,),
        {camel_to_snake(create.__name__): create.Field(),
         camel_to_snake(update.__name__): update.Field(),
         camel_to_snake(delete.__name__): delete.Field()}
    )

    return mutation
