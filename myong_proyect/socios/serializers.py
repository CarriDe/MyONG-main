from rest_framework import serializers
from .models import Socio, Direccion, Tutor, Pago

class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        fields = '__all__'

class TutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tutor
        fields = '__all__'

class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = '__all__'

class SocioSerializer(serializers.ModelSerializer):
    """Serializer para lectura: incluye relaciones anidadas"""
    direccion = DireccionSerializer(read_only=True)
    tutor_legal = TutorSerializer(many=True, read_only=True)
    
    class Meta:
        model = Socio
        fields = '__all__'

class SocioCreateSerializer(serializers.ModelSerializer):
    """Serializer para escritura: permite crear socio con dirección"""
    direccion = DireccionSerializer()
    
    class Meta:
        model = Socio
        exclude = ['fecha_alta']  # Campo automático
    
    def create(self, validated_data):
        direccion_data = validated_data.pop('direccion')
        direccion = Direccion.objects.create(**direccion_data)
        return Socio.objects.create(direccion=direccion, **validated_data)