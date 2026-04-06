from rest_framework import serializers
from .models import (
    EPGCalculation,
    EPGResults,
    EPGAuxiliaryParameters,
    EPGWarnings,
    EPGInternalData,
)


class EPGResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EPGResults
        fields = (
            "calculation",
            "predicted_losses_pct",
            "predicted_grain_size",
            "frac_100_140_pct",
            "stability_index",
            "optimal_I_by_length",
            "optimal_n_by_length",
            "x_grid",
        )
        read_only_fields = ("calculation",)


class EPGAuxiliaryParametersSerializer(serializers.ModelSerializer):
    class Meta:
        model = EPGAuxiliaryParameters
        fields = (
            "calculation",
            "vibration_level",
            "n_ogark",
            "time_from_last_cleaning",
            "roller_wear_mm",
            "ambient_T",
        )
        read_only_fields = ("calculation",)


class EPGWarningsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EPGWarnings
        fields = (
            "calculation",
            "deposits",
            "vibration",
            "cracking",
            "overheating",
        )
        read_only_fields = ("calculation",)


class EPGInternalDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EPGInternalData
        fields = (
            "calculation",
            "T_profile",
            "d_g_profile",
            "losses_profile",
            "N_segments",
        )
        read_only_fields = ("calculation",)


class EPGCalculationSerializer(serializers.ModelSerializer):
    # вложенные объекты (только для чтения) — записи создаются/обновляются отдельно
    auxiliary_params = EPGAuxiliaryParametersSerializer(read_only=True)
    results = EPGResultsSerializer(read_only=True)
    warnings_data = EPGWarningsSerializer(read_only=True)
    internal_data = EPGInternalDataSerializer(read_only=True)

    class Meta:
        model = EPGCalculation
        fields = (
            "id",
            "material",
            "diameter",
            "length",
            "mass_total",
            "I_target",
            "n_electrode",
            "plasma_offset",
            "plasma_angle",
            "gas_flow",
            "pusher_speed",
            "created_at",
            "updated_at",
            "calculated_at",
            "auxiliary_params",
            "results",
            "warnings_data",
            "internal_data",
        )
        read_only_fields = ("id", "created_at", "updated_at", "calculated_at")


