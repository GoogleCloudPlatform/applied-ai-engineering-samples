"""Functions to generate marketing copy."""
import vertexai
import config

vertexai.init(project=config.PROJECT, location=config.LOCATION)
llm = vertexai.language_models.TextGenerationModel.from_pretrained("text-bison")

def generate_marketing_copy(desc: str, attributes: list[str]) -> str:
    """Given list of product IDs, join category names.
    
    Args:
        desc: sparse description of product
        attributes: list of product attributes

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
    }
    response = llm.predict(
        prompt,
        **llm_parameters
    )
    return response.text