import requests
import json
import os

# Google Places API Key
API_KEY = 'AIzaSyDxGl_GyPEoQGWeSkUvgO_HpiO6Nz3pw6w'

def get_place_data(query, place_type):
    # Parámetros de búsqueda en Google Places
    params = {
        'query': query,
        'location': '36.7213,-4.4216',  # Coordenadas aproximadas de Málaga
        'radius': 15000,  # Radio de búsqueda en metros
        'type': place_type,  # Tipo de lugar (bar, restaurant, night_club)
        'key': API_KEY  # API key de Google
    }   

    # Realizamos la petición a la API de Google Places
    response = requests.get('https://maps.googleapis.com/maps/api/place/textsearch/json', params=params)
    results = response.json().get('results', [])

    # Para cada lugar, obtenemos más detalles (como el teléfono, web y email si existiera)
    place_data = []
    for place in results:
        name = place.get('name')
        place_id = place.get('place_id')

        # Solicitud para obtener detalles adicionales del lugar
        details_url = f'https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={API_KEY}'
        details_response = requests.get(details_url)
        details = details_response.json().get('result', {})

        phone_number = details.get('formatted_phone_number', 'No phone number available')
        website = details.get('website', 'No website available')
        email = details.get('email', 'No email available')  # Campo de email (si existiera, que en este caso no está presente en Google Places)

        # Añadimos los datos a la lista
        place_data.append({
            'name': name,
            'phone_number': phone_number,
            'website': website,
            'email': email  # Aunque no será proporcionado por Google Places, lo añadimos por si quieres integrarlo con otra fuente
        })

    return place_data

def save_to_json(data, filename='places_data2.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Datos guardados en {filename}.")

# Recopilamos datos de bares, restaurantes y clubes
bars_data = get_place_data('bares', 'bar')
restaurants_data = get_place_data('restaurantes', 'restaurant')
clubs_data = get_place_data('pubs', 'night_club')

# Unimos todos los datos en una sola lista
all_places_data = bars_data + restaurants_data + clubs_data

# Guardamos en un archivo JSON
save_to_json(all_places_data)
