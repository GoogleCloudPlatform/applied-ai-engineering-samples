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

import { setQuickEditPanelContent } from './utils.js';

/**
 * Home page ui logic
 *
 * @type {*}
 */

// TODO: need to hook into dom ready event
const elements = document.querySelectorAll('.editable-section');
console.log(elements);
elements.forEach((element) => {
  element.addEventListener('click', async (e) => {
    element.style.border = '1px solid green';
    // only get the first element ideally should be
    // all children except the button element
    console.log(element.children[0].innerHTML);
    setQuickEditPanelContent(element.children[0].innerHTML);
  });
});

/**
 * Bound green box for given element
 *
 * @param {*} msg
 * @param {*} element
 */
function testBindEvent(msg, element) {
  element.style.border = '1px solid green';
  const select = element.cloneNode(true);
  // only get the first element ideally should be
  // all children except the button element
  console.log(select);
  select.removeChild(select.lastChild);
  setQuickEditPanelContent(select.innerHTML);
}

window.testBindEvent = testBindEvent;
