from rest_framework import serializers
from .models import DetectionRecord, AlertLog


class AlertLogSerializer(serializers.ModelSerializer):
    class Meta:
        model  = AlertLog
        fields = ['id', 'phone_number', 'message_sid', 'message_body', 'success', 'error_message', 'sent_at']
        read_only_fields = fields


class DetectionRecordSerializer(serializers.ModelSerializer):
    alerts          = AlertLogSerializer(many=True, read_only=True)
    input_filename  = serializers.ReadOnlyField()
    result_filename = serializers.ReadOnlyField()
    input_file_url  = serializers.SerializerMethodField()
    result_file_url = serializers.SerializerMethodField()

    class Meta:
        model  = DetectionRecord
        fields = [
            'id', 'detection_type', 'media_type', 'status',
            'input_file', 'input_filename', 'input_file_url',
            'result_file', 'result_filename', 'result_file_url',
            'pothole_count', 'pothole_detected',
            'alert_sent', 'alert_sent_at',
            'processing_time_ms', 'error_message',
            'created_at', 'updated_at', 'alerts',
        ]
        read_only_fields = [
            'status', 'pothole_count', 'pothole_detected',
            'alert_sent', 'alert_sent_at', 'processing_time_ms',
            'error_message', 'created_at', 'updated_at',
        ]

    def get_input_file_url(self, obj):
        request = self.context.get('request')
        if obj.input_file and request:
            return request.build_absolute_uri(obj.input_file.url)
        return None

    def get_result_file_url(self, obj):
        request = self.context.get('request')
        if obj.result_file and request:
            return request.build_absolute_uri(obj.result_file.url)
        return None


class PotholeDetectionInputSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        allowed = [
            'image/jpeg', 'image/png', 'image/jpg',
            'video/mp4', 'video/avi', 'video/quicktime', 'video/x-msvideo',
        ]
        if value.content_type not in allowed:
            raise serializers.ValidationError(
                f"Unsupported file type: {value.content_type}. Allowed: jpg, png, mp4, avi"
            )
        return value


class LaneDetectionInputSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        allowed = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-msvideo']
        if value.content_type not in allowed:
            raise serializers.ValidationError(
                f"Unsupported file type: {value.content_type}. Lane detection requires a video (mp4, avi, mov)."
            )
        return value


class AlertInputSerializer(serializers.Serializer):
    detection_id = serializers.IntegerField()

    def validate_detection_id(self, value):
        try:
            record = DetectionRecord.objects.get(id=value)
        except DetectionRecord.DoesNotExist:
            raise serializers.ValidationError(f"Detection record #{value} not found.")
        if not record.pothole_detected:
            raise serializers.ValidationError("No potholes detected in this record. Cannot send alert.")
        return value
