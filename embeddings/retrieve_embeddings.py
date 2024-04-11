import re
import io
import sys 
import pandas as pd
from dbconnectors import pgconnector,bqconnector
from agents import EmbedderAgent, ResponseAgent


embedder = EmbedderAgent('vertex')
responder = ResponseAgent('gemini-pro')

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


def retrieve_embeddings(SOURCE, EXAMPLES, SCHEMA="public"): 
    """ Augment all the DB schema blocks to create document for embedding """
    
    example_prompt_sql_embeddings=pd.DataFrame()

    if SOURCE == "cloudsql-pg":
    

        table_schema_sql = pgconnector.return_table_schema_sql(SCHEMA)
        table_desc_df = pgconnector.retrieve_df(table_schema_sql)
        
        column_schema_sql = pgconnector.return_column_schema_sql(SCHEMA)
        column_name_df = pgconnector.retrieve_df(column_schema_sql)
        

         #GENERATE MISSING DESCRIPTIONS
        table_desc_df,column_name_df= responder.generate_missing_descriptions(SOURCE,table_desc_df,column_name_df)
       
        ### TABLE EMBEDDING ###
        """
        This SQL returns a df containing the cols table_schema, table_name, table_description, table_column (with cols in the table)
        for the schema specified above, e.g. 'retail'
        """
        table_details_chunked = []

        for index_aug, row_aug in table_desc_df.iterrows():

            cur_table_name = str(row_aug['table_name'])
            cur_table_schema = str(row_aug['table_schema'])
            curr_col_name = str(row_aug['table_column'])
            curr_tbl_desc = str(row_aug['table_description'])


            col_comments_text=f"""Schema Name: {cur_table_schema} | Table Name: {cur_table_name} (Table Description - {curr_tbl_desc}) | Columns List: [{curr_col_name}]"""

            r = {"table_schema": cur_table_schema,"table_name": cur_table_name,"content": col_comments_text}
            table_details_chunked.append(r)

        table_details_embeddings = get_embedding_chunked(table_details_chunked, 10)


        ### COLUMN EMBEDDING ###
        """
        This SQL returns a df containing the cols table_schema, table_name, column_name, data_type, column_description, table_description, primary_key, column_constraints
        for the schema specified above, e.g. 'retail'
        """
        
        tablecolumn_details_chunked = []

        for index_aug, row_aug in column_name_df.iterrows():

            cur_table_name = str(row_aug['table_name'])
            cur_table_owner = str(row_aug['table_schema'])
            curr_col_name = str(row_aug['table_schema'])+'.'+str(row_aug['table_name'])+'.'+str(row_aug['column_name'])
            curr_col_datatype = str(row_aug['data_type'])
            curr_col_description = str(row_aug['column_description'])
            curr_col_constraints = str(row_aug['column_constraints'])
            curr_column_name = str(row_aug['column_name'])


            col_comments_text=f"""Schema Name:{cur_table_owner} | Table Name: {cur_table_name} (Table description: {curr_col_description}) | Column details: {curr_col_name} (Data type: {curr_col_datatype})(column description: {curr_col_description})(constraints: {curr_col_constraints})"""

            r = {"table_schema": cur_table_owner,"table_name": cur_table_name,"column_name":curr_column_name, "content": col_comments_text}
            tablecolumn_details_chunked.append(r)

        tablecolumn_details_embeddings = get_embedding_chunked(tablecolumn_details_chunked, 10)

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
            curr_col_name = str(row_aug['table_column'])
            curr_tbl_desc = str(row_aug['table_description'])


            col_comments_text=f"""Full Table Name : {cur_project_name}.{cur_table_schema}.{cur_table_name} | (Table Description - {curr_tbl_desc}) | Columns List: [{curr_col_name}]"""

            r = {"table_schema": cur_table_schema,"table_name": cur_table_name,"content": col_comments_text}
            table_details_chunked.append(r)

        table_details_embeddings = get_embedding_chunked(table_details_chunked, 10)


        ### COLUMN EMBEDDING ###
        """
        This SQL returns a df containing the cols table_schema, table_name, column_name, data_type, column_description, table_description, primary_key, column_constraints
        for the schema specified above, e.g. 'retail'
        """

        tablecolumn_details_chunked = []

        for index_aug, row_aug in column_name_df.iterrows():
            cur_project_name =str(row_aug['project_id'])
            cur_table_name = str(row_aug['table_name'])
            cur_table_owner = str(row_aug['table_schema'])
            curr_col_name = str(row_aug['table_schema'])+'.'+str(row_aug['table_name'])+'.'+str(row_aug['column_name'])
            curr_col_datatype = str(row_aug['data_type'])
            curr_col_description = str(row_aug['column_description'])
            curr_col_constraints = str(row_aug['column_constraints'])
            curr_column_name = str(row_aug['column_name'])


            col_comments_text=f"""Full Table Name : {cur_project_name}.{cur_table_schema}.{cur_table_name} | (Table description: {curr_col_description}) | Column details: {curr_col_name} (Data type: {curr_col_datatype})(column description: {curr_col_description})(constraints: {curr_col_constraints})"""

            r = {"table_schema": cur_table_owner,"table_name": cur_table_name,"column_name":curr_column_name, "content": col_comments_text}
            tablecolumn_details_chunked.append(r)

        tablecolumn_details_embeddings = get_embedding_chunked(tablecolumn_details_chunked, 10)


    if EXAMPLES: 
    ### KNOWN GOOD SQL QUESTION EMBEDDING ###
        try: 
            sample_query_sql=f"select * from query_example_embeddings"
            sql_example_df = pgconnector.retrieve_df(sample_query_sql)
            example_sql_details_chunked = []

            for _, row_aug in sql_example_df.iterrows():

                example_user_question = str(row_aug['prompt'])
                example_generated_sql = str(row_aug['sql'])
                emb =  embedder.create(example_user_question)

                r = {"example_user_question": example_user_question,"example_generated_sql": example_generated_sql,"embedding": emb}
                example_sql_details_chunked.append(r)

            example_prompt_sql_embeddings = pd.DataFrame(example_sql_details_chunked)
        except: 
            print("Caching is enabled, but no Cache found. Please instantiate your DB Cache first.")

    return table_details_embeddings, tablecolumn_details_embeddings, example_prompt_sql_embeddings



if __name__ == '__main__': 
    from utilities import EXAMPLES
    SOURCE = 'cloudsql-pg'
    t, c, e = retrieve_embeddings(SOURCE, EXAMPLES, SCHEMA="public") 