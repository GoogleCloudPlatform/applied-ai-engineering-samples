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
 * Imagen API call to get a new generated image
 *
 * @async
 * @param {*} data
 * @param {*} apiUrl
 * @param {*} t
 * @return {*}
 */
async function imagen(data, apiUrl, t) {
  console.log(`data=${JSON.stringify(data)}`);
  const resp = await fetch(apiUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  const body = await resp.json();
  t.data.file.url = body.image_urls[0];
  t.ui.fillImage(t.data.file.url);
}

/**
 * Description placeholder
 *
 * @class WSMImage
 * @typedef {WSMImage}
 * @extends {ImageTool}
 */
class WSMImage extends ImageTool {
  // /**
  //  * Shows caption input
  //  *
  //  * @param {string} text - caption text
  //  * @returns {void}
  //  */
  // fillCaption(text) {
  //   console.log(`fillCaption(${text})`)
  //   if (this.nodes.caption) {
  //     this.nodes.caption.innerHTML = text;
  //   }
  //   if(this.ui.readOnly && (text == "" || !text) ){
  //     this.nodes.caption.display = "none";
  //   }
  // }
  __actions = [
    {
      name: 'Prompt',
      icon:
          `<img src="/static/img/icons/vertexai.svg" width="24" height="24"/>`,
      title: 'Refine',
      toggle: false,
      action: this.__refine_image_action,
    },
    {
      name: 'Generate',
      icon:
          `<img src="/static/img/icons/vertexai.svg" width="24" height="24"/>`,
      title: 'Generate',
      toggle: false,
      action: this.__generate_image_action,
    },
    {
      name: 'SmallSize',
      icon: `<img src="/static/img/icons/ssize.svg" width="18" height="18"/>`,
      title: 'Small Size',
      toggle: false,
      action: () => this.__setWidthSize('S'),
    },
    {
      name: 'MediumSize',
      icon: '<img src="/static/img/icons/msize.svg" width="18" height="18"/>',
      title: 'Medium Size',
      toggle: false,
      action: () => this.__setWidthSize('M'),
    },
    {
      name: 'LargaSize',
      icon: '<img src="/static/img/icons/lsize.svg" width="20" height="20"/>',
      title: 'Large Size',
      toggle: false,
      action: () => this.__setWidthSize('L'),
    },
    {
      name: 'Auto',
      icon:
          `<img src="/static/img/icons/autosize.svg" width="18" height="18"/>`,
      title: 'Auto Size',
      toggle: false,
      action: () => this.__setWidthSize(''),
    },
  ];

  /**
   * Description placeholder
   *
   * @param {*} size
   */
  __setWidthSize(size) {
    let finalWidth = 'unset';
    switch (size) {
      case 'S':
        finalWidth = '100px';
        break;
      case 'M':
        finalWidth = '500px';
        break;
      case 'L':
        finalWidth = '700px';
        break;
    }
    this.ui.nodes.imageContainer.style.width = finalWidth;
  }

  /**
   * Description placeholder
   *
   * @param {*} name
   * @return {*}
   */
  __create_prompt_window(name) {
    if (document.getElementById(`image_generative_ai_action_div_${name}`)) {
      return null;
    }
    const div = document.createElement('div');
    div.id = `image_generative_ai_action_div_${name}`;
    // div.style = "card-text";
    // const input = document.createElement("input");
    // input.id = `image_generative_ai_action_input_${name}`;
    // input.placeholder = "Prompt...";
    const input = document.createElement('div');
    input.setAttribute('contenteditable', true);
    input.id = `image_generative_ai_action_input_${name}`;
    input.setAttribute('data-placeholder', 'Prompt...');
    input.width = '100px';
    input.setAttribute('class', 'cdx-input ce-paragraphLineBreakable cdx-block');
    const button = document.createElement('button');
    button.id = `image_generative_ai_action_button_${name}`;
    button.value = 'Generate';
    button.innerText = 'Generate';
    div.appendChild(input);
    div.appendChild(button);
    if (name == 'Prompt') {
      console.log(`this.imagen_refine_url=${this.imagen_refine_url}`);

      button.addEventListener('click', async (e) => {
        console.log(`name=${name}`);

        console.log(`${input.innerTEXT}`);

        const prompt = input.innerText;
        const image_url = this.data?.file?.url;
        // const existing_img =
        // document.querySelector(".image-tool__image-picture");
        const existingImg = this.ui.nodes.wrapper.querySelector(
            '.image-tool__image-picture',
        );
        console.log(`existing image=${existingImg}`);
        if (existingImg) {
          console.log(existingImg.outerHTML);
          existingImg.parentNode.removeChild(existingImg);
          existingImg.remove();
        }
        this.ui.toggleStatus('loading');
        e.target.parentNode.remove();
        await imagen(
            {
              image_url: image_url,
              target_region: prompt,
            },
            this.imagen_refine_url,
            this,
        );
      });
    } else if (name == 'Generate') {
      console.log(`this.imagen_generate_url=${this.imagen_generate_url}`);
      button.addEventListener('click', async (e) => {
        console.log(`${input.innerTEXT}`);

        // const prompt = input.value;
        const prompt = input.innerText;
        const existingImg = this.ui.nodes.wrapper.querySelector(
            '.image-tool__image-picture',
        );
        console.log(`existing image=${existingImg}`);
        if (existingImg) {
          console.log(existingImg.outerHTML);
          existingImg.remove();
        }
        this.ui.toggleStatus('loading');
        e.target.parentNode.remove();
        await imagen(
            {
              prompt: prompt,
            },
            this.imagen_generate_url,
            this,
        );
      });
    }

    return div;
  }

  /**
   * Description placeholder
   *
   * @param {*} name
   */
  __refine_image_action(name) {
    const div = this.__create_prompt_window(name);
    if (div) {
      this.block.holder.appendChild(div);
    }
  }

  __generate_image_action(name) {
    const div = this.__create_prompt_window(name);
    if (div) {
      this.block.holder.appendChild(div);
    }
  }

  /**
   * Description placeholder
   *
   * @return {*}
   */
  render() {
    const result = super.render(this.data);
    if (this.ui.readOnly &&
        (this.ui.nodes.caption.innerText == '' ||
         !this.ui.nodes.caption.innerText)) {
      this.ui.nodes.caption.style.visibility = 'hidden';
    } else {
      this.ui.nodes.caption.style.visibility = 'visible';
    }
    return result;
  }
  /**
   * Creates an instance of WSMImage.
   *
   * @constructor
   * @param {*} props
   */
  constructor(props) {
    super(props);
    this.imagen_refine_url = props.config.imagen_refine_url;
    this.imagen_generate_url = props.config.imagen_generate_url;
    this.config.actions = this.__actions.map((a) => {
      const r = {
        ...a,
        action: a.action.bind(this),
      };
      return r;
    });
  }
}
