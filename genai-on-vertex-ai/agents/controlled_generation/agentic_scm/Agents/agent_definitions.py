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


from Agents import  Agent


def get_InspectorAgent(model):
    """
    "This inspector agent analyzes images of aircraft parts to classify whether the part displayed is broken or not. 
    For this, the agent expects an image_path in string format."
    """ 

    response_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "understanding": {
                    "type": "string",
                },
                "chain_of_thought": {
                    "type": "string",
                },
                "response": {
                    "type": "string",
                },
                "function": {
                    "type": "string",
                },
                "function_name": {
                    "type": "string",
                },
                "function_args": {
                    "type": "string",
                },
                "execute_function": {
                    "type": "string",
                    "enum": [
                        "True",
                        "False"
                    ],
                }, 
                "aircraft_model": {
                    "type": "string"
                }
            },
            "required": ["understanding", "chain_of_thought", "response", "function", "function_name", "function_args"],
        },
    }




    PERSONA = "Inspector Agent"


    INSTRUCTIONS = """
                    You are an inspector agent that analyzes images of aircraft parts to determine whether they are broken or not. 
                    Use the tools at your disposal to run the analysis for an incoming image_path string.
                    Populate the "aircraft_model" field in your response with the Aircraft Model mentioned in the image filename. 
                    Mention the aircraft model in your overall response.  
                """


    tools = """def analyze_image(image_path: str):
                    \"\"\"Analyzes an image to detect damage in insulator parts.

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
                    \"\"\"
    """



    # Create an instance of the Agent class
    agent = Agent(model, response_schema, PERSONA, INSTRUCTIONS, tools)

    return agent 


def get_DocumentAgent(model):
    """
    "This document agent queries different document bases to answer an incoming question."
    """ 

    response_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "understanding": {
                    "type": "string",
                },
                "chain_of_thought": {
                    "type": "string",
                },
                "response": {
                    "type": "string",
                },
                "function": {
                    "type": "string",
                },
                "function_name": {
                    "type": "string",
                },
                "function_args": {
                    "type": "string",
                },
                "execute_function": {
                    "type": "string",
                    "enum": [
                        "True",
                        "False"
                    ],
                }, 
            },
            "required": ["understanding", "chain_of_thought", "response", "function", "function_name", "function_args"],
        },
    }




    PERSONA = "Document Agent"


    INSTRUCTIONS = """
                    You are a document agent that answers user questions and retrieves requested information.
                    Avoid just returning the document and page number. If possible, summarize the contents returned to you back to the user.
                """


    tools = """def search_manuals(query):
                \"\"\"
                Performs a search query to retrieve information for a question on aircraft manuals. 

                Args:
                    query: The search query text.

                Returns:
                    str: string with filename in which the info was found, the page number, and the answer to the question.
                \"\"\"
            def search_safety_reports(query):
                \"\"\"
                Performs a search query to retrieve information for a question on aircraft annual safety reports. 

                Args:
                    query: The search query text.

                Returns:
                    str: string with filename in which the info was found, the page number, and the answer to the question.
                \"\"\"
    """



    # Create an instance of the Agent class
    agent = Agent(model, response_schema, PERSONA, INSTRUCTIONS, tools)

    return agent 



def get_ScheduleAgent(model):
    """
    This Schedule Agent can retrieve employees and their licences, as well as employee and workshop availability. 
    """ 

    response_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "understanding": {
                    "type": "string",
                },
                "chain_of_thought": {
                    "type": "string",
                },
                "response": {
                    "type": "string",
                },
                "function": {
                    "type": "string",
                },
                "function_name": {
                    "type": "string",
                },
                "function_args": {
                    "type": "string",
                },
                "execute_function": {
                    "type": "string",
                    "enum": [
                        "True",
                        "False"
                    ],
                }, 
            },
            "required": ["understanding", "chain_of_thought", "response", "function", "function_name", "function_args"],
        },
    }




    PERSONA = "Scheduler Agent"


    INSTRUCTIONS = """
                    You are a scheduler agent. Your task is to find licensed employees by their names that can support with structural repairs, engine maintenance, or annual inspection, depending on what is asked by the user. 
                    - do not refer to the employees by their ID. instead, use their names.
                    - execute the tools one after the other, until you can provide all the necessary information at once. 
                    - Once you know the availability of the employee and the workshop, provide the next 3 slots where both the employee and the workshop are free.  
                    - If the user writes "I need to schedule for Engine Maintenance." put the prompt "I need to schedule for Engine Maintenance." into the agents_prompt field.
                    - It is your job to provide the exact dates back to the user. 
                    
                    Use the tools available to you to: 
                    1. Find the 'Employee Name' with the proper license by checking the 'Specialization' to do the task the user asked for. If there are multiple employees that meet the requirement, provide their names to the user and let them know you are proceeding with one of them (select at random).
                    2. Retrieve the availability of this employee by using their name, e.g. Jane Doe.  
                    3. Provide the dates for the next three available 1 hour slots for the employee in the format DD.MM.YYYY HH:MM. 

                    It is of UPMOST importance that you set 'execute_function' to FALSE once you are done calling tools. 

                """


    tools = """def get_employees(): 
                    \"\"\"Retrieves employee data from BigQuery and returns a DataFrame.

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
                    \"\"\"
                def get_upcoming_events(calendar_instance):
                    \"\"\"Retrieves upcoming events from a specified public Google Calendar.

                    This function fetches events for the next 30 days from a given public 
                    Google Calendar. It uses the Google Calendar API with an API key 
                    for access.

                    Args:
                        calendar_instance: A string identifier for the calendar. Valid options are:
                                            - 'John Smith'

                    Returns:
                        A list of event objects from the specified calendar, or a string error 
                        message if the provided `calendar_instance` is invalid.
                    \"\"\"
    """



    # Create an instance of the Agent class
    agent = Agent(model, response_schema, PERSONA, INSTRUCTIONS, tools)

    return agent 





def get_CustomsAgent(model):
    """
    This Customs Agent analyzes preferential treatment status for items based on CSV API response.
    It extracts details such as Material Number (MATNR), Plant (WERKS), Preference Eligibility (PREFE), Region, and the expiry date.
    The agent can check for a product at the supplier side, provide it's product ID, quantity left, price, and origin. 
    The agent can further check the preferential treatment status for certain items. 
    """

    response_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "understanding": {
                    "type": "string",
                },
                "chain_of_thought": {
                    "type": "string",
                },
                "response": {
                    "type": "string",
                },
                "function": {
                    "type": "string",
                },
                "function_name": {
                    "type": "string",
                },
                "function_args": {
                    "type": "string",
                },
                "execute_function": {
                    "type": "string",
                    "enum": [
                        "True",
                        "False"
                    ],
                },
            },
            "required": ["understanding", "chain_of_thought", "response", "function", "function_name", "function_args"],
        },
    }

    PERSONA = "Customs Agent"

    INSTRUCTIONS = """
                    You are a customs agent that helps to analyze the preferential status of materials for international trade.
                    Your job is to first find the material number for a given product, then interpret the information from a CSV response, such as Material Number (MATNR),
                    Plant (WERKS), Preference Eligibility (PREFE), Region, and Preference Date (PREDA).
                    - Figure out the part number for a given product by checking the 'ID' field from the returned dataframe response.
                    - Identify if the material for a part number is eligible for preferential treatment in any specific region (e.g., EU).
                    - Summarize which regions have preference eligibility and which do not, based on the data.
                    - Clearly state the eligibility status and provide the validity period for each region.

                    If a user is asking solely about the quantity, origin, or price of a product, you do not need to provide the preferential status details.
                """

    tools = """def getBOM() -> pd.DataFrame:
                    \"\"\"Reads a CSV file ('Files/guidebushBOM.csv') and returns a Pandas DataFrame.

                    The CSV file contains a bill of materials (BOM) for a product, 
                    likely an airplane wing slat, with details on its components, 
                    quantities, prices, suppliers, and origins.

                    Returns:
                        pd.DataFrame: A DataFrame containing the BOM data, with columns such as:
                                    'ItemType', 'ItemParent', 'Transformat', 'Transformat id', 
                                    'Quantity', 'UnitOfQuant', 'Name', 'Description', 
                                    'PriceAmount', 'PriceCurrenc', 'Price Type', 'HsCode', 
                                    'Supplierid', 'Origin', 'Sorting', 'Product Mate', 'STLAL', 'MSTAE'.
                    \"\"\"

                def get_preference_status() -> pd.DataFrame:
                    \"\"\"Analyzes a CSV file to determine the preferential status of materials.

                    Reads a CSV file ('Files/DeterminationOutput.csv'), extracts material details 
                    (MATNR, WERKS, GZOLX, PREFE, PREDA, CODE), and determines preferential 
                    treatment eligibility for each material in different regions.

                    Returns:
                        df: A dataframe of the preferential treatment status for each material, 
                            including eligibility and region information.
                    \"\"\"
    """

    # Create an instance of the Agent class
    agent = Agent(model, response_schema, PERSONA, INSTRUCTIONS, tools)

    return agent