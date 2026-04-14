from django.urls import path
from .views import (
    register_view,
    login_view,
    logout_view,
    me_view,
    change_password_view,
    get_csrf_token
)

urlpatterns = [
    # Auth endpoints
    path('register/', register_view, name='auth_register'),
    path('login/', login_view, name='auth_login'),
    path('logout/', logout_view, name='auth_logout'),
    path('me/', me_view, name='auth_me'),
    path('change-password/', change_password_view, name='auth_change_password'),

    # CSRF token (для совместимости)
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),
]
