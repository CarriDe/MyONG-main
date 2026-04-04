from django.db import models
from datetime import date
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

# Create your models here.
class Direccion(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    calle = models.CharField(max_length=200, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    piso = models.CharField(max_length=10, blank=True, null=True)
    otros = models.CharField(max_length=50, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    provincia = models.CharField(max_length=50, blank=True, null=True)
    codigo_postal = models.DecimalField(max_digits=5, decimal_places=0)
    pais = models.CharField(max_length=100, default='España')
    
    def __str__(self):
        return f"{self.calle}, {self.numero}, {self.ciudad} ({self.pais})"

# Modelo tutor legal:
class Tutor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=200)
    telefono = models.DecimalField(max_digits=9, decimal_places=0)
    email = models.EmailField(unique=True)
    documento_identidad = models.CharField(max_length=9, unique=True, null=True)
    
    # Relación uno a uno con dirección
    direccion = models.OneToOneField(Direccion, on_delete=models.CASCADE, related_name='tutor_legal', null=True)
    
    def __str__(self):
        return self.nombre
    
## Modelo Socio:
# Si un socio es menor de edad, necestará un tutor legal ( mayor de edad).
# Si un socio no domicilia sus pagos, el campo IBAN puede quedar vacío y
# además lo identicamos por el campo docimiciliado
# Los socios pueden tener distintos roles.
class Socio(models.Model):
    ROLES = [('ROOT', 'Superusuario'), ('ADMIN', 'Directivo'), ('USER', 'Usuario')]

    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=5, choices=ROLES, default='USER')

    fecha_nacimiento = models.DateField()
    telefono = models.DecimalField(max_digits=9, decimal_places=0)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    menor_edad = models.BooleanField()
    domicilia_pago = models.BooleanField(default=True)
    IBAN = models.CharField(max_length=34, blank=True, null=True)
    documento_identidad = models.CharField(max_length=9, unique=True, null=True)
    
    # Relación uno a uno con dirección
    direccion = models.OneToOneField(Direccion, on_delete=models.CASCADE, related_name='socio', null=True)
    
    # Relación opcional con tutor legal
    tutor_legal = models.ManyToManyField(Tutor, blank=True, null=True, related_name='socios')
    
    @property
    def es_menor(self):
       
        today = date.today()
        born = self.fecha_nacimiento
        edad = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        return edad < 18

    def __str__(self):
        return self.nombre

## Modelo para pagos de socios
## Los pagos estarán relacionados con un socio
## Cada pago tendrá una fecha, un importe y un estado (pendiente, completado, fallido)
## Los pagos se pueden hacer por transferencia y tendrán que validarse por un admin
## Otros pagos se realizan mediante remesa bancaria: Si se devuelve el recibo, 
## el estado del pago será devuelto.
class Pago(models.Model):
    ESTADO_PAGOS = [('PENDIENTE', 'Pendiente'),
                    ('COMPLETADO', 'Completado'), 
                    ('EN_TRAMITE', 'En tramite'),
                    ('DEVUELTO', 'Devuelto')]
    
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    socio = models.ForeignKey(Socio, on_delete=models.PROTECT, related_name='pagos')
    
    mes = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    anio = models.PositiveSmallIntegerField(validators=[MinValueValidator(2000), MaxValueValidator(2100)])

    cuota_base_aplicada = models.DecimalField(max_digits=6, decimal_places=2)
    estado = models.CharField(max_length=12, choices=ESTADO_PAGOS, default='PENDIENTE')

    class Meta:
        unique_together = ('socio', 'mes', 'anio')
        ordering = ['-anio', '-mes']

    def __str__(self):
        return f"Pago {self.mes}/{self.anio} - {self.socio.nombre} - {self.estado}"