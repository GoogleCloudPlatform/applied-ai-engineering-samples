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

export class StatusHandler {
  constructor() {
    this.functionInfo = null;
    this.initialize();
  }

  initialize() {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => {
        this.functionInfo = document.getElementById('functionInfo');
      });
    } else {
      this.functionInfo = document.getElementById('functionInfo');
    }
  }

  update(functionName, params = {}) {
    // Get the element again if we don't have it yet
    if (!this.functionInfo) {
      this.functionInfo = document.getElementById('functionInfo');
    }
    
    if (this.functionInfo) {
      const timestamp = new Date().toLocaleTimeString();
      let content = `[${timestamp}] Function: ${functionName}\n`;

      if (functionName === 'get_weather') {
        if (params.status === 'requesting') {
          content += `Requesting weather for: ${params.city}...`;
        } else if (params.status === 'received' && params.weather) {
          const weather = params.weather;
          if (weather.error) {
            content += `Error: ${weather.error}`;
          } else {
            content += `Weather in ${weather.city}, ${weather.country}:\n`;
            content += `Temperature: ${weather.temperature}°C\n`;
            content += `Conditions: ${weather.description}\n`;
            content += `Humidity: ${weather.humidity}%\n`;
            content += `Wind Speed: ${weather.windSpeed} m/s`;
          }
        }
      } else if (functionName === 'get_stock_price') {
        if (params.status === 'requesting') {
          content += `Requesting stock price for: ${params.symbol}...`;
        } else if (params.status === 'received' && params.stock) {
          const stock = params.stock;
          if (stock.error) {
            content += `Error: ${stock.error}`;
          } else {
            content += `Stock Information for ${stock.symbol}:\n`;
            content += `Current Price: $${stock.currentPrice}\n`;
            content += `Change: ${stock.change > 0 ? '+' : ''}${stock.change} (${stock.percentChange}%)\n`;
            content += `Day Range: $${stock.lowPrice} - $${stock.highPrice}\n`;
            content += `Open: $${stock.openPrice}\n`;
            content += `Previous Close: $${stock.previousClose}`;
          }
        }
      }

      this.functionInfo.textContent = content;
    }
  }
}

// Create and export a singleton instance
export const statusHandler = new StatusHandler(); 