# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from apache_beam.testing.test_pipeline import TestPipeline
from custom_transforms.gcs_input_fn import GCSInputFn, LogInputFn
from custom_transforms.gcs_loader_fn import GCSLoaderFn
from custom_transforms.split_document_fn import SplitDocumentFn
from custom_transforms.upsert_vector_search_fn import UpsertToVectorSearchFn
from custom_transforms.url_input_fn import URLInputFn
from custom_transforms.url_loader_fn import URLLoaderFn


class ConfigExtractor:

  def __init__(self, message_data):
    self.message_data = message_data

  def get_input_config(self):
    return self.message_data.get("input", {}).get("config", {})

  def get_data_loader_config(self):
    return self.message_data.get("data_loader", {}).get("config", {})

  def get_document_splitter_config(self):
    return self.message_data.get("document_splitter", {}).get("config", {})

  def get_vector_store_config(self):
    return self.message_data.get("vector_store", {}).get("config", {})


class CustomPipelineOptions(PipelineOptions):

  @classmethod
  def _add_argparse_args(cls, parser):
    parser.add_argument(
        "--window_size",
        type=float,
        default=1.0,
        help="Output file's window size in minutes.",
    )


def create_test_input():
  # Simulate PubSub messages
  return [
      json.dumps({
          "input": {
              "type": "url",
              "config": {"url": "https://en.wikipedia.org/wiki/Google"},
          },
          "data_loader": {
              "type": "document_ai",
              "config": {
                  "project_id": "abhishekbhgwt-llm",
                  "location": "us",
                  "processor_name": "projects/360429251832/locations/us/processors/4ad5818534023450",
                  "gcs_output_path": "gs://rag_pg_test_bucket/output",
              },
          },
          "document_splitter": {
              "type": "recursive_character",
              "config": {"chunk_size": 1000, "chunk_overlap": 200},
          },
          "vector_store": {
              "type": "vertex_ai",
              "config": {
                  "project_id": "abhishekbhgwt-llm",
                  "region": "us-central1",
                  "index_id": "7028698449302257664",
                  "endpoint_id": "6309811358783242240",
                  "embedding_model": "text-embedding-004",
                  "index_name": "alphabet_test_index",
              },
          },
      }).encode("utf-8")
  ]


def batch_if_needed(key_value_pair):
  key, docs = key_value_pair
  if isinstance(docs, list):
    doc_list = docs
  else:
    doc_list = [docs]

  if len(doc_list) > 1000:
    for i in range(0, len(doc_list), 1000):
      yield (key, doc_list[i : i + 1000])
  else:
    yield (key, doc_list)


def is_gcs_input(element):
  return element["input"]["type"] == "gcs"


def is_url_input(element):
  return element["input"]["type"] == "url"


def extract_config(element):
  config_extractor = ConfigExtractor(element)
  return (
      element["message_id"],
      {
          "input_config": config_extractor.get_input_config(),
          "data_loader_config": config_extractor.get_data_loader_config(),
          "document_splitter_config": (
              config_extractor.get_document_splitter_config()
          ),
          "vector_store_config": config_extractor.get_vector_store_config(),
          "raw_message": element,
      },
  )


def run(argv=None):
  pipeline_options = PipelineOptions(argv)
  pipeline_options.view_as(StandardOptions).streaming = True
  custom_options = pipeline_options.view_as(CustomPipelineOptions)

  with TestPipeline(options=pipeline_options) as p:
    # Create input PCollection and extract configs
    inputs = (
        p
        | "CreateTestInput" >> beam.Create(create_test_input())
        | "LogInput" >> beam.ParDo(LogInputFn())
        | "DecodeJSON" >> beam.Map(lambda x: json.loads(x.decode("utf-8")))
    )

    # Split inputs by type using Filters
    gcs_inputs = inputs | "FilterGCSInputs" >> beam.Filter(
        lambda x: x["input"]["type"] == "gcs"
    )
    url_inputs = inputs | "FilterURLInputs" >> beam.Filter(
        lambda x: x["input"]["type"] == "url"
    )

    # Process each input type
    processed_gcs = gcs_inputs | "ProcessGCSInputs" >> beam.ParDo(GCSInputFn())
    processed_url = url_inputs | "ProcessURLInputs" >> beam.ParDo(URLInputFn())

    # Load documents using separate loaders
    loaded_gcs_docs = processed_gcs | "LoadGCSDocuments" >> beam.ParDo(
        GCSLoaderFn()
    )
    loaded_url_docs = processed_url | "LoadURLDocuments" >> beam.ParDo(
        URLLoaderFn()
    )

    # Merge loaded documents
    merged_docs = (
        loaded_gcs_docs,
        loaded_url_docs,
    ) | "MergeLoadedDocs" >> beam.Flatten()

    # Split documents
    split_docs = merged_docs | "SplitDocuments" >> beam.ParDo(SplitDocumentFn())

    # Window and batch splits
    windowed_splits = split_docs | "Windowing" >> beam.WindowInto(
        beam.window.FixedWindows(int(custom_options.window_size * 60))
    )
    grouped_splits = windowed_splits | "GroupByKey" >> beam.GroupByKey()
    batched_splits = grouped_splits | "BatchIfNeeded" >> beam.FlatMap(
        batch_if_needed
    )

    # Upsert to Vector Search
    results = batched_splits | "UpsertToVectorSearch" >> beam.ParDo(
        UpsertToVectorSearchFn()
    )

    # Log results
    results | "LogResults" >> beam.Map(logging.info)


if __name__ == "__main__":
  logging.getLogger().setLevel(logging.INFO)
  run()
