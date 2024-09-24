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

// import { Annotation } from "./annotation-bundle";

/**
 * Description placeholder
 *
 * @class CollaborationComments2
 * @typedef {CollaborationComments2}
 * @extends {Annotation}
 */
class CollaborationComments2 extends Annotation {
  /**
   * Description placeholder
   *
   * @param {*} text
   * @param {*} termWrapper
   */
  applySuggestion(text, termWrapper) {
    console.log(`[${text}]`);
    this.api.selection.expandToTag(termWrapper);

    const sel = window.getSelection();
    const range = sel.getRangeAt(0);

    const unwrappedContent = range.extractContents();
    console.log(`unwrappedContent=${unwrappedContent}`);
    unwrappedContent.textContent = text;
    console.log(`unwrappedContent.textContent=${unwrappedContent.textContent}`);
    termWrapper.parentNode.removeChild(termWrapper);

    range.insertNode(unwrappedContent);

    sel.removeAllRanges();
    sel.addRange(range);
  }

  /**
   * Description placeholder
   *
   * @return {*}
   */
  getPopup() {
    const popup = super.getPopup();
    if (popup.querySelector('.cdx-annotation_popup-btn-suggestion')) {
      return popup;
    } else {
      const container = popup.querySelector('.cdx-annotation_popup-footer');
      const suggestion = document.createElement('button');
      suggestion.classList.add('cdx-button');
      suggestion.classList.add('cdx-annotation_popup-btn-remove');
      suggestion.classList.add('cdx-annotation_popup-btn-suggestion');
      suggestion.textContent = 'Suggestion';
      suggestion.addEventListener('click', async (e) => {
        e.preventDefault();
        const title = popup.querySelector('.cdx-annotation_popup-inp-title');
        const comment = popup.querySelector('.cdx-annotation_popup-inp-text');
        const response = await fetch('/vertex-llm/ai_refine_text', {
          method: 'POST',
          body: JSON.stringify({
            selected_text: title.value,
            instruction: comment.value,
            model_name: 'gemini-1.5-pro-001',
            max_output_tokens: 8192,
            temperature: 0,
            top_p: 0.8,
            top_k: 40,
          }),
          headers: {
            'Content-Type': 'application/json',
          },
        });
        const data = await response.json();
        const suggestedText = data.response;
        console.log(`===>>>${suggestedText}`);
        console.log(
            document.querySelector(
                `.cdx-annotation_popup-footer-for-suggestions`),
        );
        const existing = document.querySelector(
            '.cdx-annotation_popup-footer-for-suggestions',
        );
        if (existing) {
          existing.parentElement.removeChild(existing);
        }
        const div = document.createElement('div');
        div.classList.add('cdx-annotation_popup-footer');
        div.classList.add('cdx-annotation_popup-footer-for-suggestions');
        const suggestionArea = document.createElement('div');
        suggestionArea.id = 'cdx-annotation_popup-inp-text-suggestion-area';
        suggestionArea.classList.add('cdx-annotation_popup-inp-text');
        const applyButton = document.createElement('button');
        applyButton.classList.add('cdx-button');
        applyButton.classList.add('cdx-annotation_popup-btn-remove');
        applyButton.classList.add('cdx-annotation_popup-btn-apply');
        applyButton.textContent = 'Apply';
        applyButton.addEventListener('click', (e) => {
          document.querySelector('.cdx-annotation_popup-btn-save').click();
          const termWrapper = this.api.selection.findParentTag(
              this.tag,
              'cdx-annotation',
          );
          console.log(`termWrapper=>`);
          console.log(termWrapper);
          this.applySuggestion(suggestedText, termWrapper);
        });
        suggestionArea.textContent = suggestedText;
        div.appendChild(suggestionArea);
        div.appendChild(applyButton);
        document.querySelector('.cdx-annotation_popup-form').appendChild(div);
      });
      container.appendChild(suggestion);
      return popup;
    }
  }
}
