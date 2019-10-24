from django.test import TestCase
from graphene import Context
from graphene.test import Client

import schema
from authentication.models import User
from workspaces.models import Workspace


class UserModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='user', password='user', is_superuser=False)
        cls.admin_user = User.objects.create(username='admin', password='admin', is_superuser=True)

    def test_create_user_as_user(self):
        client = Client(schema.schema)
        with open('authentication/tests/create_user_as_user.graphql', 'r') as query_file:
            query = query_file.read()
        count_before = User.objects.count()
        executed = client.execute(query, context=Context(user=self.user))
        self.assertEquals(executed, {
            'errors': [
                {
                    'message': 'User not authorized.',
                    'locations': [
                        {
                            'line': 2,
                            'column': 5
                        }
                    ],
                    'path':
                        [
                            'createUser'
                        ]
                }
            ],
            'data': {
                'createUser': None
            }
        })
        count_after = User.objects.count()
        self.assertEquals(count_after, count_before)

    def test_create_user_as_admin_user(self):
        client = Client(schema.schema)
        with open('authentication/tests/create_user_as_admin_user.graphql', 'r') as query_file:
            query = query_file.read()
        executed = client.execute(query, context=Context(user=self.admin_user))
        created_user_id = executed['data']['createUser']['user']['id']
        self.assertEquals(executed, {
            'data': {
                'createUser': {
                    'user': {
                        'id': created_user_id,
                        'username': 'as_admin_user',
                        'isSuperuser': True
                    }
                }
            }
        })
        user = User.objects.get(id=created_user_id)
        self.assertEquals(user.username, 'as_admin_user')
        self.assertTrue(user.check_password('as_admin_user'))
        self.assertTrue(user.is_superuser)
        self.assertEquals(user.is_staff, user.is_superuser)
        self.assertTrue(hasattr(user, 'workspace'))
        workspace = user.workspace
        self.assertEquals(workspace.id, 3)

    def test_delete_created_user_as_user(self):
        client = Client(schema.schema)
        with open('authentication/tests/create_user_as_admin_user.graphql', 'r') as query_file:
            query = query_file.read()
        executed = client.execute(query, context=Context(user=self.admin_user))
        created_user_id = executed['data']['createUser']['user']['id']

        with open('authentication/tests/delete_created_user_as_user.graphql', 'r') as query_file:
            query = query_file.read()
        executed = client.execute(query, variables={'id': created_user_id}, context=Context(user=self.user))
        self.assertEquals(executed, {
            'errors': [
                {
                    'message': 'User not authorized.',
                    'locations': [
                        {
                            'line': 2,
                            'column': 5
                        }
                    ],
                    'path':
                        [
                            'deleteUser'
                        ]
                }
            ],
            'data': {
                'deleteUser': None
            }
        })
        user = User.objects.get(id=created_user_id)
        self.assertEquals(user.username, 'as_admin_user')
        self.assertTrue(user.check_password('as_admin_user'))
        self.assertTrue(user.is_superuser)
        self.assertEquals(user.is_staff, user.is_superuser)
        self.assertTrue(hasattr(user, 'workspace'))
        workspace = user.workspace
        self.assertEquals(workspace.id, created_user_id)

    def test_delete_created_user_as_admin_user(self):
        client = Client(schema.schema)
        with open('authentication/tests/create_user_as_admin_user.graphql', 'r') as query_file:
            query = query_file.read()
        executed = client.execute(query, context=Context(user=self.admin_user))
        created_user_id = executed['data']['createUser']['user']['id']

        with open('authentication/tests/delete_created_user_as_admin_user.graphql', 'r') as query_file:
            query = query_file.read()
        executed = client.execute(query, variables={'id': created_user_id}, context=Context(user=self.admin_user))
        print(executed)
        self.assertEquals(executed, {
            'data': {
                'deleteUser': {
                    'id': created_user_id
                }
            }
        })
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=created_user_id)
        with self.assertRaises(Workspace.DoesNotExist):
            Workspace.objects.get(id=created_user_id)
