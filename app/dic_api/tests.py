"""
Тесты API DIC-анализов.

Проверяется граница доступа: список анализов закрыт для анонимов
(`permission_classes = [IsAuthenticated]` на AnalysisTaskViewSet) и открыт
по валидному JWT.
"""
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

PASSWORD = "SuperSecret123"


@pytest.fixture
def api() -> APIClient:
    return APIClient()


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(
        username="dic-tester", password=PASSWORD
    )


@pytest.fixture
def auth_api(api, user) -> APIClient:
    response = api.post(
        reverse("auth_login"),
        {"username": user.username, "password": PASSWORD},
        format="json",
    )
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['tokens']['access']}")
    return api


@pytest.mark.django_db
def test_analyses_list_requires_authentication(api):
    response = api.get(reverse("dic-analysis-list"))

    assert response.status_code in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    )


@pytest.mark.django_db
def test_analyses_list_is_available_to_authenticated_user(auth_api):
    response = auth_api.get(reverse("dic-analysis-list"))

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_creating_analysis_requires_authentication(api):
    response = api.post(reverse("dic-analysis-list"), {})

    assert response.status_code in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    )
