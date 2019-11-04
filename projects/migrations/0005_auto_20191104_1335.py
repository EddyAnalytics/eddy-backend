# Generated by Django 2.2.6 on 2019-11-04 13:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_auto_20191016_1732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataconnectortype',
            name='integration',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='data_connector_types', to='integrations.Integration'),
        ),
    ]
