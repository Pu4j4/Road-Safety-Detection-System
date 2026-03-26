web: python download_models.py && python manage.py migrate && gunicorn road_safety_detection_system.wsgi --bind 0.0.0.0:$PORT --workers 1 --timeout 120
