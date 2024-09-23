import requests
import json
import google.auth
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path

# Google Places API Key
API_KEY = 'AIzaSyDxGl_GyPEoQGWeSkUvgO_HpiO6Nz3pw6w'

# Google Sheets setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '103713341624095431306'  # ID de la hoja de Google
RANGE_NAME = 'A1'  # Donde se insertarán los datos (puedes ajustar)

def get_place_data(query, place_type):
    # Parámetros de búsqueda en Google Places
    params = {
        'query': query,
        'location': '36.7213,-4.4216',  # Coordenadas aproximadas de Málaga
        'radius': 15000,  # Radio de búsqueda en metros
        'type': place_type,  # Tipo de lugar (puede ser bar o restaurant)
        'key': API_KEY  # API key de Google
    }   

    # Realizamos la petición a la API de Google Places
    response = requests.get('https://maps.googleapis.com/maps/api/place/textsearch/json', params=params)
    results = response.json().get('results', [])

    # Para cada lugar, obtenemos más detalles (como el teléfono y la web)
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

        # Añadimos los datos a la lista
        place_data.append([name, phone_number, website])

    return place_data

def save_to_google_sheet(data):
    creds = None
    # Cargar las credenciales del archivo token
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # Si no hay credenciales válidas, hacemos login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Guardamos las credenciales para futuras ejecuciones
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # Llamamos a la API de Google Sheets para escribir datos
    body = {
        'values': data
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
        valueInputOption='RAW', body=body).execute()
    print(f"{result.get('updatedCells')} celdas actualizadas.")

# Recopilamos datos de bares, restaurantes y clubes
bars_data = get_place_data('bars in Malaga', 'bar')
restaurants_data = get_place_data('restaurants in Malaga', 'restaurant')
clubs_data = get_place_data('night clubs in Malaga', 'night_club')

# Unimos todos los datos en una sola lista
all_places_data = bars_data + restaurants_data + clubs_data

# Guardamos en Google Sheets
save_to_google_sheet(all_places_data)
