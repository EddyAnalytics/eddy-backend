import graphene
from graphene_django import DjangoObjectType

from authentication.models import User
from authentication.schema import UserType
from projects import models
from projects.models import Project, DataConnector
from utils.exceptions import ForbiddenException, NotFoundException, UnauthorizedException
from utils.utils import IntID
from workspaces.models import Workspace


# Project
class ProjectType(DjangoObjectType):
    class Meta:
        model = Project
        exclude = ('id', 'user')

    id = graphene.Field(IntID, required=True)
    user = graphene.Field(UserType, required=True)


class ProjectQuery(graphene.ObjectType):
    project = graphene.Field(ProjectType, id=IntID(required=True))

    @classmethod
    def resolve_project(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        try:
            project = Project.objects.get(pk=kwargs.get('id'))
        except Project.DoesNotExist:
            # any user can only request projects that exist
            raise NotFoundException()

        # any user can only request projects associated to itself
        if project.user != info.context.user:
            raise ForbiddenException()

        return project

    all_projects = graphene.Field(graphene.List(ProjectType))

    @classmethod
    def resolve_all_projects(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        # any user can only request projects associated to itself
        all_projects = Project.objects.filter(user=info.context.user)

        return all_projects


class CreateProject(graphene.Mutation):
    class Arguments:
        workspace_id = IntID(required=True)
        label = graphene.String()

    project = graphene.Field(ProjectType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        create_kwargs = dict(kwargs)
        create_kwargs['user_id'] = info.context.user.id

        try:
            workspace = Workspace.objects.get(pk=kwargs.get('workspace_id'))
        except Workspace.DoesNotExist:
            # any user can only create a project if it associates it to a workspace
            raise NotFoundException()

        if workspace.user != info.context.user:
            raise ForbiddenException()

        create_kwargs['workspace_id'] = workspace.id

        project = Project()

        for key, value in create_kwargs.items():
            setattr(project, key, value)

        project.save()

        return CreateProject(project=project)


class UpdateProject(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)
        label = graphene.String()

    project = graphene.Field(ProjectType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        update_kwargs = dict(kwargs)

        try:
            project = Project.objects.get(pk=kwargs.get('id'))
        except Project.DoesNotExist:
            # any user can only update projects that exist
            raise NotFoundException()

        if project.user != info.context.user:
            # any user can only update projects associated to itself
            raise ForbiddenException()

        for key, value in update_kwargs.items():
            setattr(project, key, value)

        project.save()

        return UpdateProject(project=project)


class DeleteProject(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)

    project = graphene.Field(ProjectType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        try:
            project = Project.objects.get(pk=kwargs.get('id'))
        except Project.DoesNotExist:
            # any user can only update projects that exist
            raise NotFoundException()

        if project.user != info.context.user:
            # any user can only delete projects associated to itself
            raise ForbiddenException()

        project.delete()

        return DeleteProject(project=None)


class ProjectMutation(object):
    create_project = CreateProject.Field()
    update_project = UpdateProject.Field()
    delete_project = DeleteProject.Field()


# DataConnector
class DataConnectorType(DjangoObjectType):
    class Meta:
        model = DataConnector
        exclude = ('id', 'user')

    id = IntID(required=True)
    user = graphene.Field(UserType, required=True)


class DataConnectorQuery(graphene.ObjectType):
    data_connector = graphene.Field(DataConnectorType, id=IntID(required=True))

    @classmethod
    def resolve_data_connector(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        try:
            data_connector = DataConnector.objects.get(pk=kwargs.get('id'))
        except DataConnector.DoesNotExist:
            # any user can only request data_connectors that exist
            raise NotFoundException()

        # any user can only request data_connectors associated to itself
        if data_connector.user != info.context.user:
            raise ForbiddenException()

        return data_connector

    all_data_connectors = graphene.Field(graphene.List(DataConnectorType))

    @classmethod
    def resolve_all_data_connectors(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        # any user can only request all_data_connectors associated to itself
        all_data_connectors = DataConnector.objects.filter(user=info.context.user)

        return all_data_connectors


class CreateDataConnector(graphene.Mutation):
    class Arguments:
        project_id = IntID(required=True)
        label = graphene.String(required=True)
        data_connector_type_id = IntID(required=True)
        config = graphene.JSONString(required=True)

    data_connector = graphene.Field(DataConnectorType)

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
            # any user can only create a data_connector if it associates it to a project
            raise NotFoundException()

        if project.user != info.context.user:
            raise ForbiddenException()

        create_kwargs['project_id'] = project.id

        try:
            data_connector_type = models.DataConnectorType.objects.get(pk=kwargs.get('data_connector_type_id'))
        except models.DataConnectorType.DoesNotExist:
            # any user can only create a data_connector if it associates it to a data_connector_type
            raise NotFoundException()

        create_kwargs['data_connector_type_id'] = data_connector_type.id

        data_connector = DataConnector()

        for key, value in create_kwargs.items():
            setattr(data_connector, key, value)

        data_connector.save()

        return CreateDataConnector(data_connector=data_connector)


class UpdateDataConnector(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)
        label = graphene.String()
        # TODO maybe add data_connector_type
        config = graphene.JSONString()

    data_connector = graphene.Field(DataConnectorType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        update_kwargs = dict(kwargs)

        try:
            data_connector = DataConnector.objects.get(pk=kwargs.get('id'))
        except DataConnector.DoesNotExist:
            # any user can only update data_connectors that exist
            raise NotFoundException()

        if data_connector.user != info.context.user:
            # any user can only update data_connectors associated to itself
            raise ForbiddenException()

        for key, value in update_kwargs.items():
            setattr(data_connector, key, value)

        data_connector.save()

        return UpdateDataConnector(data_connector=data_connector)


class DeleteDataConnector(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)

    data_connector = graphene.Field(DataConnectorType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        try:
            data_connector = DataConnector.objects.get(pk=kwargs.get('id'))
        except DataConnector.DoesNotExist:
            # any user can only delete data_connectors that exist
            raise NotFoundException()

        if data_connector.user != info.context.user:
            # any user can only delete data_connectors associated to itself
            raise ForbiddenException()

        data_connector.delete()

        # TODO maybe add some hooks to delete other blocks and stuff

        return DeleteDataConnector(data_connector=data_connector)


class DataConnectorMutation(object):
    create_data_connector = CreateDataConnector.Field()
    update_data_connector = UpdateDataConnector.Field()
    delete_data_connector = DeleteDataConnector.Field()


# DataConnectorType
class DataConnectorTypeType(DjangoObjectType):
    class Meta:
        model = models.DataConnectorType
        exclude = ('id', 'data_connectors')

    id = IntID(required=True)


class DataConnectorTypeQuery(graphene.ObjectType):
    data_connector_type = graphene.Field(DataConnectorTypeType, id=IntID(required=True))

    @classmethod
    def resolve_data_connector_type(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        try:
            data_connector_type = models.DataConnectorType.objects.get(pk=kwargs.get('id'))
        except models.DataConnectorType.DoesNotExist:
            # any user can only request data_connector_types that exist
            raise NotFoundException()

        return data_connector_type

    all_data_connector_types = graphene.Field(graphene.List(DataConnectorTypeType))

    @classmethod
    def resolve_all_data_connector_types(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        all_data_connector_types = models.DataConnectorType.objects.filter()

        return all_data_connector_types


class CreateDataConnectorType(graphene.Mutation):
    class Arguments:
        label = graphene.String(required=True)
        config = graphene.JSONString(required=True)

    data_connector_type = graphene.Field(DataConnectorTypeType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        create_kwargs = dict(kwargs)

        if not info.context.user.is_superuser:
            # only superusers can create data_connector_types
            raise ForbiddenException()

        data_connector_type = models.DataConnectorType()

        for key, value in create_kwargs.items():
            setattr(data_connector_type, key, value)

        data_connector_type.save()

        return CreateDataConnectorType(data_connector_type=data_connector_type)


class UpdateDataConnectorType(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)
        label = graphene.String()
        config = graphene.JSONString()

    data_connector_type = graphene.Field(DataConnectorTypeType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        update_kwargs = dict(kwargs)

        if not info.context.user.is_superuser:
            # only superusers can update data_connector_types
            raise ForbiddenException()

        try:
            data_connector_type = models.BlockType.objects.get(pk=kwargs.get('id'))
        except models.DataConnectorType.DoesNotExist:
            # any superuser can only update data_connector_types that exist
            raise NotFoundException()

        for key, value in update_kwargs.items():
            setattr(data_connector_type, key, value)

        data_connector_type.save()

        return CreateDataConnectorType(data_connector_type=data_connector_type)


class DeleteDataConnectorType(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)

    data_connector_type = graphene.Field(DataConnectorTypeType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        if not info.context.user.is_superuser:
            # only superusers can delete data_connector_types
            raise ForbiddenException()

        try:
            data_connector_type = models.DataConnectorType.objects.get(pk=kwargs.get('id'))
        except models.DataConnectorType.DoesNotExist:
            # any superuser can only delete data_connector_types that exist
            raise NotFoundException()

        data_connector_type.delete()

        return DeleteDataConnectorType(data_connector_type=data_connector_type)


class DataConnectorTypeMutation(object):
    create_data_connector_type = CreateDataConnectorType.Field()
    update_data_connector_type = UpdateDataConnectorType.Field()
    delete_data_connector_type = DeleteDataConnectorType.Field()


query_list = [ProjectQuery, DataConnectorQuery, DataConnectorTypeQuery]
mutation_list = [ProjectMutation, DataConnectorMutation, DataConnectorTypeMutation]
