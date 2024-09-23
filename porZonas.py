import requests
import json
import os
import time

# Google Places API Key
API_KEY = 'AIzaSyDxGl_GyPEoQGWeSkUvgO_HpiO6Nz3pw6w'

def get_place_data(query, place_type, location, radius=500):
    # Parámetros de búsqueda inicial
    params = {
        'query': query,
        'location': location,  # Coordenadas en formato "lat,long"
        'radius': radius,  # Radio de búsqueda más pequeño en metros
        'type': place_type,
        'key': API_KEY
    }

    place_data = []
    has_next_page = True
    next_page_token = None

    while has_next_page:
        # Si existe un token de página siguiente, se añade a los parámetros
        if next_page_token:
            params['pagetoken'] = next_page_token

        # Realizamos la petición a la API de Google Places
        response = requests.get('https://maps.googleapis.com/maps/api/place/textsearch/json', params=params)
        results = response.json().get('results', [])
        next_page_token = response.json().get('next_page_token')

        # Para cada lugar, obtenemos más detalles (como el teléfono, la web y el email si está disponible)
        for place in results:
            name = place.get('name')
            place_id = place.get('place_id')

            # Solicitud para obtener detalles adicionales del lugar
            details_url = f'https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={API_KEY}'
            details_response = requests.get(details_url)
            details = details_response.json().get('result', {})

            phone_number = details.get('formatted_phone_number', 'No phone number available')
            website = details.get('website', 'No website available')
            email = details.get('email', 'No email available')

            # Añadimos los datos a la lista
            place_data.append({
                'name': name,
                'phone_number': phone_number,
                'website': website,
                'email': email
            })

        # Si no hay más páginas, salimos del bucle
        if not next_page_token:
            has_next_page = False
        else:
            # Esperamos un poco antes de hacer la siguiente solicitud
            time.sleep(2)

    return place_data

def save_to_json(data, filename):
    # Crear la carpeta 'places' si no existe
    folder_path = 'places'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Guardar el archivo en la carpeta 'places'
    file_path = os.path.join(folder_path, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Datos guardados en {file_path}.")

# Coordenadas aproximadas para diferentes puntos en Málaga y sus subzonas (divididos en 4 subzonas por cada zona principal)
zones = {
    'Centro': {
        'centro_norte': '36.7250,-4.4216',
        'centro_sur': '36.7180,-4.4216',
        'centro_este': '36.7213,-4.4160',
        'centro_oeste': '36.7213,-4.4272'
    },
    'Norte': {
        'norte_norte': '36.7360,-4.4165',
        'norte_sur': '36.7265,-4.4165',
        'norte_este': '36.7322,-4.4110',
        'norte_oeste': '36.7322,-4.4220'
    },
    'Sur': {
        'sur_norte': '36.7130,-4.4226',
        'sur_sur': '36.7050,-4.4226',
        'sur_este': '36.7085,-4.4170',
        'sur_oeste': '36.7085,-4.4280'
    },
    'Este': {
        'este_norte': '36.7220,-4.4100',
        'este_sur': '36.7150,-4.4100',
        'este_este': '36.7185,-4.4045',
        'este_oeste': '36.7185,-4.4175'
    },
    'Oeste': {
        'oeste_norte': '36.7265,-4.4320',
        'oeste_sur': '36.7185,-4.4320',
        'oeste_este': '36.7225,-4.4272',
        'oeste_oeste': '36.7225,-4.4370'
    }
}

# Radio más pequeño de búsqueda en metros para cada subzona
radius = 500

# Realizamos la búsqueda en cada subzona de cada área principal
for zone, subzones in zones.items():
    for subzone_name, location_coords in subzones.items():
        # Buscamos los datos de bares, restaurantes y clubes en cada subzona
        bars_data = get_place_data('bars in Malaga', 'bar', location_coords, radius)
        restaurants_data = get_place_data('restaurants in Malaga', 'restaurant', location_coords, radius)
        clubs_data = get_place_data('night clubs in Malaga', 'night_club', location_coords, radius)

        # Unimos los datos de bares, restaurantes y clubes para esta subzona
        all_places_data = bars_data + restaurants_data + clubs_data

        # Guardamos los datos en un archivo JSON diferente para cada subzona
        filename = f'places_data_{subzone_name}.json'
        save_to_json(all_places_data, filename)
