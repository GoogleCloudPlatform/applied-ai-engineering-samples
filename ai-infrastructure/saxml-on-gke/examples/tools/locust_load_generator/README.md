# Load Generator

**Load Generator** is a [Locust.io](https://locust.io/) based tool for generating load on LLM model endpoints. The Locust runtime has been integrated with Pubsub and BigQuery to enhance default metrics tracking and analysis. Load Generator is deployed in a [Locust distributed configuration](https://docs.locust.io/en/stable/running-distributed.html) as a Kubernetes deployment. The manifests for the deployment are located in the `manifests` folder.

The following diagram demonstrates the desing of **Load Generator**.
