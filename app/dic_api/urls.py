from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AnalysisTaskViewSet,
    get_csrf_token,
    register_view,
    login_view,
    logout_view,
    me_view,
    change_password_view
)

router = DefaultRouter()
router.register(r'analyses', AnalysisTaskViewSet, basename='dic-analysis')

urlpatterns = [
    path('', include(router.urls)),
    
    # Auth endpoints
    path('auth/register/', register_view, name='auth_register'),
    path('auth/login/', login_view, name='auth_login'),
    path('auth/logout/', logout_view, name='auth_logout'),
    path('auth/me/', me_view, name='auth_me'),
    path('auth/change-password/', change_password_view, name='auth_change_password'),
    
    # CSRF token (для совместимости)
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),
]
