# Safety Evaluation with ShieldGemma, NLP Content Moderation and Perspective API
This repository contains eleven Jupyter notebooks designed for evaluating the safety of large language models (LLMs).  The notebooks cover various aspects of safety evaluation, from understanding the underlying technologies to deploying and testing safety mechanisms in different environments.

The notebooks are organized into three main sections:

**1. Understanding:** These notebooks provide foundational knowledge about content safety and the tools used for evaluation.

* **1.1-Content_Safety.ipynb:** Introduces the concept of content safety and demonstrates how to use ShieldGemma, a fine-tuned model for detecting harmful content. This notebook shows how to use a pre-trained Gemma model for content moderation.

* **1.2-Gemma2_Deployment.ipynb:** Explains how to deploy Gemma 2 models on Vertex AI using different deployment options (TPU, GPU). This notebook walks through the steps of deploying Gemma 2 to Vertex AI using HexLLM and the Text Generation Inference (TGI) service.

* **1.3-Gemma2_Fine_Tuning.ipynb:** Guides you through fine-tuning a Gemma 2 model using a custom dataset and deploying the fine-tuned model. This shows how to fine-tune a Gemma 2 model for improved performance and then deploy it.

* **1.4-Content_Moderation.ipynb:** Demonstrates the use of Google Cloud Natural Language API for content moderation. This notebook demonstrates how to use the Google Cloud Natural Language API's content moderation capabilities.

* **1.5-Content_Moderation_Perspective_API.ipynb:** Shows how to use the Perspective API for toxicity detection. This illustrates the use of the Perspective API for identifying toxicity in text.


**2. Setup:** These notebooks focus on setting up the necessary environment and deploying the safety models.

* **2.1-ShieldGemma_Deployment.ipynb:** Provides detailed steps for deploying ShieldGemma on Vertex AI using HexLLM. This notebook guides you through the specific steps for deploying ShieldGemma.

* **2.2-Enable_APIs.ipynb:** Explains how to enable the required Google Cloud APIs for safety evaluation. This notebook simply describes the API enabling steps.


**3. Usage:** These notebooks demonstrate how to use the deployed safety models for different evaluation scenarios.

* **3.1-Design.ipynb:** Presents the design and implementation of a safety evaluation framework using ShieldGemma, Perspective API, and the Natural Language API.  This notebook details the framework used for safety evaluations.

* **3.2-Development.ipynb:** Shows how to integrate safety evaluations into the development workflow using unit tests and continuous integration.  This notebook illustrates integrating safety checks into a development pipeline.

* **3.3-Staging.ipynb:** Guides you through deploying and testing the safety evaluation pipeline in a staging environment. This notebook shows a staging deployment and testing methodology.

* **3.4-Production.ipynb:** Explains how to deploy the complete safety evaluation pipeline to a production environment. This notebook details production deployment considerations.


**To Use These Notebooks:**

1.  **Prerequisites:** You will need a Google Cloud Platform (GCP) project with appropriate billing enabled and necessary APIs enabled (as detailed in the notebooks). You'll also need to install the required Python packages listed in each notebook.  A Hugging Face token might be required for some operations.

2.  **Running the Notebooks:**  Each notebook is self-contained and provides instructions on how to execute the code.  Follow the instructions in each notebook sequentially.  Remember to replace placeholder values (like `PROJECT_ID`, `REGION`, `BUCKET_URI`, `HF_TOKEN`, `ENDPOINT`) with your actual GCP project and resource details.

3.  **Order of Execution:** It's highly recommended to run the notebooks in the order they are presented, as they build upon each other. The "Understanding" section provides the context, the "Setup" section prepares the environment, and the "Usage" section demonstrates the application of the safety evaluation framework.


This collection of notebooks provides a comprehensive guide to building and deploying a robust safety evaluation pipeline for LLMs on Google Cloud Platform.  Remember to always consult the Google Cloud documentation for the most up-to-date information on APIs, services, and best practices.
