# Load Generator

**Load Generator** is a [Locust.io](https://locust.io/) based tool for generating load on LLM model endpoints. The Locust runtime has been integrated with Pubsub and BigQuery to enhance default metrics tracking and analysis. Load Generator is deployed in a [Locust distributed configuration](https://docs.locust.io/en/stable/running-distributed.html) as  Kubernetes deployments. The manifests for the deployment are located in the `manifests` folder.

The following diagram demonstrates the design of **Load Generator**.

TBD

## Deploy 

Update the `kustomization.yaml` in the `3-load_generator/locust_load_generator/manifests` folder with the namespace created during the base environment setup. This namespace will be used to deploy Locust master and Locust workers. You can retrieve the namespace name by executing `terraform output namespace` from the `environment\1-base_environment` folder.

From the `environment/3-load_generator/locust_load_generator/manifests` folder run:
```
kustomize edit set namespace <SAXML_NAMESPACE> 
```

Update the `parameters.env` in the `3-load_generator/locust_load_generator/manifests` folder with the values matching your environment. 

- `KSA` - the Kubernetes service account to use for Workload Identity. You can retrieve the name of the account by executing `terraform output ksa_name` from the `environment\1-base_environment` folder.
- `NUM_LOCUST_WORKERS` - the number of Locust workers to spawn
- `TOPIC_NAME` - the name of the Pubsub topic used for tracking Locust metrics. You can retrieve it by executing `terraform output locust_metrics_topic_name` from the `environment\3-load_generator/terraform` folder.
- `PROJECT_ID` - your project ID

If your Locust script uses a Hugging Face tokenizer, create a hugging face secret to store your Hugging Face access token.

```
kubectl create secret generic hugging-face --from-literal=token='<YOUR_TOKEN>' -n <YOUR NAMESPACE>
```


To deploy Locust master and Locust workers run the following command from the `3-load_generator/locust_load_generator` folder:

```
skaffold run --default-repo <ARTIFACT_REGISTRY_PATH>
```

Replace `<ARTIFACT_REGISTRY_PATH>` with the path to your Artifact Registry. If you created an Artifact Registry during the base environment setup you can retrieve the path by executing `terraform output artifact_registry_image_path` from the `environment\1-base_environment` folder.


## Run tests

