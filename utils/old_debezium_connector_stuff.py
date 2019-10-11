# import json
#
# import graphene
# import requests
# from django.conf import settings
# from django.db import models
# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver
# from graphene_django import DjangoObjectType
#
# from authentication.models import User
# from authentication.schema import UserType
# from utils.exceptions import UnauthorizedException, NotFoundException, ForbiddenException, ConflictException
# from utils.utils import IntID
#
#
# class DebeziumConnector(models.Model):
#     id = models.AutoField(primary_key=True)
#     user = models.ForeignKey('authentication.User', models.CASCADE, related_name='debezium_connectors')
#     name = models.CharField(max_length=200)
#     config = models.OneToOneField('integrations.DebeziumConnectorConfig', models.CASCADE, related_name='connector')
#
#
@receiver(post_save, sender=DebeziumConnector)
def post_save_debezium_connector(signal, sender, instance: DebeziumConnector, using, **kwargs):
    connector = instance
    config = connector.config

    url = 'http://' + settings.DEBEZIUM_HOST + ':' + settings.DEBEZIUM_PORT + '/connectors/'

    headers = dict()
    headers['Accept'] = 'application/json'
    headers['Content-Type'] = 'application/json'

    config_dict = dict()
    config_dict['connector.class'] = config.connector_class
    config_dict['tasks.max'] = config.tasks_max
    config_dict['database.hostname'] = config.database_hostname
    config_dict['database.port'] = config.database_port
    config_dict['database.user'] = config.database_user
    config_dict['database.password'] = config.database_password
    config_dict['database.server.id'] = config.database_server_id
    config_dict['database.server.name'] = config.database_server_name
    config_dict['database.whitelist'] = config.database_whitelist
    config_dict['database.history.kafka.bootstrap.servers'] = config.database_history_kafka_bootstrap_servers
    config_dict['database.history.kafka.topic'] = config.database_history_kafka_topic

    connector_dict = dict()
    connector_dict['name'] = connector.name
    connector_dict['config'] = config_dict

    data = json.dumps(connector_dict)

    requests.post(url, headers=headers, data=data)
#
#
# @receiver(post_delete, sender=DebeziumConnector)
# def post_delete_debezium_connector(signal, sender, instance: DebeziumConnector, using, **kwargs):
#     connector = instance
#
#     url = 'http://' + settings.DEBEZIUM_HOST + ':' + settings.DEBEZIUM_PORT + '/connectors/' + connector.name + '/'
#
#     headers = dict()
#     headers['Accept'] = 'application/json'
#     headers['Content-Type'] = 'application/json'
#
#     requests.delete(url, headers=headers)
#
#
# class DebeziumConnectorConfig(models.Model):
#     id = models.AutoField(primary_key=True)
#     user = models.ForeignKey('authentication.User', models.CASCADE, related_name='debezium_connector_configs')
#     connector_class = models.CharField(max_length=200)
#     tasks_max = models.IntegerField()
#     database_hostname = models.CharField(max_length=200)
#     database_port = models.IntegerField()
#     database_user = models.CharField(max_length=200)
#     database_password = models.CharField(max_length=200)
#     database_server_id = models.IntegerField()
#     database_server_name = models.CharField(max_length=200)
#     database_whitelist = models.CharField(max_length=200)
#     database_history_kafka_bootstrap_servers = models.CharField(max_length=200)
#     database_history_kafka_topic = models.CharField(max_length=200)
#
#
# @receiver(post_save, sender=DebeziumConnectorConfig)
# def post_save_debezium_connector_config(signal, sender, instance: DebeziumConnectorConfig, using, **kwargs):
#     config = instance
#     if hasattr(config, 'connector'):
#         connector = config.connector
#         url = 'http://' + settings.DEBEZIUM_HOST + ':' + settings.DEBEZIUM_PORT + '/connectors/' + connector.name + '/config/'
#
#         headers = dict()
#         headers['Accept'] = 'application/json'
#         headers['Content-Type'] = 'application/json'
#
#         config_dict = dict()
#         config_dict['connector.class'] = config.connector_class
#         config_dict['tasks.max'] = config.tasks_max
#         config_dict['database.hostname'] = config.database_hostname
#         config_dict['database.port'] = config.database_port
#         config_dict['database.user'] = config.database_user
#         config_dict['database.password'] = config.database_password
#         config_dict['database.server.id'] = config.database_server_id
#         config_dict['database.server.name'] = config.database_server_name
#         config_dict['database.whitelist'] = config.database_whitelist
#         config_dict['database.history.kafka.bootstrap.servers'] = config.database_history_kafka_bootstrap_servers
#         config_dict['database.history.kafka.topic'] = config.database_history_kafka_topic
#
#         data = json.dumps(config_dict)
#
#         requests.put(url, headers=headers, data=data)
#
#
# # DebeziumConnector
# class DebeziumConnectorType(DjangoObjectType):
#     class Meta:
#         model = DebeziumConnector
#         exclude = ('id', 'user')
#
#     id = IntID(required=True)
#     user = graphene.Field(UserType, required=True)
#
#
# class DebeziumConnectorQuery(graphene.ObjectType):
#     debezium_connector = graphene.Field(DebeziumConnectorType, id=IntID(required=True))
#
#     @classmethod
#     def resolve_debezium_connector(cls, root, info, **kwargs):
#         if not isinstance(info.context.user, User):
#             # any user needs to be authenticated
#             raise UnauthorizedException()
#
#         try:
#             debezium_connector = DebeziumConnector.objects.get(pk=kwargs.get('id'))
#         except DebeziumConnector.DoesNotExist:
#             # any user can only request connectors that exist
#             raise NotFoundException()
#
#         # any user can only request connectors associated to itself
#         if debezium_connector.user != info.context.user:
#             raise ForbiddenException()
#
#         return debezium_connector
#
#     all_debezium_connectors = graphene.Field(graphene.List(DebeziumConnectorType))
#
#     @classmethod
#     def resolve_all_debezium_connectors(cls, root, info, **kwargs):
#         if not isinstance(info.context.user, User):
#             # any user needs to be authenticated
#             raise UnauthorizedException()
#
#         # any user can only request connectors associated to itself
#         all_debezium_connectors = DebeziumConnector.objects.filter(user=info.context.user)
#
#         return all_debezium_connectors
#
#
# class CreateDebeziumConnector(graphene.Mutation):
#     class Arguments:
#         name = graphene.String(required=True)
#         config_id = IntID(required=True)
#
#     debezium_connector = graphene.Field(DebeziumConnectorType)
#
#     @classmethod
#     def mutate(cls, root, info, **kwargs):
#         if not isinstance(info.context.user, User):
#             # any user needs to be authenticated
#             raise UnauthorizedException()
#
#         create_kwargs = dict(kwargs)
#
#         create_kwargs['user_id'] = info.context.user.id
#
#         try:
#             config = DebeziumConnectorConfig.objects.get(pk=kwargs.get('config_id'))
#         except DebeziumConnectorConfig.DoesNotExist:
#             # any user can only create a connector if it associates it to a config
#             raise NotFoundException()
#
#         if config.user != info.context.user:
#             raise ForbiddenException()
#
#         if hasattr(config, 'connector'):
#             # any connector must have a config associated to itself
#             raise ConflictException()
#
#         create_kwargs['config_id'] = config.id
#
#         debezium_connector = DebeziumConnector()
#
#         for key, value in create_kwargs.items():
#             setattr(debezium_connector, key, value)
#
#         debezium_connector.save()
#
#         return CreateDebeziumConnector(debezium_connector=debezium_connector)
#
#
# class DeleteDebeziumConnector(graphene.Mutation):
#     class Arguments:
#         id = IntID(required=True)
#
#     debezium_connector = graphene.Field(DebeziumConnectorType)
#
#     @classmethod
#     def mutate(cls, root, info, **kwargs):
#         if not isinstance(info.context.user, User):
#             # any user needs to be authenticated
#             raise UnauthorizedException()
#
#         try:
#             debezium_connector = DebeziumConnector.objects.get(pk=kwargs.get('id'))
#         except DebeziumConnector.DoesNotExist:
#             # any user can only delete connectors that exist
#             raise NotFoundException()
#
#         if debezium_connector.user != info.context.user:
#             # any user can only delete connectors that are associated to itself
#             raise ForbiddenException()
#
#         debezium_connector.delete()
#
#         return DeleteDebeziumConnector(debezium_connector=None)
#
#
# class DebeziumConnectorMutation(object):
#     create_debezium_connector = CreateDebeziumConnector.Field()
#     delete_debezium_connector = DeleteDebeziumConnector.Field()
#
#
# # DebeziumConnectorConfig
# class DebeziumConnectorConfigType(DjangoObjectType):
#     class Meta:
#         model = DebeziumConnectorConfig
#         exclude = ('id', 'user')
#
#     id = IntID(required=True)
#     user = graphene.Field(UserType, required=True)
#
#
# class DebeziumConnectorConfigQuery(graphene.ObjectType):
#     debezium_connector_config = graphene.Field(DebeziumConnectorConfigType, id=IntID(required=True))
#
#     @classmethod
#     def resolve_debezium_connector_config(cls, root, info, **kwargs):
#         if not isinstance(info.context.user, User):
#             # any user needs to be authenticated
#             raise UnauthorizedException()
#         try:
#             debezium_connector_config = DebeziumConnectorConfig.objects.get(pk=kwargs.get('id'))
#         except DebeziumConnectorConfig.DoesNotExist:
#             # any user can only request configs that exist
#             raise NotFoundException()
#
#         if debezium_connector_config.user != info.context.user:
#             # any user can only request configs associated to itself
#             raise ForbiddenException()
#
#         return debezium_connector_config
#
#     all_debezium_connector_configs = graphene.Field(graphene.List(DebeziumConnectorConfigType))
#
#     @classmethod
#     def resolve_all_debezium_connector_configs(cls, root, info, **kwargs):
#         if not isinstance(info.context.user, User):
#             # any user needs to be authenticated
#             raise UnauthorizedException()
#
#         # any user can only request configs associated to itself
#         all_debezium_connector_configs = DebeziumConnectorConfig.objects.filter(user=info.context.user)
#
#         return all_debezium_connector_configs
#
#
# class CreateDebeziumConnectorConfig(graphene.Mutation):
#     class Arguments:
#         connector_class = graphene.String(required=True)
#         tasks_max = graphene.Int(required=True)
#         database_hostname = graphene.String(required=True)
#         database_port = graphene.Int(required=True)
#         database_user = graphene.String(required=True)
#         database_password = graphene.String(required=True)
#         database_server_id = graphene.Int(required=True)
#         database_server_name = graphene.String(required=True)
#         database_whitelist = graphene.String(required=True)
#         database_history_kafka_bootstrap_servers = graphene.String(required=True)
#         database_history_kafka_topic = graphene.String(required=True)
#
#     debezium_connector_config = graphene.Field(DebeziumConnectorConfigType)
#
#     @classmethod
#     def mutate(cls, root, info, **kwargs):
#         if not isinstance(info.context.user, User):
#             # any user needs to be authenticated
#             raise UnauthorizedException()
#
#         create_kwargs = dict(kwargs)
#
#         create_kwargs['user_id'] = info.context.user.id
#
#         debezium_connector_config = DebeziumConnectorConfig()
#
#         for key, value in create_kwargs.items():
#             setattr(debezium_connector_config, key, value)
#
#         debezium_connector_config.save()
#
#         return CreateDebeziumConnectorConfig(debezium_connector_config=debezium_connector_config)
#
#
# class UpdateDebeziumConnectorConfig(graphene.Mutation):
#     class Arguments:
#         id = IntID(required=True)
#         connector_class = graphene.String()
#         tasks_max = graphene.Int()
#         database_hostname = graphene.String()
#         database_port = graphene.Int()
#         database_user = graphene.String()
#         database_password = graphene.String()
#         database_server_id = graphene.Int()
#         database_server_name = graphene.String()
#         database_whitelist = graphene.String()
#         database_history_kafka_bootstrap_servers = graphene.String()
#         database_history_kafka_topic = graphene.String()
#
#     debezium_connector_config = graphene.Field(DebeziumConnectorConfigType)
#
#     @classmethod
#     def mutate(cls, root, info, **kwargs):
#         if not isinstance(info.context.user, User):
#             # any user needs to be authenticated
#             raise UnauthorizedException()
#
#         update_kwargs = dict(kwargs)
#
#         try:
#             debezium_connector_config = DebeziumConnectorConfig.objects.get(pk=kwargs.get('id'))
#         except DebeziumConnectorConfig.DoesNotExist:
#             # any user can only update configs that exist
#             raise NotFoundException()
#
#         if debezium_connector_config.user != info.context.user:
#             # any user can only update configs associated to itself
#             raise ForbiddenException()
#
#         for key, value in update_kwargs.items():
#             setattr(debezium_connector_config, key, value)
#
#         debezium_connector_config.save()
#
#         return UpdateDebeziumConnectorConfig(debezium_connector_config=debezium_connector_config)
#
#
# class DeleteDebeziumConnectorConfig(graphene.Mutation):
#     class Arguments:
#         id = IntID(required=True)
#
#     debezium_connector_config = graphene.Field(DebeziumConnectorConfigType)
#
#     @classmethod
#     def mutate(cls, root, info, **kwargs):
#         if not isinstance(info.context.user, User):
#             # any user needs to be authenticated
#             raise UnauthorizedException()
#
#         try:
#             debezium_connector_config = DebeziumConnectorConfig.objects.get(pk=kwargs.get('id'))
#         except DebeziumConnectorConfig.DoesNotExist:
#             # any user can only delete configs that exist
#             raise NotFoundException()
#
#         if debezium_connector_config.user != info.context.user:
#             # any user can only delete configs associated to itself
#             raise ForbiddenException()
#
#         if hasattr(debezium_connector_config, 'connector'):
#             # any connector must have a config associated to itself
#             raise ConflictException()
#
#         debezium_connector_config.delete()
#
#         return DeleteDebeziumConnectorConfig(debezium_connector_config=None)
#
#
# class DebeziumConnectorConfigMutation(object):
#     create_debezium_connector_config = CreateDebeziumConnectorConfig.Field()
#     update_debezium_connector_config = UpdateDebeziumConnectorConfig.Field()
#     delete_debezium_connector_config = DeleteDebeziumConnectorConfig.Field()
