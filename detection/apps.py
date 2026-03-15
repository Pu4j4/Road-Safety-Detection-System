from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class DetectionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'detection'
    verbose_name = 'Road Safety Detection System'

    def ready(self):
        try:
            from detection.ml_service import load_models
            load_models()
        except Exception as e:
            logger.error(f"Failed to load ML models on startup: {e}")