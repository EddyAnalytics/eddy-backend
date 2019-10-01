from celery import Celery

app = Celery('eddy_backend')

app.config_from_object('django.conf:settings', namespace='CELERY')
