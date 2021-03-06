import json

import graphene
from graphene_django import DjangoObjectType

import eddy_backend.celery
from authentication.models import User
from authentication.schema import UserType
from pipelines import models
from pipelines.models import Pipeline, Block
from projects.models import Project
from utils.exceptions import UnauthorizedException, NotFoundException, ForbiddenException
from utils.utils import IntID


# Pipeline
class PipelineType(DjangoObjectType):
    class Meta:
        model = Pipeline
        exclude = ('id', 'user')

    id = IntID(required=True)
    user = graphene.Field(UserType, required=True)


class PipelineQuery(graphene.ObjectType):
    pipeline = graphene.Field(PipelineType, id=IntID(required=True))

    @classmethod
    def resolve_pipeline(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        try:
            pipeline = Pipeline.objects.get(pk=kwargs.get('id'))
        except Pipeline.DoesNotExist:
            # any user can only request pipelines that exist
            raise NotFoundException()

        # any user can only request pipelines associated to itself
        if pipeline.user != info.context.user:
            raise ForbiddenException()

        return pipeline

    all_pipelines = graphene.Field(graphene.List(PipelineType))

    @classmethod
    def resolve_all_pipelines(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        # any user can only request pipelines associated to itself
        all_pipelines = Pipeline.objects.filter(user=info.context.user)

        return all_pipelines


class CreatePipeline(graphene.Mutation):
    class Arguments:
        project_id = IntID(required=True)
        label = graphene.String(required=True)

    pipeline = graphene.Field(PipelineType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        create_kwargs = dict(kwargs)

        create_kwargs['user'] = info.context.user

        try:
            project = Project.objects.get(pk=kwargs.get('project_id'))
        except Project.DoesNotExist:
            # any user can only create a pipeline if it associates it to a project
            raise NotFoundException()

        if project.user != info.context.user:
            raise ForbiddenException()

        del create_kwargs['project_id']
        create_kwargs['project'] = project

        pipeline = Pipeline()

        for key, value in create_kwargs.items():
            setattr(pipeline, key, value)

        pipeline.save()

        return CreatePipeline(pipeline=pipeline)


class UpdatePipeline(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)
        label = graphene.String()
        config = graphene.JSONString()

    pipeline = graphene.Field(PipelineType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        update_kwargs = dict(kwargs)

        try:
            pipeline = Pipeline.objects.get(pk=kwargs.get('id'))
        except Pipeline.DoesNotExist:
            # any user can only update pipelines that exist
            raise NotFoundException()

        for key, value in update_kwargs.items():
            setattr(pipeline, key, value)

        pipeline.save()

        return UpdatePipeline(pipeline=pipeline)


class DeletePipeline(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)

    id = graphene.Field(IntID)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        try:
            pipeline = Pipeline.objects.get(pk=kwargs.get('id'))
        except Pipeline.DoesNotExist:
            # any user can only update pipelines that exist
            raise NotFoundException()

        if pipeline.user != info.context.user:
            # any user can only delete pipelines associated to itself
            raise ForbiddenException()

        pipeline.delete()

        return DeletePipeline(id=kwargs.get('id'))


class PipelineMutation(object):
    create_pipeline = CreatePipeline.Field()
    update_pipeline = UpdatePipeline.Field()
    delete_pipeline = DeletePipeline.Field()


# Block
class BlockType(DjangoObjectType):
    class Meta:
        model = Block
        exclude = ('id', 'user')

    id = IntID(required=True)
    user = graphene.Field(UserType, required=True)


class BlockQuery(graphene.ObjectType):
    block = graphene.Field(BlockType, id=IntID(required=True))

    @classmethod
    def resolve_block(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        try:
            block = Block.objects.get(pk=kwargs.get('id'))
        except Block.DoesNotExist:
            # any user can only request blocks that exist
            raise NotFoundException()

        # any user can only request blocks associated to itself
        if block.user != info.context.user:
            raise ForbiddenException()

        return block

    all_blocks = graphene.Field(graphene.List(BlockType))

    @classmethod
    def resolve_all_blocks(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        # any user can only request blocks associated to itself
        all_blocks = Block.objects.filter(user=info.context.user)

        return all_blocks


class CreateBlock(graphene.Mutation):
    class Arguments:
        pipeline_id = IntID(required=True)
        label = graphene.String(required=True)
        block_type_id = IntID(required=True)
        config = graphene.JSONString(required=True)

    block = graphene.Field(BlockType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        create_kwargs = dict(kwargs)

        create_kwargs['user'] = info.context.user

        try:
            pipeline = Pipeline.objects.get(pk=kwargs.get('pipeline_id'))
        except Pipeline.DoesNotExist:
            # any user can only create a block if it associates it to a pipeline
            raise NotFoundException()

        if pipeline.user != info.context.user:
            raise ForbiddenException()

        del create_kwargs['pipeline_id']
        create_kwargs['pipeline'] = pipeline

        try:
            block_type = models.BlockType.objects.get(pk=kwargs.get('block_type_id'))
        except models.BlockType.DoesNotExist:
            # any user can only create a block if it associates it to a block_type
            raise NotFoundException()

        del create_kwargs['block_type_id']
        create_kwargs['block_type'] = block_type

        block = Block()

        for key, value in create_kwargs.items():
            setattr(block, key, value)

        block.save()

        return CreateBlock(block=block)


class UpdateBlock(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)
        label = graphene.String()
        config = graphene.JSONString()

    block = graphene.Field(BlockType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        update_kwargs = dict(kwargs)

        try:
            block = Block.objects.get(pk=kwargs.get('id'))
        except Block.DoesNotExist:
            # any user can only update blocks that exist
            raise NotFoundException()

        if block.user != info.context.user:
            # any user can only update blocks associated to itself
            raise ForbiddenException()

        for key, value in update_kwargs.items():
            setattr(block, key, value)

        block.save()

        return UpdateBlock(block=block)


class DeleteBlock(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)

    id = graphene.Field(IntID)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        try:
            block = Block.objects.get(pk=kwargs.get('id'))
        except Block.DoesNotExist:
            # any user can only delete blocks that exist
            raise NotFoundException()

        if block.user != info.context.user:
            # any user can only delete blocks associated to itself
            raise ForbiddenException()

        block.delete()

        return DeleteBlock(id=kwargs.get('id'))


class BlockMutation(object):
    create_block = CreateBlock.Field()
    update_block = UpdateBlock.Field()
    delete_block = DeleteBlock.Field()


# BlockType
class BlockTypeType(DjangoObjectType):
    class Meta:
        model = models.BlockType
        exclude = ('id', 'blocks')

    id = IntID(required=True)


class BlockTypeQuery(graphene.ObjectType):
    block_type = graphene.Field(BlockTypeType, id=IntID(required=True))

    @classmethod
    def resolve_block_type(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        try:
            block_type = models.BlockType.objects.get(pk=kwargs.get('id'))
        except models.BlockType.DoesNotExist:
            # any user can only request block_types that exist
            raise NotFoundException()

        return block_type

    all_block_types = graphene.Field(graphene.List(BlockTypeType))

    @classmethod
    def resolve_all_block_types(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        all_block_types = models.BlockType.objects.filter()

        return all_block_types


class CreateBlockType(graphene.Mutation):
    class Arguments:
        label = graphene.String(required=True)
        config = graphene.JSONString(required=True)

    block_type = graphene.Field(BlockTypeType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        create_kwargs = dict(kwargs)

        if not info.context.user.is_superuser:
            # only superusers can create block_types
            raise ForbiddenException()

        block_type = models.BlockType()

        for key, value in create_kwargs.items():
            setattr(block_type, key, value)

        block_type.save()

        return CreateBlockType(block_type=block_type)


class UpdateBlockType(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)
        label = graphene.String()
        config = graphene.JSONString()

    block_type = graphene.Field(BlockTypeType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        update_kwargs = dict(kwargs)

        if not info.context.user.is_superuser:
            # only superusers can update block_types
            raise ForbiddenException()

        try:
            block_type = models.BlockType.objects.get(pk=kwargs.get('id'))
        except models.BlockType.DoesNotExist:
            # any superuser can only update block_types that exist
            raise NotFoundException()

        for key, value in update_kwargs.items():
            setattr(block_type, key, value)

        block_type.save()

        return CreateBlockType(block_type=block_type)


class DeleteBlockType(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)

    id = graphene.Field(IntID)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        if not info.context.user.is_superuser:
            # only superusers can delete block_types
            raise ForbiddenException()

        try:
            block_type = models.BlockType.objects.get(pk=kwargs.get('id'))
        except models.BlockType.DoesNotExist:
            # any superuser can only delete block_types that exist
            raise NotFoundException()

        block_type.delete()

        return DeleteBlockType(id=kwargs.get('id'))


class BlockTypeMutation(object):
    create_block_type = CreateBlockType.Field()
    update_block_type = UpdateBlockType.Field()
    delete_block_type = DeleteBlockType.Field()


class SendCeleryTask(graphene.Mutation):
    class Arguments:
        task_type = graphene.String(required=True)
        config = graphene.JSONString(required=True)

    ok = graphene.Field(graphene.Boolean)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if kwargs.get('task_type') == 'flink':
            eddy_backend.celery.app.send_task('app.submit_flink_sql', (json.dumps(kwargs.get('config')),))
        elif kwargs.get('task_type') == 'beam':
            eddy_backend.celery.app.send_task('app.submit_beam_sql', (json.dumps(kwargs.get('config')),))
        elif kwargs.get('task_type') == 'beam-python':
            eddy_backend.celery.app.send_task('app.submit_beam_python', (json.dumps(kwargs.get('config')),))
        else:
            raise NotFoundException()

        return SendCeleryTask(ok=True)


class SendCeleryTaskMutation(object):
    send_celery_task = SendCeleryTask.Field()


query_list = [PipelineQuery, BlockQuery, BlockTypeQuery]
mutation_list = [PipelineMutation, BlockMutation, BlockTypeMutation, SendCeleryTaskMutation]
