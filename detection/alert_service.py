import logging
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def send_pothole_alert(detection_record):
    from .models import AlertLog

    message_body = (
        f"🚨 Pothole Alert!\n"
        f"Potholes detected in uploaded {'video' if detection_record.media_type == 'video' else 'image'}.\n"
        f"Count: {detection_record.pothole_count}\n"
        f"Detection ID: #{detection_record.id}\n"
        f"Time: {detection_record.created_at.strftime('%Y-%m-%d %H:%M IST')}\n"
        f"Please investigate and arrange repair."
    )

    try:
        from twilio.rest import Client
        client  = Client(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message_body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=settings.MUNICIPALITY_PHONE,
        )
        alert = AlertLog.objects.create(
            detection=detection_record, phone_number=settings.MUNICIPALITY_PHONE,
            message_sid=message.sid, message_body=message_body, success=True,
        )
        detection_record.alert_sent    = True
        detection_record.alert_sent_at = timezone.now()
        detection_record.save(update_fields=['alert_sent', 'alert_sent_at'])
        logger.info(f"✅ SMS sent. SID: {message.sid}")
        return {'success': True, 'message_sid': message.sid, 'alert_id': alert.id}

    except Exception as e:
        AlertLog.objects.create(
            detection=detection_record, phone_number=settings.MUNICIPALITY_PHONE,
            message_sid='', message_body=message_body, success=False, error_message=str(e),
        )
        return {'success': False, 'error': str(e)}
