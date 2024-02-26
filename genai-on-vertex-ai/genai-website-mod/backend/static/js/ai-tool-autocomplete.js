/* eslint-disable no-invalid-this */
/*
 * Copyright 2023 Google LLC
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
 * Debounce a given function by 2s
 * @param {func} func
 * @param {number} timeout
 * @return {any}
 */
function debounce(func, timeout = 2000) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      func.apply(this, args);
    }, timeout);
  };
}

class AIText extends Paragraph {
  predictionServiceClient;
  project;
  location;
  publisher;
  model;

  static get toolbox() {
    return {
      title: 'Vertex AI Autocomplete',
      icon: '<img src="/static/img/icons/vertexai.svg" width="18" height="18"/>',
    };
  }

  constructor({ api, block, config, data }) {
    super({
      api,
      block,
      config,
      data,
    });
  }

  async getAICompletion(content) {
    if (!content) return;

    try {
      const response = await fetch('/vertex-llm/ai-autocomplete', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ paragraph_content: content }), // Send content to the backend
      });

      if (!response.ok) {
        throw new Error(
            `Backend API request failed with status ${response.status}`,
        );
      }

      console.log(response);
      const result = await response.json();
      console.log(result);

      const aiSuggestions = document.createElement('span');
      aiSuggestions.innerHTML = '';
      aiSuggestions.id = 'ai-suggestions';
      aiSuggestions.style.color = 'lightgray';
      aiSuggestions.innerHTML = result.response; // Update based on your backend response structure

      this._element.appendChild(aiSuggestions);
    } catch (error) {
      console.error('Error in backend API request:', error);
    }
  }

  onInput = debounce((e) => {
    if (
      this._element.querySelector('#ai-suggestions') ||
      e.inputType === 'deleteContentBackward' ||
      e.inputType === 'deleteContentForward' ||
      e.inputType === 'insertParagraph' ||
      e.inputType === 'insertFromPaste' ||
      e.inputType === 'insertFromDrop' ||
      !e.target.innerHTML
    ) {
      return;
    }

    this.getAICompletion(e.target.innerHTML);
  });

  onKeyUp(e) {
    if (e.code === 'Escape' || e.code === 'Backspace') {
      this._element.querySelector('#ai-suggestions')?.remove();
      return;
    }

    if (e.code === 'AltLeft' || e.code === 'AltRight') {
      const aiSuggestionElement =
        this._element.querySelector('#ai-suggestions');
      const aiSuggestionElementTextContent = aiSuggestionElement?.textContent;

      if (!aiSuggestionElementTextContent) return;

      const aiSuggestionTextNode = document.createTextNode(
          aiSuggestionElementTextContent,
      );

      this._element.appendChild(aiSuggestionTextNode);
      aiSuggestionElement.remove();
      return;
    }

    if (e.code !== 'Backspace' && e.code !== 'Delete') {
      return;
    }

    const { textContent } = this._element;

    if (textContent === '') {
      this._element.innerHTML = '';
    }
  }

  drawView() {
    const div = document.createElement('DIV');

    div.classList.add(this._CSS.wrapper, this._CSS.block);
    div.contentEditable = false;
    div.dataset.placeholder = this.api.i18n.t(this._placeholder);

    if (this._data.text) {
      div.innerHTML = this._data.text;
    }

    if (!this.readOnly) {
      div.contentEditable = true;
      div.addEventListener('keyup', this.onKeyUp);
      div.addEventListener('input', this.onInput);
    }

    return div;
  }
}
