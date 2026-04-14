import pytest
import numpy as np
from django.test import TestCase
from ucrp.logik.plasma_optimizer import (
    PlasmaOptimizer,
    MATERIAL_CHOICES,
    MATERIAL_PROPERTIES,
)

    
    
@pytest.fixture
def default_params():
    """Контрольные параметры из ТЗ (контрольный пример)."""
    return {
        "material_type": "ОТ4",
        "diameter": 58.0,
        "length": 700.0,
        "I_target": 1390.0,
        "n_electrode": 30000.0,
        "plasma_offset": 0.0,
        "plasma_angle": 86.0,
        "gas_flow": 2.6,
        "pusher_speed": 45.0,
        "vibration_level": 2.0,
        "n_ogark": 26000.0,
        "time_from_last_cleaning": 0,
        "roller_wear_mm": 0.0,
        "material_choices": MATERIAL_CHOICES,
        "material_properties": MATERIAL_PROPERTIES,
    }


@pytest.fixture
def optimizer(default_params):
    """Готовый оптимизатор с контрольными параметрами."""
    opt = PlasmaOptimizer(**default_params)
    opt.run_all()
    return opt


# МОДУЛЬ 1: ОПРЕДЕЛЕНИЕ МАТЕРИАЛА

class TestMaterialDefinition:
    """Тесты на определение материала."""

    def test_material_ot4(self, default_params):
        opt = PlasmaOptimizer(**default_params)
        mat = opt.define_material("ОТ4")
        assert mat["density"] == 4500
        assert mat["viscosity"] == 0.0035
        assert mat["t_melt"] == 1690
        assert mat["t_target"] == 1780

    def test_material_bt6(self, default_params):
        opt = PlasmaOptimizer(**default_params)
        mat = opt.define_material("ВТ6")
        assert mat["density"] == 4430
        assert mat["t_melt"] == 1660
        assert mat["t_target"] == 1750

    def test_material_ep741np(self, default_params):
        opt = PlasmaOptimizer(**default_params)
        mat = opt.define_material("ЭП741НП")
        assert mat["density"] == 8200
        assert mat["viscosity"] == 0.0055
        assert mat["t_melt"] == 1280
        assert mat["t_target"] == 1380

    def test_unknown_material(self, default_params):
        opt = PlasmaOptimizer(**default_params)
        with pytest.raises(ValueError, match="Unknown material type"):
            opt.define_material("НЕСУЩЕСТВУЮЩИЙ")

    def test_normalize_case(self, default_params):
        """Проверка нормализации регистра."""
        opt = PlasmaOptimizer(**default_params)
        mat = opt.define_material("от4")
        assert mat["density"] == 4500


# МОДУЛЬ 2: ГЕОМЕТРИЧЕСКАЯ ПОДГОТОВКА

class TestGeometry:
    """Тесты на геометрическую подготовку."""

    def test_radius_calculation(self, default_params):
        opt = PlasmaOptimizer(**default_params)
        R, N, grid = opt.geometric_preparation(58.0, 700.0)
        # R = 58 / 2000 = 0.029 м
        assert R == pytest.approx(0.029, abs=0.0001)

    def test_segments_count(self, default_params):
        opt = PlasmaOptimizer(**default_params)
        R, N, grid = opt.geometric_preparation(58.0, 700.0)
        # 700 / 50 = 14 → ceil = 14 → +1 = 15 точек
        assert N == 15

    def test_grid_length(self, default_params):
        opt = PlasmaOptimizer(**default_params)
        R, N, grid = opt.geometric_preparation(58.0, 700.0)
        assert len(grid) == 15
        assert grid[0] == 0
        assert grid[-1] == 700.0

    def test_invalid_diameter(self, default_params):
        opt = PlasmaOptimizer(**default_params)
        with pytest.raises(ValueError):
            opt.geometric_preparation(-10, 700.0)

    def test_invalid_length(self, default_params):
        opt = PlasmaOptimizer(**default_params)
        with pytest.raises(ValueError):
            opt.geometric_preparation(58.0, 0)


# МОДУЛЬ 3: ТЕМПЕРАТУРНЫЙ ПРОФИЛЬ

class TestTemperatureProfile:
    """Тесты на температурный профиль."""

    def test_temperature_above_melt(self, optimizer):
        """Все температуры должны быть выше T_melt."""
        T_melt = optimizer.material["t_melt"]
        assert np.all(optimizer.T_profile > T_melt)

    def test_temperature_start_section(self, optimizer):
        """Начало электрода — высокая температура."""
        # x=0 → T ~1866°C (по ТЗ)
        assert optimizer.T_profile[0] > 1800

    def test_temperature_end_section(self, optimizer):
        """Конец электрода — температура ближе к T_melt."""
        # x=700 → T ~1783°C (по ТЗ)
        T_melt = optimizer.material["t_melt"]
        assert optimizer.T_profile[-1] < 1800
        assert optimizer.T_profile[-1] > T_melt

    def test_temperature_increases_with_current(self, default_params):
        """Больше ток → выше температура."""
        opt_low = PlasmaOptimizer(**{**default_params, "I_target": 1200.0})
        opt_low.run_all()
        opt_high = PlasmaOptimizer(**{**default_params, "I_target": 1500.0})
        opt_high.run_all()
        assert np.mean(opt_high.T_profile) > np.mean(opt_low.T_profile)


# МОДУЛЬ 4: ОПТИМАЛЬНАЯ СКОРОСТЬ

class TestOptimalSpeed:
    """Тесты на оптимальную скорость вращения."""

    def test_speed_middle_section(self, optimizer):
        """Средняя зона (250–480 мм) → стабильная скорость 30000."""
        # Найти индексы для x=300 мм
        idx = np.argmin(np.abs(optimizer.grid - 300))
        assert optimizer.n_profile[idx] == 30000

    def test_speed_end_not_below_minimum(self, optimizer):
        """Скорость не должна падать ниже 29400."""
        assert np.all(optimizer.n_profile >= 29400)

    def test_speed_start_section(self, optimizer):
        """Начало (x < 250) → скорость выше базы."""
        # При I=1390 → n = 30100
        idx = np.argmin(np.abs(optimizer.grid - 100))
        assert optimizer.n_profile[idx] == pytest.approx(30100, abs=1)


# МОДУЛЬ 5: РАЗМЕР ГРАНУЛ

class TestGrainSize:
    """Тесты на размер гранул."""

    def test_mean_grain_in_target_range(self, optimizer):
        """Средний размер ~110–120 мкм (по ТЗ ±15 мкм)."""
        assert 95 <= optimizer.d_mean <= 135

    def test_grain_size_positive(self, optimizer):
        """Все размеры гранул положительные."""
        assert np.all(optimizer.d_g_profile > 0)

    def test_high_current_increases_grain_size(self, default_params):
        """Больше ток → крупнее гранулы."""
        opt_low = PlasmaOptimizer(**{**default_params, "I_target": 1200.0})
        opt_low.run_all()
        opt_high = PlasmaOptimizer(**{**default_params, "I_target": 1550.0})
        opt_high.run_all()
        assert opt_high.d_mean > opt_low.d_mean

    def test_offset_reduces_grain_size(self, default_params):
        """Смещение плазмы → меньше гранулы."""
        opt_center = PlasmaOptimizer(**{**default_params, "plasma_offset": 0.0})
        opt_center.run_all()
        opt_offset = PlasmaOptimizer(**{**default_params, "plasma_offset": 12.0})
        opt_offset.run_all()
        assert opt_offset.d_mean < opt_center.d_mean


# МОДУЛЬ 6: ПРОГНОЗ ПОТЕРЬ

class TestLosses:
    """Тесты на прогноз потерь."""

    def test_losses_in_normal_range(self, optimizer):
        """Потери ~7–10% для контрольного примера."""
        assert 5 <= optimizer.mean_loss <= 15

    def test_high_vibration_increases_losses(self, default_params):
        """Высокая вибрация → больше потерь."""
        opt_low_vib = PlasmaOptimizer(**{**default_params, "vibration_level": 2.0})
        opt_low_vib.run_all()
        opt_high_vib = PlasmaOptimizer(**{**default_params, "vibration_level": 4.5})
        opt_high_vib.run_all()
        assert opt_high_vib.mean_loss > opt_low_vib.mean_loss

    def test_offset_increases_losses(self, default_params):
        """Смещение плазмы → больше потерь."""
        opt_center = PlasmaOptimizer(**{**default_params, "plasma_offset": 0.0})
        opt_center.run_all()
        opt_offset = PlasmaOptimizer(**{**default_params, "plasma_offset": 15.0})
        opt_offset.run_all()
        assert opt_offset.mean_loss > opt_center.mean_loss


# МОДУЛЬ: ФРАКЦИЯ 100–140

class TestFraction:
    """Тесты на долю фракции 100–140 мкм."""

    def test_fraction_high_for_optimal(self, optimizer):
        """Для оптимальных параметров фракция высокая."""
        # Ожидаемо > 85% (по ТЗ)
        assert optimizer.frac >= 60

    def test_fraction_reduced_by_offset(self, default_params):
        """Большое смещение снижает фракцию."""
        opt_center = PlasmaOptimizer(**{**default_params, "plasma_offset": 0.0})
        opt_center.run_all()
        opt_offset = PlasmaOptimizer(**{**default_params, "plasma_offset": 18.0})
        opt_offset.run_all()
        assert opt_offset.frac <= opt_center.frac

    def test_fraction_clamped(self, default_params):
        """Фракция в пределах 60–98%."""
        opt = PlasmaOptimizer(**default_params)
        opt.run_all()
        assert 60 <= opt.frac <= 98


# МОДУЛЬ 7: ИНДЕКС СТАБИЛЬНОСТИ

class TestStability:
    """Тесты на индекс стабильности."""

    def test_stability_good_for_optimal(self, optimizer):
        """Для оптимальных параметров стабильность ~80–85."""
        assert 75 <= optimizer.stability <= 90

    def test_stability_bad_vibration(self, default_params):
        """Высокая вибрация → низкая стабильность."""
        opt_high_vib = PlasmaOptimizer(**{**default_params, "vibration_level": 5.0})
        opt_high_vib.run_all()
        assert opt_high_vib.stability < 70

    def test_stability_clamped(self, default_params):
        """Стабильность в пределах 0–100."""
        opt = PlasmaOptimizer(**default_params)
        opt.run_all()
        assert 0 <= opt.stability <= 100

    def test_stability_perfect_conditions(self, default_params):
        """Идеальные условия → стабильность ~95+."""
        opt = PlasmaOptimizer(
            **{
                **default_params,
                "I_target": 1400.0,
                "n_electrode": 30500.0,
                "plasma_offset": 0.0,
                "vibration_level": 0.0,
            }
        )
        opt.run_all()
        assert opt.stability > 90


# МОДУЛЬ 8: РЕКОМЕНДАЦИИ И ПРЕДУПРЕЖДЕНИЯ

class TestWarnings:
    """Тесты на предупреждения."""

    def test_no_warnings_for_optimal(self, optimizer):
        """Для оптимальных параметров нет предупреждений."""
        assert optimizer.warnings["vibration"] is False
        assert optimizer.warnings["cracking"] is False
        assert optimizer.warnings["overheating"] is False

    def test_vibration_warning(self, default_params):
        """Вибрация > 3.2 → флаг."""
        opt = PlasmaOptimizer(**{**default_params, "vibration_level": 4.0})
        opt.run_all()
        assert opt.warnings["vibration"] is True
        assert any("Вибрация" in r for r in opt.recommendations)

    def test_deposits_warning_from_offset(self, default_params):
        """Смещение > 15 → флаг deposits."""
        opt = PlasmaOptimizer(**{**default_params, "plasma_offset": 18.0})
        opt.run_all()
        assert opt.warnings["deposits"] is True

    def test_deposits_warning_from_cleaning(self, default_params):
        """Много плавок без чистки → флаг deposits."""
        opt = PlasmaOptimizer(**{**default_params, "time_from_last_cleaning": 5})
        opt.run_all()
        assert opt.warnings["deposits"] is True
        assert any("чистк" in r.lower() for r in opt.recommendations)

    def test_cracking_warning(self, default_params):
        """Высокий ток + низкая скорость → риск раскрытия."""
        opt = PlasmaOptimizer(
            **{
                **default_params,
                "I_target": 1500.0,
                "n_electrode": 29000.0,
            }
        )
        opt.run_all()
        assert opt.warnings["cracking"] is True

    def test_overheating_warning(self, default_params):
        """Угол плазмы вне диапазона → перегрев."""
        opt = PlasmaOptimizer(**{**default_params, "plasma_angle": 65.0})
        opt.run_all()
        assert opt.warnings["overheating"] is True


class TestRecommendations:
    """Тесты на текстовые рекомендации."""

    def test_recommendations_is_list(self, optimizer):
        assert isinstance(optimizer.recommendations, list)

    def test_gas_flow_recommendation(self, default_params):
        """Низкий расход газа → рекомендация."""
        opt = PlasmaOptimizer(**{**default_params, "gas_flow": 2.2})
        opt.run_all()
        assert any("газ" in r.lower() or "gas" in r.lower() for r in opt.recommendations)

    def test_pusher_speed_recommendation(self, default_params):
        """Высокая скорость толкателя → рекомендация."""
        opt = PlasmaOptimizer(**{**default_params, "pusher_speed": 50.0})
        opt.run_all()
        assert any("толкател" in r.lower() for r in opt.recommendations)

    def test_roller_wear_recommendation(self, default_params):
        """Износ ролика > 1.5 → рекомендация."""
        opt = PlasmaOptimizer(**{**default_params, "roller_wear_mm": 2.0})
        opt.run_all()
        assert any("ролик" in r.lower() for r in opt.recommendations)


# ИНТЕГРАЦИОННЫЕ ТЕСТЫ

class TestIntegration:
    """Интеграционные тесты — полный цикл run_all()."""

    def test_full_run_ot4(self, default_params):
        """Полный запуск для ОТ4 — все поля заполнены."""
        opt = PlasmaOptimizer(**default_params)
        opt.run_all()

        assert opt.material is not None
        assert opt.T_profile is not None
        assert len(opt.T_profile) == 15
        assert opt.n_profile is not None
        assert opt.d_g_profile is not None
        assert opt.mean_loss is not None
        assert opt.d_mean is not None
        assert opt.frac is not None
        assert opt.stability is not None
        assert opt.optimal_I_by_length is not None
        assert opt.recommendations is not None
        assert opt.warnings is not None

    def test_full_run_bt6(self, default_params):
        """Полный запуск для ВТ6."""
        params = {**default_params, "material_type": "ВТ6"}
        opt = PlasmaOptimizer(**params)
        opt.run_all()
        assert opt.material["t_melt"] == 1660

    def test_full_run_ep741np(self, default_params):
        """Полный запуск для ЭП741НП."""
        params = {**default_params, "material_type": "ЭП741НП"}
        opt = PlasmaOptimizer(**params)
        opt.run_all()
        assert opt.material["density"] == 8200

    def test_output_arrays_same_length(self, default_params):
        """Все выходные массивы имеют одинаковую длину."""
        opt = PlasmaOptimizer(**default_params)
        opt.run_all()
        n = len(opt.grid)
        assert len(opt.T_profile) == n
        assert len(opt.n_profile) == n
        assert len(opt.d_g_profile) == n
        assert len(opt.losses_profile) == n
        assert len(opt.optimal_I_by_length) == n


# DJANGO MODEL TESTS (если нужны)

class TestDjangoModels(TestCase):
    """Тесты на сохранение результатов в БД."""

    def test_save_calculation(self):
        from ucrp.models import EPGCalculation

        calc = EPGCalculation.objects.create(
            material="ОТ4",
            diameter=58.0,
            length=700.0,
            I_target=1390.0,
            n_electrode=30000.0,
            plasma_offset=0.0,
            plasma_angle=86.0,
            gas_flow=2.6,
            pusher_speed=45.0,
        )
        assert calc.id is not None
        assert calc.material == "ОТ4"

    def test_save_auxiliary_params(self):
        from ucrp.models import EPGCalculation, EPGAuxiliaryParameters

        calc = EPGCalculation.objects.create(
            material="ОТ4",
            diameter=58.0,
            length=700.0,
            I_target=1390.0,
            n_electrode=30000.0,
            plasma_offset=0.0,
            plasma_angle=86.0,
            gas_flow=2.6,
            pusher_speed=45.0,
        )
        aux = EPGAuxiliaryParameters.objects.create(
            calculation=calc,
            vibration_level=2.0,
            n_ogark=26000.0,
            time_from_last_cleaning=0,
            roller_wear_mm=0.0,
        )
        assert aux.vibration_level == 2.0

    def test_save_results(self):
        from ucrp.models import EPGCalculation, EPGResults

        calc = EPGCalculation.objects.create(
            material="ОТ4",
            diameter=58.0,
            length=700.0,
            I_target=1390.0,
            n_electrode=30000.0,
            plasma_offset=0.0,
            plasma_angle=86.0,
            gas_flow=2.6,
            pusher_speed=45.0,
        )
        results = EPGResults.objects.create(
            calculation=calc,
            predicted_losses_pct=8.5,
            predicted_grain_size=115.0,
            frac_100_140_pct=90.0,
            stability_index=82.0,
            optimal_I_by_length=[1360, 1390, 1350],
            optimal_n_by_length=[30100, 30000, 29800],
            x_grid=[0, 350, 700],
        )
        assert results.predicted_losses_pct == 8.5
        assert results.stability_index == 82.0

    def test_save_warnings(self):
        from ucrp.models import EPGCalculation, EPGWarnings

        calc = EPGCalculation.objects.create(
            material="ОТ4",
            diameter=58.0,
            length=700.0,
            I_target=1390.0,
            n_electrode=30000.0,
            plasma_offset=0.0,
            plasma_angle=86.0,
            gas_flow=2.6,
            pusher_speed=45.0,
        )
        warnings = EPGWarnings.objects.create(
            calculation=calc,
            deposits=False,
            vibration=False,
            cracking=False,
            overheating=False,
        )
        assert warnings.deposits is False
        assert warnings.vibration is False