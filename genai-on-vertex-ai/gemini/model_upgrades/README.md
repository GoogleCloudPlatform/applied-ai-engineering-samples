# Eval Recipes for upgrading to Gemini 2

This directory contains Eval Recipes for common GenAI tasks. 
The goal is to accelerate the process of upgrading to the latest version of Gemini and minimize the risk of regression.
- An Eval Recipe is a minimalistic example of an automated evaluation that includes a prompt template and an evaluation dataset. 
- The included evaluation datasets are very small, which makes it possible to run each Eval Recipe in less than 1 minute.
- Eval Recipes are lightweight and easy to learn - the entire configuration for most tasks fits on one screen.
- Each Eval Recipe includes 3 alternative implementations:
    - Colab notebook based on Vertex GenAI Evaluation Service
    - Command line script based on Vertex GenAI Evaluation Service
    - Command line script based on Promptfoo
- Eval Recipes can be customized by replacing the prompt template and the evaluation dataset.


| Eval Recipe | Vertex AI Colab | Vertex AI Script | Promptfoo |
| -------- | ------- | -------- | ------- |
| Document QnA | [view](./document_qna/vertex_colab/document_qna_eval.ipynb) | [view](./document_qna/vertex_script/README.md) | [view](./document_qna/promptfoo/README.md) |
| Summarization | [view](./summarization/vertex_colab/summarization_eval.ipynb) | [view](./summarization/vertex_script/README.md) | [view](./summarization/promptfoo/README.md) |
| Text Classification | [view](./text_classification/vertex_colab/text_classification_eval.ipynb) | [view](./text_classification/vertex_script/README.md) | [view](./text_classification/promptfoo/README.md) |
| Multi-turn Chat | [view](./multiturn_chat/vertex_colab/multiturn_chat_eval.ipynb) | [view](./multiturn_chat/vertex_script/README.md) | [view](./multiturn_chat/promptfoo/README.md) |
| Instruction Following | [view](./instruction_following/vertex_colab/instruction_following_eval.ipynb) | [view](./instruction_following/vertex_script/README.md) | [view](./instruction_following/promptfoo/README.md) |

