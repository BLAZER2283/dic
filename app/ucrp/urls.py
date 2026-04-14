from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import EPGCalculationViewSet

router = DefaultRouter()
router.register(r'calculations', EPGCalculationViewSet, basename='calculation')
urlpatterns = [
    
]
urlpatterns += router.urls