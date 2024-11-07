# Safety Evaluation - 1.Understanding the components of safety evaluation

This directory contains Jupyter Notebooks exploring various aspects of large language model (LLM) safety.  Each notebook focuses on a specific method or tool for evaluating and mitigating risks associated with LLMs.

## Notebooks:

1. **`1.1-Content_Safety.ipynb`**: **Content Safety Evaluation using ShieldGemma**

   This notebook demonstrates how to use the ShieldGemma model to assess the safety of text, specifically identifying potentially harmful content such as hate speech, sexually explicit material, and dangerous instructions.  It provides code examples for classifying both user prompts and model-generated responses. The notebook leverages the `keras-nlp` library for model loading and prediction.


2. **`1.2-Gemma2_Deployment.ipynb`**: **Deploying Gemma2 Models on Vertex AI**

   This notebook guides you through the deployment of Gemma2 LLMs (various sizes) to Google Cloud's Vertex AI platform. It offers deployment options using Hex-LLM on TPUs and the Hugging Face Text Generation Inference (TGI) on GPUs, showcasing different deployment strategies and hardware choices depending on model size and performance needs.


3. **`1.3-Gemma2_Fine_Tuning.ipynb`**: **Fine-tuning Gemma2 with LoRA on Vertex AI**

   This notebook provides a complete example of fine-tuning a Gemma2 LLM using LoRA (Low-Rank Adaptation) on Vertex AI. It details the process of setting up the training job, specifying hyperparameters, and managing resources. The fine-tuned model is then deployed for inference.


4. **`1.4-Content_Moderation.ipynb`**: **Content Moderation using Google Cloud Natural Language API**

   This notebook explores content moderation capabilities using Google Cloud's Natural Language API. It shows how to analyze text for potentially inappropriate content and receive confidence scores for various categories of harmful content.


5. **`1.5-Content_Moderation_Perspective_API.ipynb`**: **Content Moderation using Perspective API**

   This notebook utilizes the Perspective API to analyze text and assess its toxicity and other harmful attributes.  It demonstrates how to make API requests, receive scores for various attributes (toxicity, severe toxicity, identity attacks, etc.), and display the results in a user-friendly format.


## Prerequisites:

Before running these notebooks, ensure you have:

* A Google Cloud Platform (GCP) project with appropriate billing enabled.
* The necessary APIs enabled (specified in each notebook).
* The required Python libraries installed (listed in each notebook).
* A Hugging Face access token (`HF_TOKEN`) with read access to the necessary models.  This token should be set as an environment variable.


## Running the Notebooks:

Each notebook provides detailed instructions and comments within the code.  Follow the instructions in each notebook to set up the environment, configure parameters, and run the code. Remember to fill in the necessary placeholders for project IDs, region, and bucket URIs.


## Note:

Some notebooks utilize restricted resources and might require specific permissions and quota requests within your GCP project.  Ensure you have the necessary permissions before running these notebooks.  Always review and understand the code before executing it.

