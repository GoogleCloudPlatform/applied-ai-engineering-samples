"""HTTP Server to interact with SAX Cluster, SAX Admin Server, and SAX Model Server."""

import logging

from fastapi import FastAPI, HTTPException, status
from typing import Optional
from pydantic import BaseModel
import sax


class ModelOptions(BaseModel):
    temperature: Optional[float] = None
    top_k: Optional[int] = None
    top_p: Optional[float] = None
    per_example_max_decode_steps: Optional[int] = None


class Query(BaseModel):
    prompt: str
    model_id: str
    model_options: Optional[ModelOptions]


class Model(BaseModel):
    model_id: str
    model_path: str
    checkpoint: str
    replicas: int


app = FastAPI()


@app.get("/")
def read_root():
    return {'message': 'HTTP Server for SAX Client'}


@app.get("/listcell")
def list_cell(model_id: str):
    try:
        details = sax.ListDetail(model_id)
        response = {
            'model': model_id,
            'model_path': details.model,
            'checkpoint': details.ckpt,
            'max_replicas': details.max_replicas,
            'active_replicas': details.active_replicas,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Exception in Saxml client: {e}"
        )
    return response


@app.post("/generate", status_code=status.HTTP_200_OK)
def lm_generate(query: Query):
    """Invokes lm.generate method on SAX Model Server."""
    try:
        print(query)
        sax.ListDetail(query.model_id)
        model_open = sax.Model(query.model_id)
        lm = model_open.LM()
        completions = lm.Generate(query.prompt)
        lm = _lm_models.get(query.model_id)
        if not lm:
            raise RuntimeError(f"Unsupported model: {query.model_id}")
        response = {'completions': completions}
    except Exception as e:
        logging.error("Exception when invoking Saxml client: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Exception in Saxml client: {e}")
    return response


@app.post("/publish", status_code=status.HTTP_200_OK)
def publish(model: Model):
    try:
        sax.Publish(model.model_id, model.model_path,
                    model.checkpoint, model.replicas)
        response = {
            'model': model.model_id,
            'path': model.model_path,
            'checkpoint': model.checkpoint,
            'replicas': model.replicas,
        }
    except Exception as e:
        logging.error("Exception when invoking Saxml client: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Exception in Saxml client: {e}")
    return response


@app.post("/unpublish", status_code=status.HTTP_200_OK)
def unpublish(model_id: str):
    try:
        sax.Unpublish(model_id)
        response = {'model': model_id}
    except Exception as e:
        logging.error("Exception when invoking Saxml client: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Exception in Saxml client: {e}")
    return response


@app.put("/update", status_code=status.HTTP_200_OK)
def update(model: Model):
    try:
        sax.Update(model.model_id, model.model_path,
                   model.checkpoint, model.replicas)
        response = {
            'model': model.model_id,
            'path': model.model_path,
            'checkpoint': model.checkpoint,
            'replicas': model.replicas,
        }
    except Exception as e:
        logging.error("Exception when invoking Saxml client: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Exception in Saxml client: {e}")
    return response
