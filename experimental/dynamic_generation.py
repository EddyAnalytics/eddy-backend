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
def mutate_factory_create(model):
    @classmethod
    def mutate(cls, self, info, **kwargs):
        target = model()
        for field in model._meta.fields:
            if field.name != 'id' and field.name in kwargs.keys():
                if type(field) == graphene.ID:
                    foreign = graphene.relay.Node.get_node_from_global_id(info, kwargs.get(field.name))
                    setattr(target, field.name, foreign)
                else:
                    setattr(target, field.name, kwargs.get(field.name))
        target.save()
        return cls(**{camel_to_snake(model.__name__): target})

    return mutate


# dynamically generate Create* classes (CreateDebeziumConnector, CreateDebeziumConnectorConfig)
def model_to_create(model, node):
    django_type_to_graphene_type = {
        models.IntegerField: graphene.Int,
        models.CharField: graphene.String,
        models.OneToOneField: graphene.ID
    }

    arguments = type(
        'Arguments',
        (),
        {field.name: django_type_to_graphene_type[type(field)]() for field in model._meta.fields if
         not isinstance(field, models.AutoField)}
    )

    create = type(
        'Create' + model.__name__,
        (graphene.Mutation,),
        {'Arguments': arguments, camel_to_snake(model.__name__): graphene.Field(node),
         'mutate': mutate_factory_create(model)}
    )

    return create


# factory for mutate methods for Update* mutations
def mutate_factory_update(model):
    @classmethod
    def mutate(cls, self, info, **kwargs):
        id = kwargs.get('id')

        if id is None:
            return None

        target = graphene.relay.Node.get_node_from_global_id(info, id)

        if target is None:
            return None

        for field in model._meta.fields:
            if field.name != 'id' and field.name in kwargs.keys():
                if type(field) == graphene.ID:
                    foreign = graphene.relay.Node.get_node_from_global_id(info, kwargs.get(field.name))
                    setattr(target, field.name, foreign)
                else:
                    setattr(target, field.name, kwargs.get(field.name))
        target.save()
        return cls(**{camel_to_snake(model.__name__): target})

    return mutate


# dynamically generate Update* classes (CreateDebeziumConnector, CreateDebeziumConnectorConfig)
def model_to_update(model, node):
    django_type_to_graphene_type = {
        models.IntegerField: graphene.Int,
        models.CharField: graphene.String,
        models.OneToOneField: graphene.ID
    }

    arguments = type(
        'Arguments',
        (),
        {field.name: django_type_to_graphene_type[type(field)]() for field in model._meta.fields if
         not isinstance(field, models.AutoField)}
    )

    update = type(
        'Update' + model.__name__,
        (graphene.Mutation,),
        {'Arguments': arguments, camel_to_snake(model.__name__): graphene.Field(node),
         'mutate': mutate_factory_create(model)}
    )

    return update


# factory for mutate methods for Delete* mutations
def mutate_factory_delete(model):
    @classmethod
    def mutate(cls, self, info, **kwargs):
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
    django_type_to_graphene_type = {
        models.IntegerField: graphene.Int,
        models.CharField: graphene.String,
        models.OneToOneField: graphene.ID,
    }

    arguments = type(
        'Arguments',
        (),
        {field.name: django_type_to_graphene_type[type(field)]() for field in model._meta.fields if
         not isinstance(field, models.AutoField)}
    )

    delete = type(
        'Delete' + model.__name__,
        (graphene.Mutation,),
        {'Arguments': arguments, camel_to_snake(model.__name__): graphene.Field(node),
         'mutate': mutate_factory_create(model)}
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

# def model_to_delete(model: models.Model, Node: Type):
#     def mutate(self, info, **kwargs):
#         id = kwargs.get('id')
#         if id is None:
#             return None
#
#         target = graphene.relay.Node.get_node_from_global_id(info, id)
#
#         if target is None:
#             return None
#
#         target.delete()
#         return self.__class__()
#
#     Arguments = type('Arguments',
#                      (),
#                      {'id': graphene.ID()}
#                      )
#
#     Delete = type('Delete' + model.__name__,
#                   (graphene.Mutation,),
#                   {'Arguments': Arguments, 'mutate': mutate}
#                   )
#     return Delete
