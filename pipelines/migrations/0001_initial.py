# Generated by Django 2.2.6 on 2019-10-09 13:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_mysql.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlockType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('label', models.CharField(max_length=200)),
                ('config', django_mysql.models.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='Pipeline',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('label', models.CharField(max_length=200)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pipelines', to='projects.Project')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pipelines', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('label', models.CharField(max_length=200)),
                ('config', django_mysql.models.JSONField(default=dict)),
                ('block_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocks', to='pipelines.BlockType')),
                ('pipeline', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocks', to='pipelines.Pipeline')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocks', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
