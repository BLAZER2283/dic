from rest_framework import viewsets, status
from rest_framework.response import Response
from django.utils import timezone
from .models import EPGCalculation
from .serealisation import EPGCalculationSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny

class EPGCalculationViewSet(viewsets.ModelViewSet):
    queryset = EPGCalculation.objects.all()
    serializer_class = EPGCalculationSerializer
    
    def get_permissions(self):
        if self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return [IsAuthenticated()]
        return [AllowAny()]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
    
        calculation = serializer.save(user=request.user)
        
        return Response(
            {"calculation_id": calculation.id, "status": "started"},
            status=status.HTTP_202_ACCEPTED)