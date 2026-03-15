from django.urls import path
from .api_views import (
    PotholeDetectionAPIView,
    LaneDetectionAPIView,
    SendAlertAPIView,
    DetectionHistoryAPIView,
    DetectionDetailAPIView,
    DashboardStatsAPIView,
)

urlpatterns = [
    path('detect/pothole/',  PotholeDetectionAPIView.as_view(), name='api-pothole-detect'),
    path('detect/lane/',     LaneDetectionAPIView.as_view(),    name='api-lane-detect'),
    path('alert/send/',      SendAlertAPIView.as_view(),        name='api-send-alert'),
    path('history/',         DetectionHistoryAPIView.as_view(), name='api-history'),
    path('history/<int:pk>/',DetectionDetailAPIView.as_view(),  name='api-history-detail'),
    path('stats/',           DashboardStatsAPIView.as_view(),   name='api-stats'),
]
