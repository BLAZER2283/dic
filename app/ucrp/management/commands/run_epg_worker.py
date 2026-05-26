
import time
import logging
import traceback
from django.core.management.base import BaseCommand
from django.utils import timezone
from ucrp.models import (
    EPGCalculation, EPGResults, EPGWarnings, EPGInternalData,
    MATERIAL_CHOICES, MATERIAL_PROPERTIES,
)
from ucrp.logik.plasma_optimizer import PlasmaOptimizer
logger = logging.getLogger(__name__)
class Command(BaseCommand):
    help = 'Запускает воркер для обработки EPG-расчётов'
    def handle(self, *args, **options):
        self.stdout.write('EPG Worker запущен. Ожидание задач...')
        while True:
            try:
                calc = EPGCalculation.objects.filter(calculated_at__isnull=True).first()
                if calc:
                    self.stdout.write(f'Взял расчёт #{calc.id}')
                    aux_params = getattr(calc, 'auxiliary_params', None)
                    try:
                        optimizer = PlasmaOptimizer(
                            material_type=calc.material,
                            diameter=calc.diameter,
                            length=calc.length,
                            I_target=calc.I_target,
                            n_electrode=calc.n_electrode,
                            plasma_offset=calc.plasma_offset,
                            plasma_angle=calc.plasma_angle,
                            gas_flow=calc.gas_flow,
                            pusher_speed=calc.pusher_speed,
                            vibration_level=aux_params.vibration_level if aux_params else 2.0,
                            n_ogark=aux_params.n_ogark if aux_params else 26000.0,
                            time_from_last_cleaning=aux_params.time_from_last_cleaning if aux_params else 0,
                            roller_wear_mm=aux_params.roller_wear_mm if aux_params else 0.0,
                            material_choices=MATERIAL_CHOICES,
                            material_properties=MATERIAL_PROPERTIES,
                        )
                        optimizer.run_all()
                        EPGResults.objects.create(
                            calculation=calc,
                            predicted_losses_pct=float(optimizer.mean_loss),
                            predicted_grain_size=float(optimizer.d_mean),
                            frac_100_140_pct=float(optimizer.frac),
                            stability_index=float(optimizer.stability),
                            optimal_I_by_length=optimizer.optimal_I_by_length.tolist(),
                            optimal_n_by_length=optimizer.n_profile.tolist(),
                            x_grid=optimizer.grid.tolist(),
                        )
                        EPGWarnings.objects.create(
                            calculation=calc,
                            deposits=optimizer.warnings.get('deposits', False),
                            vibration=optimizer.warnings.get('vibration', False),
                            cracking=optimizer.warnings.get('cracking', False),
                            overheating=optimizer.warnings.get('overheating', False),
                        )
                        EPGInternalData.objects.create(
                            calculation=calc,
                            T_profile=optimizer.T_profile.tolist(),
                            d_g_profile=optimizer.d_g_profile.tolist(),
                            losses_profile=optimizer.losses_profile.tolist(),
                            N_segments=int(optimizer.n_segments),
                        )
                        calc.calculated_at = timezone.now()
                        calc.save()
                        self.stdout.write(f'Расчёт #{calc.id} завершён')
                    except Exception as e:
                        logger.exception(f'Ошибка расчёта #{calc.id}')
                        # можно добавить поле error_message в EPGCalculation при желании
                        self.stdout.write(self.style.ERROR(f'Расчёт #{calc.id} упал: {e}'))
                else:
                    time.sleep(1)
            except Exception as e:
                logger.exception('Ошибка в цикле воркера')
                time.sleep(5)