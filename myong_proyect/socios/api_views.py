from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from datetime import date

from .models import Socio, Pago
from .serializers import SocioSerializer, SocioCreateSerializer, PagoSerializer

class SocioViewSet(viewsets.ModelViewSet):
    """
    Proporciona operaciones CRUD completas para el modelo Socio.
    Hereda de ModelViewSet que incluye: list, create, retrieve, update, destroy
    """
    queryset = Socio.objects.select_related('direccion').prefetch_related('tutor_legal')
    
    def get_serializer_class(self):
        """Usa diferente serializer según la acción"""
        if self.action in ['create', 'update', 'partial_update']:
            return SocioCreateSerializer
        return SocioSerializer

class PagoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para consultar pagos.
    Soporta filtrado por socio y año mediante query params.
    """
    serializer_class = PagoSerializer
    
    def get_queryset(self):
        queryset = Pago.objects.select_related('socio')
        
        # Filtrado opcional por parámetros URL
        socio_id = self.request.query_params.get('socio')
        year = self.request.query_params.get('year', date.today().year)
        
        if socio_id:
            queryset = queryset.filter(socio__id=socio_id)
        
        return queryset.filter(anio=year)

# Endpoint funcional adicional (alternativa a acciones de ViewSet)
@api_view(['GET'])
def pagos_por_socio(request, socio_id):
    """
    Endpoint personalizado para obtener pagos de un socio específico.
    Accesible en: /api/socios/<uuid>/pagos/
    """
    year = request.query_params.get('year', date.today().year)
    pagos = Pago.objects.filter(socio__id=socio_id, anio=year).order_by('mes')
    
    return Response({
        'socio_id': str(socio_id),
        'year': year,
        'pagos': PagoSerializer(pagos, many=True).data,
        'total_meses': pagos.count(),
        'total_pagado': sum(p.monto for p in pagos if p.pagado),
    })