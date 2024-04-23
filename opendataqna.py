from google.api_core.exceptions import NotFound
from google.cloud import aiplatform
import pandas as pd
import vertexai
import asyncio


from agents import EmbedderAgent, BuildSQLAgent, DebugSQLAgent, ValidateSQLAgent, ResponseAgent
from utilities import PROJECT_ID, PG_SCHEMA, PG_REGION
from dbconnectors import pgconnector



embedder = EmbedderAgent('vertex') 

vertexai.init(project=PROJECT_ID, location=PG_REGION)
aiplatform.init(project=PROJECT_ID, location=PG_REGION)



num_similar_matches = 10 
similarity_score_matches = 0.3

RUN_DEBUGGER = True 
EXECUTE_FINAL_SQL = True 

import os
import sys
module_path = os.path.abspath(os.path.join('..'))

import configparser
config = configparser.ConfigParser()
config.read(module_path+'/config.ini')

PROJECT_ID = config['GCP']['PROJECT_ID']
DATA_SOURCE = config['CONFIG']['DATA_SOURCE']
VECTOR_STORE = config['CONFIG']['VECTOR_STORE']
PG_SCHEMA = config['PGCLOUDSQL']['PG_SCHEMA']
PG_DATABASE = config['PGCLOUDSQL']['PG_DATABASE']
PG_USER = config['PGCLOUDSQL']['PG_USER']
PG_REGION = config['PGCLOUDSQL']['PG_REGION'] 
PG_INSTANCE = config['PGCLOUDSQL']['PG_INSTANCE'] 
PG_PASSWORD = config['PGCLOUDSQL']['PG_PASSWORD']
BQ_OPENDATAQNA_DATASET_NAME = config['BIGQUERY']['BQ_OPENDATAQNA_DATASET_NAME']
BQ_LOG_TABLE_NAME = config['BIGQUERY']['BQ_LOG_TABLE_NAME'] 
BQ_DATASET_REGION = config['BIGQUERY']['BQ_DATASET_REGION']
BQ_DATASET_NAME = config['BIGQUERY']['BQ_DATASET_NAME']
BQ_TABLE_LIST = config['BIGQUERY']['BQ_TABLE_LIST']


# Fetch the USER_DATABASE based on data source
from dbconnectors import pgconnector, bqconnector
if DATA_SOURCE=='bigquery':
    USER_DATABASE=BQ_DATASET_NAME 
    src_connector = bqconnector
else: 
    USER_DATABASE=PG_SCHEMA
    src_connector = pgconnector

print("Source selected is : "+ str(DATA_SOURCE) + "\nSchema or Dataset Name is : "+ str(USER_DATABASE))
print("Vector Store selected is : "+ str(VECTOR_STORE))


# Set the vector store paramaters
if VECTOR_STORE=='bigquery-vector':
    instance_name=None
    database_name=BQ_OPENDATAQNA_DATASET_NAME
    schema=USER_DATABASE
    database_user=None
    database_password=None
    region=BQ_DATASET_REGION
    vector_connector = bqconnector
    call_await = False

else:
    instance_name=PG_INSTANCE
    database_name=PG_DATABASE
    schema=USER_DATABASE
    database_user=PG_USER
    database_password=PG_PASSWORD
    region=PG_REGION
    vector_connector = pgconnector
    call_await=True


num_table_matches = 5
num_column_matches = 10
similarity_threshold = 0.3
num_sql_matches=3


RUN_DEBUGGER = True 
EXECUTE_FINAL_SQL = True 

from google.api_core.exceptions import NotFound
from google.cloud import aiplatform
import vertexai

from agents import EmbedderAgent, BuildSQLAgent, DebugSQLAgent, ValidateSQLAgent, ResponseAgent, VisualizeAgent


embedder = EmbedderAgent('vertex') 

SQLBuilder = BuildSQLAgent('gemini-pro')
SQLChecker = ValidateSQLAgent('gemini-pro')
SQLDebugger = DebugSQLAgent('gemini-pro')
Responder = ResponseAgent('gemini-pro')
Visualize = VisualizeAgent ()

found_in_vector = 'N'
final_sql='Not Generated Yet'

vertexai.init(project=PROJECT_ID, location=region)
aiplatform.init(project=PROJECT_ID, location=region)

print("\033[1mData Source :- "+ DATA_SOURCE)
print("Vector Store :- "+ VECTOR_STORE)
print("Schema :- "+USER_DATABASE)
    
# Suggested question for 'fda_food' dataset: "What are the top 5 cities with highest recalls?"
#  Suggested question for 'google_dei' dataset: "How many asian men were part of the leadership workforce in 2021?"

prompt_for_question = "Please enter your question for source :" + DATA_SOURCE + " and database : " + USER_DATABASE
user_question = input(prompt_for_question) #Uncomment if you want to ask question yourself
# user_question = '' # Or Enter Question here

print("Asked Question :- "+user_question)




async def generate_sql(user_question):

  # SQLBuilder = BuildSQLAgent('gemini-pro')
  # SQLChecker = ValidateSQLAgent('gemini-pro')
  # SQLDebugger = DebugSQLAgent()
  # Responder = ResponseAgent('gemini-pro')

  # # Fetch the embedding of the user's input question 
  # embedded_question = embedder.create(user_question)

  # # Look for exact matches in known questions 
  # exact_sql_history = pgconnector.getExactMatches(user_question) 

  # if exact_sql_history is not None: 
  #   final_sql = exact_sql_history


  # else:
  #   # No exact match found. Proceed looking for similar entries in db 
  #   similar_sql = await pgconnector.getSimilarMatches('example', PG_SCHEMA, embedded_question, num_similar_matches, similarity_score_matches)

  #   # Retrieve matching tables and columns 
  #   tables_schema = await pgconnector.getSimilarMatches('table', PG_SCHEMA, embedded_question, num_similar_matches, similarity_score_matches)
  #   tables_detailed_schema = await pgconnector.getSimilarMatches('column', PG_SCHEMA, embedded_question, num_similar_matches, similarity_score_matches)

  #   # If similar table and column schemas found: 
  #   if len(tables_schema.replace('Schema(values):','').replace(' ','')) > 0 or len(tables_detailed_schema.replace('Column name(type):','').replace(' ','')) > 0 :

  #     # GENERATE SQL
  #     generated_sql = SQLBuilder.build_postgresql(user_question,tables_schema,tables_detailed_schema,similar_sql)

  #     if 'unrelated_answer' in generated_sql :
  #       invalid_response=True

  #     # If agent assessment is valid, proceed with checks  
  #     else:
  #       invalid_response=False

  #       if RUN_DEBUGGER: 
  #         generated_sql, invalid_response = SQLDebugger.start_debugger(generated_sql, user_question, SQLChecker, pgconnector, tables_schema, tables_detailed_schema, similar_sql) 

  #       final_sql=generated_sql


  #   # No matching table found 
  #   else:
  #     invalid_response=True
  #     print('No tables found in Vector ...')


  #   if not invalid_response:
  #     try: 
  #       if EXECUTE_FINAL_SQL is True:
  #               final_exec_result_df=pgconnector.retrieve_df(final_sql.replace("```sql","").replace("```","").replace("EXPLAIN ANALYZE ",""))
  #               print('\n Question: ' + user_question + '\n')
  #               print('\n Final SQL Execution Result: \n')
  #               print(final_exec_result_df)
  #               response = final_exec_result_df
  #               print(Responder.run(user_question, response))


  #       else:  # Do not execute final SQL
  #               print("Not executing final SQL since EXECUTE_FINAL_SQL variable is False\n ")
  #               response = "Please enable the Execution of the final SQL so I can provide an answer"
  #               print(Responder.run(user_question, response))

  #     except Exception as e: 
  #       print(f"An error occured. Aborting... Error Message: {e}")
  #   else:  # Do not execute final SQL
  #       print("Not executing final SQL as it is invalid, please debug!")
  #       response = "I am sorry, I could not come up with a valid SQL."
  #       print(Responder.run(user_question, response))

  # Fetch the embedding of the user's input question 
  embedded_question = embedder.create(user_question)

  # Reset AUDIT_TEXT
  AUDIT_TEXT = ''

  AUDIT_TEXT = AUDIT_TEXT + "\nUser Question : " + str(user_question) + "\nUser Database : " + str(USER_DATABASE)
  process_step = "\n\nGet Exact Match: "
  # Look for exact matches in known questions 
  exact_sql_history = vector_connector.getExactMatches(user_question) 

  if exact_sql_history is not None:
      found_in_vector = 'Y' 
      final_sql = exact_sql_history
      invalid_response = False
      AUDIT_TEXT = AUDIT_TEXT + "\nExact match has been found" 


  else:
      # No exact match found. Proceed looking for similar entries in db 
      AUDIT_TEXT = AUDIT_TEXT +  process_step + "\nNo exact match found looking for similar entries and schema"
      process_step = "\n\nGet Similar Match: "
      if call_await:
          similar_sql = await vector_connector.getSimilarMatches('example', USER_DATABASE, embedded_question, num_sql_matches, similarity_threshold)
      else:
          similar_sql = vector_connector.getSimilarMatches('example', USER_DATABASE, embedded_question, num_sql_matches, similarity_threshold)

      process_step = "\n\nGet Table and Column Schema: "
      # Retrieve matching tables and columns
      if call_await: 
          table_matches =  await vector_connector.getSimilarMatches('table', USER_DATABASE, embedded_question, num_table_matches, similarity_threshold)
          column_matches =  await vector_connector.getSimilarMatches('column', USER_DATABASE, embedded_question, num_column_matches, similarity_threshold)
      else:
          table_matches =  vector_connector.getSimilarMatches('table', USER_DATABASE, embedded_question, num_table_matches, similarity_threshold)
          column_matches =  vector_connector.getSimilarMatches('column', USER_DATABASE, embedded_question, num_column_matches, similarity_threshold)

      AUDIT_TEXT = AUDIT_TEXT +  process_step + "\nRetrieved Similar Entries, Table Schema and Column Schema: \n" + '\nRetrieved Tables: \n' + str(table_matches) + '\n\nRetrieved Columns: \n' + str(column_matches) + '\n\nRetrieved Known Good Queries: \n' + str(similar_sql)
      # If similar table and column schemas found: 
      if len(table_matches.replace('Schema(values):','').replace(' ','')) > 0 or len(column_matches.replace('Column name(type):','').replace(' ','')) > 0 :

          # GENERATE SQL
          process_step = "\n\nBuild SQL: "
          generated_sql = SQLBuilder.build_sql(DATA_SOURCE,user_question,table_matches,column_matches,similar_sql)
          final_sql=generated_sql
          AUDIT_TEXT = AUDIT_TEXT + process_step +  "\nGenerated SQL: " + str(generated_sql)
          
          if 'unrelated_answer' in generated_sql :
              invalid_response=True

          # If agent assessment is valid, proceed with checks  
          else:
              invalid_response=False

              if RUN_DEBUGGER: 
                  generated_sql, invalid_response, AUDIT_TEXT = SQLDebugger.start_debugger(DATA_SOURCE, generated_sql, user_question, SQLChecker, table_matches, column_matches, AUDIT_TEXT, similar_sql) 
                  # AUDIT_TEXT = AUDIT_TEXT + '\n Feedback from Debugger: \n' + feedback_text

              final_sql=generated_sql
              AUDIT_TEXT = AUDIT_TEXT + "\nFinal SQL after Debugger: \n" +str(final_sql)


      # No matching table found 
      else:
          invalid_response=True
          print('No tables found in Vector ...')
          AUDIT_TEXT = AUDIT_TEXT + "\n No tables have been found in the Vector DB..."

  print(f'\n\n AUDIT_TEXT: \n {AUDIT_TEXT}')

  return generated_sql, AUDIT_TEXT



# asyncio.run(main('How many asian men were part of the leadership workforce in 2021?'))
# # Which city has maximum number of sales? 
# #How many asian men were part of the leadership workforce?



