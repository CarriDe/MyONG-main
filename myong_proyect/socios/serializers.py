from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Socio, Direccion, Tutor, Pago
from .dni_utils import check_dni


class DNIValidatorSerializer(serializers.Serializer):
    """
    Serializer para validar documentos de identidad españoles.
    Reutiliza la lógica de check_dni() para evitar duplicación.
    """
    documento = serializers.CharField(max_length=9, required=True)
    
    def validate_documento(self, value):
        """
        Valida usando la función check_dni().
        Si check_dni() devuelve valido: False, lanza ValidationError.
        """
        resultado = check_dni(value)
        if not resultado.get('valido'):
            raise ValidationError(resultado.get('error', 'DNI inválido'))
        return value


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
    documento_identidad = serializers.CharField(max_length=9, required=False, allow_blank=True)
    
    class Meta:
        model = Socio
        exclude = ['fecha_registro', 'id']  # Campos automáticos
    
    def validate_documento_identidad(self, value):
        """Valida el DNI si se proporciona"""
        if value:  # Solo validar si se proporciona
            validador = DNIValidatorSerializer(data={'documento': value})
            if not validador.is_valid():
                raise ValidationError(validador.errors['documento'])
        return value
    
    def create(self, validated_data):
        direccion_data = validated_data.pop('direccion')
        direccion = Direccion.objects.create(**direccion_data)
        return Socio.objects.create(direccion=direccion, **validated_data)