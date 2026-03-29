from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.middleware.csrf import get_token

from .models import AnalysisTask, Sample
from .serealisers import (
    AnalysisTaskSerializer,
    AnalysisTaskCreateSerializer,
    SampleSerializer,
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    ChangePasswordSerializer
)
from .dic_bisnes_logik.default_methods import DefaultMethodsMixin
from .dic_bisnes_logik.logik_image import ImageActionsMixin
from .dic_bisnes_logik.generate import PdfGenerateMixin


class AnalysisTaskViewSet(
    DefaultMethodsMixin,
    ImageActionsMixin,
    PdfGenerateMixin,
    viewsets.ModelViewSet
):
    """
    ViewSet для работы с задачами DIC анализа.
    """

    queryset = AnalysisTask.objects.all().select_related(
        'sample', 'parameters', 'images', 'results'
    ).order_by('-created_at')
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [AllowAny]
    filterset_fields = ['status', 'sample__material']
    search_fields = ['name', 'id', 'sample__name']
    ordering_fields = ['created_at', 'completed_at', 'processing_time']

    def get_serializer_class(self):
        if self.action == 'create':
            return AnalysisTaskCreateSerializer
        return AnalysisTaskSerializer

    def create(self, request, *args, **kwargs):
        """Создание новой задачи анализа."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()

        # Запускаем обработку в отдельном потоке
        from .dic_bisnes_logik.help_methods import HelpMethods
        import threading

        images = task.images
        parameters = task.parameters

        thread = threading.Thread(
            target=HelpMethods()._process_dic_task,
            args=(
                str(task.id),
                images.image_before.path,
                images.image_after.path,
                parameters.subset_size,
                parameters.step,
                parameters.max_iter,
                parameters.min_correlation,
            ),
            daemon=True,
        )
        thread.start()

        response_serializer = AnalysisTaskSerializer(
            task, context={"request": request}
        )
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)



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
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Refresh токен обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        return Response({'message': 'Успешный выход'})
    except Exception as e:
        return Response(
            {'error': 'Неверный токен'},
            status=status.HTTP_400_BAD_REQUEST
        )


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
