import os
import tempfile
import logging
from django.core.files.base import ContentFile
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import AllowAny

from .models import DetectionRecord, AlertLog
from .serializers import (
    DetectionRecordSerializer,
    PotholeDetectionInputSerializer,
    LaneDetectionInputSerializer,
    AlertInputSerializer,
)

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class PotholeDetectionAPIView(APIView):
    """POST /api/detect/pothole/ — Upload image or video for pothole detection."""
    authentication_classes = []
    permission_classes     = [AllowAny]
    parser_classes         = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = PotholeDetectionInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = serializer.validated_data['file']
        is_image      = 'image' in uploaded_file.content_type
        media_type    = 'image' if is_image else 'video'
        ext           = os.path.splitext(uploaded_file.name)[1] or ('.jpg' if is_image else '.mp4')

        record = DetectionRecord.objects.create(
            detection_type=('pothole'),
            media_type=media_type,
            input_file=uploaded_file,
            status='processing',
        )

        try:
            from .ml_service import detect_potholes_image, detect_potholes_video

            input_path      = record.input_file.path
            result_filename = f"pothole_result_{record.id}{ext}"

            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                tmp_path = tmp.name

            meta = detect_potholes_image(input_path, tmp_path) if is_image else detect_potholes_video(input_path, tmp_path)

            with open(tmp_path, 'rb') as f:
                record.result_file.save(result_filename, ContentFile(f.read()), save=False)
            os.unlink(tmp_path)

            record.status             = 'completed'
            record.pothole_count      = meta['pothole_count']
            record.pothole_detected   = meta['pothole_detected']
            record.processing_time_ms = meta['processing_time_ms']
            record.save()

            out = DetectionRecordSerializer(record, context={'request': request})
            return Response({
                'success': True,
                'message': f"{'Potholes detected!' if meta['pothole_detected'] else 'No potholes found.'} ({meta['pothole_count']} detections)",
                'data': out.data,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.exception("Pothole detection failed")
            record.status        = 'failed'
            record.error_message = str(e)
            record.save()
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class LaneDetectionAPIView(APIView):
    """POST /api/detect/lane/ — Upload video for lane detection."""
    authentication_classes = []
    permission_classes     = [AllowAny]
    parser_classes         = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = LaneDetectionInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = serializer.validated_data['file']
        ext           = os.path.splitext(uploaded_file.name)[1] or '.mp4'

        record = DetectionRecord.objects.create(
            detection_type='lane',
            media_type='video',
            input_file=uploaded_file,
            status='processing',
        )

        try:
            from .ml_service import detect_lanes_video

            input_path      = record.input_file.path
            result_filename = f"lane_result_{record.id}{ext}"

            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                tmp_path = tmp.name

            meta = detect_lanes_video(input_path, tmp_path)

            with open(tmp_path, 'rb') as f:
                record.result_file.save(result_filename, ContentFile(f.read()), save=False)
            os.unlink(tmp_path)

            record.status             = 'completed'
            record.processing_time_ms = meta['processing_time_ms']
            record.save()

            out = DetectionRecordSerializer(record, context={'request': request})
            return Response({
                'success': True,
                'message': f"Lane detection complete. Processed {meta['frames_processed']} frames.",
                'data': out.data,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.exception("Lane detection failed")
            record.status        = 'failed'
            record.error_message = str(e)
            record.save()
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class SendAlertAPIView(APIView):
    """POST /api/alert/send/ — Send Twilio SMS alert to municipality."""
    authentication_classes = []
    permission_classes     = [AllowAny]

    def post(self, request):
        serializer = AlertInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        record = DetectionRecord.objects.get(id=serializer.validated_data['detection_id'])

        from .alert_service import send_pothole_alert
        result = send_pothole_alert(record)

        if result['success']:
            return Response({
                'success': True,
                'message': f"Alert sent to municipality! SID: {result['message_sid']}",
                'alert_id': result['alert_id'],
            })
        return Response({'success': False, 'error': result['error']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DetectionHistoryAPIView(generics.ListAPIView):
    """GET /api/history/ — Paginated detection history. Params: ?type=pothole|lane &status=completed|failed"""
    serializer_class = DetectionRecordSerializer

    def get_queryset(self):
        qs = DetectionRecord.objects.all()
        if t := self.request.query_params.get('type'):
            qs = qs.filter(detection_type=t)
        if s := self.request.query_params.get('status'):
            qs = qs.filter(status=s)
        return qs

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


class DetectionDetailAPIView(generics.RetrieveAPIView):
    """GET /api/history/<id>/ — Single detection record detail."""
    queryset         = DetectionRecord.objects.all()
    serializer_class = DetectionRecordSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


class DashboardStatsAPIView(APIView):
    """GET /api/stats/ — Dashboard summary statistics."""

    def get(self, request):
        from django.db.models import Sum, Avg

        recent     = DetectionRecord.objects.order_by('-created_at')[:5]
        recent_data = DetectionRecordSerializer(recent, many=True, context={'request': request}).data

        return Response({
            'total_detections':    DetectionRecord.objects.count(),
            'pothole_detections':  DetectionRecord.objects.filter(detection_type='pothole').count(),
            'lane_detections':     DetectionRecord.objects.filter(detection_type='lane').count(),
            'alerts_sent':         DetectionRecord.objects.filter(alert_sent=True).count(),
            'total_potholes_found': DetectionRecord.objects.aggregate(s=Sum('pothole_count'))['s'] or 0,
            'avg_processing_time_ms': round(v, 1) if (v := DetectionRecord.objects.filter(
                status='completed', processing_time_ms__isnull=False
            ).aggregate(a=Avg('processing_time_ms'))['a']) else None,
            'recent_detections':   recent_data,
        })