import graphene
from graphene_django import DjangoObjectType

from authentication.models import User
from authentication.schema import UserType
from dashboards import models
from dashboards.models import Dashboard, Widget
from projects.models import Project
from utils.exceptions import NotFoundException, UnauthorizedException, ForbiddenException
from utils.utils import IntID


# Dashboard
class DashboardType(DjangoObjectType):
    class Meta:
        model = Dashboard
        exclude = ('id', 'user')

    id = IntID(required=True)
    user = graphene.Field(UserType, required=True)


class DashboardQuery(graphene.ObjectType):
    dashboard = graphene.Field(DashboardType, id=IntID(required=True))

    @classmethod
    def resolve_dashboard(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        try:
            dashboard = Dashboard.objects.get(pk=kwargs.get('id'))
        except Dashboard.DoesNotExist:
            # any user can only request dashboards that exist
            raise NotFoundException()

        # any user can only request dashboards associated to itself
        if dashboard.user != info.context.user:
            raise ForbiddenException()

        return dashboard

    all_dashboards = graphene.Field(graphene.List(DashboardType))

    @classmethod
    def resolve_all_dashboards(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        # any user can only request dashboards associated to itself
        all_dashboards = Dashboard.objects.filter(user=info.context.user)

        return all_dashboards


class CreateDashboard(graphene.Mutation):
    class Arguments:
        project_id = IntID(required=True)
        label = graphene.String(required=True)

    dashboard = graphene.Field(DashboardType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        create_kwargs = dict(kwargs)

        create_kwargs['user_id'] = info.context.user.id

        try:
            project = Project.objects.get(pk=kwargs.get('project_id'))
        except Project.DoesNotExist:
            # any user can only create a dashboard if it associates it to a project
            raise NotFoundException()

        if project.user != info.context.user:
            raise ForbiddenException()

        create_kwargs['project_id'] = project.id

        dashboard = Dashboard()

        for key, value in create_kwargs.items():
            setattr(dashboard, key, value)

        dashboard.save()

        return CreateDashboard(dashboard=dashboard)


class UpdateDashboard(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)
        label = graphene.String()

    dashboard = graphene.Field(DashboardType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        update_kwargs = dict(kwargs)

        try:
            dashboard = Dashboard.objects.get(pk=kwargs.get('id'))
        except Dashboard.DoesNotExist:
            # any user can only update dashboards that exist
            raise NotFoundException()

        for key, value in update_kwargs.items():
            setattr(dashboard, key, value)

        dashboard.save()

        return UpdateDashboard(dashboard=dashboard)


class DeleteDashboard(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)

    dashboard = graphene.Field(DashboardType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        try:
            dashboard = Dashboard.objects.get(pk=kwargs.get('id'))
        except Dashboard.DoesNotExist:
            # any user can only update dashboards that exist
            raise NotFoundException()

        if dashboard.user != info.context.user:
            # any user can only delete dashboards associated to itself
            raise ForbiddenException()

        dashboard.delete()

        return DeleteDashboard(dashboard=None)


class DashboardMutation(object):
    create_dashboard = CreateDashboard.Field()
    update_dashboard = UpdateDashboard.Field()
    delete_dashboard = DeleteDashboard.Field()


# Widget
class WidgetType(DjangoObjectType):
    class Meta:
        model = Widget
        exclude = ('id', 'user')

    id = IntID(required=True)
    user = graphene.Field(UserType, required=True)


class WidgetQuery(graphene.ObjectType):
    widget = graphene.Field(WidgetType, id=IntID(required=True))

    @classmethod
    def resolve_block(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        try:
            widget = Widget.objects.get(pk=kwargs.get('id'))
        except Widget.DoesNotExist:
            # any user can only request widgets that exist
            raise NotFoundException()

        # any user can only request widgets associated to itself
        if widget.user != info.context.user:
            raise ForbiddenException()

        return widget

    all_widgets = graphene.Field(graphene.List(WidgetType))

    @classmethod
    def resolve_all_widgets(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        # any user can only request widgets associated to itself
        all_widgets = Widget.objects.filter(user=info.context.user)

        return all_widgets


class CreateWidget(graphene.Mutation):
    class Arguments:
        dashboard_id = IntID(required=True)
        label = graphene.String(required=True)
        widget_type_id = IntID(required=True)
        config = graphene.JSONString(required=True)

    widget = graphene.Field(WidgetType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        create_kwargs = dict(kwargs)

        create_kwargs['user_id'] = info.context.user.id

        try:
            dashboard = Dashboard.objects.get(pk=kwargs.get('dashboard_id'))
        except Dashboard.DoesNotExist:
            # any user can only create a widget if it associates it to a dashboard
            raise NotFoundException()

        if dashboard.user != info.context.user:
            raise ForbiddenException()

        create_kwargs['dashboard_id'] = dashboard.id

        try:
            widget_type = models.WidgetType.objects.get(pk=kwargs.get('widget_type_id'))
        except models.WidgetType.DoesNotExist:
            # any user can only create a widget if it associates it to a widget_type
            raise NotFoundException()

        create_kwargs['widget_type_id'] = widget_type.id

        widget = Widget()

        for key, value in create_kwargs.items():
            setattr(widget, key, value)

        widget.save()

        return CreateWidget(widget=widget)


class UpdateWidget(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)
        label = graphene.String()
        config = graphene.JSONString()

    widget = graphene.Field(WidgetType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        update_kwargs = dict(kwargs)

        try:
            widget = Widget.objects.get(pk=kwargs.get('id'))
        except Widget.DoesNotExist:
            # any user can only update widgets that exist
            raise NotFoundException()

        if widget.user != info.context.user:
            # any user can only update widgets associated to itself
            raise ForbiddenException()

        for key, value in update_kwargs.items():
            setattr(widget, key, value)

        widget.save()

        for key, value in update_kwargs.items():
            setattr(widget, key, value)

        widget.save()

        return UpdateWidget(widget=widget)


class DeleteWidget(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)

    widget = graphene.Field(WidgetType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        try:
            widget = Widget.objects.get(pk=kwargs.get('id'))
        except Widget.DoesNotExist:
            # any user can only delete widgets that exist
            raise NotFoundException()

        if widget.user != info.context.user:
            # any user can only delete widgets associated to itself
            raise ForbiddenException()

        widget.delete()

        # TODO maybe add some hooks to delete other blocks and stuff

        return DeleteWidget(widget=widget)


class WidgetMutation(object):
    create_widget = CreateWidget.Field()
    update_widget = UpdateWidget.Field()
    delete_widget = DeleteWidget.Field()


# WidgetType
class WidgetTypeType(DjangoObjectType):
    class Meta:
        model = models.WidgetType
        exclude = ('id', 'widgets')

    id = IntID(required=True)


class WidgetTypeQuery(graphene.ObjectType):
    widget_type = graphene.Field(WidgetTypeType, id=IntID(required=True))

    @classmethod
    def resolve_block_type(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        try:
            widget_type = models.WidgetType.objects.get(pk=kwargs.get('id'))
        except models.WidgetType.DoesNotExist:
            # any user can only request widget_types that exist
            raise NotFoundException()

        return widget_type

    all_widget_types = graphene.Field(graphene.List(WidgetTypeType))

    @classmethod
    def resolve_all_widget_types(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        all_widget_types = models.WidgetType.objects.filter()

        return all_widget_types


class CreateWidgetType(graphene.Mutation):
    class Arguments:
        label = graphene.String(required=True)
        config = graphene.JSONString(required=True)

    widget_type = graphene.Field(WidgetTypeType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        create_kwargs = dict(kwargs)

        if not info.context.user.is_superuser:
            # only superusers can create widget_types
            raise ForbiddenException()

        widget_type = models.WidgetType()

        for key, value in create_kwargs.items():
            setattr(widget_type, key, value)

        widget_type.save()

        return CreateWidgetType(widget_type=widget_type)


class UpdateWidgetType(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)
        config = graphene.JSONString()

    widget_type = graphene.Field(WidgetTypeType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        update_kwargs = dict(kwargs)

        if not info.context.user.is_superuser:
            # only superusers can update widget_types
            raise ForbiddenException()

        try:
            widget_type = models.WidgetType.objects.get(pk=kwargs.get('id'))
        except models.WidgetType.DoesNotExist:
            # any superuser can only update widget_types that exist
            raise NotFoundException()

        for key, value in update_kwargs.items():
            setattr(widget_type, key, value)

        widget_type.save()

        return UpdateWidgetType(widget_type=widget_type)


class DeleteWidgetType(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)

    widget_type = graphene.Field(WidgetTypeType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        if not info.context.user.is_superuser:
            # only superusers can delete widget_types
            raise ForbiddenException()

        try:
            widget_type = models.WidgetType.objects.get(pk=kwargs.get('id'))
        except models.WidgetType.DoesNotExist:
            # any superuser can only delete widget_types that exist
            raise NotFoundException()

        widget_type.delete()

        # TODO maybe delete orphans or something

        return DeleteWidgetType(widget_type=widget_type)


class WidgetTypeMutation(object):
    create_widget_type = CreateWidgetType.Field()
    update_widget_type = UpdateWidgetType.Field()
    delete_widget_type = DeleteWidgetType.Field()


query_list = [DashboardQuery, WidgetQuery, WidgetTypeQuery]
mutation_list = [DashboardMutation, WidgetMutation, WidgetTypeMutation]
