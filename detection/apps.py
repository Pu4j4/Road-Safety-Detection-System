from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class DetectionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'detection'
    verbose_name = 'Road Safety Detection System'

    def ready(self):
        try:
            # Download models from Google Drive if not present
            from download_models import download_models
            download_models()
        except Exception as e:
            logger.error(f"Model download failed: {e}")

        try:
            # Load models into memory
            from detection.ml_service import load_models
            load_models()
        except Exception as e:
            logger.error(f"Model loading failed: {e}")
