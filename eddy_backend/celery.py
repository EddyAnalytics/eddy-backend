from celery import Celery

app = Celery('eddy_backend')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.update({'task_routes': {
    'app.submit_beam_sql': {'queue': 'beam'},
    'app.submit_flink_sql': {'queue': 'flink'},
    'app.csv_to_kafka': {'queue': 'csv-connector'}

}, })
