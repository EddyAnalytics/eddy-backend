import re
from typing import Type

import graphene
from django.db import models
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField


def camel_to_snake(name: str) -> str:
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def snake_to_camel(word: str) -> str:
    return ''.join(x.capitalize() or '_' for x in word.split('_'))


def model_to_node(model: Type[models.Model]) -> Type:
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


def model_to_query(model: Type[models.Model], node: Type) -> Type:
    query = type(
        model.__name__ + 'Query',
        (graphene.ObjectType,),
        {camel_to_snake(model.__name__): graphene.Node.Field(node),
         'all_' + camel_to_snake(model.__name__): DjangoFilterConnectionField(node)}
    )

    return query


def mutate_factory_create(model: Type[models.Model]):
    def mutate(self, info, **kwargs):
        target = model()
        for field in model._meta.fields:
            if field.name != 'id' and field.name in kwargs.keys():
                if type(field) == graphene.ID:
                    foreign = graphene.relay.Node.get_node_from_global_id(info, kwargs.get(field.name))
                    setattr(target, field.name, foreign)
                else:
                    setattr(target, field.name, kwargs.get(field.name))
        target.save()
        return self.__class__(**{camel_to_snake(model.__name__): target})

    return mutate


def model_to_create(model: Type[models.Model], node: Type) -> Type:
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
        {'Arguments': arguments, camel_to_snake(model.__name__): graphene.Field(node), 'mutate': mutate_factory_create(model)}
    )

    return create


def model_to_mutation(model: Type[models.Model], node: Type) -> Type:
    create = model_to_create(model, node)
    mutation = type(
        create.__name__ + 'Mutation',
        (),
        {camel_to_snake(create.__name__): create.Field()}
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
