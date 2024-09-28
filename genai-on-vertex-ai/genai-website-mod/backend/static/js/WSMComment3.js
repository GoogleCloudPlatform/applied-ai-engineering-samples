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
 * @class CollaborationComments3
 * @typedef {CollaborationComments3}
 * @extends {Annotation}
 */
class CollaborationComments3 extends Annotation {
  /**
   * Creates an instance of CollaborationComments3.
   *
   * @constructor
   * @param {*} config
   */
  constructor(config) {
    super(config);
    this._config = config.config;
    if (this.actionButton) {
      this.actionButton.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" height="20" viewBox="0 -960 960 960" width="20"><path d="M480-144v-85l212-212 85 85-212 212h-85ZM144-348v-72h288v72H144Zm661-36-85-85 32-32q11-11 25.5-11t25.5 11l34 34q11 11 11 25.5T837-416l-32 32ZM144-498v-72h432v72H144Zm0-150v-72h432v72H144Z"></path></svg><svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" height="20" viewBox="0 -960 960 960" width="20"><path d="M480-144v-85l212-212 85 85-212 212h-85ZM144-348v-72h288v72H144Zm661-36-85-85 32-32q11-11 25.5-11t25.5 11l34 34q11 11 11 25.5T837-416l-32 32ZM144-498v-72h432v72H144Zm0-150v-72h432v72H144Z"></path></svg>Add comment`;
    }
  }

  /**
   * Description placeholder
   *
   * @param {*} title
   * @param {*} text
   */
  saveData(title, text) {
    title = title.trim();
    text = text.trim();

    if (title.length === 0 && text.length === 0) {
      return;
    }

    if (Annotation.currentRange) {
      this.wrap(Annotation.currentRange, title, text);
    } else if (Annotation.currentElem) {
      this.writeCommentToHTML(
          Annotation.currentElem,
          text,
          title,
          this.getCommentorId(),
      );
    }

    Annotation.currentRange = null;
    Annotation.currentElem = null;
  }

  /**
   * Description placeholder
   * @date 1/23/2024 - 5:12:13 PM
   *
   * @param {*} termWrapper
   */
  unwrap(termWrapper) {
    this.api.selection.expandToTag(termWrapper);

    const sel = window.getSelection();
    const range = sel.getRangeAt(0);

    const unwrappedContent = range.extractContents();
    termWrapper.parentNode.removeChild(termWrapper);
    range.insertNode(unwrappedContent);
    sel.removeAllRanges();
    sel.addRange(range);
  }

  /**
   * Description placeholder
   * @date 1/23/2024 - 5:12:13 PM
   *
   * @param {*} annotation
   * @param {*} attributeName
   * @return {*}
   */
  loadComments(annotation, attributeName) {
    const existingTitle = annotation.getAttribute(attributeName);
    console.log(`load existing comments=${existingTitle} | ${attributeName}`);
    console.log(existingTitle);
    let existing = null;
    if (existingTitle) {
      console.log(`existing_title...`);
      existing = JSON.parse(atob(existingTitle));
    } else {
      console.log(`no existing_title`);
      existing = [];
    }
    return existing;
  }

  /**
   * Description placeholder
   *
   * @param {*} comment
   * @param {*} title
   * @param {*} commentor
   * @return {*}
   */
  createComment(comment, title, commentor) {
    const commentBlock = {
      title: title,
      text: comment,
      time: Date.now(),
      commentor: commentor,
    };
    return commentBlock;
  }

  /**
   * Description placeholder
   *
   * @param {*} annotation
   * @param {*} comment
   * @param {*} title
   * @param {*} commentor
   */
  writeCommentToHTML(annotation, comment, title, commentor) {
    const existing = this.loadComments(annotation, 'data-text');
    const titleBlock = this.createComment(comment, title, commentor);
    existing.push(titleBlock);
    const base64data = btoa(JSON.stringify(existing));
    annotation.setAttribute('data-text', base64data);
    annotation.setAttribute('data-title', title);
  }
  /**
   * Description placeholder
   *
   * @return {*}
   */
  getCommentorId() {
    const userName = this._config.get_user_name();
    return userName;
  }
  /**
   * Description placeholder
   *
   * @param {*} range
   * @param {*} title
   * @param {*} text
   */
  wrap(range, title, text) {
    /**
     * Create a wrapper for highlighting
     */
    const annotation = document.createElement(this.tag);
    const userId = this.getCommentorId();

    annotation.classList.add(Annotation.CSS.baseClass);
    console.log(`wrap...${text} | ${title}`);
    this.writeCommentToHTML(annotation, text, title, this.getCommentorId());

    /**
     * SurroundContent throws an error if the Range splits
     * a non-Text node with only one of its boundary points
     * @see {@link https://developer.mozilla.org/en-US/docs/Web/API/Range/surroundContents}
     *
     * // range.surroundContents(span);
     */
    annotation.appendChild(range.extractContents());
    range.insertNode(annotation);

    /**
     * Expand (add) selection to highlighted block
     */
    this.api.selection.expandToTag(annotation);
  }

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
    // Update Text
    popup.querySelector('.cdx-annotation_popup-inp-title').placeholder =
        'Comment Title';
    popup.querySelector('.cdx-annotation_popup-title').innerText =
        'Add Comment';
    popup.querySelector('.cdx-annotation_popup-inp-text').placeholder =
        'Comment...';
    popup.querySelector('.cdx-annotation_popup-btn-save')
        .addEventListener('click', (e) => {
          console.log(`*** Saving Review Comments...`);
          console.log(this._config);
          if (this._config.is_review_page) {
            this._config.save_function();
          }
        });
    if (popup.querySelector('.cdx-annotation_popup-btn-suggestion')) {
      popup.querySelector('.cdx-annotation_popup-history').innerHTML = '';
      if (popup.querySelector(
              '#cdx-annotation_popup-inp-text-suggestion-area')) {
        popup
            .querySelector(
                '#cdx-annotation_popup-inp-text-suggestion-area',
                )
            .innerHTML = '';
      }
      popup.querySelector('.cdx-annotation_popup-inp-text').innreText = '';
      console.log(`===>>>`);
      console.log(popup.querySelector('.cdx-annotation_popup-inp-text'));
      return popup;
    } else {
      const history = document.createElement('div');
      history.classList.add('cdx-annotation_popup-inp-title');
      history.classList.add('cdx-annotation_popup-history');
      const historyContainer = popup.querySelector(
          '.cdx-annotation_popup-content',
      );
      historyContainer.appendChild(history);

      document.querySelector('.cdx-annotation_popup-form')
          .appendChild(historyContainer);
      const container = popup.querySelector('.cdx-annotation_popup-footer');
      const suggestion = document.createElement('button');
      suggestion.classList.add('cdx-button');
      suggestion.classList.add('cdx-annotation_popup-btn-remove');
      suggestion.classList.add('cdx-annotation_popup-btn-suggestion');
      suggestion.textContent = 'Suggestion';
      suggestion.addEventListener('click', async (e) => {
        e.preventDefault();
        const title = popup.querySelector('.cdx-annotation_popup-inp-title');
        const comment = popup
                            .querySelector(
                                '.cdx-annotation_popup-history',
                                )
                            .textContent;
        const response = await fetch('/vertex-llm/ai_refine_text', {
          method: 'POST',
          body: JSON.stringify({
            selected_text: title.value,
            instruction: comment,
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
                '.cdx-annotation_popup-footer-for-suggestions'),
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

  /**
   * Description placeholder
   */
  checkState() {
    const termTag = this.api.selection.findParentTag(
        this.tag,
        Annotation.CSS.baseClass,
    );

    this.button.classList.toggle(this.iconClasses.active, !!termTag);
    this.actionButton.classList.toggle(
        Annotation.CSS.actionShowButton,
        !!termTag,
    );
    if (termTag) {
      this.actionButton.onclick = () => {
        Annotation.currentRange = null;
        Annotation.currentElem = termTag;
        const base64String = termTag.getAttribute('data-text');
        console.log(`base64String=${base64String}`);
        const decodedText = atob(base64String);
        this.openPopup(termTag.getAttribute('data-title'), decodedText);
      };
    }
  }
  /**
   * Description placeholder
   *
   * @param {*} title
   * @param {*} text
   */
  openPopup(title, text) {
    const popup = this.getPopup();
    const inputTitle = popup.querySelector(
        `.${Annotation.CSS.popupInputTitle}`,
    );
    let comments = null;
    if (text) {
      comments = JSON.parse(text);  // TODO:
    }
    if (inputTitle) {
      if (title) {
        inputTitle.value = title;
      } else {
        inputTitle.value = null;
      }
    }

    const inputText = popup.querySelector(`.${Annotation.CSS.popupInputText}`);
    inputText.value = '';
    const inputHistory = popup.querySelector('.cdx-annotation_popup-history');
    let tags = '';
    if (inputHistory && text) {
      const history = JSON.parse(text);
      history.forEach((c) => {
        tags += `<li><div class="card-text">${c.commentor}</div>
                            <small>${new Date(c.time).toTimeString()}</small>
                            <div class="card-text">${c.text}</div>
                </li>`;
      });
      inputHistory.innerHTML = `<ul>${tags}</ul>`;
    }

    const removeButton = popup.querySelector(
        `.${Annotation.CSS.popupRemoveButton}`,
    );
    if (removeButton) {
      if (Annotation.currentElem) {
        removeButton.style.display = null;
      } else {
        removeButton.style.display = 'none';
      }
    }

    popup.classList.remove(Annotation.CSS.popupHidden);
  }
}
