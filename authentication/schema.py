import graphene
from graphene_django import DjangoObjectType

from authentication.models import User
from utils.exceptions import UnauthorizedException, NotFoundException, ForbiddenException
from utils.utils import IntID


# User
class UserType(DjangoObjectType):
    class Meta:
        model = User
        exclude = ('password', 'last_login', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined',
                   'id', 'groups', 'user_permisisons')

    id = IntID(required=True)


class UserQuery(graphene.ObjectType):
    """
    A normal user can only query itself.
    A super user can query any user.
    """
    user = graphene.Field(UserType, id=IntID(required=True))

    @classmethod
    def resolve_user(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            raise UnauthorizedException()

        try:
            user = User.objects.get(pk=kwargs.get('id'))
        except User.DoesNotExist:
            raise NotFoundException()

        if not info.context.user.is_superuser:
            if user != info.context.user:
                raise ForbiddenException()

        return user

    """
    A normal user can only query itself.
    A super user can query any user.
    """
    all_users = graphene.Field(graphene.List(UserType))

    @classmethod
    def resolve_all_users(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            raise UnauthorizedException()

        if not info.context.user.is_superuser:
            all_users = User.objects.filter(pk=info.context.user.id)
        else:
            all_users = User.objects.all()

        return all_users


class CreateUser(graphene.Mutation):
    """
    A normal user can not create users.
    A super user can create users.
    """

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        is_superuser = graphene.Boolean(required=True)

    user = graphene.Field(UserType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            raise UnauthorizedException()

        if not info.context.user.is_superuser:
            raise ForbiddenException()

        user = User()

        create_kwargs = dict(kwargs)

        del create_kwargs['password']

        for key, value in create_kwargs.items():
            setattr(user, key, value)

        user.set_password(kwargs.get('password'))

        user.is_staff = user.is_superuser

        user.save()

        return CreateUser(user=user)


class UpdateUser(graphene.Mutation):
    """
    A normal user can only update itself.
    A normal user can not update super user status.
    A super user can update any users.
    A super user can update super user status.
    """

    class Arguments:
        id = IntID(required=True)
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        is_superuser = graphene.Boolean(required=True)

    user = graphene.Field(UserType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            raise UnauthorizedException()

        try:
            user = User.objects.get(pk=kwargs.get('id'))
        except User.DoesNotExist:
            raise NotFoundException()

        if not info.context.user.is_superuser:
            if user != info.context.user:
                raise ForbiddenException()

        update_kwargs = dict(kwargs)

        if not info.context.user.is_superuser:
            del update_kwargs['is_superuser']

        del update_kwargs['password']

        for key, value in update_kwargs.items():
            setattr(user, key, value)

        user.set_password(kwargs.get('password'))

        user.is_staff = user.is_superuser

        user.save()

        return UpdateUser(user=user)


class DeleteUser(graphene.Mutation):
    """
    A normal user can only delete itself.
    A super user can delete any users.
    """

    class Arguments:
        id = IntID(required=True)

    id = graphene.Field(IntID)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if not isinstance(info.context.user, User):
            raise UnauthorizedException()

        try:
            user = User.objects.get(pk=kwargs.get('id'))
        except User.DoesNotExist:
            raise NotFoundException()

        if not info.context.user.is_superuser:
            if user != info.context.user:
                raise ForbiddenException()

        user.delete()

        return DeleteUser(id=kwargs.get('id'))


class UserMutation(object):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()


query_list = [UserQuery]
mutation_list = [UserMutation]
