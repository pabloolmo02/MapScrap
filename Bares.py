import requests
import json

# Reemplaza con tu API key de Google Places
API_KEY = 'AIzaSyDxGl_GyPEoQGWeSkUvgO_HpiO6Nz3pw6w'

# URL del endpoint de Google Places
API_URL = 'https://maps.googleapis.com/maps/api/place/textsearch/json'

# Definir los parámetros de la búsqueda
params = {
    'query': 'bars in Malaga',
    'location': '36.7213,-4.4216',  # Coordenadas aproximadas de Málaga
    'radius': 15000,  # Radio de búsqueda en metros
    'type': 'restaurant',  # Tipo de lugar (puede ser bar o restaurant)
    'key': API_KEY  # API key de Google
}

# Hacer la solicitud a la API de Google Places
response = requests.get(API_URL, params=params)

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    data = response.json()
    print(data)
    exit()

    # Procesar y mostrar los resultados
    for place in data['results']:
        name = place.get('name')
        address = place.get('formatted_address')
        email = details.get('email', 'No email available')  # Nota: el email no siempre está disponible en la API.
        website = details.get('website', 'No website available')
        place_data.append([name, phone_number, website])  # Añade email si está disponible.

        try:
            # Obtener detalles adicionales como número de teléfono
            place_id = place['place_id']
            details_url = f'https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={API_KEY}'
            details_response = requests.get(details_url)
            details_data = details_response.json()
            phone_number = details_data['result'].get('formatted_phone_number', 'No phone number available')

            # Imprimir resultados
            print(f"Nombre: {name}")
            print(f"Dirección: {address}")
            print(f"Teléfono: {phone_number}")
            print('-' * 40)
        except KeyError:
            print(f"No se pudo obtener información detallada para {name}")
else:
    print(f"Error en la solicitud: {response.status_code}")
