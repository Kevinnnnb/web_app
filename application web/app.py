from bottle import Bottle, run, template, request, response, redirect
import requests
import requests_cache
import pandas as pd
from retry_requests import retry
import datetime
import json
import openai

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
api_key = 'AIzaSyBf8GB8MJ9X8lfemvQV3PIFdU1s1Ge97Vg'  # Clé API Google
openai_api_key = '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'  # Remplacez par votre clé API OpenAI

def get_location_coordinates(location_name, api_key):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location_name}&key={api_key}"
    response = requests.get(url, verify=False)  # Ignorer la vérification SSL
    data = response.json()
    if 'results' in data and data['results']:  # Vérifier que la liste n'est pas vide
        location_data = data['results'][0]
        if 'geometry' in location_data and 'location' in location_data['geometry']:
            return location_data['geometry']['location']['lat'], location_data['geometry']['location']['lng']
    return None, None  # Si la ville n'est pas trouvée, renvoyer None

app = Bottle()

@app.route('/sudoku')
def sudoku():
    return template('/Users/kevin/Desktop/application web/templates/sudoku.html')


@app.route('/start')
def index():
    return template('/Users/kevin/Desktop/application web/templates/index.html')

@app.route('/snake')
def snake():
    return template('/Users/kevin/Desktop/application web/templates/snake.html')

PASSWORD = 'uc9z37h8mn'

@app.route('/heart')
def heart():
    return template('/Users/kevin/Desktop/application web/templates/heart.html')

@app.route('/')
def home():
    if request.get_cookie("logged_in", secret='votre_clé_secrète'):
        return template('/Users/kevin/Desktop/application web/templates/password.html')
    else:
        redirect('/login')

@app.route('/login', method=['GET', 'POST'])
def login():
    error = False
    if request.method == 'POST':
        if request.forms.get('password') == PASSWORD:
            response.set_cookie("logged_in", True, secret='votre_clé_secrète')
            redirect('/heart')
        else:
            error = True
    return template('/Users/kevin/Desktop/application web/templates/password.html', error=error)


@app.route('/home', method='POST')
def welcome():
    name = request.forms.get('name')
    city = request.forms.get('city')

    latitude, longitude = get_location_coordinates(city, api_key)
    if latitude is None or longitude is None:
        return template('<p>La ville {{ville}} n\'a pas été trouvée. Veuillez réessayer.</p>', ville=city)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["temperature_2m", "rain", "windspeed_10m"]
    }
    response = requests.get(url, params=params).json()

    if 'hourly' not in response:
        return template('<p>Les données météo pour {{ville}} n\'ont pas pu être récupérées. Veuillez réessayer plus tard.</p>', ville=city)

    hourly = response['hourly']
    hourly_temperature_2m = hourly['temperature_2m']
    hourly_rain = hourly['rain']
    hourly_wind_speed_10m = hourly['windspeed_10m']

    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly['time'][0], utc=True),
            end=pd.to_datetime(hourly['time'][-1], utc=True),
            freq='H'
        )
    }
    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["rain"] = hourly_rain
    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m

    variable1 = round(hourly_data["temperature_2m"][-1], 0)
    variable2 = hourly_data["rain"][-1]
    variable3 = round(hourly_data["wind_speed_10m"][-1], 1)

    base_url = "http://transport.opendata.ch/v1/stationboard"
    params = {
        "station": city,
        "limit": 1,
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if "stationboard" in data and len(data["stationboard"]) > 0:
            for departure in data["stationboard"]:
                category = departure["category"]
                number = departure["number"]
                destination = departure["to"]
                departure_time = departure["stop"]["departure"]
                formatted_time = datetime.datetime.strptime(departure_time, "%Y-%m-%dT%H:%M:%S%z").strftime("%H:%M")
                train = f"{category} {number} pour {destination} - Départ à {formatted_time}"
        else:
            train = f"Aucun départ trouvé pour {city}."
    else:
        train = f"Impossible de récupérer les données de départ pour {city}."

    return template('/Users/kevin/Desktop/application web/templates/acceuil.html', 
                    var1=round(variable1-5,1), 
                    var2=variable2, 
                    var3=variable3, 
                    nom=name, 
                    ville=city, 
                    train=train,
                    latitude=latitude,
                    longitude=longitude,
    )

@app.route('/next_train')
def next_train():
    city = request.query.city
    base_url = "http://transport.opendata.ch/v1/stationboard"
    params = {
        "station": city,
        "limit": 1,
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if "stationboard" in data and len(data["stationboard"]) > 0:
            for departure in data["stationboard"]:
                category = departure["category"]
                number = departure["number"]
                destination = departure["to"]
                departure_time = departure["stop"]["departure"]
                formatted_time = datetime.datetime.strptime(departure_time, "%Y-%m-%dT%H:%M:%S%z").strftime("%H:%M")
                train = f"{category} {number} pour {destination} - Départ à {formatted_time}"
        else:
            train = f"Aucun départ trouvé pour {city}."
    else:
        train = f"Impossible de récupérer les données de départ pour {city}."

    response.content_type = 'application/json'
    return json.dumps({"train": train})


@app.route('/gpt_response', method='POST')
def gpt_response():
    data = request.json
    question = data.get('text')

    # Configurez votre clé API OpenAI
    openai.api_key = openai_api_key

    # Appel à l'API OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0125",  # Modèle de chat spécifique
        messages=[{"role": "system", "content": "Vous : " + question}],
        temperature=0.7,
        max_tokens=1500
    )

    bot_response = response['choices'][0]['message']['content']

    response.content_type = 'application/json'
    return json.dumps({"response": bot_response})

if __name__ == '__main__':
    print("\n""\n""\n""\n""\n""\n")
    print("\n""\n""\n""\n""\n""\n")
    print("\n""\n""\n""\n""\n""\n")
    print('application is polling ...')
    print("\n")
    run(app, host='localhost', port=8080, debug=True)