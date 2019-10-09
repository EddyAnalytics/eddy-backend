import graphene
from graphene_django import DjangoObjectType

from authentication.models import User
from authentication.schema import UserType
from utils.exceptions import UnauthorizedException, ForbiddenException, NotFoundException
from utils.utils import IntID
from workspaces.models import Workspace


# Workspace
class WorkspaceType(DjangoObjectType):
    class Meta:
        model = Workspace
        exclude = ('id', 'user')

    id = graphene.Field(IntID, required=True)
    user = graphene.Field(UserType, required=True)


class WorkspaceQuery(graphene.ObjectType):
    workspace = graphene.Field(WorkspaceType, id=IntID(required=True))

    @classmethod
    def resolve_workspace(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        try:
            workspace = Workspace.objects.get(pk=kwargs.get('id'))
        except Workspace.DoesNotExist:
            # any user can only request workspaces that exist
            raise NotFoundException()

        # any user can only request workspaces associated to itself
        if workspace.user != info.context.user:
            raise ForbiddenException()

        return workspace

    all_workspaces = graphene.Field(graphene.List(WorkspaceType))

    @classmethod
    def resolve_all_workspaces(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        # any user can only request workspaces associated to itself
        all_workspaces = Workspace.objects.filter(user=info.context.user)

        return all_workspaces


class WorkspaceMutation(object):
    pass


query_list = [WorkspaceQuery]
mutation_list = [WorkspaceMutation]
