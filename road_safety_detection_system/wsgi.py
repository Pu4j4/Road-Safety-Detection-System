import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'road_safety_detection_system.settings')
application = get_wsgi_application()
