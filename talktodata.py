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




async def main(user_question):

  SQLBuilder = BuildSQLAgent('gemini-pro')
  SQLChecker = ValidateSQLAgent('gemini-pro')
  SQLDebugger = DebugSQLAgent()
  Responder = ResponseAgent('gemini-pro')

  # Fetch the embedding of the user's input question 
  embedded_question = embedder.create(user_question)

  # Look for exact matches in known questions 
  exact_sql_history = pgconnector.getExactMatches(user_question) 

  if exact_sql_history is not None: 
    final_sql = exact_sql_history


  else:
    # No exact match found. Proceed looking for similar entries in db 
    similar_sql = await pgconnector.getSimilarMatches('example', PG_SCHEMA, embedded_question, num_similar_matches, similarity_score_matches)

    # Retrieve matching tables and columns 
    tables_schema = await pgconnector.getSimilarMatches('table', PG_SCHEMA, embedded_question, num_similar_matches, similarity_score_matches)
    tables_detailed_schema = await pgconnector.getSimilarMatches('column', PG_SCHEMA, embedded_question, num_similar_matches, similarity_score_matches)

    # If similar table and column schemas found: 
    if len(tables_schema.replace('Schema(values):','').replace(' ','')) > 0 or len(tables_detailed_schema.replace('Column name(type):','').replace(' ','')) > 0 :

      # GENERATE SQL
      generated_sql = SQLBuilder.build_postgresql(user_question,tables_schema,tables_detailed_schema,similar_sql)

      if 'unrelated_answer' in generated_sql :
        invalid_response=True

      # If agent assessment is valid, proceed with checks  
      else:
        invalid_response=False

        if RUN_DEBUGGER: 
          generated_sql, invalid_response = SQLDebugger.start_debugger(generated_sql, user_question, SQLChecker, pgconnector, tables_schema, tables_detailed_schema, similar_sql) 

        final_sql=generated_sql


    # No matching table found 
    else:
      invalid_response=True
      print('No tables found in Vector ...')


    if not invalid_response:
      try: 
        if EXECUTE_FINAL_SQL is True:
                final_exec_result_df=pgconnector.retrieve_df(final_sql.replace("```sql","").replace("```","").replace("EXPLAIN ANALYZE ",""))
                print('\n Question: ' + user_question + '\n')
                print('\n Final SQL Execution Result: \n')
                print(final_exec_result_df)
                response = final_exec_result_df
                print(Responder.run(user_question, response))


        else:  # Do not execute final SQL
                print("Not executing final SQL since EXECUTE_FINAL_SQL variable is False\n ")
                response = "Please enable the Execution of the final SQL so I can provide an answer"
                print(Responder.run(user_question, response))

      except Exception as e: 
        print(f"An error occured. Aborting... Error Message: {e}")
    else:  # Do not execute final SQL
        print("Not executing final SQL as it is invalid, please debug!")
        response = "I am sorry, I could not come up with a valid SQL."
        print(Responder.run(user_question, response))



# asyncio.run(main('How many asian men were part of the leadership workforce in 2021?'))
# # Which city has maximum number of sales? 
# #How many asian men were part of the leadership workforce?



