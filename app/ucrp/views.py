from rest_framework.viewsets import ModelViewSet
from .models import (
    EPGCalculation,
    EPGResults,
    EPGAuxiliaryParameters,
    EPGWarnings,
    EPGInternalData,
)
from .serealisation import (
    EPGResultsSerializer,
    EPGAuxiliaryParametersSerializer,
    EPGWarningsSerializer,
    EPGInternalDataSerializer,
    EPGResultsSerializer,   
)

from .logik import perform_calculation