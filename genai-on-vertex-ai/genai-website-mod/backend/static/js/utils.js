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
 * Global reference to Quick Edit Panel
 *
 * @type {*}
 */
const quickEditPanel = document.getElementById('offcanvasExample');
/**
 * Global reference to Quick Edit Panel Content
 *
 * @type {*}
 */
const quickEditPanelContent = document.getElementById(
    'quick-edit-panel-content',
);

/**
 * Display Loading Circle for Any Element
 *
 * @export
 * @param {*} elementId
 */
export function drawLoading(elementId) {
  const element = document.getElementById(elementId);
  const loading = `<div class="d-flex justify-content-center">
                  <div class="spinner-border text-primary m-5" role="status">
                    <span class="visually-hidden">Loading...</span>
                  </div>
                </div>`;
  element.innerHTML = loading;
}

/**
 * Set title for Sidebar Popup
 *
 * @export
 * @param {*} elementId
 * @param {*} label
 */
export function drawSidePanelLabel(elementId, label) {
  const element = document.getElementById(elementId);
  element.innerHTML = label;
}

/**
 * Set content for Sidebar Popup
 *
 * @export
 * @param {*} content
 */
export function setQuickEditPanelContent(content) {
  quickEditPanelContent.innerHTML = content;
}

/**
 * Attach custom event offcanvas to change styles
 * of component that being edited (persist 1px border transparent)
 * to avoid jiggery effect when hovering the editable component
 */
quickEditPanel.addEventListener('hidden.bs.offcanvas', function() {
  const components = document.querySelectorAll('.hidden-border');
  components.forEach((element) => {
    element.style.border = '1px solid transparent';
  });
});

/**
 * Description placeholder
 *
 * @export
 * @async
 * @param {*} path
 * @param {*} method
 * @param {*} jsonPayload
 * @return {unknown}
 */
export async function invokeAPI(path, method, jsonPayload) {
  const conversationId = getCurrentConversationId();
  const auth = await getFirebaseAuth();
  const token = await auth.currentUser.getIdToken();
  const response = await fetch(path, {
    method: method,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      'x-csm-conversation-id': conversationId,
    },
    body: JSON.stringify(jsonPayload),
  });
  return response;
}
