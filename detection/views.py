from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from .models import DetectionRecord


def dashboard(request):
    context = {
        'total':          DetectionRecord.objects.count(),
        'pothole_total':  DetectionRecord.objects.filter(detection_type='pothole').count(),
        'lane_total':     DetectionRecord.objects.filter(detection_type='lane').count(),
        'alerts_sent':    DetectionRecord.objects.filter(alert_sent=True).count(),
        'total_potholes': DetectionRecord.objects.aggregate(s=Sum('pothole_count'))['s'] or 0,
        'recent':         DetectionRecord.objects.order_by('-created_at')[:8],
    }
    return render(request, 'detection/dashboard.html', context)


def pothole_detection(request):
    return render(request, 'detection/pothole_detection.html')


def lane_detection(request):
    return render(request, 'detection/lane_detection.html')


def history(request):
    records = DetectionRecord.objects.all()
    detection_type = request.GET.get('type', '')
    record_status  = request.GET.get('status', '')
    if detection_type:
        records = records.filter(detection_type=detection_type)
    if record_status:
        records = records.filter(status=record_status)
    return render(request, 'detection/history.html', {
        'records':       records,
        'filter_type':   detection_type,
        'filter_status': record_status,
    })


def detection_detail(request, pk):
    record = get_object_or_404(DetectionRecord, pk=pk)
    return render(request, 'detection/detail.html', {'record': record})
