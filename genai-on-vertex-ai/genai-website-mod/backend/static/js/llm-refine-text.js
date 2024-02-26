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
 * Description placeholder
 *
 * @class RefineTextTool
 * @typedef {RefineTextTool}
 */
class RefineTextTool {
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
   * Creates an instance of RefineTextTool.
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
   * render method contract (EditorJs)
   *
   * @return {*}
   */
  render() {
    this.button = document.createElement('button');
    this.button.type = 'button';
    this.button.classList.add('ce-inline-tool');
    this.button.innerHTML = `<span class="google-symbols"> pen_spark </span>`;

    return this.button;
  }

  /**
   * Description placeholder
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
    theInput.placeholder = 'Describe the style you want to refine in';
    this.promptField.appendChild(theInput);
    this.promptField.appendChild(theButton);
    return this.promptField;
  }

  /**
   * Description placeholder
   * @date 1/23/2024 - 5:03:39 PM
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
        message: 'Please select some text to refine',
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
  async refineText(text, prompt) {
    // Replace this with your actual LLM backend request and response parsing
    const response = await fetch('/vertex-llm/ai_refine_text', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ selected_text: text, instruction: prompt }),
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
    selectedRange.deleteContents();
    selectedRange.insertNode(document.createTextNode('Loading ⏳ ...'));
    const refinedText = this.refineText(selectedText, prompt)
        .then((result) => {
          const divSuggestion = document.createElement('div');
          const textOriginal = document.createTextNode(selectedText);
          const btnSuggestion = document.createElement('button');
          btnSuggestion.id = 'temp-suggestion-replace-btn';
          btnSuggestion.addEventListener('click', (e) =>
            this.handleReplace(e, textOriginal),
          );
          btnSuggestion.textContent = 'Replace';
          divSuggestion.appendChild(document.createTextNode(result));
          divSuggestion.appendChild(btnSuggestion);
          divSuggestion.style.border = '1px solid grey';
          selectedRange.deleteContents();
          selectedRange.insertNode(divSuggestion);
          selectedRange.insertNode(textOriginal);
        })
        .catch((err) => console.log('ERROR on submitting prompt', err));
  }

  /**
   * Description placeholder
   *
   * @param {*} e
   * @param {*} originalTextElement
   */
  handleReplace(e, originalTextElement) {
    console.log(e.currentTarget);
    e.currentTarget.parentNode.parentNode.removeChild(originalTextElement);
    e.currentTarget.parentNode.removeChild(e.currentTarget);
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
