# Generated by Django 2.2.5 on 2019-09-26 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('debezium_connectors', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='debeziumconnector',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='debeziumconnectorconfig',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]