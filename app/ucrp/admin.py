from django.contrib import admin
from .models import (
    EPGCalculation,
    EPGAuxiliaryParameters,
    EPGResults,
    EPGWarnings,
    EPGInternalData
)   

admin.site.register(EPGCalculation)
admin.site.register(EPGAuxiliaryParameters)
admin.site.register(EPGResults)
admin.site.register(EPGWarnings)
admin.site.register(EPGInternalData)