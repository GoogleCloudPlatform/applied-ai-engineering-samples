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
 * @date 1/23/2024 - 4:52:20 PM
 *
 * @type {{ anyTuneName: { class: any; config: { default: string; blocks: {
 *     header: string; list: string; }; }; }; header: { class: any;
 *     inlineToolbar: boolean; config: { placeholder: string; }; shortcut:
 *     string; tunes: {}; }; ... 4 more ...; color: { ...; }; }}
 */
const columnTools = {
  anyTuneName: {
    class: AlignmentBlockTune,
    config: {
      default: 'left',
      blocks: {
        header: 'center',
        list: 'right',
      },
    },
  },
  header: {
    class: HeaderWM,
    inlineToolbar: true,
    config: {
      placeholder: 'Header',
    },
    shortcut: 'CMD+SHIFT+H',
    tunes: ['anyTuneName'],
  },
  alert: Alert,
  paragraph: {
    class: ParagraphWM,
    inlineToolbar: true,
    // tunes: ['anyTuneName'],
  },
  delimiter: Delimiter,
  image: {
    class: WSMImage,
    config: {
      imagen_url: '/imagen/api/refine-image',
      uploader: {
        async uploadByFile(file) {
          // Create a FormData object
          const formData = new FormData();

          // Append the file directly to the FormData
          formData.append('file', file);

          // Send the request to the server
          const response = await fetch('/web-edit/api/upload-image', {
            method: 'POST',
            body: formData,
          });

          // Wait for the response to be parsed as JSON
          const data = await response.json();
          // Return the response data
          return {
            success: 1,
            file: {
              url: data.url,
            },
          };
        },
      },
    },
  },
  color: {
    class: ColorPlugin,  // if load from CDN, please try: window.ColorPlugin
    config: {
      colorCollections: [
        '#EC7878',
        '#9C27B0',
        '#673AB7',
        '#3F51B5',
        '#0070FF',
        '#03A9F4',
        '#00BCD4',
        '#4CAF50',
        '#8BC34A',
        '#CDDC39',
        '#FFF',
      ],
      defaultColor: '#FF1300',
      type: 'text',
      customPicker: true,  // add a button to allow selecting any colour
    },
    AnyButton: {
      class: AnyButton,
      inlineToolbar: false,
      config: {
        css: {
          btnColor: 'btn--gray',
        },
      },
    },
    inlineToolbar: ['marker', 'link', 'bold', 'italic'],
  },
};

/**
 * Main configuration object for EditorJS instance
 */
const main_tools = {
  aiText: {
    class: AIText,
  },
  anyTuneName: {
    class: AlignmentBlockTune,
    config: {
      default: 'left',
      blocks: {
        header: 'center',
        list: 'right',
      },
    },
  },
  // annotation: CollaborationComments3,
  annotation: {
    class: CollaborationComments3,
    config: {
      is_review_page: window.location.pathname.indexOf('review') >= 0,
      get_user_name: () => {
        const button = document.getElementById('impersonate2-as-button');
        if (button) {
          console.log(button.options[button.selectedIndex].value);
          return button.options[button.selectedIndex].value;
        } else {
          return 'User';
        }
      },
      save_function: saveReview,
    },
  },
  // Load Official Tools
  header: {
    class: HeaderWM,
    inlineToolbar: ['marker', 'link', 'bold', 'italic'],
    config: {
      placeholder: 'Header',
    },
    shortcut: 'CMD+SHIFT+H',
    tunes: ['anyTuneName'],
  },
  /**
   * Or pass class directly without any configuration
   */
  image: SimpleImage,
  list: {
    class: List,
    inlineToolbar: true,
    shortcut: 'CMD+SHIFT+L',
  },
  checklist: {
    class: Checklist,
    inlineToolbar: true,
  },
  quote: {
    class: Quote,
    inlineToolbar: true,
    config: {
      quotePlaceholder: 'Enter a quote',
      captionPlaceholder: 'Quote\'s author',
    },
    shortcut: 'CMD+SHIFT+O',
    tunes: ['anyTuneName'],
  },
  warning: Warning,
  marker: {
    class: Marker,
    shortcut: 'CMD+SHIFT+M',
  },
  code: {
    class: CodeTool,
    shortcut: 'CMD+SHIFT+C',
  },
  delimiter: Delimiter,
  inlineCode: {
    class: InlineCode,
    shortcut: 'CMD+SHIFT+C',
  },
  linkTool: {
    class: LinkTool,
    config: {
      // Your backend endpoint for url data fetching
      endpoint: '/hello/fetch-url-data',
    },
    inlineToolbar: true,
  },
  refineTextTool: {
    class: RefineTextTool,
    inlineToolbar: true,
  },

  embed: Embed,
  table: {
    class: Table,
    inlineToolbar: true,
    shortcut: 'CMD+ALT+T',
    tunes: ['anyTuneName'],
  },
  alert: Alert,
  paragraph: {
    class: ParagraphWM,
    inlineToolbar: true,
    tunes: ['anyTuneName'],
  },
  AnyButton: {
    class: AnyButton,
    inlineToolbar: true,
  },
  breakLine: {
    class: BreakLine,
    inlineToolbar: true,
    shortcut: 'CMD+SHIFT+ENTER',
  },

  translateTool: {
    class: TranslateTool,
  },

  image: {
    class: WSMImage,
    config: {
      imagen_refine_url: '/imagen/api/refine-image2',
      imagen_generate_url: '/imagen/api/generate-images',
      uploader: {
        async uploadByFile(file) {
          // Create a FormData object
          const formData = new FormData();

          // Append the file directly to the FormData
          formData.append('file', file);

          // Send the request to the server
          const response = await fetch('/web-edit/api/upload-image', {
            method: 'POST',
            body: formData,
          });

          // Wait for the response to be parsed as JSON
          const data = await response.json();
          // Return the response data
          return {
            success: 1,
            file: {
              url: data.url,
            },
          };
        },
      },
    },
  },
  color: {
    class: ColorPlugin,  // if load from CDN, please try: window.ColorPlugin
    config: {
      colorCollections: [
        '#EC7878',
        '#9C27B0',
        '#673AB7',
        '#3F51B5',
        '#0070FF',
        '#03A9F4',
        '#00BCD4',
        '#4CAF50',
        '#8BC34A',
        '#CDDC39',
        '#FFF',
      ],
      defaultColor: '#FF1300',
      type: 'text',
      customPicker: true,  // add a button to allow selecting any colour
    },
  },
  columns: {
    class: editorjsColumns,
    config: {
      // Pass the library instance to the columns instance.
      EditorJsLibrary: EditorJS,
      tools: columnTools,  // IMPORTANT! ref the column_tools
    },
  },
};

/**
 * Description placeholder
 *
 * @type {*}
 */
const toggleButton = document.getElementById('toggle-readonly');
/**
 * Description placeholder
 *
 * @type {*}
 */
const saveButton = document.getElementById('save-button');
/**
 * Description placeholder
 *
 * @type {*}
 */
const output = document.getElementById('output');
/**
 * Description placeholder
 *
 * @type {*}
 */
const aiReviewButton = document.getElementById('ai-review-button');
/**
 * Description placeholder
 * @date 1/23/2024 - 4:52:20 PM
 *
 * @type {*}
 */
const aiTranslateButton = document.getElementById('ai-translate-button');
/**
 * Description placeholder
 *
 * @type {*}
 */
const gotoButton = document.getElementById('goto-button');
/**
 * Description placeholder
 *
 * @type {*}
 */
const goto2Button = document.getElementById('goto2-button');
/**
 * Description placeholder
 *
 * @type {*}
 */
const impersonateButton = document.getElementById('impersonate-as-button');
/**
 * Description placeholder
 *
 * @type {*}
 */
const impersonate2Button = document.getElementById('impersonate2-as-button');
/**
 * Description placeholder
 *
 * @type {*}
 */
const reviewButton = document.getElementById('review-button');
/**
 * Description placeholder
 *
 * @type {*}
 */
const publishButton = document.getElementById('publish-button');
/**
 * Description placeholder
 *
 * @type {*}
 */
const filePath = window.location.href;  // Get the current page URL
/**
 * Description placeholder
 *
 * @type {*}
 */
const pageOverlay = document.getElementById('popup-overlay');

/**
 * Save the review article
 */
function saveReview() {
  editor.save().then((savedData) => {
    fetch('/web-edit/api/save-review', {
      method: 'POST',
      body: JSON.stringify({
        content: JSON.stringify(savedData),
        url: filePath,
        state: 'REVIEW',
      }),
      headers: {
        'Content-Type': 'application/json',
      },
    });
    // output.innerHTML = JSON.stringify(savedData, null, 4);
  });
}

/**
 * Description placeholder
 *
 * @param {*} msg
 */
function showOverlay(msg) {
  pageOverlay.style.display = 'flex';
  pageOverlay.innerHTML = msg;
}

/**
 * Description placeholder
 *
 * @param {*} msg
 */
function hideOverlay(msg) {
  pageOverlay.style.display = 'none';
}

/**
 * Description placeholder
 *
 * @param {*} data
 * @return {{}}
 */
function groupById(data) {
  const groupedData = {};
  // Loop through each object in the data list
  for (const obj of data) {
    const id = obj.id;
    // Check if an array already exists for the current ID
    if (!groupedData.hasOwnProperty(id)) {
      // Create a new array for the ID if it doesn't exist
      groupedData[id] = [];
    }
    // Push the current object to the corresponding array
    groupedData[id].push(obj);
  }
  // Flatten the grouped data into a single array
  const flattenedData = [];
  for (const id in groupedData) {
    for (const obj of groupedData[id]) {
      flattenedData.push(obj);
    }
  }

  return flattenedData;
}

if (toggleButton) {
  toggleButton.addEventListener('click', () => {
    editor.readOnly.toggle();
    // Update button text based on current state
    toggleButton.textContent =
        editor.readOnly ? 'Enable Editing' : 'Disable Editing';
  });
}

if (aiReviewButton) {
  aiReviewButton.addEventListener('click', () => {
    editor.save().then((savedData) => {
      showOverlay(`<div style="display: flex; flex-direction: column;">
                            <h4><span class="google-symbols">
                            spark
                            </span> Creating AI Suggestions...</h4>
                            <p class="m-0">Please wait while we work our 
                            AI magic...</p>
                        </div>`);
      fetch('/vertex-llm/ai-review', {
        method: 'POST',
        body: JSON.stringify({
          webpage_body: savedData,
          model_name: 'gemini-1.5-pro-001',
        }),
        headers: {
          'Content-Type': 'application/json',
        },
      })
          .then((response) => response.json())  // Parse JSON response
          .then((data) => {
            if (!data || !data.modified_webpage_body) {
              throw new Error('Missing required data in response');
            }
            // Extract modified webpage body
            const aiSuggestBlocks = data.modified_webpage_body.blocks;
            const groupedBlocks = groupById(aiSuggestBlocks);
            data.modified_webpage_body.blocks = groupedBlocks;
            console.log(data.modified_webpage_body);
            // Update the editor with the suggested blocks
            editor.render(data.modified_webpage_body);
            hideOverlay();
          })
          .then(() => {
            // Handle successful save
            console.log('AI suggestions saved successfully!');
          })
          .catch((error) => {
            hideOverlay();
            console.error('Error:', error);
          });
    });
  });
}

if (aiTranslateButton) {
  aiTranslateButton.addEventListener('change', () => {
    editor.save().then((savedData) => {
      showOverlay('Localising page content ...');
      const targetLanguage = aiTranslateButton.value;
      fetch('/vertex-llm/ai_translate_webpage', {
        method: 'POST',
        body: JSON.stringify({
          prompt: savedData,
          target_language: targetLanguage,
          model_name: 'gemini-1.5-pro-001',
          max_output_tokens: 8192,
          temperature: 0.0,
          top_p: 0.8,
          top_k: 40,
        }),
        headers: {
          'Content-Type': 'application/json',
        },
      })
          .then((response) => response.json())  // Parse JSON response
          .then((data) => {
            if (!data || !data.response) {
              throw new Error('Missing required data in response');
            }
            // Extract modified webpage body
            const aiTranslateBlocks = data.response;
            editor.render(aiTranslateBlocks);
            hideOverlay();
          })
          .then(() => {
            // Handle successful save
            console.log('AI suggestions saved successfully!');
          })
          .catch((error) => {
            hideOverlay();
            console.error('Error:', error);
          });
    });
  });
}

if (gotoButton) {
  gotoButton.addEventListener('change', () => {
    handleGotoButtonClick(gotoButton.value);
  });
}

if (goto2Button) {
  goto2Button.addEventListener('change', () => {
    handleGotoButtonClick(goto2Button.value);
  });
}

if (saveButton) {
  console.log(`saveButton found!`);
  saveButton.addEventListener('click', () => {
    editor.save().then((savedData) => {
      showOverlay('Saving Page ...');
      const response = fetch('/web-edit/api/save-draft', {
                         method: 'POST',
                         body: JSON.stringify({
                           content: JSON.stringify(savedData),
                           url: filePath,
                           state: 'draft',
                         }),
                         headers: {
                           'Content-Type': 'application/json',
                         },
                       }).then(() => {
        console.log(response);
        console.log(JSON.stringify(savedData, null, 4));
        hideOverlay();
      });
    });
  });
}

if (reviewButton) {
  reviewButton.addEventListener('click', () => {
    editor.save().then((savedData) => {
      showOverlay('Submitting Page to Review ...');
      const response = fetch('/web-edit/api/submit-review', {
                         method: 'POST',
                         body: JSON.stringify({
                           content: JSON.stringify(savedData),
                           url: filePath,
                           state: 'review',
                         }),
                         headers: {
                           'Content-Type': 'application/json',
                         },
                       }).then(() => {
        console.log(response);
        console.log(JSON.stringify(savedData, null, 4));
        hideOverlay();
      });
    });
  });
}

if (publishButton) {
  publishButton.addEventListener('click', () => {
    editor.save().then((savedData) => {
      showOverlay('Publishing Page to Production ...');
      const response = fetch('/web-edit/api/publish', {
                         method: 'POST',
                         body: JSON.stringify({
                           content: JSON.stringify(savedData),
                           url: filePath,
                           state: 'production',
                         }),
                         headers: {
                           'Content-Type': 'application/json',
                         },
                       })
                           .then((publishResult) => {
                             document.stepper.to(3);
                             console.log('publishResult:', publishResult);
                           })
                           .then(() => {
                             console.log(response);
                             console.log(JSON.stringify(savedData, null, 4));
                             hideOverlay();
                           });
    });
  });
}

/**
 * Description placeholder
 * @date 1/23/2024 - 4:52:19 PM
 *
 * @param {*} page
 */
function handleGotoButtonClick(page) {
  const selectedPage = page;
  switch (selectedPage) {
    case 'viewer':
      window.location = window.location.href.replace(
          /(edit|review|publish)/,
          '',
      );

      // window.location =  (trimmedUrl.endsWith('/') ?
      // trimmedUrl.slice(0, -1) : trimmedUrl) + '/';
      break;
    case 'editor':
      window.location = window.location.href.replace(
          /(edit|review|publish)/,
          'edit',
      );
      break;
    case 'reviewer':
      window.location = window.location.href.replace(
          /(edit|review|publish)/,
          'review',
      );
      break;
    default:
      window.location = window.location.href.replace(
          /(edit|review|publish)/,
          '',
      );
      break;
  }
  showOverlay('Loading...');
}
