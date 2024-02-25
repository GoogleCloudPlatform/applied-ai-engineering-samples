/*
 * Copyright 2024 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/* eslint-disable no-undef */

const magnifier = document.getElementsByClassName('search-controls-magnifier');

if (magnifier) {
  const searchButton = magnifier[0].children[0];
  if (searchButton) {
    searchButton.addEventListener('click', (e) => {
      console.log(`search button event`);
      gtag('event', 'search', {
        event_category: 'Search',
        event_label: document.getElementById('search-bar-query').value,
      });
    });
  } else {
    console.log('no searchButton');
  }
} else {
  console.log('no magnifier');
}
