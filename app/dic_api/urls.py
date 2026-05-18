from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnalysisTaskViewSet
from ucrp.views import EPGCalculationViewSet

router = DefaultRouter()
router.register(r'analyses', AnalysisTaskViewSet, basename='dic-analysis')
router.register(r'calculations', EPGCalculationViewSet, basename='calculation')

urlpatterns = [
    path('', include(router.urls)),

]
