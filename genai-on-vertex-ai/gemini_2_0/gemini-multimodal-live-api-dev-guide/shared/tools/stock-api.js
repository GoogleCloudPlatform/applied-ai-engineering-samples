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

const FINNHUB_API_KEY = '<YOUR_FINNHUB_API_KEY>';

export async function getStockPrice(symbol) {
  try {
    const url = `https://finnhub.io/api/v1/quote?symbol=${encodeURIComponent(symbol)}&token=${FINNHUB_API_KEY}`;
    console.log('Fetching stock data from:', url);
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Finnhub API failed with status: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Check if we got valid data
    if (data.c === 0 && data.h === 0 && data.l === 0) {
      return {
        error: `Could not find stock data for symbol: ${symbol}`
      };
    }

    return {
      currentPrice: data.c,
      change: data.d,
      percentChange: data.dp,
      highPrice: data.h,
      lowPrice: data.l,
      openPrice: data.o,
      previousClose: data.pc,
      symbol: symbol.toUpperCase()
    };
  } catch (error) {
    console.error('Detailed error:', {
      message: error.message,
      stack: error.stack,
      type: error.name
    });
    return {
      error: `Error fetching stock price for ${symbol}: ${error.message}`
    };
  }
} 