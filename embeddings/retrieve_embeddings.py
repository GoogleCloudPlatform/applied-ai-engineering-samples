import re
import io
import sys 
import pandas as pd
from dbconnectors import pgconnector,bqconnector
from agents import EmbedderAgent, ResponseAgent
from utilities import PG_SCHEMA, PROJECT_ID, PG_INSTANCE, PG_DATABASE, PG_USER, PG_PASSWORD, PG_REGION, BQ_OPENDATAQNA_DATASET_NAME, DATA_SOURCE, BQ_REGION

embedder = EmbedderAgent('vertex')
responder = ResponseAgent('gemini-1.0-pro')

def get_embedding_chunked(textinput, batch_size): 
    for i in range(0, len(textinput), batch_size):
        request = [x["content"] for x in textinput[i : i + batch_size]]
        response = embedder.create(request) # Vertex Textmodel Embedder 

        # Store the retrieved vector embeddings for each chunk back.
        for x, e in zip(textinput[i : i + batch_size], response):
            x["embedding"] = e

    # Store the generated embeddings in a pandas dataframe.
    out_df = pd.DataFrame(textinput)
    return out_df


def retrieve_embeddings(SOURCE, SCHEMA="public"): 
    """ Augment all the DB schema blocks to create document for embedding """

    if SOURCE == "cloudsql-pg":
    
        table_schema_sql = pgconnector.return_table_schema_sql(SCHEMA)
        table_desc_df = pgconnector.retrieve_df(table_schema_sql)
        
        column_schema_sql = pgconnector.return_column_schema_sql(SCHEMA)
        column_name_df = pgconnector.retrieve_df(column_schema_sql)
        

         #GENERATE MISSING DESCRIPTIONS
        table_desc_df,column_name_df= responder.generate_missing_descriptions(SOURCE,table_desc_df,column_name_df)
       
        ### TABLE EMBEDDING ###
        """
        This SQL returns a df containing the cols table_schema, table_name, table_description, table_columns (with cols in the table)
        for the schema specified above, e.g. 'retail'
        """
        table_details_chunked = []

        for index_aug, row_aug in table_desc_df.iterrows():

            cur_table_name = str(row_aug['table_name'])
            cur_table_schema = str(row_aug['table_schema'])
            curr_col_names = str(row_aug['table_columns'])
            curr_tbl_desc = str(row_aug['table_description'])


            table_detailed_description=f"""
            Table Name: {cur_table_name} |
            Schema Name: {cur_table_schema} |
            Table Description - {curr_tbl_desc}) | 
            Columns List: [{curr_col_names}]"""

            r = {"table_schema": cur_table_schema,"table_name": cur_table_name,"content": table_detailed_description}
            table_details_chunked.append(r)

        table_details_embeddings = get_embedding_chunked(table_details_chunked, 10000)


        ### COLUMN EMBEDDING ###
        """
        This SQL returns a df containing the cols table_schema, table_name, column_name, data_type, column_description, table_description, primary_key, column_constraints
        for the schema specified above, e.g. 'retail'
        """
        
        column_details_chunked = []

        for index_aug, row_aug in column_name_df.iterrows():

            cur_table_name = str(row_aug['table_name'])
            cur_table_owner = str(row_aug['table_schema'])
            curr_col_name = str(row_aug['table_schema'])+'.'+str(row_aug['table_name'])+'.'+str(row_aug['column_name'])
            curr_col_datatype = str(row_aug['data_type'])
            curr_col_description = str(row_aug['column_description'])
            curr_col_constraints = str(row_aug['column_constraints'])
            curr_column_name = str(row_aug['column_name'])


            column_detailed_description=f"""Schema Name:{cur_table_owner} |  Column Name: {curr_col_name} (Data type: {curr_col_datatype}) | Table Name: {cur_table_name} | (column description: {curr_col_description})(constraints: {curr_col_constraints})"""

            r = {"table_schema": cur_table_owner,"table_name": cur_table_name,"column_name":curr_column_name, "content": column_detailed_description}
            column_details_chunked.append(r)

        column_details_embeddings = get_embedding_chunked(column_details_chunked, 10000)


    elif SOURCE=='bigquery':

        table_schema_sql = bqconnector.return_table_schema_sql(SCHEMA)
        table_desc_df = bqconnector.retrieve_df(table_schema_sql)

        column_schema_sql = bqconnector.return_column_schema_sql(SCHEMA)
        column_name_df = bqconnector.retrieve_df(column_schema_sql)
        #GENERATE MISSING DESCRIPTIONS
        table_desc_df,column_name_df= responder.generate_missing_descriptions(SOURCE,table_desc_df,column_name_df)
        
        #TABLE EMBEDDINGS
        table_details_chunked = []

        for index_aug, row_aug in table_desc_df.iterrows():
            cur_project_name =str(row_aug['project_id'])
            cur_table_name = str(row_aug['table_name'])
            cur_table_schema = str(row_aug['table_schema'])
            curr_col_names = str(row_aug['table_columns'])
            curr_tbl_desc = str(row_aug['table_description'])


            table_detailed_description=f"""
            Full Table Name : {cur_project_name}.{cur_table_schema}.{cur_table_name} |
            Table Columns List: [{curr_col_names}] |
            Table Description: {curr_tbl_desc} """

            r = {"table_schema": cur_table_schema,"table_name": cur_table_name,"content": table_detailed_description}
            table_details_chunked.append(r)

        table_details_embeddings = get_embedding_chunked(table_details_chunked, 10000)


        ### COLUMN EMBEDDING ###
        """
        This SQL returns a df containing the cols table_schema, table_name, column_name, data_type, column_description, table_description, primary_key, column_constraints
        for the schema specified above, e.g. 'retail'
        """

        column_details_chunked = []

        for index_aug, row_aug in column_name_df.iterrows():
            cur_project_name =str(row_aug['project_id'])
            cur_table_name = str(row_aug['table_name'])
            cur_table_owner = str(row_aug['table_schema'])
            curr_col_name = str(row_aug['table_schema'])+'.'+str(row_aug['table_name'])+'.'+str(row_aug['column_name'])
            curr_col_datatype = str(row_aug['data_type'])
            curr_col_description = str(row_aug['column_description'])
            curr_col_constraints = str(row_aug['column_constraints'])
            curr_column_name = str(row_aug['column_name'])


            column_detailed_description=f"""
            Column Name: {curr_col_name}|
            Full Table Name : {cur_project_name}.{cur_table_schema}.{cur_table_name} |
            Data type: {curr_col_datatype}|
            Column description: {curr_col_description}|
            Column Constraints: {curr_col_constraints} """

            r = {"table_schema": cur_table_owner,"table_name": cur_table_name,"column_name":curr_column_name, "content": column_detailed_description}
            column_details_chunked.append(r)

        column_details_embeddings = get_embedding_chunked(column_details_chunked, 10000)


    return table_details_embeddings, column_details_embeddings
    


if __name__ == '__main__':
    SOURCE = 'cloudsql-pg'
    t, c = retrieve_embeddings(SOURCE, SCHEMA="public") 