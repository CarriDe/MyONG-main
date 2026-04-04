# socios/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import Socio, Direccion, Tutor
from datetime import date

class DireccionForm(forms.ModelForm):
    codigo_postal = forms.CharField(
        max_length=5,
        validators=[RegexValidator(r'^\d{5}$', 'El código postal debe tener 5 dígitos')]
    )
    
    class Meta:
        model = Direccion
        fields = ['calle', 'numero', 'piso', 'otros', 'ciudad', 'provincia', 'codigo_postal', 'pais']
        widgets = {
            'calle': forms.TextInput(attrs={'placeholder': 'Calle'}),
            'numero': forms.TextInput(attrs={'placeholder': 'Número'}),
            'piso': forms.TextInput(attrs={'placeholder': 'Piso/Portal'}),
            'otros': forms.TextInput(attrs={'placeholder': 'Escalera, Puerta...'}),
            'ciudad': forms.TextInput(attrs={'placeholder': 'Ciudad'}),
            'provincia': forms.TextInput(attrs={'placeholder': 'Provincia'}),
            'pais': forms.TextInput(attrs={'placeholder': 'País'}),
        }

class TutorForm(forms.ModelForm):
    telefono = forms.CharField(
        max_length=9,
        validators=[RegexValidator(r'^\d{9}$', 'El teléfono debe tener 9 dígitos')]
    )
    
    class Meta:
        model = Tutor
        fields = ['nombre', 'apellidos', 'telefono', 'email', 'documento_identidad']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre del tutor'}),
            'apellidos': forms.TextInput(attrs={'placeholder': 'Apellidos del tutor'}),
            'email': forms.EmailInput(attrs={'placeholder': 'tutor@example.com'}),
            'documento_identidad': forms.TextInput(attrs={'placeholder': 'DNI/NIE'}),
        }

class SocioForm(forms.ModelForm):
    # Sobrescribimos el campo telefono para validarlo
    telefono = forms.CharField(
        max_length=9,
        validators=[RegexValidator(r'^\d{9}$', 'El teléfono debe tener 9 dígitos')]
    )
    
    # Campo para confirmar si necesita tutor
    incluir_tutor = forms.BooleanField(
        required=False,
        label='Este es un socio menor de edad (requiere tutor legal)'
    )
    
    class Meta:
        model = Socio
        fields = [
            'nombre', 'apellidos', 'email', 'role',
            'fecha_nacimiento', 'telefono', 'documento_identidad',
            'menor_edad', 'domicilia_pago', 'IBAN'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Miguel'}),
            'apellidos': forms.TextInput(attrs={'placeholder': 'Aparicio Sánchez'}),
            'email': forms.EmailInput(attrs={'placeholder': 'socio@fpvirtualaragon.com'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'documento_identidad': forms.TextInput(attrs={'placeholder': 'DNI/NIE'}),
            'IBAN': forms.TextInput(attrs={'placeholder': 'ES9121000418450200051332'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validación 1: IBAN obligatorio si domicilia pago
        if cleaned_data.get('domicilia_pago') and not cleaned_data.get('IBAN'):
            self.add_error('IBAN', 'El IBAN es obligatorio si se domicilia el pago')
           
        # Validación 2: Si es menor de edad, debe marcarse como tal
        fecha_nacimiento = cleaned_data.get('fecha_nacimiento')
        if fecha_nacimiento:
            today = date.today()
            edad = today.year - fecha_nacimiento.year - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
            if edad < 18 and not cleaned_data.get('menor_edad'):
                self.add_error('menor_edad', 'Debe marcarse como menor de edad')
            # Si es mayor, asegurarnos que el campo menor_edad es False
            if edad >= 18 and cleaned_data.get('menor_edad'):
                cleaned_data['menor_edad'] = False
        
        # Validación 3: Email único (case insensitive)
        email = cleaned_data.get('email')
        if email and Socio.objects.filter(email__iexact=email).exists():
            self.add_error('email', 'Ya existe un socio con este email')
        
        return cleaned_data
    
    def save(self, commit=True):
        # Guardar el socio
        socio = super().save(commit=False)
        
        # Aquí podrías añadir lógica adicional si es necesario
        # por ejemplo, enviar email de bienvenida
        
        if commit:
            socio.save()
        return socio