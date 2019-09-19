from django.db import models
from django.apps import apps
from rest_framework import filters
from database.choices import ID_OBJ, ID_OPERATION
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.renderers import BrowsableAPIRenderer
from django_filters.filters import NumberFilter
from dynamic_rest.serializers import DynamicModelSerializer
from dynamic_rest.viewsets import DynamicModelViewSet
from dynamic_rest.routers import DynamicRouter

import re


class DefaultPagination(LimitOffsetPagination):
    default_limit = 50
    max_limit = 50


class BrowsableAPIRendererWithoutForms(BrowsableAPIRenderer):
    """Renders the browsable api, but excludes the forms."""

    def get_context(self, *args, **kwargs):
        ctx = super().get_context(*args, **kwargs)
        ctx['display_edit_forms'] = True

        return ctx


def Camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def snake_ToCamel(word):
    return ''.join(x.capitalize() or '_' for x in word.split('_'))


def get_filter(model):
    Meta = type(
        'Meta',
        (),
        {'model': model,
         'fields': ['before_block', 'after_block', 'before_time', 'after_time'] +
                   [field.name for field in model._meta.get_fields() if type(field).__name__ != "ManyToOneRel"],
         },
    )
    filterset_attrs = {
        'after_block': NumberFilter(name="block", lookup_type='gt'),
        'before_block': NumberFilter(name="block", lookup_type='lt'),
        'Meta': Meta,
        'filter_overrides': {
            models.OneToOneField: {
                'filter_class': NumberFilter
            },
            models.ForeignKey: {
                'filter_class': NumberFilter
            },
            models.ManyToManyField: {
                'filter_class': NumberFilter
            },
        }
    }
    return type(model.__name__ + 'FilterSet', (filters.FilterSet,), filterset_attrs)


def model_to_viewset(model, depth=0):
    Meta = type('Meta', (), {'model': model, 'depth': depth})
    serializer = type(
        model.__name__ + 'Serializer',
        (DynamicModelSerializer,),
        {'filter_backends': (filters.DjangoFilterBackend,), 'Meta': Meta},
    )
    return type(
        model.__name__ + 'ViewSet',
        (DynamicModelViewSet,),
        {'queryset': model.objects.all(),
         'serializer_class': serializer,
         'pagination_class': DefaultPagination,
         'filter_backends': (filters.DjangoFilterBackend,),
         'filter_class': get_filter(model),
         }
    )


router = DynamicRouter()
api_models = ["Block"] + list(ID_OBJ.values()) + [snake_ToCamel(operation) for id, operation in ID_OPERATION]
for model_name in api_models:
    model = apps.get_model(app_label='database', model_name=model_name)
    router.register(r'%s' % Camel_to_snake(model.__name__), model_to_viewset(model))
