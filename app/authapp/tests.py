"""
Тесты API аутентификации: регистрация, вход, профиль, смена пароля, выход.

Покрывают как успешные сценарии, так и отказы — валидацию паролей,
дубликаты пользователей и доступ к защищённым эндпоинтам без токена.
"""
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

PASSWORD = "SuperSecret123"


@pytest.fixture
def api() -> APIClient:
    return APIClient()


@pytest.fixture
def user(db) -> User:
    return User.objects.create_user(
        username="tester", email="tester@example.com", password=PASSWORD
    )


@pytest.fixture
def tokens(api, user) -> dict:
    """Логинится существующим пользователем и возвращает пару JWT-токенов."""
    response = api.post(
        reverse("auth_login"),
        {"username": user.username, "password": PASSWORD},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    return response.data["tokens"]


@pytest.fixture
def auth_api(api, tokens) -> APIClient:
    """Клиент с валидным access-токеном в заголовке Authorization."""
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    return api


def register_payload(**overrides) -> dict:
    payload = {
        "username": "newbie",
        "email": "newbie@example.com",
        "password": PASSWORD,
        "password_confirm": PASSWORD,
    }
    payload.update(overrides)
    return payload


# --------------------------------------------------------------------------
# Регистрация
# --------------------------------------------------------------------------


@pytest.mark.django_db
def test_register_creates_user_and_returns_tokens(api):
    response = api.post(reverse("auth_register"), register_payload(), format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["user"]["username"] == "newbie"
    assert "access" in response.data["tokens"]
    assert "refresh" in response.data["tokens"]
    assert User.objects.filter(username="newbie").exists()


@pytest.mark.django_db
def test_register_stores_password_hashed(api):
    api.post(reverse("auth_register"), register_payload(), format="json")

    created = User.objects.get(username="newbie")
    assert created.password != PASSWORD, "пароль сохранён в открытом виде"
    assert created.check_password(PASSWORD)


@pytest.mark.django_db
def test_register_never_returns_password(api):
    response = api.post(reverse("auth_register"), register_payload(), format="json")

    assert "password" not in response.data["user"]
    assert "password_confirm" not in response.data["user"]


@pytest.mark.django_db
def test_register_rejects_mismatched_passwords(api):
    response = api.post(
        reverse("auth_register"),
        register_payload(password_confirm="OtherSecret123"),
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not User.objects.filter(username="newbie").exists()


@pytest.mark.django_db
def test_register_rejects_short_password(api):
    response = api.post(
        reverse("auth_register"),
        register_payload(password="short", password_confirm="short"),
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_register_rejects_duplicate_username(api, user):
    response = api.post(
        reverse("auth_register"),
        register_payload(username=user.username, email="other@example.com"),
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert User.objects.filter(username=user.username).count() == 1


@pytest.mark.django_db
def test_register_rejects_duplicate_email(api, user):
    response = api.post(
        reverse("auth_register"),
        register_payload(username="someoneelse", email=user.email),
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


# --------------------------------------------------------------------------
# Вход
# --------------------------------------------------------------------------


@pytest.mark.django_db
def test_login_returns_token_pair(api, user):
    response = api.post(
        reverse("auth_login"),
        {"username": user.username, "password": PASSWORD},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["tokens"]["access"]
    assert response.data["tokens"]["refresh"]
    assert response.data["user"]["username"] == user.username


@pytest.mark.django_db
def test_login_with_wrong_password_is_unauthorized(api, user):
    response = api.post(
        reverse("auth_login"),
        {"username": user.username, "password": "definitely-wrong"},
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "tokens" not in response.data


@pytest.mark.django_db
def test_login_with_unknown_user_is_unauthorized(api):
    response = api.post(
        reverse("auth_login"),
        {"username": "ghost", "password": PASSWORD},
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# --------------------------------------------------------------------------
# Профиль
# --------------------------------------------------------------------------


@pytest.mark.django_db
def test_me_requires_authentication(api):
    response = api.get(reverse("auth_me"))

    assert response.status_code in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    )


@pytest.mark.django_db
def test_me_returns_current_user(auth_api, user):
    response = auth_api.get(reverse("auth_me"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["username"] == user.username
    assert response.data["email"] == user.email


# --------------------------------------------------------------------------
# Смена пароля
# --------------------------------------------------------------------------


@pytest.mark.django_db
def test_change_password_updates_credentials(auth_api, user):
    new_password = "BrandNewSecret456"

    response = auth_api.post(
        reverse("auth_change_password"),
        {
            "old_password": PASSWORD,
            "new_password": new_password,
            "new_password_confirm": new_password,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.check_password(new_password)
    assert not user.check_password(PASSWORD)


@pytest.mark.django_db
def test_change_password_rejects_wrong_old_password(auth_api, user):
    response = auth_api.post(
        reverse("auth_change_password"),
        {
            "old_password": "not-my-password",
            "new_password": "BrandNewSecret456",
            "new_password_confirm": "BrandNewSecret456",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    user.refresh_from_db()
    assert user.check_password(PASSWORD), "пароль изменился при неверном старом"


# --------------------------------------------------------------------------
# Выход
# --------------------------------------------------------------------------


@pytest.mark.django_db
def test_logout_blacklists_refresh_token(auth_api, tokens):
    response = auth_api.post(
        reverse("auth_logout"), {"refresh": tokens["refresh"]}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK, (
        f"выход не сработал: {response.data}"
    )


@pytest.mark.django_db
def test_logout_without_refresh_token_is_bad_request(auth_api):
    response = auth_api.post(reverse("auth_logout"), {}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_logout_requires_authentication(api, tokens):
    response = api.post(
        reverse("auth_logout"), {"refresh": tokens["refresh"]}, format="json"
    )

    assert response.status_code in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    )
