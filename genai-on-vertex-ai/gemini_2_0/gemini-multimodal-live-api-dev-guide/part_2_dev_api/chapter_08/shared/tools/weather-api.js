/**
 * Copyright 2024 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

const OPENWEATHER_API_KEY = '<YOUR_OPENWEATHER_API_KEY>';

export async function getWeather(city) {
  try {
    // First get coordinates for the city
    const geoUrl = `https://api.openweathermap.org/geo/1.0/direct?q=${encodeURIComponent(city)}&limit=1&appid=${OPENWEATHER_API_KEY}`;
    console.log('Fetching geo data from:', geoUrl);
    const geoResponse = await fetch(geoUrl);
    if (!geoResponse.ok) {
      throw new Error(`Geo API failed with status: ${geoResponse.status}`);
    }
    const geoData = await geoResponse.json();

    if (!geoData.length) {
      return {
        error: `Could not find location: ${city}`
      };
    }

    const { lat, lon } = geoData[0];

    // Then get weather data
    const weatherUrl = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&units=metric&appid=${OPENWEATHER_API_KEY}`;
    console.log('Fetching weather data from:', weatherUrl);
    const weatherResponse = await fetch(weatherUrl);
    if (!weatherResponse.ok) {
      throw new Error(`Weather API failed with status: ${weatherResponse.status}`);
    }
    const weatherData = await weatherResponse.json();

    return {
      temperature: weatherData.main.temp,
      description: weatherData.weather[0].description,
      humidity: weatherData.main.humidity,
      windSpeed: weatherData.wind.speed,
      city: weatherData.name,
      country: weatherData.sys.country
    };
  } catch (error) {
    console.error('Detailed error:', {
      message: error.message,
      stack: error.stack,
      type: error.name
    });
    return {
      error: `Error fetching weather for ${city}: ${error.message}`
    };
  }
} 