from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EPGCalculationViewSet

router = DefaultRouter()
router.register(r'calculations', EPGCalculationViewSet, basename='calculation')

urlpatterns = [
    path('', include(router.urls))
]