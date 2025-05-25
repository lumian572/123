# spider_qunaer/django_setup.py
import os
import django

def setup_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hunan_web.settings')
    django.setup()