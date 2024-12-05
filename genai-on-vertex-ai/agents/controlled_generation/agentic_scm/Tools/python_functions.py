
# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import yaml
import requests
import subprocess
import json
import pandas as pd
import pytz
from googleapiclient.errors import HttpError 



def load_config():
    """Loads configuration parameters from settings.yaml in the root directory."""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_file = os.path.join(root_dir, "settings.yaml")
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    return config

# Load the configuration
config = load_config()

# Access the project_id
project_id = config["project_id"]
location = config["location"]
app_id_manuals = config["app_id_manuals"]
app_id_safety_reports = config["app_id_safety_reports"]
dataset_id = config["dataset_id"]
table_id = config["table_id"]
bq_project_id = config["bq_project_id"]
gcal_api_key = config["gcal_api_key"]
johnSmith_gcal_ID = config["johnSmith_gcal_ID"]


########################################################################################################################
# ANALYZE IMAGE 
########################################################################################################################

def analyze_image(image_path: str):
    """Analyzes an image to detect damage in insulator parts.

    This function uses the Gemini Pro model to analyze an image and determine 
    if the insulator parts within the image are damaged. It expects the model 
    to return a JSON array with image descriptions and damage information.

    Args:
        image_path (str): The path to the image file to be analyzed.

    Returns:
        tuple: A tuple containing the image description and a boolean value 
               indicating whether damage was detected.

    Raises:
        JSONDecodeError: If the model output is not a valid JSON array.
        IndexError: If the JSON array is empty or does not contain the expected fields.
    """
    from vertexai.generative_models import GenerativeModel, Content, Part, GenerationConfig, Image
    import json 

    model = GenerativeModel("gemini-1.5-flash-001")

    # text_part = Part.from_text("Why is sky blue?")
    image_part = Part.from_image(Image.load_from_file(image_path))

    instructions= """
                Tell me if the aircraft parts in the image are broken. Be very specific in your response. 
                If the image contains an aircraft wing, tell me if the broken part is the slat or the flap. 
                Respond with a valid JSON array of objects in this format:
                {image_description: "", damaged: ""}. Where 'damaged' is a boolean variable.
                Don't append anything other than the objects in response like "```json" etc.}
                """

    # Now construct the content with the image bytes
    contents = [
        instructions,
        image_part 
    ]

    output = model.generate_content(contents, stream=False).text

    outputjson=json.loads(output)
    first_item = outputjson[0]
    image_description = first_item['image_description']
    damaged = first_item['damaged']
    return image_description, damaged




########################################################################################################################
# SEARCH MANUALS AND REPORTS 
########################################################################################################################

def search_manuals(query):
    """
    Performs a search query to retrieve information for a question on aircraft manuals. 

    Args:
        query: The search query text.

    Returns:
        str: string with filename in which the info was found, the page number, and the answer to the question.
    """
    # Get access token
    access_token = (
        subprocess.check_output("gcloud auth print-access-token", shell=True)
        .decode("utf-8")
        .strip()
    )

    # Construct API URL
    url = f"https://discoveryengine.googleapis.com/v1/projects/{project_id}/locations/global/collections/default_collection/engines/{app_id_manuals}/servingConfigs/default_search:search"

    # Prepare request headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Prepare request body
    request_body = {
        "query": query

    }

    # Make API request
    response = requests.post(url, headers=headers, data=json.dumps(request_body))

    # Check for errors
    response.raise_for_status()

    # Return response
    search_results = response.json()
    title = search_results["results"][0]["document"]["derivedStructData"]["title"]
    pageNumber = search_results["results"][0]["document"]["derivedStructData"]["extractive_answers"][0]["pageNumber"]
    content = search_results["results"][0]["document"]["derivedStructData"]["extractive_answers"][0]["content"]
    return (f"Filename: {title}, pageNumber: {pageNumber}, searchResult: {content}")


def search_safety_reports(query):
    """
    Performs a search query to retrieve information for a question on aircraft annual safety reports. 

    Args:
        query: The search query text.

    Returns:
        str: string with filename in which the info was found, the page number, and the answer to the question.
    """
    # Get access token
    access_token = (
        subprocess.check_output("gcloud auth print-access-token", shell=True)
        .decode("utf-8")
        .strip()
    )

    # Construct API URL
    url = f"https://discoveryengine.googleapis.com/v1/projects/{project_id}/locations/global/collections/default_collection/engines/{app_id_safety_reports}/servingConfigs/default_search:search"

    # Prepare request headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Prepare request body
    request_body = {
        "query": query

    }

    # Make API request
    response = requests.post(url, headers=headers, data=json.dumps(request_body))

    # Check for errors
    response.raise_for_status()

    # Return response
    search_results = response.json()
    title = search_results["results"][0]["document"]["derivedStructData"]["title"]
    pageNumber = search_results["results"][0]["document"]["derivedStructData"]["extractive_answers"][0]["pageNumber"]
    content = search_results["results"][0]["document"]["derivedStructData"]["extractive_answers"][0]["content"]
    return (f"Filename: {title}, pageNumber: {pageNumber}, searchResult: {content}")



########################################################################################################################
# GET EMPLOYEES FROM BIGQUERY TABLE  
########################################################################################################################

from google.cloud import bigquery
import pandas as pd

def read_bigquery_table(project_id, dataset_id, table_id):
  """Reads a BigQuery table into a Pandas DataFrame.

  Args:
    project_id: The ID of the Google Cloud project.
    dataset_id: The ID of the BigQuery dataset.
    table_id: The ID of the BigQuery table.

  Returns:
    A Pandas DataFrame containing the data from the BigQuery table.
  """

  client = bigquery.Client(project=project_id)
  table_ref = client.dataset(dataset_id).table(table_id)
  table = client.get_table(table_ref) 

  df = client.list_rows(table).to_dataframe()
  return df


def get_employees(): 
    """Retrieves employee data from BigQuery and returns a DataFrame.

    Fetches employee information, including their specializations and licenses,
    from the 'employees' table in the 'ascm' dataset in BigQuery.

    Args:
        project_id: The ID of the Google Cloud project where the BigQuery dataset
                    is located. This should be provided as an argument to the
                    function or set as an environment variable.

    Returns:
        A Pandas DataFrame containing the employee data, including the following
        columns:
        - Employee ID
        - Employee Name
        - License Held
        - License Expiration Date
        - Contact Number
        - Specialization
    """

    df = read_bigquery_table(bq_project_id, dataset_id, table_id)
    data = df.to_dict(orient='records')
    return data 


########################################################################################################################
# GET CALENDARS 
########################################################################################################################

from googleapiclient.discovery import build
import datetime

def get_upcoming_events(calendar_instance):
    """Retrieves upcoming events from a specified public Google Calendar.

    This function fetches events for the next 30 days from a given public 
    Google Calendar. It uses the Google Calendar API with an API key 
    for access.

    Args:
        calendar_instance: A string identifier for the calendar. Valid options are:
                            - 'Jane Doe'

    Returns:
        A list of event objects from the specified calendar, or a string error 
        message if the provided `calendar_instance` is invalid.
    """

    if calendar_instance == 'John Smith':
        calendar_id = johnSmith_gcal_ID

    # elif calendar_instance == 'John Smith':
    #     calendar_id = johnSmith_gcal_ID

    else: 
        return "You did not provide a valid calendar instance."
    

    API_KEY = gcal_api_key
    service = build('calendar', 'v3', developerKey=API_KEY)

    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    time_min = now.isoformat()
    time_max = (now + datetime.timedelta(days=7)).isoformat()

    try:
        events_result = service.events().list(
            calendarId=calendar_id, timeMin=time_min, timeMax=time_max,
            singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items',  [])
    except HttpError as e:
        print(f"Full error: {e}")  # This will show more detailed info.
        if e.resp.status in [400, 401, 403, 404]:
            print(e.resp)
            print(e.uri)
            print(e.content)
        return "HTTP Error occured"

    available_slots = []
    for day in range(7):
        start_time = now + datetime.timedelta(days=day)
        end_time = start_time + datetime.timedelta(hours=23, minutes=59) # Check for slots until the end of each day. 
        for hour in range(9, 18): # Check for slots from 9 AM to 6 PM. You can adjust this range.
            slot_start = start_time.replace(hour=hour, minute=0, second=0, microsecond=0)
            slot_end = slot_start + datetime.timedelta(hours=1)
            
            is_available = True

            for event in events:
                event_start = datetime.datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')).replace('Z', '+00:00'))
                event_end = datetime.datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')).replace('Z', '+00:00'))

                if slot_start < event_end and slot_end > event_start:
                    is_available = False
                    break
            
            if is_available:
                available_slots.append(slot_start.astimezone(pytz.timezone('CET')).strftime('%Y-%m-%d %H:%M'))  # Format the time string as YYYY-MM-DD HH:MM
                if len(available_slots) == 3:
                    return available_slots
    
    if not available_slots:
        return "No available slots found in the next 7 days."

    return available_slots




########################################################################################################################
# GET PREFERENTIAL STATUS 
########################################################################################################################

def get_preference_status() -> pd.DataFrame:
    """Analyzes a CSV file to determine the preferential status of materials.

    Reads a CSV file ('Files/DeterminationOutput.csv'), extracts material details 
    (MATNR, WERKS, GZOLX, PREFE, PREDA, CODE), and determines preferential 
    treatment eligibility for each material in different regions.

    Returns:
        df: A dataframe of the preferential treatment status for each material, 
             including eligibility and region information.
    """
    
    csv_path = "Files/DeterminationOutput.csv"
    df = pd.read_csv(csv_path)

    # Convert the DataFrame to a dictionary
    data = df.to_dict(orient='records')


    return data



########################################################################################################################
# GET BILL OF MATERIALS  
########################################################################################################################
def getBOM() -> pd.DataFrame:
    """Reads a CSV file ('Files/guidebushBOM.csv') and returns a Pandas DataFrame.

    The CSV file contains a bill of materials (BOM) for a product, 
    likely an airplane wing slat, with details on its components, 
    quantities, prices, suppliers, and origins.

    Returns:
        pd.DataFrame: A DataFrame containing the BOM data, with columns such as:
                    'ItemType', 'ItemParent', 'Transformat', 'Transformat id', 
                    'Quantity', 'UnitOfQuant', 'Name', 'Description', 
                    'PriceAmount', 'PriceCurrenc', 'Price Type', 'HsCode', 
                    'Supplierid', 'Origin', 'Sorting', 'Product Mate', 'STLAL', 'MSTAE'.
    """
    csv_path = "Files/guidebushBOM.csv"
    df = pd.read_csv(csv_path)
    data = df.to_dict(orient='records')
    return data




