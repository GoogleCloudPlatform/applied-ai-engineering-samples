# Safety Evaluation - 2.Setup notebooks for the Safety Evaluation

This directory contains the setup notebooks for the safety evaluation.  These notebooks are crucial for deploying the ShieldGemma model and enabling the necessary Google Cloud APIs.

## 2.1-ShieldGemma_Deployment.ipynb

This notebook handles the deployment of the ShieldGemma model to Vertex AI.  It includes:

* **Authentication:** Authenticates with Google Cloud and Hugging Face.  Requires setting the `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_REGION`, and `HF_TOKEN` environment variables or providing them as notebook parameters.
* **API Enablement:** Enables the necessary Vertex AI and Compute Engine APIs.
* **Quota Check:** Checks the project's quota for the specified TPU type and region to ensure sufficient resources are available for deployment.  Provides instructions for requesting additional quota if needed.
* **Model Deployment:** Deploys the selected ShieldGemma model (2B, 9B, or 27B) to a Vertex AI endpoint using a specified TPU configuration.  Allows for choosing between dedicated or shared endpoints.
* **Safety Policy Integration:** Includes code for defining safety policies and generating prompts for evaluating model outputs against those policies.  Demonstrates how to use the deployed endpoint to classify prompts and responses based on pre-defined harm types (Dangerous Content, Hate Speech, Sexually Explicit Information, Harassment). This includes example usage of the functions.
* **Resource Cleanup (Optional):** Provides an option to delete the deployed model and endpoint after the evaluation.

**Before running:**

1. Set up your Google Cloud project.
2. Obtain a Hugging Face token with read access.
3. Set the environment variables `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_REGION`, and `HF_TOKEN`, or provide these values as parameters in the notebook.
4. Ensure you have the required Google Cloud permissions.


## 2.2-Enable_APIs.ipynb

This notebook enables the necessary Google Cloud APIs required for the safety evaluation. These APIs include:

* **Comment Analyzer API:** Used for sentiment analysis and potentially other text analysis tasks using Perspective API.
* **Cloud Natural Language API:** Provides advanced natural language processing capabilities.
* **Vertex AI API:**  The core API for interacting with Vertex AI services, including model deployment and management.
* **Compute Engine API:** Required for managing the Compute Engine resources used for model deployment.
* **Cloud Build API:** Used for building and deploying container images.

**Before running:**

1. Set up your Google Cloud project.
2.  Ensure you have the necessary Google Cloud permissions.

This notebook simplifies the process of enabling these APIs, ensuring a smoother setup for the safety evaluation.  It uses `gcloud` commands to automate the API enablement process.  The notebook also installs the necessary Python libraries for interacting with these APIs.
