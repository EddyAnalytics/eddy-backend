# Generated by Django 2.2.6 on 2019-10-08 13:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Workspace',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('label', models.CharField(max_length=200)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to=settings.AUTH_USER_MODEL)),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='workspaces.Workspace')),
            ],
        ),
    ]
