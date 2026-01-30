from rest_framework.parsers import MultiPartParser, FormParser
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import rest_framework
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import DICAnalysis
from .serealisers import DICAnalysisSerializer, DICAnalysisCreateSerializer
from django.http import JsonResponse
from django.middleware.csrf import get_token
from .dic_bisnes_logik.default_methods import DefaultMethodsMixin
from .dic_bisnes_logik.logik_image import ImageActionsMixin
from .dic_bisnes_logik.generate import PdfGenerateMixin


class DICAnalysisViewSet(
    DefaultMethodsMixin,
    ImageActionsMixin,
    PdfGenerateMixin,
):
    """
    ViewSet для работы с задачами DIC анализа.
    Поддерживает создание, просмотр статуса и результатов.
    """

    queryset = DICAnalysis.objects.all().order_by('-created_at')
    parser_classes = (MultiPartParser, FormParser)
    filterset_fields = ['status']
    search_fields = ['name', 'id']
    ordering_fields = ['created_at', 'completed_at', 'processing_time', 'max_displacement']
    permission_classes = [rest_framework.permissions.AllowAny]
    
    def get_queryset(self):
        import time
        time.sleep(8)
        return super().get_queryset()   
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DICAnalysisCreateSerializer
        return DICAnalysisSerializer

@require_POST
@csrf_exempt
def register_view(request):
    """Регистрация нового пользователя."""
    import json
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
    except:
        username = request.POST.get('username')
        password = request.POST.get('password')

    if not username or not password:
        return JsonResponse({'error': 'Username and password are required'}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Username already exists'}, status=400)

    try:
        user = User.objects.create_user(username=username, password=password)
        login(request, user)

        return JsonResponse({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_POST
@csrf_exempt
def login_view(request):
    """Вход пользователя."""
    import json
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
    except:
        username = request.POST.get('username')
        password = request.POST.get('password')

    if not username or not password:
        return JsonResponse({'error': 'Username and password are required'}, status=400)

    user = authenticate(username=username, password=password)

    if user is not None:
        login(request, user)
        return JsonResponse({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    else:
        return JsonResponse({'error': 'Invalid credentials'}, status=401)

@require_POST
@csrf_exempt
def logout_view(request):
    """Выход пользователя."""
    logout(request)
    return JsonResponse({'message': 'Logged out successfully'})

def get_csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})
