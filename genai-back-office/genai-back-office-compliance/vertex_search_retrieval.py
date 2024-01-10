from google.cloud import discoveryengine_v1beta as vertexaisearch
import pandas as pd
import json
from typing import Union
from google.protobuf.json_format import MessageToDict
from google.cloud import aiplatform
from vertexai.language_models import TextGenerationModel, ChatModel
from vertexai.preview.generative_models import (
    GenerationConfig,
    GenerativeModel,
    Image,
    Part,
)


# LOAD CONFIG DATA 
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
PROJECT_ID = config['CREDENTIALS']['PROJECT_ID']
SEARCH_ENGINE_ID = config['CREDENTIALS']['SEARCH_ENGINE_ID']
LOCATION = config['CREDENTIALS']['LOCATION']
PROJECT_LOCATION = config['CREDENTIALS']['PROJECT_LOCATION']

# Initialize Vertex AI
import vertexai
vertexai.init(project=PROJECT_ID, location=PROJECT_LOCATION)


def search_with_summary(MODEL, project_id: str, location: str, data_store: str, serving_config: str, search_query: str, search_engine_id: str, serving_config_id : str):
  # Gen App Builder Enterprise Search
  client = vertexaisearch.SearchServiceClient()
  # The full resource name of the search engine serving config
  # e.g. projects/{project_id}/locations/{location}
  serving_config = client.serving_config_path(
    project=project_id,
    location=location,
    data_store=search_engine_id,
    serving_config=serving_config_id,
  )

  request = vertexaisearch.SearchRequest(
    serving_config=serving_config,
    query=search_query,
  )

  response = client.search(request)
  results = []
  for res in response.results:
    results.append(res)

  # to results dataframe
  response = MessageToDict(results[0]._pb)
  results_dataframe = pd.DataFrame.from_dict(get_documents(results))

  # construct references
  #print("JSON data created from the search results!")
  #references_dataframe = getSnippets(results_dataframe)

  # Summarize with PaLM
  #aiplatform.init(project=palm_project_id, location=palm_location)


  prompt = f"""
  You are filling out the CDP Questionnaire for your organization, which is Alphabet. Don't refer to Alphabet in third-person, instead opt for "Alphabet" and "we".  
  The following are the results from a query "{search_query}" in JSON format.
  Using only the JSON below, summarize the JSON to provide an answer. Make sure to generate a natural response and avoid starting the sentences the same way.
  Make sure not to use any citations for the summary except for what's contained in the JSON below.
  Once you've created a summary, append to the summary a list of citations relevant in creating the summary from link and title values in the JSON, with each citation in the form of "found in 'title' article, at 'link'"
  Don't hint back to the reference in your answer, only include them in the citations section. 
  For general descriptions, produce at least 500 words.  
  {results_dataframe.to_json(orient='records')}
  """


  if MODEL == "gemini-pro": 
      model = GenerativeModel(MODEL)

      prediction = model.generate_content(prompt, stream=False)


  else: 
    model = TextGenerationModel.from_pretrained(MODEL)

    prediction = model.predict(
        prompt,
        # Optional:
        max_output_tokens=1024,
        temperature=0.65,
        top_p=0.8,
        top_k=40,
    )

  # safety_categories = prediction._prediction_response[0][0]['safetyAttributes']
  # if safety_categories["blocked"] == True:
  #   print("This response was blocked due to safety concerns. Please restate your question.")
  #   print(f"""The prompt that was blocked is as follows:
  #   {prompt}
  #   """)
  #   return("Error")
  # else:
  #   return(prediction.text)

  return prediction.text


def get_documents(objects):
    """
    Return a list of documents from a list of objects.
    """
    docs = []
    for doc in objects:
      response = MessageToDict(doc._pb)
      docs.append(response["document"])
    return docs

def vertex_search_response(
    MODEL, 
    search_query: str,
    search_engine_id: str= SEARCH_ENGINE_ID,
    search_engine_name: str= "esg-demo",
    project_id: str= PROJECT_ID,
    location: str= LOCATION,
    serving_config_id: str= "default_config" 
    ) :


  response = search_with_summary(MODEL, project_id, location, search_engine_id, serving_config_id, search_query, search_engine_id, serving_config_id)
  return response

