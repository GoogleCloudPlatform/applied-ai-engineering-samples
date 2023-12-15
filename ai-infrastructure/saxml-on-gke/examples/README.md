# Model deployment and benchmarking examples

This folder contains examples of deploying and load testing various Large Language models. Currently, the following examples are available:

- [Llama-2 7B](llama2-7b/README.md)

## Build deployment and load testing tools

In most of the examples, you will utilize the Checkpoint Converter and Load Generator tools. The Checkpoint Converter tool is used to convert original model checkpoints to the format required by Saxml. The Load Generator is a [Locust.io](https://locust.io/) based system designed to stress test a model with user-provided test prompts and capture test metrics in Big Query. Both tools run as workloads on your GKE cluster. Before proceeding with the examples, you need to build container images that package these tools.

You can build the container images with Cloud Build.

Set the ARTIFACT_REGISTRY variable to your Artifact Registry path. If you created an Artifact Registry during the base environment setup you can retrieve the path by executing `terraform output artifact_registry_image_path`` from the `environment\1-base_environment` folder

```
ARTIFACT_REGISTRY="your-artifact-registry-path"
CHECKPOINT_CONVERTER_IMAGE_URI="$ARTIFACT_REGISTRY/checkpoint-converter:latest"
LOAD_GENERATOR_IMAGE_URI="$ARTIFACT_REGISTRY/load-generator:latest"

gcloud builds submit \
--config build.yaml \
--substitutions _CHECKPOINT_CONVERTER_IMAGE_URI=$CHECKPOINT_CONVERTER_IMAGE_URI,_LOAD_GENERATOR_IMAGE_URI=$LOAD_GENERATOR_IMAGE_URI
```



