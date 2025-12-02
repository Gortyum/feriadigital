# appferiadigital/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from django.conf import settings
from datetime import datetime,  timedelta
from django.db.models import Q, Sum, Count
from django.views.decorators.csrf import csrf_protect
from .models import Usuario, Puesto, Producto, Reserva, Feria, Categoria
import re
from .clima_service import ClimaService


def validar_rut(rut):
    """Validación básica de formato RUT chileno"""
    patron = r'^\d{7,8}-[\dkK]$'
    return bool(re.match(patron, rut))

def validar_email(email):
    """Validación básica de email"""
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(patron, email))

@csrf_protect
def login_view(request):
    if request.session.get('usuario_id'):
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        contrasena = request.POST.get('contrasena', '')
        
        if not email or not contrasena:
            messages.error(request, 'Debe ingresar email y contraseña')
            return render(request, 'login.html')
        
        try:
            usuario = Usuario.objects.get(email=email)
            if check_password(contrasena, usuario.contrasena):
                request.session['usuario_id'] = usuario.id_usuario
                request.session['usuario_rol'] = usuario.rol
                request.session['usuario_nombre'] = usuario.nombre
                messages.success(request, f'Bienvenido {usuario.nombre}')
                return redirect('dashboard')
            else:
                messages.error(request, 'Credenciales incorrectas')
        except Usuario.DoesNotExist:
            messages.error(request, 'Credenciales incorrectas')
    
    return render(request, 'login.html')

@csrf_protect
def registro_view(request):
    if request.method == 'POST':
        rut = request.POST.get('rut', '').strip()
        nombre = request.POST.get('nombre', '').strip()
        email = request.POST.get('email', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        rol = request.POST.get('rol', '')
        contrasena = request.POST.get('contrasena', '')
        confirmar = request.POST.get('confirmar', '')
        
        # Validaciones
        if not all([rut, nombre, email, rol, contrasena]):
            messages.error(request, 'Todos los campos obligatorios deben ser completados')
            return render(request, 'registro.html')
        
        if not validar_rut(rut):
            messages.error(request, 'Formato de RUT inválido (Ej: 12345678-9)')
            return render(request, 'registro.html')
        
        if not validar_email(email):
            messages.error(request, 'Formato de email inválido')
            return render(request, 'registro.html')
        
        if len(contrasena) < 6:
            messages.error(request, 'La contraseña debe tener al menos 6 caracteres')
            return render(request, 'registro.html')
        
        if contrasena != confirmar:
            messages.error(request, 'Las contraseñas no coinciden')
            return render(request, 'registro.html')
        
        if Usuario.objects.filter(Q(rut=rut) | Q(email=email)).exists():
            messages.error(request, 'El RUT o email ya están registrados')
            return render(request, 'registro.html')
        
        # Crear usuario
        usuario = Usuario.objects.create(
            rut=rut,
            nombre=nombre,
            email=email,
            telefono=telefono,
            rol=rol,
            contrasena=make_password(contrasena)
        )
        
        messages.success(request, 'Registro exitoso. Inicie sesión')
        return redirect('login')
    
    return render(request, 'registro.html')

def logout_view(request):
    request.session.flush()
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('login')

def dashboard_view(request):
    if not request.session.get('usuario_id'):
        return redirect('login')
    
    usuario_rol = request.session.get('usuario_rol')
    context = {'rol': usuario_rol}
    return render(request, 'dashboard.html', context)

# VISTAS CLIENTE
def lista_puestos_view(request):
    if not request.session.get('usuario_id'):
        return redirect('login')
    
    if request.session.get('usuario_rol') != 'cliente':
        messages.error(request, 'Acceso denegado')
        return redirect('dashboard')
    
    puestos = Puesto.objects.select_related('id_feria', 'id_usuario').all()
    context = {'puestos': puestos}
    return render(request, 'lista_puestos.html', context)

def detalle_puesto_view(request, id_puesto):
    if not request.session.get('usuario_id'):
        return redirect('login')
    
    if request.session.get('usuario_rol') != 'cliente':
        messages.error(request, 'Acceso denegado')
        return redirect('dashboard')
    
    puesto = get_object_or_404(Puesto, id_puesto=id_puesto)
    productos = Producto.objects.filter(id_puesto=puesto).select_related('id_categoria')
    context = {'puesto': puesto, 'productos': productos}
    return render(request, 'detalle_puesto.html', context)

def crear_reserva_view(request):
    if not request.session.get('usuario_id'):
        return redirect('login')
    
    if request.session.get('usuario_rol') != 'cliente':
        messages.error(request, 'Acceso denegado')
        return redirect('dashboard')
    
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        cantidad = request.POST.get('cantidad')
        
        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, 'Cantidad inválida')
            return redirect('lista_puestos')
        
        producto = get_object_or_404(Producto, id_producto=producto_id)
        
        if cantidad > producto.stock:
            messages.error(request, 'Stock insuficiente')
            return redirect('detalle_puesto', id_puesto=producto.id_puesto.id_puesto)
        
        usuario = Usuario.objects.get(id_usuario=request.session.get('usuario_id'))
        
        Reserva.objects.create(
            id_usuario=usuario,
            id_producto=producto,
            cantidad=cantidad
        )
        
        producto.stock -= cantidad
        producto.save()
        
        messages.success(request, 'Reserva creada exitosamente')
        return redirect('detalle_puesto', id_puesto=producto.id_puesto.id_puesto)
    
    return redirect('lista_puestos')

# VISTAS VENDEDOR
def mi_puesto_view(request):
    if not request.session.get('usuario_id'):
        return redirect('login')
    
    if request.session.get('usuario_rol') != 'vendedor':
        messages.error(request, 'Acceso denegado')
        return redirect('dashboard')
    
    usuario = Usuario.objects.get(id_usuario=request.session.get('usuario_id'))
    
    if request.method == 'POST':
        feria_id = request.POST.get('feria_id')
        numero_puesto = request.POST.get('numero_puesto', '').strip()
        
        if not feria_id:
            messages.error(request, 'Debe seleccionar una feria')
        else:
            feria = get_object_or_404(Feria, id_feria=feria_id)
            Puesto.objects.create(
                id_feria=feria,
                id_usuario=usuario,
                numero_puesto=numero_puesto
            )
            messages.success(request, 'Puesto creado exitosamente')
            return redirect('mi_puesto')
    
    puestos = Puesto.objects.filter(id_usuario=usuario).select_related('id_feria')
    ferias = Feria.objects.all()
    context = {'puestos': puestos, 'ferias': ferias}
    return render(request, 'mi_puesto.html', context)

def agregar_producto_view(request):
    if not request.session.get('usuario_id'):
        return redirect('login')
    
    if request.session.get('usuario_rol') != 'vendedor':
        messages.error(request, 'Acceso denegado')
        return redirect('dashboard')
    
    usuario = Usuario.objects.get(id_usuario=request.session.get('usuario_id'))
    puestos = Puesto.objects.filter(id_usuario=usuario)
    
    if not puestos.exists():
        messages.error(request, 'Debe crear un puesto primero')
        return redirect('mi_puesto')
    
    if request.method == 'POST':
        puesto_id = request.POST.get('puesto_id')
        nombre = request.POST.get('nombre', '').strip()
        stock = request.POST.get('stock')
        categoria_id = request.POST.get('categoria_id')
        
        try:
            stock = int(stock)
            if stock < 0:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, 'Stock inválido')
            return redirect('agregar_producto')
        
        if not nombre:
            messages.error(request, 'El nombre es obligatorio')
            return redirect('agregar_producto')
        
        puesto = get_object_or_404(Puesto, id_puesto=puesto_id, id_usuario=usuario)
        categoria = None
        if categoria_id:
            categoria = get_object_or_404(Categoria, id_categoria=categoria_id)
        
        Producto.objects.create(
            id_puesto=puesto,
            id_categoria=categoria,
            nombre_producto=nombre,
            stock=stock
        )
        
        messages.success(request, 'Producto agregado exitosamente')
        return redirect('agregar_producto')
    
    categorias = Categoria.objects.all()
    context = {'puestos': puestos, 'categorias': categorias}
    return render(request, 'agregar_producto.html', context)

def mis_reservas_view(request):
    if not request.session.get('usuario_id'):
        return redirect('login')
    
    if request.session.get('usuario_rol') != 'vendedor':
        messages.error(request, 'Acceso denegado')
        return redirect('dashboard')
    
    usuario = Usuario.objects.get(id_usuario=request.session.get('usuario_id'))
    puestos = Puesto.objects.filter(id_usuario=usuario)
    productos = Producto.objects.filter(id_puesto__in=puestos)
    reservas = Reserva.objects.filter(id_producto__in=productos).select_related('id_usuario', 'id_producto')
    
    context = {'reservas': reservas}
    return render(request, 'mis_reservas.html', context)

def mis_reservas_cliente_view(request):
    """Ver todas las reservas del cliente"""
    if not request.session.get('usuario_id'):
        return redirect('login')
    
    if request.session.get('usuario_rol') != 'cliente':
        messages.error(request, 'Acceso denegado')
        return redirect('dashboard')
    
    usuario = Usuario.objects.get(id_usuario=request.session.get('usuario_id'))
    reservas = Reserva.objects.filter(id_usuario=usuario).select_related(
        'id_producto__id_puesto__id_feria'
    ).order_by('-fecha_reserva')
    
    context = {'reservas': reservas}
    return render(request, 'mis_reservas_cliente.html', context)


def cancelar_reserva_view(request, id_reserva):
    """Cancelar una reserva y devolver stock"""
    if not request.session.get('usuario_id'):
        return redirect('login')
    
    if request.session.get('usuario_rol') != 'cliente':
        messages.error(request, 'Acceso denegado')
        return redirect('dashboard')
    
    usuario = Usuario.objects.get(id_usuario=request.session.get('usuario_id'))
    reserva = get_object_or_404(Reserva, id_reserva=id_reserva, id_usuario=usuario)
    
    # Devolver stock
    if reserva.id_producto:
        producto = reserva.id_producto
        producto.stock += reserva.cantidad
        producto.save()
    
    reserva.delete()
    messages.success(request, 'Reserva cancelada exitosamente')
    return redirect('mis_reservas_cliente')


def buscar_productos_view(request):
    """Buscar productos por nombre o categoría"""
    if not request.session.get('usuario_id'):
        return redirect('login')
    
    if request.session.get('usuario_rol') != 'cliente':
        messages.error(request, 'Acceso denegado')
        return redirect('dashboard')
    
    query = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria')
    
    productos = Producto.objects.select_related(
        'id_puesto__id_feria', 'id_categoria'
    ).filter(stock__gt=0)
    
    if query:
        productos = productos.filter(nombre_producto__icontains=query)
    
    if categoria_id:
        productos = productos.filter(id_categoria_id=categoria_id)
    
    categorias = Categoria.objects.all()
    context = {
        'productos': productos,
        'categorias': categorias,
        'query': query,
        'categoria_seleccionada': categoria_id
    }
    return render(request, 'buscar_productos.html', context)


def lista_ferias(request):
    """Lista de ferias con clima"""
    ferias = Feria.objects.all()
    
    # Agregar clima a cada feria
    for feria in ferias:
        if feria.ciudad:
            feria.clima = ClimaService.obtener_clima_por_ciudad(feria.ciudad)
        else:
            feria.clima = None
    
    return render(request, 'lista_ferias.html', {'ferias': ferias})

def detalle_feria(request, feria_id):
    """Detalle de una feria con clima"""
    feria = get_object_or_404(Feria, id_feria=feria_id)
    puestos = Puesto.objects.filter(id_feria=feria)
    
    # Obtener clima
    clima = None
    if feria.ciudad:
        clima = ClimaService.obtener_clima_por_ciudad(feria.ciudad)
    
    return render(request, 'detalle_feria.html', {
        'feria': feria,
        'puestos': puestos,
        'clima': clima
    })


# ========== VISTAS VENDEDOR - ADICIONALES ==========

def editar_producto_view(request, id_producto):
    """Editar información de un producto"""
    if not request.session.get('usuario_id'):
        return redirect('login')
    
    if request.session.get('usuario_rol') != 'vendedor':
        messages.error(request, 'Acceso denegado')
        return redirect('dashboard')
    
    usuario = Usuario.objects.get(id_usuario=request.session.get('usuario_id'))
    producto = get_object_or_404(
        Producto, 
        id_producto=id_producto,
        id_puesto__id_usuario=usuario
    )
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        stock = request.POST.get('stock')
        categoria_id = request.POST.get('categoria_id')
        
        try:
            stock = int(stock)
            if stock < 0:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, 'Stock inválido')
            return redirect('editar_producto', id_producto=id_producto)
        
        if not nombre:
            messages.error(request, 'El nombre es obligatorio')
            return redirect('editar_producto', id_producto=id_producto)
        
        producto.nombre_producto = nombre
        producto.stock = stock
        
        if categoria_id:
            categoria = get_object_or_404(Categoria, id_categoria=categoria_id)
            producto.id_categoria = categoria
        else:
            producto.id_categoria = None
        
        producto.save()
        messages.success(request, 'Producto actualizado exitosamente')
        return redirect('mis_productos')
    
    categorias = Categoria.objects.all()
    context = {'producto': producto, 'categorias': categorias}
    return render(request, 'editar_producto.html', context)


def eliminar_producto_view(request, id_producto):
    """Eliminar un producto (solo si no tiene reservas)"""
    if not request.session.get('usuario_id'):
        return redirect('login')
    
    if request.session.get('usuario_rol') != 'vendedor':
        messages.error(request, 'Acceso denegado')
        return redirect('dashboard')
    
    usuario = Usuario.objects.get(id_usuario=request.session.get('usuario_id'))
    producto = get_object_or_404(
        Producto, 
        id_producto=id_producto,
        id_puesto__id_usuario=usuario
    )
    
    # Verificar si tiene reservas activas
    if Reserva.objects.filter(id_producto=producto).exists():
        messages.error(request, 'No se puede eliminar: el producto tiene reservas activas')
        return redirect('mis_productos')
    
    producto.delete()
    messages.success(request, 'Producto eliminado exitosamente')
    return redirect('mis_productos')


def mis_productos_view(request):
    """Ver todos los productos del vendedor"""
    if not request.session.get('usuario_id'):
        return redirect('login')
    
    if request.session.get('usuario_rol') != 'vendedor':
        messages.error(request, 'Acceso denegado')
        return redirect('dashboard')
    
    usuario = Usuario.objects.get(id_usuario=request.session.get('usuario_id'))
    puestos = Puesto.objects.filter(id_usuario=usuario)
    productos = Producto.objects.filter(
        id_puesto__in=puestos
    ).select_related('id_puesto', 'id_categoria').order_by('id_puesto', 'nombre_producto')
    
    context = {'productos': productos}
    return render(request, 'mis_productos.html', context)


def actualizar_estado_reserva_view(request, id_reserva):
    """Marcar reserva como completada o procesada"""
    if not request.session.get('usuario_id'):
        return redirect('login')
    
    if request.session.get('usuario_rol') != 'vendedor':
        messages.error(request, 'Acceso denegado')
        return redirect('dashboard')
    
    usuario = Usuario.objects.get(id_usuario=request.session.get('usuario_id'))
    
    # Verificar que la reserva pertenece a un producto del vendedor
    reserva = get_object_or_404(
        Reserva,
        id_reserva=id_reserva,
        id_producto__id_puesto__id_usuario=usuario
    )
    
    # Aquí podrías agregar un campo de estado a Reserva si lo deseas
    # Por ahora, simplemente la eliminamos como "completada"
    reserva.delete()
    messages.success(request, 'Reserva procesada exitosamente')
    return redirect('mis_reservas')


def estadisticas_vendedor_view(request):
    """Ver estadísticas de ventas y reservas"""
    if not request.session.get('usuario_id'):
        return redirect('login')
    
    if request.session.get('usuario_rol') != 'vendedor':
        messages.error(request, 'Acceso denegado')
        return redirect('dashboard')
    
    usuario = Usuario.objects.get(id_usuario=request.session.get('usuario_id'))
    puestos = Puesto.objects.filter(id_usuario=usuario)
    productos = Producto.objects.filter(id_puesto__in=puestos)
    
    # Estadísticas
    total_productos = productos.count()
    total_stock = productos.aggregate(total=Sum('stock'))['total'] or 0
    total_reservas = Reserva.objects.filter(id_producto__in=productos).count()
    cantidad_reservada = Reserva.objects.filter(
        id_producto__in=productos
    ).aggregate(total=Sum('cantidad'))['total'] or 0
    
    # Productos más reservados
    productos_populares = Reserva.objects.filter(
        id_producto__in=productos
    ).values(
        'id_producto__nombre_producto'
    ).annotate(
        total_reservado=Sum('cantidad')
    ).order_by('-total_reservado')[:5]
    
    # Reservas recientes (últimos 7 días)
    fecha_limite = datetime.now().date() - timedelta(days=7)
    reservas_recientes = Reserva.objects.filter(
        id_producto__in=productos,
        fecha_reserva__gte=fecha_limite
    ).count()
    
    context = {
        'total_productos': total_productos,
        'total_stock': total_stock,
        'total_reservas': total_reservas,
        'cantidad_reservada': cantidad_reservada,
        'productos_populares': productos_populares,
        'reservas_recientes': reservas_recientes
    }
    return render(request, 'estadisticas_vendedor.html', context)


def editar_puesto_view(request, id_puesto):
    """Editar información del puesto"""
    if not request.session.get('usuario_id'):
        return redirect('login')
    
    if request.session.get('usuario_rol') != 'vendedor':
        messages.error(request, 'Acceso denegado')
        return redirect('dashboard')
    
    usuario = Usuario.objects.get(id_usuario=request.session.get('usuario_id'))
    puesto = get_object_or_404(Puesto, id_puesto=id_puesto, id_usuario=usuario)
    
    if request.method == 'POST':
        numero_puesto = request.POST.get('numero_puesto', '').strip()
        feria_id = request.POST.get('feria_id')
        
        if feria_id:
            feria = get_object_or_404(Feria, id_feria=feria_id)
            puesto.id_feria = feria
        
        puesto.numero_puesto = numero_puesto
        puesto.save()
        
        messages.success(request, 'Puesto actualizado exitosamente')
        return redirect('mi_puesto')
    
    ferias = Feria.objects.all()
    context = {'puesto': puesto, 'ferias': ferias}
    return render(request, 'editar_puesto.html', context)


def eliminar_puesto_view(request, id_puesto):
    """Eliminar un puesto (solo si no tiene productos)"""
    if not request.session.get('usuario_id'):
        return redirect('login')
    
    if request.session.get('usuario_rol') != 'vendedor':
        messages.error(request, 'Acceso denegado')
        return redirect('dashboard')
    
    usuario = Usuario.objects.get(id_usuario=request.session.get('usuario_id'))
    puesto = get_object_or_404(Puesto, id_puesto=id_puesto, id_usuario=usuario)
    
    # Verificar si tiene productos
    if Producto.objects.filter(id_puesto=puesto).exists():
        messages.error(request, 'No se puede eliminar: el puesto tiene productos asociados')
        return redirect('mi_puesto')
    
    puesto.delete()
    messages.success(request, 'Puesto eliminado exitosamente')
    return redirect('mi_puesto')


# ========== VISTAS COMUNES ==========

def perfil_view(request):
    """Ver y editar perfil de usuario"""
    if not request.session.get('usuario_id'):
        return redirect('login')
    
    usuario = Usuario.objects.get(id_usuario=request.session.get('usuario_id'))
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        email = request.POST.get('email', '').strip()
        
        if not nombre:
            messages.error(request, 'El nombre es obligatorio')
            return redirect('perfil')
        
        # Verificar email único
        if email != usuario.email:
            if Usuario.objects.filter(email=email).exists():
                messages.error(request, 'El email ya está registrado')
                return redirect('perfil')
            
            if not validar_email(email):
                messages.error(request, 'Formato de email inválido')
                return redirect('perfil')
        
        usuario.nombre = nombre
        usuario.telefono = telefono
        usuario.email = email
        usuario.save()
        
        request.session['usuario_nombre'] = usuario.nombre
        messages.success(request, 'Perfil actualizado exitosamente')
        return redirect('perfil')
    
    context = {'usuario': usuario}
    return render(request, 'perfil.html', context)


def cambiar_contrasena_view(request):
    """Cambiar contraseña del usuario"""
    if not request.session.get('usuario_id'):
        return redirect('login')
    
    if request.method == 'POST':
        contrasena_actual = request.POST.get('contrasena_actual', '')
        nueva_contrasena = request.POST.get('nueva_contrasena', '')
        confirmar_nueva = request.POST.get('confirmar_nueva', '')
        
        usuario = Usuario.objects.get(id_usuario=request.session.get('usuario_id'))
        
        if not check_password(contrasena_actual, usuario.contrasena):
            messages.error(request, 'Contraseña actual incorrecta')
            return redirect('cambiar_contrasena')
        
        if len(nueva_contrasena) < 6:
            messages.error(request, 'La nueva contraseña debe tener al menos 6 caracteres')
            return redirect('cambiar_contrasena')
        
        if nueva_contrasena != confirmar_nueva:
            messages.error(request, 'Las contraseñas no coinciden')
            return redirect('cambiar_contrasena')
        
        usuario.contrasena = make_password(nueva_contrasena)
        usuario.save()
        
        messages.success(request, 'Contraseña cambiada exitosamente')
        return redirect('perfil')
    
    return render(request, 'cambiar_contrasena.html')


# Utilidad de validación (ya existente, incluida para referencia)
def validar_rut(rut):
    """Validación básica de formato RUT chileno"""
    import re
    patron = r'^\d{7,8}-[\dkK]$'
    return bool(re.match(patron, rut))


def validar_email(email):
    """Validación básica de email"""
    import re
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(patron, email))