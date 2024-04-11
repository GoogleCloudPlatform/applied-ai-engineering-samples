# -*- coding: utf-8 -*-


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


from flask import Flask, request, jsonify, render_template
import logging as log
import json
import datetime
import urllib
import re
import time
import textwrap
import pandas as pd
from flask_cors import CORS
from dbconnectors import pgconnector, bqconnector
from embeddings.store_embeddings import add_sql_embedding
from agents import EmbedderAgent, BuildSQLAgent, DebugSQLAgent, ValidateSQLAgent, VisualizeAgent, ResponseAgent

import os
import sys
module_path = os.path.abspath(os.path.join('..'))

import configparser
config = configparser.ConfigParser()
config.read('config.ini')

PROJECT_ID = config['GCP']['PROJECT_ID'] 
PG_SCHEMA = config['PGCLOUDSQL']['PG_SCHEMA']
PG_DATABASE = config['PGCLOUDSQL']['PG_DATABASE']
PG_USER = config['PGCLOUDSQL']['PG_USER']
PG_REGION = config['PGCLOUDSQL']['PG_REGION'] 
PG_INSTANCE = config['PGCLOUDSQL']['PG_INSTANCE'] 
PG_PASSWORD = config['PGCLOUDSQL']['PG_PASSWORD'] 
BQ_DATASET_REGION = config['BIGQUERY']['BQ_DATASET_REGION']
BQ_DATASET_NAME = config['BIGQUERY']['BQ_DATASET_NAME']
BQ_TALK2DATA_DATASET_NAME = config['BIGQUERY']['BQ_TALK2DATA_DATASET_NAME']
BQ_LOG_TABLE_NAME = config['BIGQUERY']['BQ_LOG_TABLE_NAME']
BQ_TABLE_LIST = config['BIGQUERY']['BQ_TABLE_LIST']

embedder = EmbedderAgent('vertex') 

SQLBuilder = BuildSQLAgent('gemini-pro')
SQLChecker = ValidateSQLAgent('gemini-pro')
SQLDebugger = DebugSQLAgent()
Responder = ResponseAgent('gemini-pro')
Visualize = VisualizeAgent ()

num_similar_matches = 10 
similarity_score_matches = 0.3

RUN_DEBUGGER = True 
EXECUTE_FINAL_SQL = True 

app = Flask(__name__) 
cors = CORS(app, resources={r"/*": {"origins": "*"}})



@app.route("/available_databases", methods=["GET"])
def getBDList():
    try:

        # final_sql_bq="""SELECT DISTINCT concat(table_schema, '-bigquery') as table_schema from table_embeddings"""
        # result_bq_df = pgconnector.retrieve_df(final_sql_bq)

#         final_sql="""SELECT
#   DISTINCT CONCAT(table_schema, (CASE
#         WHEN table_schema IN ('HHS_Program_Counts','fda_food') THEN '-bigquery'
#       ELSE
#       '-postgres'
#     END
#       )) AS table_schema
# FROM
#   table_details_embeddings"""
        final_sql="""SELECT
  DISTINCT CONCAT(table_schema,'-',source_type) AS table_schema
FROM
  table_details_embeddings"""
        result = pgconnector.retrieve_df(final_sql)
    
        print(result)
    
        responseDict = { 
                "ResponseCode" : 200, 
                "KnownDB" : result.to_json(orient='records'),
                "Error":""
                } 
        return jsonify(responseDict)
    except Exception as e:
        # util.write_log_entry("Issue was encountered while generating the SQL, please check the logs!" + str(e))
        responseDict = { 
                "ResponseCode" : 500, 
                "KnownDB" : "There was problem finding connecting to the resource. Please retry later!.",
                "Error":"Issue was encountered while generating the SQL, please check the logs!"  + str(e)
                } 
        return jsonify(responseDict)




@app.route("/embed_sql", methods=["POST"])
async def embedSql():
    try:
        envelope = str(request.data.decode('utf-8'))
        envelope=json.loads(envelope)
        user_database=envelope.get('user_database')
        final_sql = envelope.get('generated_sql')
        user_question = envelope.get('user_question')
            
        sql_embedding_df = await add_sql_embedding(user_question, final_sql,user_database)
        responseDict = { 
                   "ResponseCode" : 201, 
                   "Message" : "Example SQL has been accepted for embedding",
                   "Error":""
                   } 
        return jsonify(responseDict)
    except Exception as e:
        # util.write_log_entry("Issue was encountered while generating the SQL, please check the logs!" + str(e))
        responseDict = { 
                   "ResponseCode" : 500, 
                   "KnownDB" : "There was problem finding connecting to the resource. Please retry later!.",
                   "Error":"Issue was encountered while embedding the SQL as example."  + str(e)
                   } 
        return jsonify(responseDict)




@app.route("/run_query", methods=["POST"])
def getSQLResult():
    try:
        print("Extracting the knwon SQLs from the example embeddings.")
        envelope = str(request.data.decode('utf-8'))
        envelope=json.loads(envelope)
        print("request payload: "+ str(envelope))
        user_database = envelope.get('user_database')
        final_sql = envelope.get('generated_sql')

        source_type = get_source_type(user_database)

        if source_type=='bigquery':
            result = bqconnector.retrieve_df(final_sql)
        else:
            result = pgconnector.retrieve_df(final_sql)
        df_len = result[result.columns[0]].count()
        if df_len > 10:
            result = result.head(10)
        print(result.to_json(orient='records'))

        responseDict = { 
                   "ResponseCode" : 200, 
                   "KnownDB" : result.to_json(orient='records'),
                   "Error":""
                   } 
        return jsonify(responseDict)
    except Exception as e:
        # util.write_log_entry("Issue was encountered while running the generated SQL, please check the logs!" + str(e))
        responseDict = { 
                   "ResponseCode" : 500, 
                   "KnownDB" : "",
                   "Error":"Issue was encountered while running the generated SQL, please check the logs!" + str(e)
                   } 
        return jsonify(responseDict)




@app.route("/get_known_sql", methods=["POST"])
def getKnownSQL():
    print("Extracting the known SQLs from the example embeddings.")
    envelope = str(request.data.decode('utf-8'))
    envelope=json.loads(envelope)
    
    user_database = envelope.get('user_database')


    try:

        final_sql="""select distinct
        example_user_question,
        example_generated_sql 
        from example_prompt_sql_embeddings
        where table_schema = '{user_database}' LIMIT 5""".format(user_database=user_database)
        print("Executing SQL: "+ final_sql)
        result = pgconnector.retrieve_df(final_sql)
        print(result.to_json(orient='records'))

        responseDict = { 
                   "ResponseCode" : 200, 
                   "KnownSQL" : result.to_json(orient='records'),
                   "Error":""
                   } 
        return jsonify(responseDict)
    except Exception as e:
        # util.write_log_entry("Issue was encountered while generating the SQL, please check the logs!" + str(e))
        responseDict = { 
                   "ResponseCode" : 500, 
                   "KnownSQL" : "There was problem finding connecting to the resource. Please retry later!.",
                   "Error":"Issue was encountered while generating the SQL, please check the logs!"  + str(e)
                   } 
        return jsonify(responseDict)


def get_source_type(user_database):
    sql=f'''SELECT
  DISTINCT source_type AS table_schema
FROM
  table_details_embeddings where table_schema='{user_database}' '''
    result = pgconnector.retrieve_df(sql)
    
    print("Source Found: "+ str(result.iloc[0, 0]))
    # if user_database in ('HHS_Program_Counts','fda_food'):
    #     return "bigquery"
    # else:
    #     return "cloudsql-pg"
    return str(result.iloc[0, 0])

@app.route("/generate_sql", methods=["POST"])
async def generateSQL():
   AUDIT_TEXT=''
   found_in_vector = 'N'
   process_step=''
   final_sql='Not Generated Yet'
   envelope = str(request.data.decode('utf-8'))
#    print("Here is the request payload " + envelope)
   envelope=json.loads(envelope)
   
   user_question = envelope.get('user_question')
   user_database = envelope.get('user_database')
   corrected_sql = ''
   source_type = get_source_type(user_database)
#    print(source_type)
   AUDIT_TEXT = AUDIT_TEXT + "User Question : " + str(user_question) + "\nUser Database : " + str(user_database) + "\nSource : " + source_type
   
   try:
    embedded_question = embedder.create(user_question)
    process_step = "Get Exact Match"
    exact_sql_history = pgconnector.getExactMatches(user_question)
        
    if exact_sql_history is not None:
        found_in_vector = 'Y'
        final_sql = exact_sql_history
        invalid_response = False
        AUDIT_TEXT = AUDIT_TEXT + "\nExact match has been found"

    else:
        AUDIT_TEXT = AUDIT_TEXT + "\nNo exact match found looking for similar entries and schema"
        # No exact match found. Proceed looking for similar entries in db 
        process_step = "Get Similar Match"
        similar_sql = await pgconnector.getSimilarMatches('example',user_database, embedded_question, num_similar_matches, similarity_score_matches)

        process_step = "Get Table and Column Schema"
        # Retrieve matching tables and columns 
        tables_schema = await pgconnector.getSimilarMatches('table',user_database, embedded_question, num_similar_matches, similarity_score_matches)
        tables_detailed_schema = await pgconnector.getSimilarMatches('column',user_database, embedded_question, num_similar_matches, similarity_score_matches)

        AUDIT_TEXT = AUDIT_TEXT + "\n Retrived Similar Entries, Table Schema and Column Schema"
        # If similar table and column schemas found: 
        if len(tables_schema.replace('Schema(values):','').replace(' ','')) > 0 or len(tables_detailed_schema.replace('Column name(type):','').replace(' ','')) > 0 :

            # GENERATE SQL
            process_step = "Build SQL"
            generated_sql = SQLBuilder.build_sql(source_type,user_question,tables_schema,tables_detailed_schema,similar_sql)
            # print(generated_sql)
            final_sql=generated_sql
            AUDIT_TEXT = AUDIT_TEXT + "\n Generated SQL : " + str(generated_sql)

            if 'unrelated_answer' in generated_sql :
                invalid_response=True
                AUDIT_TEXT = AUDIT_TEXT + "\n Unrelated Question Asked"

            # If agent assessment is valid, proceed with checks  
            else:
                invalid_response=False

                AUDIT_TEXT = AUDIT_TEXT + "\nRunning Debugger \n"
                process_step = "Run Debugger"
                if RUN_DEBUGGER:
                    generated_sql, invalid_response, AUDIT_TEXT = SQLDebugger.start_debugger(source_type,generated_sql, user_question, SQLChecker, tables_schema, tables_detailed_schema,AUDIT_TEXT, similar_sql) 


                    # generated_sql, invalid_response, AUDIT_TEXT = SQLDebugger.start_debugger(source_type,user_database,generated_sql, user_question, SQLChecker, pgconnector, tables_schema, tables_detailed_schema,AUDIT_TEXT, similar_sql) 

                final_sql=generated_sql
                # print(AUDIT_TEXT)
                # print(generated_sql)

                AUDIT_TEXT = AUDIT_TEXT + "\nFinal SQL after Debugger : " +str(final_sql)


        # No matching table found 
        else:
            invalid_response=True
            print('No tables found in Vector ...')
            AUDIT_TEXT = AUDIT_TEXT + "\n No tables have been found in the Vector DB..."

    if not invalid_response:
        responseDict = { 
                   "ResponseCode" : 200, 
                   "GeneratedSQL" : final_sql,
                   "Error":""
                   }          
        
        # return jsonify(responseDict)

    else:  # Do not execute final SQL

        print("Not executing final SQL as it is invalid, please debug!")
        response = "I am sorry, I could not come up with a valid SQL."
        _resp = Responder.run(user_question, response)
        # print(_resp)
        AUDIT_TEXT = AUDIT_TEXT + "\n Model says " + str(_resp) 

    
        responseDict = { 
                   "ResponseCode" : 200, 
                   "GeneratedSQL" : _resp,
                   "Error":""
                   }
    bqconnector.make_audit_entry(source_type, user_database, "gemini-pro", user_question, final_sql, found_in_vector, "", process_step, "", AUDIT_TEXT)
    return jsonify(responseDict)

   except Exception as e:
    # util.write_log_entry("Issue was encountered while generating the SQL, please check the logs!" + str(e))
    responseDict = { 
                   "ResponseCode" : 500, 
                   "GeneratedHQL" : "",
                   "Error":"Issue was encountered while generating the SQL, please check the logs!"  + str(e)
                   } 
    bqconnector.make_audit_entry(source_type, user_database, "gemini-pro", user_question, final_sql, found_in_vector, "", process_step, str(e), AUDIT_TEXT)
    return jsonify(responseDict)

@app.route("/generate_viz", methods=["POST"])
async def generateViz():
    envelope = str(request.data.decode('utf-8'))
    # print("Here is the request payload " + envelope)
    envelope=json.loads(envelope)

    user_question = envelope.get('user_question')
    generated_sql = envelope.get('generated_sql')
    sql_results = envelope.get('sql_results')

    chart_js=''

    try:
        chart_js = Visualize.generate_charts(user_question,generated_sql,sql_results)
        responseDict = { 
        "ResponseCode" : 200, 
        "GeneratedChartjs" : chart_js,
        "Error":""
        }
        return jsonify(responseDict)

    except Exception as e:
        # util.write_log_entry("Cannot generate the Visualization!!!, please check the logs!" + str(e))
        responseDict = { 
                "ResponseCode" : 500, 
                "GeneratedHQL" : "",
                "Error":"Issue was encountered while generating the Google Chart, please check the logs!"  + str(e)
                } 
        return jsonify(responseDict)

     

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))