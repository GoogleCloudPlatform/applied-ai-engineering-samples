# Tuning foundational models with Vertex AI

This repository provides a comprehensive Jupyter notebook that illustrates the step-by-step procedure for tuning foundational models (PaLM 2) with Google Cloud's Vertex AI. This repository will guide users through the entire setup and integration process – starting from environment setup, foundational model selection, to tuning it with Vertex AI.

Architecture:    
![Architecture](/images/architecture.png "Architecture")


## Repository structure

```
.
├── images
└── notebooks
```

- [`/images`](/images): Architecture diagrams.  
- [`/notebooks`](/notebooks): Sample notebooks demonstrating the concepts covered in this demonstration.  


## Notebook

The notebook listed below was developed to explain the concepts exposed in this repository:  
- [Getting Started](/notebooks/vertexai-model-tuning.ipynb) (vertexai-model-tuning.ipynb): Run, tune and evaluate a foundational model.


# Environment Setup

This section outlines the steps to configure the Google Cloud environment that is required in order to run the notebooks and demonstration provided in this repository.  
You will be interacting with the following resource:
 - A user-managed instance of Vertex AI Workbench serves as your development setting and the main interface to Vertex AI services.  
 

### Select a Google Cloud project

In the Google Cloud Console, on the project selector page, [select or create a Google Cloud project](https://console.cloud.google.com/projectselector2).  
> **As this is a DEMONSTRATION, you need to be a project owner in order to set up the environment.**


### Enable the required services

From [Cloud Shell](https://cloud.google.com/shell/docs/using-cloud-shelld.google.com/shell/docs/using-cloud-shell), run the following commands to enable the required Cloud APIs:

```bash
export PROJECT_ID=<YOUR_PROJECT_ID>
 
gcloud config set project $PROJECT_ID
 
gcloud services enable \
  cloudbuild.googleapis.com \
  compute.googleapis.com \
  cloudresourcemanager.googleapis.com \
  iam.googleapis.com \
  container.googleapis.com \
  cloudapis.googleapis.com \
  containerregistry.googleapis.com \
  iamcredentials.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com \
  notebooks.googleapis.com \
  aiplatform.googleapis.com \
  storage.googleapis.com \
```

**Note**: When you work with Vertex AI user-managed notebooks, be sure that all the services that you're using are enabled and white-listed.

### Configure Vertex AI Workbench

Create a user-managed notebooks instance from the command line.
 
**Note**: Make sure that you're following these steps in the same project as before.
 
In Cloud Shell, enter the following command.  
 - For `<YOUR_INSTANCE_NAME>`, enter a name starting with a lower-case letter followed by lower-case letters, numbers or dash sign.  
 - For `<YOUR_LOCATION>`, add a zone (for example, `us-central1-a` or `europe-west4-a`).

```bash
PROJECT_ID=$(gcloud config list --format 'value(core.project)')
INSTANCE_NAME=<YOUR_INSTANCE_NAME>
LOCATION=<YOUR_LOCATION>
gcloud notebooks instances create $INSTANCE_NAME \
     --vm-image-project=deeplearning-platform-release \
     --vm-image-family=common-cpu-notebooks \
     --machine-type=n1-standard-4 \
     --location=$LOCATION
```

Vertex AI Workbench creates a user-managed notebook instance based on the properties that you specified and then automatically starts the instance. When the instance is ready to use, Vertex AI Workbench activates an **Open JupyterLab** link next to the instance name in the [Vertex AI Workbench Cloud Console](https://console.cloud.google.com/vertex-ai/workbench/user-managed) page. To connect to your user-managed notebooks instance, click **Open JupyterLab**.

On Jupyterlab `Launcher Page`, click on `Terminal` to start a new terminal.  
Clone the repository to your notebook instance:

> git clone https://github.com/GoogleCloudPlatform/gcp-genai-samples


## Getting help

If you have any questions or if you found any problems with this repository, please report through GitHub issues.
