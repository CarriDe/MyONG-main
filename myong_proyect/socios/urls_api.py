from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .api_views import SocioViewSet, PagoViewSet, pagos_por_socio, check_dni_endpoint

# Crea el router y registra los ViewSets
router = DefaultRouter()
router.register(r'socios', SocioViewSet)      # Genera /api/socios/
router.register(r'pagos', PagoViewSet, basename='pago')  # Genera /api/pagos/

# Las URLs generadas incluyen:
# /socios/          -> list (GET), create (POST)
# /socios/{id}/     -> retrieve (GET), update (PUT/PATCH), destroy (DELETE)

urlpatterns = [
    # Endpoint para validar DNI
    path('socios/check-dni/', check_dni_endpoint, name='api_check_dni'),
    re_path(r'^socios/check-dni$', check_dni_endpoint),
    # Endpoint personalizado para pagos por socio
    path('socios/<uuid:socio_id>/pagos/', pagos_por_socio, name='api_pagos_socio'),
    path('', include(router.urls)),
]