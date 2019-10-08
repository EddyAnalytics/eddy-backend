import graphene
from graphene_django import DjangoObjectType

from authentication.models import User
from utils.exceptions import UnauthorizedException, NotFoundException, ForbiddenException
from utils.utils import IntID


# User
class UserType(DjangoObjectType):
    class Meta:
        model = User
        exclude = ('id', 'password')

    id = IntID(required=True)


class UserQuery(graphene.ObjectType):
    user = graphene.Field(UserType, id=IntID(required=True))

    @classmethod
    def resolve_user(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        try:
            user = User.objects.get(pk=kwargs.get('id'))
        except User.DoesNotExist:
            # any user can only request users that exist
            raise NotFoundException()

        # any superuser can request any user
        if not info.context.user.is_superuser:
            # any user can only request users associated to itself
            if user != info.context.user:
                raise ForbiddenException()

        return user

    all_users = graphene.Field(graphene.List(UserType))

    @classmethod
    def resolve_all_users(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        if not info.context.user.is_superuser:
            # any user can only request connectors associated to itself
            all_users = User.objects.filter(pk=info.context.user.id)
        else:
            # any superuser can request any user
            all_users = User.objects.all()

        return all_users


class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        is_superuser = graphene.Boolean(required=True)

    user = graphene.Field(UserType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        create_kwargs = dict(kwargs)

        del create_kwargs['password']

        if not info.context.user.is_superuser:
            raise ForbiddenException()

        user = User()

        for key, value in create_kwargs.items():
            setattr(user, key, value)

        user.set_password(kwargs.get('password'))

        user.save()

        return CreateUser(user=user)


class UpdateUser(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        is_superuser = graphene.Boolean(required=True)

    user = graphene.Field(UserType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        update_kwargs = dict(kwargs)

        del update_kwargs['password']

        try:
            user = User.objects.get(pk=kwargs.get('id'))
        except User.DoesNotExist:
            # any superuser can only update users that exist
            raise NotFoundException()

        # any superuser can update any user
        if not info.context.user.is_superuser:
            # non superusers can update anything but the is_superuser state
            del update_kwargs['is_superuser']
            # any user can only update users associated to itself
            if user != info.context.user:
                raise ForbiddenException()

        for key, value in update_kwargs.items():
            setattr(user, key, value)

        user.set_password(kwargs.get('password'))

        user.save()

        return UpdateUser(user=user)


class DeleteUser(graphene.Mutation):
    class Arguments:
        id = IntID(required=True)

    user = graphene.Field(UserType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            # any user needs to be authenticated
            raise UnauthorizedException()

        try:
            user = User.objects.get(pk=kwargs.get('id'))
        except User.DoesNotExist:
            raise NotFoundException()

        # any superuser can delete any user
        if not info.context.user.is_superuser:
            # any user can only delete users associated to itself
            if user != info.context.user:
                raise ForbiddenException()

        user.delete()

        return DeleteUser(user=user)


class UserMutation(object):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()


query_list = [UserQuery]
mutation_list = [UserMutation]
