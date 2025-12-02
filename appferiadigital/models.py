from django.db import models
from .clima_service import ClimaService

class Usuario(models.Model):
    ROLES = [
        ('cliente', 'Cliente'),
        ('vendedor', 'Vendedor'),
    ]

    id_usuario = models.AutoField(primary_key=True)
    rut = models.CharField(max_length=15, unique=True)
    nombre = models.CharField(max_length=100)
    puesto = models.CharField(max_length=100, blank=True, null=True)
    rol = models.CharField(max_length=10, choices=ROLES)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    contrasena = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.nombre} ({self.rol})"


# Agregar estos campos al modelo Feria
class Feria(models.Model):
    id_feria = models.AutoField(primary_key=True)
    nombre_feria = models.CharField(max_length=100)
    ubicacion_feria = models.CharField(max_length=200, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)  # Campo nuevo
    aglomeracion = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.nombre_feria


class Puesto(models.Model):
    id_puesto = models.AutoField(primary_key=True)
    id_feria = models.ForeignKey(Feria, on_delete=models.CASCADE)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='puestos')
    numero_puesto = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Puesto {self.numero_puesto or self.id_puesto} - {self.id_feria.nombre_feria}"


class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    id_puesto = models.ForeignKey(Puesto, on_delete=models.CASCADE)
    id_categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, blank=True, null=True)
    nombre_producto = models.CharField(max_length=100)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nombre_producto} ({self.id_puesto})"


class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True, blank=True)  
    cantidad = models.PositiveIntegerField()
    fecha_reserva = models.DateField(auto_now_add=True)


    def __str__(self):
        return f"Reserva {self.id_reserva} - {self.id_usuario.nombre}"


class ReservaProducto(models.Model):
    id_reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_reserva = models.IntegerField()
    unidad_de_medida = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        unique_together = (('id_reserva', 'id_producto'),)

    def __str__(self):
        return f"{self.id_producto.nombre_producto} x{self.cantidad_reserva}"
