# Simulación de utilidades de geolocalización
from geopy.distance import geodesic

def calcular_distancia(coord1, coord2):
    """Calcula la distancia en kilómetros entre dos coordenadas."""
    return geodesic(coord1, coord2).kilometers
