import requests
import json
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ClimaService:
    @staticmethod
    def obtener_clima_por_ciudad(ciudad):
        """
        Obtiene el clima actual para una ciudad específica
        """
        cache_key = f"clima_{ciudad.lower().replace(' ', '_')}"
        
        # Intentar obtener de caché primero
        clima_cache = cache.get(cache_key)
        if clima_cache:
            return clima_cache
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': f"{ciudad},CL",  # CL para Chile
                'appid': settings.OPENWEATHERMAP_API_KEY,
                'units': 'metric',  # Para temperatura en Celsius
                'lang': 'es'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            datos = response.json()
            
            # Procesar los datos del clima
            clima = {
                'temperatura': round(datos['main']['temp'], 1),
                'sensacion_termica': round(datos['main']['feels_like'], 1),
                'humedad': datos['main']['humidity'],
                'descripcion': datos['weather'][0]['description'].capitalize(),
                'icono': datos['weather'][0]['icon'],
                'viento_velocidad': round(datos['wind']['speed'] * 3.6, 1),  # Convertir a km/h
                'viento_direccion': ClimaService._obtener_direccion_viento(datos['wind'].get('deg', 0)),
                'presion': datos['main']['pressure'],
                'visibilidad': datos.get('visibility', 0) / 1000 if datos.get('visibility') else None,
                'ciudad': datos['name'],
                'pais': datos['sys']['country'],
                'amanecer': datos['sys']['sunrise'],
                'atardecer': datos['sys']['sunset'],
                'hora_actualizacion': datos['dt']
            }
            
            # Guardar en caché
            cache.set(cache_key, clima, settings.WEATHER_CACHE_TIMEOUT)
            
            return clima
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener clima para {ciudad}: {e}")
            return None
        except KeyError as e:
            logger.error(f"Error en la estructura de datos del clima: {e}")
            return None
    
    @staticmethod
    def _obtener_direccion_viento(grados):
        """
        Convierte grados a dirección cardinal
        """
        direcciones = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                      'S', 'SSO', 'SO', 'OSO', 'O', 'ONO', 'NO', 'NNO']
        idx = round(grados / (360. / len(direcciones))) % len(direcciones)
        return direcciones[idx]
    
    @staticmethod
    def obtener_clima_por_coordenadas(lat, lon):
        """
        Obtiene el clima por coordenadas (opcional)
        """
        cache_key = f"clima_{lat}_{lon}"
        
        clima_cache = cache.get(cache_key)
        if clima_cache:
            return clima_cache
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': settings.OPENWEATHERMAP_API_KEY,
                'units': 'metric',
                'lang': 'es'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            datos = response.json()
            clima = ClimaService._procesar_datos_clima(datos)
            
            cache.set(cache_key, clima, settings.WEATHER_CACHE_TIMEOUT)
            return clima
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener clima para coordenadas {lat},{lon}: {e}")
            return None
    
    @staticmethod
    def _procesar_datos_clima(datos):
        """
        Procesa los datos crudos del clima
        """
        return {
            'temperatura': round(datos['main']['temp'], 1),
            'sensacion_termica': round(datos['main']['feels_like'], 1),
            'humedad': datos['main']['humidity'],
            'descripcion': datos['weather'][0]['description'].capitalize(),
            'icono': datos['weather'][0]['icon'],
            'viento_velocidad': round(datos['wind']['speed'] * 3.6, 1),
            'viento_direccion': ClimaService._obtener_direccion_viento(datos['wind'].get('deg', 0)),
            'presion': datos['main']['pressure'],
            'ciudad': datos['name'],
            'hora_actualizacion': datos['dt']
        }
    
    @staticmethod
    def obtener_icono_url(codigo_icono):
        """
        Obtiene la URL del icono del clima
        """
        return f"http://openweathermap.org/img/wn/{codigo_icono}@2x.png"