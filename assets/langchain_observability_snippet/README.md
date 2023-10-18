# A Code Snippet for Langchain Observability/Understanding

The [notebook](./langchain-observability-snippet.ipynb) in this folder contains a code snippet that shows exact individual LLM calls [Langchain](https://www.langchain.com/) agents make during agent execution. The notebook also has a walkthrough and demonstration of the code snippet.

In complex agents, it's not always obvious exactly what text is being sent to the LLM. The code snippet implements a Langchain [callback handler](https://python.langchain.com/docs/modules/callbacks/) that exposes those calls, along with providing some basic assistance tracking and debugging Langchain chains.

## Requirements

To run the walkthrough and demonstration in the notebook you'll need access to a Google Cloud project with the [Vertex AI API](https://console.cloud.google.com/apis/library/aiplatform.googleapis.com) enabled.

The Langchain callback code snippet in the notebook can be run independently of Google Cloud, in any Python environment.

## Getting Help

If you have any questions or find any problems, please report through GitHub issues.
