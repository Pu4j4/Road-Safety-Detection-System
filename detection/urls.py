from django.urls import path
from .views import dashboard, pothole_detection, lane_detection, history, detection_detail
from django.http import HttpResponse

urlpatterns = [
    path('',                  dashboard,          name='dashboard'),
    path('pothole/',          pothole_detection,  name='pothole-detection'),
    path('lane/',             lane_detection,     name='lane-detection'),
    path('history/',          history,            name='history'),
    path('history/<int:pk>/', detection_detail,   name='detection-detail'),
    path('', lambda request: HttpResponse("Server running 🚀")),
]
