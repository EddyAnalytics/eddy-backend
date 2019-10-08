import graphene
from graphene_django import DjangoObjectType

from authentication.models import User
from authentication.schema import UserType
from integrations import models
from integrations.models import DebeziumConnector, DebeziumConnectorConfig, Integration
from utils.exceptions import UnauthorizedException, ForbiddenException, ConflictException, NotFoundException
from utils.utils import IntID
# Integration
from workspaces.models import Workspace


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
        integration_type_id = IntID(required=True)

    integration = graphene.Field(IntegrationType)

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
            # any user can only create a integration if it associates it to a workspace
            raise NotFoundException()

        if workspace.user != info.context.user:
            raise ForbiddenException()

        create_kwargs['workspace_id'] = workspace.id

        try:
            integration_type = models.IntegrationType.objects.get(pk=kwargs.get('integration_type_id'))
        except models.IntegrationType.DoesNotExist:
            # any user can only create a integration if it associates it to a integration_type
            raise NotFoundException()

        create_kwargs['integration_type_id'] = integration_type.id

        integration = Integration()

        for key, value in create_kwargs.items():
            setattr(integration, key, value)

        integration.save()

        return CreateIntegration(integration=integration)


class UpdateIntegration(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)
        label = graphene.String()

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

    integration = graphene.Field(IntegrationType)

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

        return DeleteIntegration(integration=None)


class IntegrationMutation(object):
    create_integration = CreateIntegration.Field()
    delete_integration = DeleteIntegration.Field()


# IntegrationType
class IntegrationTypeType(DjangoObjectType):
    class Meta:
        model = models.IntegrationType
        exclude = ('id', 'integrations')

    id = IntID(required=True)


class IntegrationTypeQuery(graphene.ObjectType):
    integration_type = graphene.Field(IntegrationTypeType, id=IntID(required=True))

    @classmethod
    def resolve_block_type(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        try:
            integration_type = models.IntegrationType.objects.get(pk=kwargs.get('id'))
        except models.IntegrationType.DoesNotExist:
            # any user can only request integration_types that exist
            raise NotFoundException()

        return integration_type

    all_integration_types = graphene.Field(graphene.List(IntegrationTypeType))

    @classmethod
    def resolve_all_block_types(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        all_integration_types = models.IntegrationType.objects.filter()

        return all_integration_types


class CreateIntegrationType(graphene.Mutation):
    class Arguments:
        label = graphene.String(required=True)

    integration_type = graphene.Field(IntegrationTypeType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        create_kwargs = dict(kwargs)

        if not info.context.user.is_superuser:
            # only superusers can create integration_types
            raise ForbiddenException()

        integration_type = models.IntegrationType()

        for key, value in create_kwargs.items():
            setattr(integration_type, key, value)

        integration_type.save()

        return CreateIntegrationType(integration_type=integration_type)


class UpdateIntegrationType(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)
        label = graphene.String()

    integration_type = graphene.Field(IntegrationTypeType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        update_kwargs = dict(kwargs)

        if not info.context.user.is_superuser:
            # only superusers can update integration_types
            raise ForbiddenException()

        try:
            integration_type = models.IntegrationType.objects.get(pk=kwargs.get('id'))
        except models.IntegrationType.DoesNotExist:
            # any superuser can only update block_types that exist
            raise NotFoundException()

        for key, value in update_kwargs.items():
            setattr(integration_type, key, value)

        integration_type.save()

        return CreateIntegrationType(integration_type=integration_type)


class DeleteIntegrationType(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)

    integration_type = graphene.Field(IntegrationTypeType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        if not info.context.user.is_superuser:
            # only superusers can delete integration_types
            raise ForbiddenException()

        try:
            integration_type = models.IntegrationType.objects.get(pk=kwargs.get('id'))
        except models.IntegrationType.DoesNotExist:
            # any superuser can only delete integration_types that exist
            raise NotFoundException()

        integration_type.delete()

        # TODO maybe delete orphans or something

        return DeleteIntegrationType(integration_type=integration_type)


class IntegrationtypeMutation(object):
    create_integration_type = CreateIntegrationType.Field()
    update_integration_type = UpdateIntegrationType.Field()
    delete_integration_type = DeleteIntegrationType.Field()


# DebeziumConnector
class DebeziumConnectorType(DjangoObjectType):
    class Meta:
        model = DebeziumConnector
        exclude = ('id', 'user')

    id = IntID(required=True)
    user = graphene.Field(UserType, required=True)


class DebeziumConnectorQuery(graphene.ObjectType):
    debezium_connector = graphene.Field(DebeziumConnectorType, id=IntID(required=True))

    @classmethod
    def resolve_debezium_connector(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        try:
            debezium_connector = DebeziumConnector.objects.get(pk=kwargs.get('id'))
        except DebeziumConnector.DoesNotExist:
            # any user can only request connectors that exist
            raise NotFoundException()

        # any user can only request connectors associated to itself
        if debezium_connector.user != info.context.user:
            raise ForbiddenException()

        return debezium_connector

    all_debezium_connectors = graphene.Field(graphene.List(DebeziumConnectorType))

    @classmethod
    def resolve_all_debezium_connectors(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        # any user can only request connectors associated to itself
        all_debezium_connectors = DebeziumConnector.objects.filter(user=info.context.user)

        return all_debezium_connectors


class CreateDebeziumConnector(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        config_id = IntID(required=True)

    debezium_connector = graphene.Field(DebeziumConnectorType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        create_kwargs = dict(kwargs)

        create_kwargs['user_id'] = info.context.user.id

        try:
            config = DebeziumConnectorConfig.objects.get(pk=kwargs.get('config_id'))
        except DebeziumConnectorConfig.DoesNotExist:
            # any user can only create a connector if it associates it to a config
            raise NotFoundException()

        if config.user != info.context.user:
            raise ForbiddenException()

        if hasattr(config, 'connector'):
            # any connector must have a config associated to itself
            raise ConflictException()

        create_kwargs['config_id'] = config.id

        debezium_connector = DebeziumConnector()

        for key, value in create_kwargs.items():
            setattr(debezium_connector, key, value)

        debezium_connector.save()

        return CreateDebeziumConnector(debezium_connector=debezium_connector)


class DeleteDebeziumConnector(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)

    debezium_connector = graphene.Field(DebeziumConnectorType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        try:
            debezium_connector = DebeziumConnector.objects.get(pk=kwargs.get('id'))
        except DebeziumConnector.DoesNotExist:
            # any user can only delete connectors that exist
            raise NotFoundException()

        if debezium_connector.user != info.context.user:
            # any user can only delete connectors that are associated to itself
            raise ForbiddenException()

        debezium_connector.delete()

        return DeleteDebeziumConnector(debezium_connector=None)


class DebeziumConnectorMutation(object):
    create_debezium_connector = CreateDebeziumConnector.Field()
    delete_debezium_connector = DeleteDebeziumConnector.Field()


# DebeziumConnectorConfig
class DebeziumConnectorConfigType(DjangoObjectType):
    class Meta:
        model = DebeziumConnectorConfig
        exclude = ('id', 'user')

    id = IntID(required=True)
    user = graphene.Field(UserType, required=True)


class DebeziumConnectorConfigQuery(graphene.ObjectType):
    debezium_connector_config = graphene.Field(DebeziumConnectorConfigType, id=IntID(required=True))

    @classmethod
    def resolve_debezium_connector_config(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()
        try:
            debezium_connector_config = DebeziumConnectorConfig.objects.get(pk=kwargs.get('id'))
        except DebeziumConnectorConfig.DoesNotExist:
            # any user can only request configs that exist
            raise NotFoundException()

        if debezium_connector_config.user != info.context.user:
            # any user can only request configs associated to itself
            raise ForbiddenException()

        return debezium_connector_config

    all_debezium_connector_configs = graphene.Field(graphene.List(DebeziumConnectorConfigType))

    @classmethod
    def resolve_all_debezium_connector_configs(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        # any user can only request configs associated to itself
        all_debezium_connector_configs = DebeziumConnectorConfig.objects.filter(user=info.context.user)

        return all_debezium_connector_configs


class CreateDebeziumConnectorConfig(graphene.Mutation):
    class Arguments:
        connector_class = graphene.String(required=True)
        tasks_max = graphene.Int(required=True)
        database_hostname = graphene.String(required=True)
        database_port = graphene.Int(required=True)
        database_user = graphene.String(required=True)
        database_password = graphene.String(required=True)
        database_server_id = graphene.Int(required=True)
        database_server_name = graphene.String(required=True)
        database_whitelist = graphene.String(required=True)
        database_history_kafka_bootstrap_servers = graphene.String(required=True)
        database_history_kafka_topic = graphene.String(required=True)

    debezium_connector_config = graphene.Field(DebeziumConnectorConfigType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        create_kwargs = dict(kwargs)

        create_kwargs['user_id'] = info.context.user.id

        debezium_connector_config = DebeziumConnectorConfig()

        for key, value in create_kwargs.items():
            setattr(debezium_connector_config, key, value)

        debezium_connector_config.save()

        return CreateDebeziumConnectorConfig(debezium_connector_config=debezium_connector_config)


class UpdateDebeziumConnectorConfig(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)
        connector_class = graphene.String()
        tasks_max = graphene.Int()
        database_hostname = graphene.String()
        database_port = graphene.Int()
        database_user = graphene.String()
        database_password = graphene.String()
        database_server_id = graphene.Int()
        database_server_name = graphene.String()
        database_whitelist = graphene.String()
        database_history_kafka_bootstrap_servers = graphene.String()
        database_history_kafka_topic = graphene.String()

    debezium_connector_config = graphene.Field(DebeziumConnectorConfigType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        update_kwargs = dict(kwargs)

        try:
            debezium_connector_config = DebeziumConnectorConfig.objects.get(pk=kwargs.get('id'))
        except DebeziumConnectorConfig.DoesNotExist:
            # any user can only update configs that exist
            raise NotFoundException()

        if debezium_connector_config.user != info.context.user:
            # any user can only update configs associated to itself
            raise ForbiddenException()

        for key, value in update_kwargs.items():
            setattr(debezium_connector_config, key, value)

        debezium_connector_config.save()

        return UpdateDebeziumConnectorConfig(debezium_connector_config=debezium_connector_config)


class DeleteDebeziumConnectorConfig(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)

    debezium_connector_config = graphene.Field(DebeziumConnectorConfigType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        try:
            debezium_connector_config = DebeziumConnectorConfig.objects.get(pk=kwargs.get('id'))
        except DebeziumConnectorConfig.DoesNotExist:
            # any user can only delete configs that exist
            raise NotFoundException()

        if debezium_connector_config.user != info.context.user:
            # any user can only delete configs associated to itself
            raise ForbiddenException()

        if hasattr(debezium_connector_config, 'connector'):
            # any connector must have a config associated to itself
            raise ConflictException()

        debezium_connector_config.delete()

        return DeleteDebeziumConnectorConfig(debezium_connector_config=None)


class DebeziumConnectorConfigMutation(object):
    create_debezium_connector_config = CreateDebeziumConnectorConfig.Field()
    update_debezium_connector_config = UpdateDebeziumConnectorConfig.Field()
    delete_debezium_connector_config = DeleteDebeziumConnectorConfig.Field()


query_list = [IntegrationQuery, IntegrationTypeQuery, DebeziumConnectorQuery, DebeziumConnectorConfigQuery]
mutation_list = [IntegrationMutation, IntegrationtypeMutation, DebeziumConnectorMutation,
                 DebeziumConnectorConfigMutation]
