import graphene
from graphene_django import DjangoObjectType

from authentication.models import User
from authentication.schema import UserType
from integrations.models import Integration
from utils.exceptions import UnauthorizedException, ForbiddenException, NotFoundException
from utils.utils import IntID
from workspaces.models import Workspace


# Integration
class IntegrationType(DjangoObjectType):
    class Meta:
        model = Integration
        exclude = ('id', 'user')

    id = IntID(required=True)
    user = graphene.Field(UserType, required=True)


class IntegrationQuery(graphene.ObjectType):
    integration = graphene.Field(IntegrationType, id=IntID(required=True))

    @classmethod
    def resolve_integration(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        try:
            integration = Integration.objects.get(pk=kwargs.get('id'))
        except Integration.DoesNotExist:
            # any user can only request integrations that exist
            raise NotFoundException()

        # any user can only request integrations associated to itself
        if integration.user != info.context.user:
            raise ForbiddenException()

        return integration

    all_integrations = graphene.Field(graphene.List(IntegrationType))

    @classmethod
    def resolve_all_integrations(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        # any user can only request integrations associated to itself
        all_integrations = Integration.objects.filter(user=info.context.user)

        return all_integrations


class CreateIntegration(graphene.Mutation):
    class Arguments:
        workspace_id = IntID(required=True)
        label = graphene.String(required=True)
        integration_type = graphene.String(required=True)
        supports_data_connectors = graphene.Boolean(required=True)
        config = graphene.JSONString(required=True)

    integration = graphene.Field(IntegrationType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        create_kwargs = dict(kwargs)

        create_kwargs['user'] = info.context.user

        try:
            workspace = Workspace.objects.get(pk=kwargs.get('workspace_id'))
        except Workspace.DoesNotExist:
            # any user can only create a integration if it associates it to a workspace
            raise NotFoundException()

        if workspace.user != info.context.user:
            raise ForbiddenException()

        del create_kwargs['workspace_id']
        create_kwargs['workspace'] = workspace

        integration = Integration()

        for key, value in create_kwargs.items():
            setattr(integration, key, value)

        integration.save()

        return CreateIntegration(integration=integration)


class UpdateIntegration(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)
        label = graphene.String()
        config = graphene.JSONString()

    integration = graphene.Field(IntegrationType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        update_kwargs = dict(kwargs)

        try:
            integration = Integration.objects.get(pk=kwargs.get('id'))
        except Integration.DoesNotExist:
            # any user can only update integrations that exist
            raise NotFoundException()

        if integration.user != info.context.user:
            # any user can only update integrations associated to itself
            raise ForbiddenException()

        for key, value in update_kwargs.items():
            setattr(integration, key, value)

        integration.save()

        return UpdateIntegration(integration=integration)


class DeleteIntegration(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)

    id = graphene.Field(IntID)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        try:
            integration = Integration.objects.get(pk=kwargs.get('id'))
        except Integration.DoesNotExist:
            # any user can only delete integrations that exist
            raise NotFoundException()

        if integration.user != info.context.user:
            # any user can only delete integrations that are associated to itself
            raise ForbiddenException()

        integration.delete()

        return DeleteIntegration(id=kwargs.get('id'))


class IntegrationMutation(object):
    create_integration = CreateIntegration.Field()
    update_integration = UpdateIntegration.Field()
    delete_integration = DeleteIntegration.Field()


query_list = [IntegrationQuery]
mutation_list = [IntegrationMutation]
