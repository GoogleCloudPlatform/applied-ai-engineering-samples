# developer-productivity-with-genai
Those sample assets can be used to show builders and partners with Codey APIs and other GCP services, how to solve different developer tasks such as code generation, code explanation, unit test generation, comment generation, code debugging, code migration and talk to code and doc in software development life cycles to increase developer productivity. 

## Contents
### wireframe to live website notebook covers 
User Journey - Code Generation support for more languages (HTML , CSS, Objective-C etc):

Tech Tasks:
- Generate functions
- Explain code
- Generate unit tests
- Assisted code refactoring and modification

### fine-tune codey notebook covers
User Journey - Generate code for custom libraries based on org’s private repo, new languages, and new code patterns

Tech Tasks:
- Generate functions
- Explain code
- Generate unit tests
- Assisted code refactoring/modification

### iterative debugging notebook covers 
User Journey - AI assistance to help debug issues such as null pointer exceptions.

Tech Task:
- Code debugging

### migrate code from COBOL to Java covers 
User Journey - Migrate/Upgrade/Translate code languages and framework.

Tech Task:
- Translating code from one language to another

### doc-code-search covers 
User Journey: 
Document Search to assist code review and other tasks

Tech Task
- Vertex Search + RAG + Codey + Docs + JIRA

User Journey: 
Codebase chat

Tech Task
- Codebase pattern chat for developers to ask questions regarding codebase

## Setups

For all journeys/notebooks except talk to code and doc use cases/notebook:
- Step 1: Enable Vertex AI Codey API and Vertex AI Search API 
- Step 2: Set Up Prompt Template in a GCS Bucket, you can use the prompt templates in prompt_templates folder
- Step 3: If you don’t have a fine-tuned codey api you can hit, refer to fine tune codey notebook to launch a fine-tuning job.

For talk to code and doc use cases/notebook:
- Step 1: Enable Vertex AI Conversation API
- Step 2: Build Vertex AI Search Engine with PDFs (Coding Style PDFs)
- Step 3: Build Another Vertex AI Search Engine with JIRA Issue Websites
- Step 4: Break Down Code Repository to Chunks and Store Indexes in the Vector Store (Matching Engine)
- Step 5: (Optional - only if you want to use Google Meet Bot): Deploy Cloud Functions Code which Uses MultiRetrievalQAChain to Retrieve Information (Embedding Spaces + RAG + Codey) from 3 Different Retriever Embedding Spaces
- Step 6: (Optional - only if you want to use Google Meet Bot): Call Cloud Function in Webhook in a Dialogflow Project and deploy the project to Google Meet

* If you find anything missing, please let us know.