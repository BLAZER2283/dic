from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DICAnalysisViewSet, get_csrf_token, register_view, login_view, logout_view

router = DefaultRouter()
router.register(r'analyses', DICAnalysisViewSet, basename='dic-analysis')

urlpatterns = [
    path('', include(router.urls)),
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),
    path('auth/register/', register_view, name='auth_register'),
    path('auth/login/', login_view, name='auth_login'),
    path('auth/logout/', logout_view, name='auth_logout'),
]