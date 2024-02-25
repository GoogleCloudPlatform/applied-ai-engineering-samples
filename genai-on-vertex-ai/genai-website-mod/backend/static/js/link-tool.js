/* eslint-disable no-undef */
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

/**
 * HyperlinkTool
 *
 * @class HyperlinkTool
 * @typedef {HyperlinkTool}
 */
class HyperlinkTool {
  /**
   * Marker that this is and inline tool
   * for EditorJs to parse
   *
   * @static
   * @readonly
   * @type {boolean}
   */
  static get isInlineTool() {
    return true;
  }

  /**
   * toolbox getter
   *
   * @static
   * @readonly
   */
  static get toolbox() {
    return {
      icon: '<svg xmlns="http://www.w3.org/2000/svg"viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-link"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-3 3a5 5 0 0 0 0 7.54zM14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l3-3a5 5 0 0 0 0-7.54z"/></svg>',
      title: 'Link',
    };
  }

  /**
   * Render method contract (EditorJS)
   *
   * @return {*}
   */
  render() {
    const button = document.createElement('button');
    button.classList.add('inline-tool-link');
    return button;
  }

  /**
   * Surround method contract (EditorJS)
   *
   * @param {*} range
   */
  surround(range) {
    if (!range) return;

    const urlInput = document.createElement('input');
    urlInput.placeholder = 'Enter URL';

    const selectedText = window.getSelection().toString();
    urlInput.value = selectedText;

    // Wrap selected text with <a> tag with the URL
    const aTag = document.createElement('a');
    aTag.href = `https://${urlInput.value}`;
    aTag.textContent = selectedText;
    range.surroundContents(aTag);

    // Focus on the URL input field
    urlInput.focus();

    // Remove the input field after losing focus
    urlInput.addEventListener('blur', () => {
      urlInput.parentElement.removeChild(urlInput);
    });
  }
}
