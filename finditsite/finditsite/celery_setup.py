import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finditsite.settings')

app = Celery('finditsite')

app.config_from_object('django.conf:settings', namespace='CELERY')

app = Celery('finditsite', broker='amqp://guest@localhost//', backend='rpc://')

app.autodiscover_tasks([
    'finditsite.1_better',
])

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)  # lambda: settings.INSTALLED_APPS
