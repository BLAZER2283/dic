from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnalysisTaskViewSet

router = DefaultRouter()
router.register(r'analyses', AnalysisTaskViewSet, basename='dic-analysis')

urlpatterns = [
    path('', include(router.urls)),

]
