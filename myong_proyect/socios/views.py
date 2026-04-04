# socios/views.py
from django.http import Http404
import json
import uuid
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SocioForm, DireccionForm, TutorForm
from .models import Socio, Direccion, Tutor, Pago
from datetime import date

# Datos simulados (normalmente vendrían de la base de datos)
SOCIOS_JSON = """
[
    {
        "id": "c6f3e99b-1a20-4f6a-89a3-cc7c0a1c24f1",
        "nombre": "María",
        "apellidos": "García López",
        "fecha_nacimiento": "1990-05-12",
        "telefono": "678123456",
        "email": "maria@example.com",
        "menor_edad": false,
        "IBAN": "ES9820385778983000760236",
        "documento_identidad": "12345678A",
        "direccion": {
            "calle": "Calle Mayor",
            "numero": "10",
            "piso": "2ºB",
            "otros": "",
            "ciudad": "Valdepeñas",
            "codigo_postal": "13300",
            "provincia": "Ciudad Real",
            "pais": "España"
        }
    },
    {
        "id": "d3ad1234-9876-4567-a8b9-abcdef123456",
        "nombre": "Javier",
        "apellidos": "Martínez Ruiz",
        "fecha_nacimiento": "2005-03-02",
        "telefono": "654789321",
        "email": "javier@example.com",
        "menor_edad": true,
        "IBAN": null,
        "documento_identidad": "98765432B",
        "direccion": {
            "calle": "Avenida del Vino",
            "numero": "55",
            "piso": "",
            "otros": "Bis",
            "ciudad": "Valdepeñas",
            "codigo_postal": "13300",
            "provincia": "Ciudad Real",
            "pais": "España"
        }
    }
]
"""

# Cargar los datos JSON como lista de diccionarios
SOCIOS = json.loads(SOCIOS_JSON)


# VISTA DE LISTA DE SOCIOS
def lista_socios(request):
    # Ahora vamos a recuperar los socios desde la "base de datos"
    socios = Socio.objects.select_related('direccion').all()
    return render(request, 'socios/socio_list.html', {'socios': socios})
   # return render(request, 'socios/socio_list.html', {'socios': SOCIOS})


# VISTA DE DETALLE DE UN SOCIO
def detalle_socio(request, socio_id):
    socios = Socio.objects.select_related('direccion').all() 
    print("SOCIOS ", list(socios))  # imprime todos los socios  
    socio = next((s for s in socios if str(s.id) == str(socio_id)), None)
    print("SOCIO ", socio)  # imprime el socio encontrado
    if socio is None:
        raise Http404("Socio no encontrado")

    return render(request, 'socios/socio_detail.html', {'socio': socio})


def alta_socio(request):
    if request.method == 'POST':
        socio_form = SocioForm(request.POST)
        direccion_form = DireccionForm(request.POST, prefix='direccion')
        tutor_form = TutorForm(request.POST, prefix='tutor')
        
        if socio_form.is_valid() and direccion_form.is_valid():
            # Guardar dirección primero
            direccion = direccion_form.save()
            
            # Guardar socio
            socio = socio_form.save(commit=False)
            socio.direccion = direccion
            socio.save()
            
            # Si es menor de edad y se incluye tutor
            if socio.menor_edad and tutor_form.is_valid():
                tutor = tutor_form.save()
                socio.tutor_legal.add(tutor)
                messages.success(request, f'Socio {socio.nombre} {socio.apellidos} creado con tutor legal')
            else:
                messages.success(request, f'Socio {socio.nombre} {socio.apellidos} creado exitosamente')
            
            return redirect('lista_socios')  # Cambia por tu URL
            
    else:
        socio_form = SocioForm()
        direccion_form = DireccionForm(prefix='direccion')
        tutor_form = TutorForm(prefix='tutor')
    
    return render(request, 'socios/alta_socio.html', {
        'socio_form': socio_form,
        'direccion_form': direccion_form,
        'tutor_form': tutor_form,
    })

def pagos_socio_current_year(request, socio_id):
    # Lógica para manejar los pagos del socio
    current_year = date.today().year
    current_month = date.today().month

    # Generar lista de últimos 4 años (incluyendo el actual)
    años_disponibles = list(range(current_year - 3, current_year + 1))
    
    # Aquí iría la lógica para obtener los pagos del socio desde la base de datos
    pagos = Pago.objects.filter(socio__id=socio_id, anio=current_year, mes__lte=current_month).order_by('mes')
    socio = Socio.objects.get(id=socio_id)
    return render(request, 'socios/pagos_socio_year.html', {
        'socio_id': socio_id,
        'pagos': pagos,
        'nombre_socio': socio.nombre,
        'apellidos_socio': socio.apellidos,
        'email_socio': socio.email,
        'year': current_year,
        'month': current_month,
        'domicilia_pago': socio.domicilia_pago,
        'años_disponibles': años_disponibles,    
    })

def pagos_socio_by_year(request, socio_id, year):        
    # Obtener el socio
    pagos = Pago.objects.filter(socio__id=socio_id, anio=year).order_by('mes')
    socio = Socio.objects.get(id=socio_id)

    # Generar lista de últimos 4 años (incluyendo el actual)
    current_year = date.today().year
    años_disponibles = list(range(current_year - 3, current_year + 1))
    
    # Asegurarse de que el año solicitado está en la lista
    if year not in años_disponibles:
        años_disponibles.append(year)
        años_disponibles.sort()
    
    return render(request, 'socios/pagos_socio_year.html', {
        'socio_id': socio_id,
        'pagos': pagos,
        'nombre_socio': socio.nombre,
        'apellidos_socio': socio.apellidos,
        'email_socio': socio.email,
        'year': current_year,
        'month': 12,
        'domicilia_pago': socio.domicilia_pago,
        'años_disponibles': años_disponibles,    
    })