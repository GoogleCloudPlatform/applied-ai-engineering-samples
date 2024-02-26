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

const magiContent = document.getElementById('magi-content');
if (magiContent) {
  const resultContentLinks = magiContent.querySelectorAll('.result-content a');
  if (resultContentLinks && resultContentLinks.length > 0) {
    resultContentLinks.forEach((link) => {
      link.addEventListener('click', (e) => {
        console.log(`search result click event`);
        gtag('event', 'search_result_click', {
          event_category: 'Search Result Click',
          event_label: link.getAttribute('href'),
          result_link: link.getAttribute('href'),
          search_query: document.getElementById('search-bar-query').value,
        });
      });
    });
  }
} else {
  console.log(`no magi_content`);
}
