# appferiadigital/admin.py (para administrar desde el panel de Django)
from django.contrib import admin
from .models import Usuario, Feria, Puesto, Categoria, Producto, Reserva, ReservaProducto

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('rut', 'nombre', 'email', 'rol')
    list_filter = ('rol',)
    search_fields = ('rut', 'nombre', 'email')

@admin.register(Feria)
class FeriaAdmin(admin.ModelAdmin):
    list_display = ('nombre_feria', 'ubicacion_feria', 'aglomeracion')
    search_fields = ('nombre_feria',)

@admin.register(Puesto)
class PuestoAdmin(admin.ModelAdmin):
    list_display = ('id_puesto', 'numero_puesto', 'id_feria', 'id_usuario')
    list_filter = ('id_feria',)
    search_fields = ('numero_puesto', 'id_usuario__nombre')

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo')
    search_fields = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre_producto', 'id_puesto', 'stock', 'id_categoria')
    list_filter = ('id_categoria',)
    search_fields = ('nombre_producto',)

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id_reserva', 'id_usuario', 'id_producto', 'cantidad', 'fecha_reserva')
    list_filter = ('fecha_reserva',)
    search_fields = ('id_usuario__nombre',)

@admin.register(ReservaProducto)
class ReservaProductoAdmin(admin.ModelAdmin):
    list_display = ('id_reserva', 'id_producto', 'cantidad_reserva', 'unidad_de_medida')