from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from django.middleware.csrf import get_token

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    ChangePasswordSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Регистрация нового пользователя.

    После успешной регистрации возвращает JWT токены.
    """
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.save()

    # Генерируем JWT токены
    refresh = RefreshToken.for_user(user)

    return Response({
        'user': UserSerializer(user).data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Вход пользователя.

    Принимает username и password, возвращает JWT токены.
    """
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = authenticate(
        username=serializer.validated_data['username'],
        password=serializer.validated_data['password']
    )

    if user is None:
        return Response(
            {'error': 'Неверное имя пользователя или пароль'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Генерируем JWT токены
    refresh = RefreshToken.for_user(user)

    return Response({
        'user': UserSerializer(user).data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Выход пользователя.

    Принимает refresh токен и добавляет его в blacklist.
    """
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response(
            {'error': 'Refresh токен обязателен'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Ловим только TokenError: раньше здесь стоял `except Exception`, из-за
    # которого отсутствие приложения token_blacklist выглядело как невалидный
    # токен, и сломанный выход возвращал 400 вместо ошибки конфигурации.
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except TokenError:
        return Response(
            {'error': 'Неверный токен'},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response({'message': 'Успешный выход'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """
    Получение данных текущего пользователя.
    """
    return Response(UserSerializer(request.user).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """
    Смена пароля пользователя.
    """
    serializer = ChangePasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = request.user

    # Проверяем старый пароль
    if not user.check_password(serializer.validated_data['old_password']):
        return Response(
            {'old_password': 'Неверный текущий пароль'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Устанавливаем новый пароль
    user.set_password(serializer.validated_data['new_password'])
    user.save()

    return Response({'message': 'Пароль успешно изменен'})


@api_view(['GET'])
@permission_classes([AllowAny])
def get_csrf_token(request):
    """Получение CSRF токена (для совместимости)."""
    return Response({'csrfToken': get_token(request)})
