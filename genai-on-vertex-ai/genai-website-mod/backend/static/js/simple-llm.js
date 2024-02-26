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

/**
 * Translate tool
 *
 * @class TranslateTool
 * @typedef {TranslateTool}
 */
class TranslateTool {
  /**
   * Description placeholder
   *
   * @static
   * @readonly
   * @type {boolean}
   */
  static get isInline() {
    return true;
  }

  /**
   * Creates an instance of TranslateTool.
   *
   * @constructor
   * @param {*} param0
   * @param {*} param0.config
   * @param {*} param0.api
   */
  constructor({ config, api }) {
    this.ENTER_KEY = 13;
    this.api = api;
    this.tag = 'PROMPT';
    this.config = config;
    this.button = null;
    this.modal = null;
    this.promptField = null;
    this.isOpen = false;
    this.state = false; // tracks if refinement applied to selected text
    this.nodes = {
      button: null,
      sendButton: null,
      input: null,
    };
    this.selectedText = null;
    this.selectedRange = null;
  }

  /**
   * Description placeholder
   *
   * @return {*}
   */
  render() {
    this.button = document.createElement('button');
    this.button.type = 'button';
    this.button.classList.add('ce-inline-tool');
    this.button.innerHTML = `<span class="google-symbols">
      translate
      </span>`;
    return this.button;
  }

  /**
   * Description placeholder
   * @date 1/23/2024 - 5:08:04 PM
   *
   * @return {*}
   */
  renderActions() {
    this.promptField = document.createElement(this.tag);
    const theInput = document.createElement('input');
    theInput.style.width = '89%';
    const theButton = document.createElement('button');
    theButton.innerHTML = `<span class="google-symbols">
                              send_spark
                              </span>`;
    theButton.classList.add('ce-inline-tool');
    theInput.type = 'text';
    theInput.placeholder = 'What language do you want to translate to?';
    this.promptField.appendChild(theInput);
    this.promptField.appendChild(theButton);
    return this.promptField;
  }

  /**
   * Description placeholder
   * @date 1/23/2024 - 5:08:04 PM
   *
   * @async
   * @param {*} range
   * @return {*}
   */
  async surround(range) {
    if (this.state) {
      // If refinement already applied, do nothing
      return;
    }
    this.state = true;

    const selectedText = range.toString();

    console.log(selectedText);

    if (!selectedText) {
      this.api.notifier.show({
        message: 'Please select some text to translate inline',
        style: 'warning',
      });
      return;
    }

    this.selectedText = selectedText;
    this.selectedRange = range;
    console.log('Surrond activated');
    this.promptField
        .querySelector('button')
        .addEventListener('click', (event) => {
        // if (event.keyCode === this.ENTER_KEY) {
          this.enterPressed(
              event,
              selectedText,
              this.promptField.querySelector('input').value,
              range,
          );
        // }
        });
  }

  // Implement your LLM backend request and response handling
  /**
   * Description placeholder
   *
   * @async
   * @param {*} text
   * @param {*} prompt
   * @return {unknown}
   */
  async inlineTranslateText(text, prompt) {
    // Replace this with your actual LLM backend request and response parsing
    const response = await fetch('/vertex-llm/ai-translate-inline', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ selected_text: text, target_language: prompt }),
    });

    if (!response.ok) {
      this.api.notifier.show({
        message: 'Error refining text',
        style: 'error',
      });
      return '';
    }

    const data = await response.json();
    return data.response || ''; // Replace with actual refined text response
  }

  /**
   * Description placeholder
   */
  checkState() {
    if (this.state == true) {
      this.showActions();
    } else {
      this.hideActions();
    }
  }

  /**
   * Description placeholder
   *
   * @param {*} e
   * @param {*} selectedText
   * @param {*} prompt
   * @param {*} selectedRange
   */
  enterPressed(e, selectedText, prompt, selectedRange) {
    const refinedText = this.inlineTranslateText(selectedText, prompt)
        .then((result) => {
          console.og;
          selectedRange.deleteContents();
          selectedRange.insertNode(document.createTextNode(result));
        })
        .catch((err) => console.log('ERROR on submitting prompt', err));
  }

  /**
   * Description placeholder
   */
  showActions() {
    this.promptField.hidden = false;
  }

  /**
   * Description placeholder
   */
  hideActions() {
    this.promptField.hidden = true;
  }
}
