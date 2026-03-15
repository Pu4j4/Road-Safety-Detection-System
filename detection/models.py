from django.db import models
import os


class DetectionRecord(models.Model):
    DETECTION_TYPES = [
        ('pothole', 'Pothole Detection'),
        ('lane', 'Lane Detection'),
    ]
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    detection_type    = models.CharField(max_length=20, choices=DETECTION_TYPES)
    media_type        = models.CharField(max_length=10, choices=MEDIA_TYPES)
    input_file        = models.FileField(upload_to='uploads/%Y/%m/%d/')
    result_file       = models.FileField(upload_to='results/%Y/%m/%d/', null=True, blank=True)
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    pothole_count     = models.IntegerField(default=0)
    pothole_detected  = models.BooleanField(default=False)
    alert_sent        = models.BooleanField(default=False)
    alert_sent_at     = models.DateTimeField(null=True, blank=True)
    processing_time_ms= models.FloatField(null=True, blank=True)
    error_message     = models.TextField(blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Detection Record'
        verbose_name_plural = 'Detection Records'

    def __str__(self):
        return f"{self.get_detection_type_display()} | {self.media_type} | {self.status} | {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    @property
    def input_filename(self):
        return os.path.basename(self.input_file.name) if self.input_file else ''

    @property
    def result_filename(self):
        return os.path.basename(self.result_file.name) if self.result_file else ''


class AlertLog(models.Model):
    detection     = models.ForeignKey(DetectionRecord, on_delete=models.CASCADE, related_name='alerts')
    phone_number  = models.CharField(max_length=20)
    message_sid   = models.CharField(max_length=100, blank=True)
    message_body  = models.TextField()
    success       = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    sent_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        status = "✅" if self.success else "❌"
        return f"{status} Alert to {self.phone_number} at {self.sent_at.strftime('%Y-%m-%d %H:%M')}"
