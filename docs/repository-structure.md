## 📂 **Repository Structure** <a name="repository-structure"></a>

```bash
└── backend
    ├── answer_generation_service/          # Answer Generation Cloud Function
    ├── answer_evaluation_service/          # Evaluation Service Cloud Function
    ├── pubsub_trigger_service/             # Pub/Sub Trigger Service Cloud Function
    ├── models/                             # Data models
    ├── routers/                            # FastAPI routers
    ├── utils/                              # Utility modules
    ├── workflows/                          # Cloud Workflow definition
    ├── dataflow/                           # Dataflow pipeline
    ├── firebase_setup.py                   # Setting up Firebase
    ├── main.py                             # Main FastAPI entrypoint
    ├── Dockerfile                          # Dockerfile to launch API backend
    └── requirements.txt                    # Python dependencies for backend
└── frontend
    ├── pages/                              # Streamlit front-end pages
    ├── app.py                              # Main Streamlit application
└── config.toml                             # Configuration
└── requirements.txt                        # Python dependencies
```