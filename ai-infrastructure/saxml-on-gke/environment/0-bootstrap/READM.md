## Automation bootstrap

### Update terraform.tvars

### Create automation storage and service account

```
terraform init
terraform apply 

```

### Get provider config

```
AUTOMATION_BUCKET=jk-automation-bucket
gsutil cp gs://$AUTOMATION_BUCKET/providers/env-providers.tf .
```

### Configure the backend

```
Modify the `env-providers.tf` to set the folder for the bootstrap state
```

### Give access to the automation service account

```
SERVICE_ACCOUNT=jk-automation-sa@jk-mlops-dev.iam.gserviceaccount.com
USER_ACCOUNT=your@foo.com
gcloud iam service-accounts add-iam-policy-binding $SERVICE_ACCOUNT --member="user:$USER_ACCOUNT" --role='roles/iam.serviceAccountTokenCreator'

```

### Migrate the state

```
terraform init -migrate-state 
```