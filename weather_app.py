import streamlit as st
import requests
from streamlit_folium import st_folium
import folium
from datetime import datetime

# 🌐 Validate City via Nominatim
def validate_city_osm(city):
    url = f"https://nominatim.openstreetmap.org/search?city={city}&format=json"
    try:
        response = requests.get(url, headers={"User-Agent": "streamlit-city-app"})
        return len(response.json()) > 0
    except Exception as e:
        st.sidebar.error(f"❌ Error validating city: {e}")
        return False

# 📍 Get Coordinates and Country Info
def get_city_details(city):
    url = f"https://nominatim.openstreetmap.org/search?city={city}&format=json&addressdetails=1"
    try:
        response = requests.get(url, headers={"User-Agent": "streamlit-city-app"}).json()
        if response:
            lat = float(response[0]["lat"])
            lon = float(response[0]["lon"])
            country = response[0]["address"].get("country", "Unknown")
            country_code = response[0]["address"].get("country_code", "").upper()
            return lat, lon, country, country_code
    except Exception as e:
        st.sidebar.error(f"❌ Error getting city details: {e}")
    return None, None, None, None

# 🗺️ Display Map
def show_city_on_map(lat, lon, city_name):
    try:
        m = folium.Map(location=[lat, lon], zoom_start=10)
        folium.Marker([lat, lon], tooltip=city_name).add_to(m)
        st_folium(m, width=700, height=500)
    except Exception as e:
        st.sidebar.error(f"❌ Error displaying map: {e}")

# 🌦️ Get Weather Info
def get_weather(city, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        st.sidebar.write("🔍 Weather API response:", data)  # Debug

        if data.get("cod") != 200:
            return None, None

        weather = {
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind": data["wind"]["speed"],
            "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).strftime('%H:%M:%S'),
            "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).strftime('%H:%M:%S')
        }

        # Local time from timezone offset
        if "dt" in data and "timezone" in data:
            utc_time = data["dt"]
            offset = data["timezone"]
            local_time = datetime.utcfromtimestamp(utc_time + offset).strftime('%Y-%m-%d %H:%M:%S')
        else:
            local_time = "Time data unavailable"

        return weather, local_time

    except Exception as e:
        st.sidebar.error(f"❌ Error getting weather: {e}")
        return None, None

# 🌇 Streamlit UI
st.set_page_config(page_title="City Validator", layout="wide")
st.title("City Validator 🌍")

city_name = st.text_input("Enter a city name")
API_KEY = "d76a7efa2549e110c6d3f88e0cc1fa02"  # Replace with your key

if city_name:
    if validate_city_osm(city_name):
        st.success(f"✅ '{city_name}' is a valid city!")
        lat, lon, country, country_code = get_city_details(city_name)
        if lat and lon:
            show_city_on_map(lat, lon, city_name)
            st.info(f"📍 Latitude: {lat}, Longitude: {lon}")
            st.info(f"🌐 Country: {country}")
            if country_code:
                flag_url = f"https://flagsapi.com/{country_code}/flat/64.png"
                st.image(flag_url, caption=f"{country} Flag", width=64)

            weather, local_time = get_weather(city_name, API_KEY)
            if weather:
                st.info(f"🕒 Local Time: {local_time}")
                st.subheader("🌤️ Current Weather")
                st.write(f"**Temperature:** {weather['temperature']}°C (Feels like {weather['feels_like']}°C)")
                st.write(f"**Condition:** {weather['description'].title()}")
                st.write(f"**Humidity:** {weather['humidity']}%")
                st.write(f"**Wind Speed:** {weather['wind']} m/s")
                st.write(f"**Sunrise:** {weather['sunrise']}")
                st.write(f"**Sunset:** {weather['sunset']}")
            else:
                st.warning("⚠️ Weather data not available.")
        else:
            st.warning("⚠️ Coordinates not found. Please try another city.")
    else:
        st.error("❌ That doesn’t seem to be a recognized city.")