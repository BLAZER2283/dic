import threading
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import (
    EPGCalculation,
    EPGAuxiliaryParameters,
    EPGResults,
    EPGWarnings,
    EPGInternalData,
    MATERIAL_CHOICES,
    MATERIAL_PROPERTIES
)
from .serealisation import (
    EPGCalculationSerializer,
    EPGAuxiliaryParametersSerializer,
    EPGResultsSerializer,
    EPGWarningsSerializer,
    EPGInternalDataSerializer
    )
from ucrp.logik.plasma_optimizer import PlasmaOptimizer
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
class EPGCalculationViewSet(viewsets.ModelViewSet):
    queryset = EPGCalculation.objects.all()
    serializer_class = EPGCalculationSerializer
    
    def get_permissions(self):
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
    
        calculation = serializer.save()
    
        thread = threading.Thread(
            target=self._run_optimization,
            args=(calculation.id,)
            )
        thread.start()
    
        return Response(
            {"calculation_id": calculation.id, "status": "started"},
            status=status.HTTP_202_ACCEPTED)
        return super().create(request, *args, **kwargs)
    
    def _run_optimization(self, calculation_id):
        try:
            calculation = EPGCalculation.objects.get(id=calculation_id)
    
            aux_params = getattr(calculation, 'auxiliary_params', None)
    
            optimizer = PlasmaOptimizer(
                material_type=calculation.material,
                diameter=calculation.diameter,
                length=calculation.length,
                I_target=calculation.I_target,
                n_electrode=calculation.n_electrode,
                plasma_offset=calculation.plasma_offset,
                plasma_angle=calculation.plasma_angle,
                gas_flow=calculation.gas_flow,
                pusher_speed=calculation.pusher_speed,
                vibration_level=aux_params.vibration_level if aux_params else 2.0,
                n_ogark=aux_params.n_ogark if aux_params else 26000.0,
                time_from_last_cleaning=aux_params.time_from_last_cleaning if aux_params else 0,
                roller_wear_mm=aux_params.roller_wear_mm if aux_params else 0.0,
                material_choices=MATERIAL_CHOICES,
                material_properties=MATERIAL_PROPERTIES
            )
    
            optimizer.run_all()
    
            EPGResults.objects.create(
                calculation=calculation,
                predicted_losses_pct=float(optimizer.mean_loss),
                predicted_grain_size=float(optimizer.d_mean),
                frac_100_140_pct=float(optimizer.frac),
                stability_index=float(optimizer.stability),
                optimal_I_by_length=optimizer.optimal_I_by_length.tolist(),
                optimal_n_by_length=optimizer.n_profile.tolist(),
                x_grid=optimizer.grid.tolist()
            )
    
            EPGWarnings.objects.create(
                calculation=calculation,
                deposits=optimizer.warnings.get('deposits', False),
                vibration=optimizer.warnings.get('vibration', False),
                cracking=optimizer.warnings.get('cracking', False),
                overheating=optimizer.warnings.get('overheating', False)
            )
    
            EPGInternalData.objects.create(
                calculation=calculation,
                T_profile=optimizer.T_profile.tolist(),
                d_g_profile=optimizer.d_g_profile.tolist(),
                losses_profile=optimizer.losses_profile.tolist(),
                N_segments=int(optimizer.n_segments)
            )
    
            calculation.calculated_at = timezone.now()
            calculation.save()

        except Exception as e:
            print(f"Ошибка оптимизации #{calculation_id}: {str(e)}")
