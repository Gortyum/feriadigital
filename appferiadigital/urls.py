# appferiadigital/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Cliente
    path('puestos/', views.lista_puestos_view, name='lista_puestos'),
    path('puesto/<int:id_puesto>/', views.detalle_puesto_view, name='detalle_puesto'),
    path('crear-reserva/', views.crear_reserva_view, name='crear_reserva'),
    
    # Vendedor
    path('mi-puesto/', views.mi_puesto_view, name='mi_puesto'),
    path('agregar-producto/', views.agregar_producto_view, name='agregar_producto'),
    path('mis-reservas/', views.mis_reservas_view, name='mis_reservas'),
    path('ferias/', views.lista_ferias, name='lista_ferias'),
    path('feria/<int:feria_id>/', views.detalle_feria, name='detalle_feria'),
]