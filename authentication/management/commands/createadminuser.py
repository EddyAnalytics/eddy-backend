from django.core.management.base import BaseCommand

import authentication.models


class Command(BaseCommand):
    help = 'Creates default admin user'

    def handle(self, *args, **options):
        if len(authentication.models.User.objects.all()) == 0:
            admin_user = authentication.models.User()
            admin_user.username = 'admin'
            admin_user.set_password('admin')
            admin_user.is_superuser = True
            admin_user.save()
            self.stdout.write('Admin user created')
        else:
            self.stdout.write('Admin user already exists')
