# Serving Layer

The Serving Layer handles query processing, answer generation, and evaluation.

**Experiment Orchestrator:**

- The frontend allows users to define RAG experiments by selecting retrieval methods, LLMs, and evaluation metrics.
- The backend translates user selections into a set of tasks representing different combinations of parameters.
- Cloud Workflows orchestrates the execution of these tasks, invoking the Answer Generation and Evaluation Services.

**Experiment Runner Workflow:**

- **Answer Generation Service (Cloud Function):**
    - Retrieves relevant documents based on the chosen retrieval method and the user's query.
    - Generates an answer using the specified LLM and its parameters.
- **Answer Evaluation Service (Cloud Function):**
    - Evaluates the generated answer using automated metrics (Vertex AI Rapid Eval) and collects user feedback.