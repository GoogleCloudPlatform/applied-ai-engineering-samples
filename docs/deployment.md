# Deployment

**Deploy the backend services as Cloud Functions:**

```bash
# Deploy Answer Generation Service
gcloud functions deploy execute_rag_query --runtime python39 --trigger-http --source backend/answer_generation_service

# Deploy Evaluation Service
gcloud functions deploy evaluate_rag