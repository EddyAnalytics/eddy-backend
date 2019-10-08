# Generated by Django 2.2.6 on 2019-10-08 13:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('workspaces', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Dashboard',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('label', models.CharField(max_length=200)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dashboards', to='workspaces.Project')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dashboards', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WidgetType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('label', models.CharField(max_length=200)),
                ('json_config', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Widget',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('label', models.CharField(max_length=200)),
                ('json_config', models.CharField(max_length=200)),
                ('dashboard', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='widgets', to='dashboards.Dashboard')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='widgets', to=settings.AUTH_USER_MODEL)),
                ('widget_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='widgets', to='dashboards.WidgetType')),
            ],
        ),
    ]