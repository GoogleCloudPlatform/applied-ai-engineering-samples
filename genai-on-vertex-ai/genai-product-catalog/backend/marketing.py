# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Functions to generate marketing copy."""
import config
import utils

llm = utils.get_llm()

def generate_marketing_copy(desc: str, attributes: dict[str,str]) -> str:
    """Given list of product IDs, join category names.
    
    Args:
        desc: sparse description of product
        attributes: e.g. {'color':'green', 'pattern': 'striped'}

    Returns:
        Marketing copy that can be used for a product page
    """
    prompt = f"""
      Generate a compelling and accurate product description
      for a product with the following description and attributes.

      Description:
      {desc}

      Attributes:
      {attributes}
    """
    llm_parameters = {
      "max_output_tokens": 1024,
      "temperature": 0.5,
    }
    response = llm.predict(
        prompt,
        **llm_parameters
    )
    return response.text