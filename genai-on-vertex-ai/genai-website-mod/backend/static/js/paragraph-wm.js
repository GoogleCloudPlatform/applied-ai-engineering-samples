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
 * Description placeholder
 *
 * @class ParagraphWM
 * @typedef {ParagraphWM}
 * @extends {editorjsParagraphLinebreakable}
 */
class ParagraphWM extends editorjsParagraphLinebreakable {
  /**
   * Creates an instance of ParagraphWM.
   *
   * @constructor
   * @param {*} props
   */
  constructor(props) {
    super(props);
    if (props.data.aiSuggest === true) {
      this._element.classList.add('ai-suggest');
    }
  }
}
