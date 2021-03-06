from django.db import models
from django_mysql.models import JSONField


class Dashboard(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('authentication.User', related_name='dashboards', on_delete=models.CASCADE)
    project = models.ForeignKey('projects.Project', related_name='dashboards', on_delete=models.CASCADE)
    label = models.CharField(max_length=200)

    def __str__(self):
        return self.label


class Widget(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('authentication.User', related_name='widgets', on_delete=models.CASCADE)
    dashboard = models.ForeignKey('dashboards.Dashboard', related_name='widgets', on_delete=models.CASCADE)
    label = models.CharField(max_length=200)
    widget_type = models.ForeignKey('dashboards.WidgetType', related_name='widgets', on_delete=models.CASCADE)
    config = JSONField()

    def __str__(self):
        return self.label


class WidgetType(models.Model):
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=200)
    config = JSONField()

    def __str__(self):
        return self.label
