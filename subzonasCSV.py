import requests
import json
import os
import time
import csv

# Google Places API Key
API_KEY = 'AIzaSyDxGl_GyPEoQGWeSkUvgO_HpiO6Nz3pw6w'

def get_place_data(query, place_type, location, radius=300):
    params = {
        'query': query,
        'location': location,
        'radius': radius,
        'type': place_type,
        'key': API_KEY
    }

    place_data = []
    has_next_page = True
    next_page_token = None

    while has_next_page:
        if next_page_token:
            params['pagetoken'] = next_page_token

        response = requests.get('https://maps.googleapis.com/maps/api/place/textsearch/json', params=params)
        results = response.json().get('results', [])
        next_page_token = response.json().get('next_page_token')

        for place in results:
            name = place.get('name')
            place_id = place.get('place_id')

            details_url = f'https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={API_KEY}'
            details_response = requests.get(details_url)
            details = details_response.json().get('result', {})

            phone_number = details.get('formatted_phone_number', 'No phone number available')
            website = details.get('website', 'No website available')
            email = details.get('email', 'No email available')
            location_data = details.get('geometry', {}).get('location', {})
            latitude = location_data.get('lat', 'No latitude available')
            longitude = location_data.get('lng', 'No longitude available')

            place_data.append({
                'name': name,
                'phone_number': phone_number,
                'website': website,
                'email': email,
                'latitude': latitude,
                'longitude': longitude
     })

        if not next_page_token:
            has_next_page = False
        else:
            time.sleep(2)

    return place_data

'''def save_to_json(data, filename):
    folder_path = 'places'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_path = os.path.join(folder_path, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Datos guardados en {file_path}.")'''

def save_to_csv(data, filename):
    folder_path = 'places'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_path = os.path.join(folder_path, filename)
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'phone_number', 'website', 'email', 'latitude', 'longitude'])
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f"Datos guardados en {file_path}.")

# Coordenadas aproximadas para diferentes puntos en Málaga y sus subzonas (divididos en 4 cuadrantes)
zones = {
    'Centro': {
        'centro_noroeste': '36.7260,-4.4260',
        'centro_noreste': '36.7260,-4.4170',
        'centro_suroeste': '36.7190,-4.4260',
        'centro_sureste': '36.7190,-4.4170'
    },
    'Norte': {
        'norte_noroeste': '36.7350,-4.4170',
        'norte_noreste': '36.7350,-4.4090',
        'norte_suroeste': '36.7270,-4.4170',
        'norte_sureste': '36.7270,-4.4090'
    },
    'Sur': {
        'sur_noroeste': '36.7120,-4.4220',
        'sur_noreste': '36.7120,-4.4140',
        'sur_suroeste': '36.7040,-4.4220',
        'sur_sureste': '36.7040,-4.4140'
    },
    'Este': {
        'este_noroeste': '36.7220,-4.4110',
        'este_noreste': '36.7220,-4.4030',
        'este_suroeste': '36.7150,-4.4110',
        'este_sureste': '36.7150,-4.4030'
    },
    'Oeste': {
        'oeste_noroeste': '36.7265,-4.4340',
        'oeste_noreste': '36.7265,-4.4260',
        'oeste_suroeste': '36.7195,-4.4340',
        'oeste_sureste': '36.7195,-4.4260'
    }
}

# División de cada subzona en 4 cuadrantes
subzones = {
    'noroeste': ['0.0001,-0.0001', '0.0001,0.0001', '-0.0001,-0.0001', '-0.0001,0.0001'],
    'noreste': ['0.0001,-0.0001', '0.0001,0.0001', '-0.0001,-0.0001', '-0.0001,0.0001'],
    'suroeste': ['0.0001,-0.0001', '0.0001,0.0001', '-0.0001,-0.0001', '-0.0001,0.0001'],
    'sureste': ['0.0001,-0.0001', '0.0001,0.0001', '-0.0001,-0.0001', '-0.0001,0.0001']
}

# Realizamos la búsqueda en cada subzona de cada área principal
for zone, quadrants in zones.items():
    for quadrant_name, location_coords in quadrants.items():
        # Dividir la ubicación de la subzona en 4 cuadrantes
        for subzone_suffix in ['noroeste', 'noreste', 'suroeste', 'sureste']:
            # Calculamos coordenadas para el cuadrante
            # Aquí puedes ajustar las coordenadas según la división deseada
            lat_offset = 0.0001 if 'noroeste' in subzone_suffix or 'noreste' in subzone_suffix else -0.0001
            lng_offset = 0.0001 if 'noreste' in subzone_suffix or 'sureste' in subzone_suffix else -0.0001
            subzone_location = f"{location_coords.split(',')[0]}, {float(location_coords.split(',')[1]) + lng_offset}"

            # Buscamos los datos de bares en cada cuadrante
            bars_data = get_place_data('bars in Malaga', 'bar', subzone_location, radius=300)

            # Guardamos los datos en un archivo JSON diferente para cada cuadrante
            filename = f'places_data_{zone}_{quadrant_name}.json'
            save_to_csv(bars_data, filename)
