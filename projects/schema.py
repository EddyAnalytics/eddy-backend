import graphene
from graphene_django import DjangoObjectType

from authentication.models import User
from authentication.schema import UserType
from projects.models import Project
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


query_list = [ProjectQuery]
mutation_list = [ProjectMutation]
