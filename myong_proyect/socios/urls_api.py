from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import SocioViewSet, PagoViewSet, pagos_por_socio

# Crea el router y registra los ViewSets
router = DefaultRouter()
router.register(r'socios', SocioViewSet)      # Genera /api/socios/
router.register(r'pagos', PagoViewSet, basename='pago')  # Genera /api/pagos/

# Las URLs generadas incluyen:
# /socios/          -> list (GET), create (POST)
# /socios/{id}/     -> retrieve (GET), update (PUT/PATCH), destroy (DELETE)

urlpatterns = [
    path('', include(router.urls)),
    # Endpoint personalizado para pagos por socio
    path('socios/<uuid:socio_id>/pagos/', pagos_por_socio, name='api_pagos_socio'),
]