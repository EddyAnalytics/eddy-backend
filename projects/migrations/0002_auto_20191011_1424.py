# Generated by Django 2.2.6 on 2019-10-11 14:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dataconnectortype',
            old_name='schema',
            new_name='config',
        ),
    ]