
### gcloud auth application-default login
from vertexai.preview.language_models import CodeGenerationModel
from vertexai.preview.language_models import CodeChatModel
from vertexai.preview.language_models import TextGenerationModel
from vertexai.preview.generative_models import (
    GenerationConfig,
    GenerativeModel,
    Image,
    Part,
)
from google.cloud import bigquery

# LOAD CONFIG DATA 
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
TABLE_ID = config['CREDENTIALS']['TABLE_ID']
PROJECT_ID = config['CREDENTIALS']['PROJECT_ID']
PROJECT_LOCATION = config['CREDENTIALS']['PROJECT_LOCATION']

# Initialize Vertex AI
import vertexai
vertexai.init(project=PROJECT_ID, location=PROJECT_LOCATION)


def nl2sql(query, TABLE_ID, TABLE_SCHEMA, MODEL): 
    if MODEL == "gemini-pro": 
        model = GenerativeModel(MODEL)

        output = model.generate_content(
        f"""Generate an SQL query for the following question: 
        '{query}'
        
        This is the table id: {TABLE_ID}
        The target database has the following schema: {str(TABLE_SCHEMA)}. 
        us_gender can be either "men" or "women". 

        Your output has to start with the word SELECT
        """, stream=False)

    else:     
        model = TextGenerationModel.from_pretrained(MODEL)

        output = model.predict(
        f"""Generate an SQL query for the following question: 
        '{query}'
        
        This is the table id: {TABLE_ID}
        The target database has the following schema: {str(TABLE_SCHEMA)}. 
        us_gender can be either "men" or "women". 

        Directly start with SELECT 
        """
            # The following are optional parameters:
            #max_output_tokens=1024,
            #temperature=0,
            #top_p=1,
            #top_k=5,
        )

    return(output.text.replace("`", ""))


def bq_sql_response(query, MODEL, TABLE_ID=TABLE_ID): 
    # Construct a BigQuery client object.
    client = bigquery.Client(project=PROJECT_ID)
    table = client.get_table(TABLE_ID)
    TABLE_SCHEMA = table.schema

    # text = output.text.replace("`", "")

    sql_query = nl2sql(query, TABLE_ID, TABLE_SCHEMA, MODEL)

    # Gemini does not follow the prompt properly. We need to clean the output
    sql_query = sql_query[sql_query.find('SELECT'):]

    query_job = client.query(sql_query)  # Make an API request.
    result = list() 

    for row in query_job:
        for value in row: 
            result.append(value)

    result_string = str(result)

    return result_string



def generate_sql_answer(query, MODEL): 
    sql_response = bq_sql_response(query, MODEL)

    if MODEL == "gemini-pro": 
        model = GenerativeModel(MODEL)

        output = model.generate_content(
        f"""
        CONTEXT: 
        The following has been the prompt for the previous session: 

        '{query}'
        The SQL Query returned the following information: {sql_response}.

        TASK: Formulate a full-sentence-answer given the SQL Query result to the following prompt: '{query}'
        Hint: if the question asks for a percentage, make sure to multiply the result with 100. 
        Percentages CAN NOT start with 0.x. if this is the case, you need to multiply with 100. 
        """, stream=False)



    else: 
        model = TextGenerationModel.from_pretrained(MODEL)

        output = model.predict(
        f"""
        CONTEXT: 
        The following has been the prompt for the previous session: 

        '{query}'
        The SQL Query returned the following information: {sql_response}.

        TASK: Formulate a full-sentence-answer given the SQL Query result to the following prompt: '{query}'
        Hint: if the question asks for a percentage, make sure to multiply the result with 100. 
        """, max_output_tokens=1024, temperature=0
            # The following are optional parameters:
            #max_output_tokens=1024,
            #temperature=0,
            #top_p=1,
            #top_k=5,
    )

    # print(output.text)
    return output.text 



def generate_dei_paragraph(prompt, MODEL): 

    # prompt = """
    # You are an ESG consulter that's writing the diversity section of the 2023 ESG report.
    # With the data provided to you, write a short abstract with roughly 500 words about Googles Diversity mission, the stats in 2023
    # and the differences compared to the previous year. Include the representation of women in different roles as well as the representation 
    # of underrepresented groups.
    # """

    # Retrieve the DEI table content in big query 
    query = "Retrieve all"
    response = bq_sql_response(query, MODEL)


    if MODEL == "gemini-pro": 
        model = GenerativeModel(MODEL)

        output = model.generate_content(
        f"""
        CONTEXT: 
        The following has been the prompt for the previous session: 

        '{query}'
        The SQL Query returned the following information: {response}.

        TASK: Formulate a full-sentence-answer given the SQL Query result to the following prompt: '{prompt}'
        Hint: if the question asks for a percentage, make sure to multiply the result with 100. 
        """, stream=False)

    else: 
        model = TextGenerationModel.from_pretrained(MODEL)

        output = model.predict(
        f"""
        CONTEXT: 
        The following has been the prompt for the previous session: 

        '{query}'
        The SQL Query returned the following information: {response}.

        TASK: Formulate a full-sentence-answer given the SQL Query result to the following prompt: '{prompt}'
        Hint: if the question asks for a percentage, make sure to multiply the result with 100. 
        """, max_output_tokens=1024, temperature=0
            # The following are optional parameters:
            #max_output_tokens=1024,
            #temperature=0,
            #top_p=1,
            #top_k=5,
        )

    return output.text 

prompt = """
     You are an ESG consulter that's writing the diversity section of the 2023 ESG report.
     With the data provided to you, write a short abstract with roughly 500 words about Googles Diversity mission, the stats in 2023
     and the differences compared to the previous year. Include the representation of women in different roles as well as the representation 
     of underrepresented groups.
 """


