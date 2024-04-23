import os
import asyncio
import asyncpg
import pandas as pd
import numpy as np
from pgvector.asyncpg import register_vector
from google.cloud.sql.connector import Connector
from langchain_community.embeddings import VertexAIEmbeddings
from google.cloud import bigquery
from dbconnectors import pgconnector
from agents import EmbedderAgent
from sqlalchemy.sql import text
from utilities import PG_SCHEMA, PROJECT_ID, PG_INSTANCE, PG_DATABASE, PG_USER, PG_PASSWORD, PG_REGION, BQ_OPENDATAQNA_DATASET_NAME, BQ_REGION

embedder = EmbedderAgent('vertex')


async def setup_kgq_table( project_id,
                            instance_name,
                            database_name,
                            schema,
                            database_user,
                            database_password,
                            region,
                            VECTOR_STORE = "cloudsql-pgvector"):
    """ 
    This function sets up or refreshes the Vector Store for Known Good Queries (KGQ)
    """
    if VECTOR_STORE=='bigquery-vector':

        # Create BQ Client
        client=bigquery.Client(project=project_id)

        # Delete an old table
        client.query_and_wait(f'''DROP TABLE IF EXISTS `{project_id}.{schema}.example_prompt_sql_embeddings''')
        # Create a new emptry table
        client.query_and_wait(f'''CREATE TABLE IF NOT EXISTS `{project_id}.{schema}.example_prompt_sql_embeddings` (
                              table_schema string NOT NULL, example_user_question string NOT NULL, example_generated_sql string NOT NULL,
                              embedding ARRAY<FLOAT64>)''')
        

    elif VECTOR_STORE=='cloudsql-pgvector':

        loop = asyncio.get_running_loop()
        async with Connector(loop=loop) as connector:
            # Create connection to Cloud SQL database
            conn: asyncpg.Connection = await connector.connect_async(
                f"{project_id}:{region}:{instance_name}",  # Cloud SQL instance connection name
                "asyncpg",
                user=f"{database_user}",
                password=f"{database_password}",
                db=f"{database_name}",
            )

            # Drop on old table
            await conn.execute("DROP TABLE IF EXISTS example_prompt_sql_embeddings")
            # Create a new emptry table
            await conn.execute(
            """CREATE TABLE IF NOT EXISTS example_prompt_sql_embeddings(
                                table_schema VARCHAR(1024) NOT NULL,
                                example_user_question text NOT NULL,
                                example_generated_sql text NOT NULL,
                                embedding vector(768))"""
            )

    else: raise ValueError("Not a valid parameter for a vector store.")

async def store_kgq_embeddings(df_kgq, 
                            project_id,
                            instance_name,
                            database_name,
                            schema,
                            database_user,
                            database_password,
                            region,
                            VECTOR_STORE = "cloudsql-pgvector"
                            ):
    """ 
    Create and save the Known Good Query Embeddings to Vector Store  
    """
    if VECTOR_STORE=='bigquery-vector':

        client=bigquery.Client(project=project_id)
        
        example_sql_details_chunked = []

        for _, row_aug in df_kgq.iterrows():

            example_user_question = str(row_aug['prompt'])
            example_generated_sql = str(row_aug['sql'])
            example_database_name = str(row_aug['database_name'])
            emb =  embedder.create(example_user_question)
            

            r = {"example_database_name":example_database_name,"example_user_question": example_user_question,"example_generated_sql": example_generated_sql,"embedding": emb}
            example_sql_details_chunked.append(r)

        example_prompt_sql_embeddings = pd.DataFrame(example_sql_details_chunked)

        client.query_and_wait(f'''CREATE TABLE IF NOT EXISTS `{project_id}.{schema}.example_prompt_sql_embeddings` (
            table_schema string NOT NULL, example_user_question string NOT NULL, example_generated_sql string NOT NULL,
            embedding ARRAY<FLOAT64>)''')

        for _, row in example_prompt_sql_embeddings.iterrows():
                client.query_and_wait(f'''DELETE FROM `{project_id}.{schema}.example_prompt_sql_embeddings`
                            WHERE table_schema= '{row["example_database_name"]}' and example_user_question= '{row["example_user_question"]}' '''
                                )
                    # embedding=np.array(row["embedding"])
                client.query_and_wait(f'''INSERT INTO `{project_id}.{schema}.example_prompt_sql_embeddings` 
                    VALUES ('{row["example_database_name"]}','{row["example_user_question"]}' , 
                    '{row["example_generated_sql"]}',{row["embedding"]} )''')
                    
        


    elif VECTOR_STORE=='cloudsql-pgvector':

        loop = asyncio.get_running_loop()
        async with Connector(loop=loop) as connector:
            # Create connection to Cloud SQL database
            conn: asyncpg.Connection = await connector.connect_async(
                f"{project_id}:{region}:{instance_name}",  # Cloud SQL instance connection name
                "asyncpg",
                user=f"{database_user}",
                password=f"{database_password}",
                db=f"{database_name}",
            )


            example_sql_details_chunked = []
            
            for _, row_aug in df_kgq.iterrows():

                example_user_question =  str(row_aug['prompt'])
                example_generated_sql = str(row_aug['sql'])
                example_database_name = str(row_aug['database_name'])

                emb =  embedder.create(example_user_question)

                r = {"example_database_name":example_database_name,"example_user_question": example_user_question,"example_generated_sql": example_generated_sql,"embedding": emb}
                example_sql_details_chunked.append(r)

            example_prompt_sql_embeddings = pd.DataFrame(example_sql_details_chunked)
            
            for _, row in example_prompt_sql_embeddings.iterrows():
                await conn.execute(
                        "DELETE FROM example_prompt_sql_embeddings WHERE table_schema= $1 and example_user_question=$2",
                        row["example_database_name"],
                        row["example_user_question"])
                await conn.execute(
                    "INSERT INTO example_prompt_sql_embeddings (table_schema, example_user_question, example_generated_sql, embedding) VALUES ($1, $2, $3, $4)",
                    row["example_database_name"],
                    row["example_user_question"],
                    row["example_generated_sql"],
                    str(row["embedding"]),
                )

        await conn.close()

    else: raise ValueError("Not a valid parameter for a vector store.")

if __name__ == '__main__': 
    from utilities import PG_SCHEMA, PROJECT_ID, PG_INSTANCE, PG_DATABASE, PG_USER, PG_PASSWORD, PG_REGION
    VECTOR_STORE = "cloudsql-pgvector"
    
    current_dir = os.getcwd()
    root_dir = os.path.expanduser('~')  # Start at the user's home directory

    while current_dir != root_dir:
        for dirpath, dirnames, filenames in os.walk(current_dir):
            config_path = os.path.join(dirpath, 'known_good_sql.csv')
            if os.path.exists(config_path):
                file_path = config_path  # Update root_dir to the found directory
                break  # Stop outer loop once found

        current_dir = os.path.dirname(current_dir)

    print("Known Good SQL Found at Path :: "+file_path)

    # Load the file
    df_kgq = pd.read_csv(file_path)
    df_kgq = df_kgq.loc[:, ["prompt", "sql", "database_name"]]
    df_kgq = df_kgq.dropna()

    print('Known Good SQLs Loaded into a Dataframe')

    asyncio.run(setup_kgq_table(PROJECT_ID,
                            PG_INSTANCE,
                            PG_DATABASE,
                            PG_SCHEMA,
                            PG_USER,
                            PG_PASSWORD,
                            PG_REGION,
                            VECTOR_STORE))

    asyncio.run(store_kgq_embeddings(df_kgq,
                            PROJECT_ID,
                            PG_INSTANCE,
                            PG_DATABASE,
                            PG_SCHEMA,
                            PG_USER,
                            PG_PASSWORD,
                            PG_REGION,
                            VECTOR_STORE))
