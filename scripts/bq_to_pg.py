


def create_bucket(BUCKET_NAME, PROJECT_ID):
    """Creates a new bucket."""
    from google.cloud import storage

    storage_client = storage.Client(project=PROJECT_ID)

    bucket = storage_client.bucket(BUCKET_NAME)

    if bucket.exists(): 
        print("This bucket already exists.")
    
    else:
        bucket = storage_client.create_bucket(BUCKET_NAME)
        print(f"Bucket {bucket.name} created")



def export_bq_cs(BQ_PROJECT,
                 BQ_DATABASE, 
                 BQ_TABLE,
                 BUCKET_NAME,
                 BUCKET_FILENAME,
                 PROJECT_ID): 
    """Exports Bigquery table to csv on a cloud storage bucket."""
    
    from google.cloud import bigquery
    client = bigquery.Client(project=PROJECT_ID)

    destination_uri = "gs://{}/{}".format(BUCKET_NAME, BUCKET_FILENAME)
    dataset_ref = bigquery.DatasetReference(BQ_PROJECT, BQ_DATABASE)
    table_ref = dataset_ref.table(BQ_TABLE)

    extract_job = client.extract_table(
        table_ref,
        destination_uri,
        # Location must match that of the source table.
        location="US",
    )  # API request
    extract_job.result()  # Waits for job to complete.

    print(
        f"Exported {BQ_PROJECT}:{BQ_DATABASE}.{BQ_TABLE} to {destination_uri}"
    )


def get_bq_schema(BQ_PROJECT,
                 BQ_DATABASE, 
                 BQ_TABLE,
                 PROJECT_ID): 
    
    from google.cloud import bigquery
    # client = bigquery.Client()
    client = bigquery.Client(project=PROJECT_ID)

    dataset_ref = bigquery.DatasetReference(BQ_PROJECT, BQ_DATABASE)
    table_ref = dataset_ref.table(BQ_TABLE)

    table = client.get_table(table_ref)
    field_names = [field.name for field in table.schema]
    field_types = [field.field_type for field in table.schema]

    return field_names, field_types



def get_df_schema(BUCKET_NAME,
                 PROJECT_ID): 
    
    from google.cloud import storage
    import pandas as pd 
    from google.cloud.sql.connector import Connector

    storage_client = storage.Client(project=PROJECT_ID)

    bucket = storage_client.get_bucket(BUCKET_NAME)
    blobs = bucket.list_blobs()

    for idx,blob in enumerate(blobs):
        if idx == 0: 
            URI = "gs://{}".format(blob.id).split('.csv', 1)[0]+'.csv'
            df = pd.read_csv(URI)

            cols = df.columns
            types = df.dtypes

        else: 
            break

    return cols, types




def get_sql(BQ_TABLE, field_names, field_types): 

    cols = "" 

    for i in range(len(field_names)): 
        cols += str(field_names[i]) +" "+ str(field_types[i])
        if i < (len(field_names)-1): 
            cols += ", "


    sql = f"""CREATE TABLE {BQ_TABLE}({cols})"""

    return sql


# TODO: map data types of BQ to PG, e.g. STRING -> TEXT 
async def create_pg_table(PROJECT_ID,
                          PG_REGION,
                          PG_INSTANCE,
                          PG_USER,
                          PG_PASSWORD,
                          PG_DATABASE,
                          BQ_TABLE, 
                          sql, 
                          mode="pd"): 
    """Create PG Table from BQ Schema"""
    import asyncio
    import asyncpg
    from google.cloud.sql.connector import Connector

    if mode == "pd": 
        sql = sql.replace("object", "TEXT").replace("int64", "INTEGER").replace("float64", "DOUBLE PRECISION")

    elif mode == "bq": 
        sql = sql.replace("STRING", "TEXT")

    else: raise ValueError("Supported modes are 'pd' and 'bq'.")

    loop = asyncio.get_running_loop()
    async with Connector(loop=loop) as connector:
        # Create connection to Cloud SQL database
        conn: asyncpg.Connection = await connector.connect_async(
            f"{PROJECT_ID}:{PG_REGION}:{PG_INSTANCE}",  # Cloud SQL instance connection name
            "asyncpg",
            user=f"{PG_USER}",
            password=f"{PG_PASSWORD}",
            db=f"{PG_DATABASE}",
        )

        await conn.execute(f"DROP TABLE IF EXISTS {BQ_TABLE} CASCADE")
        # Create the table.
        await conn.execute(sql)

        await conn.close()




async def import_to_pg(PROJECT_ID,
                          PG_REGION,
                          PG_INSTANCE,
                          PG_USER,
                          PG_PASSWORD,
                          PG_DATABASE,
                          BQ_TABLE, 
                          BUCKET_NAME,
                          field_types, 
                          mode="pd"): 
    from google.cloud import storage
    import pandas as pd 
    import asyncio
    import asyncpg
    # import datetime as dt 
    from google.cloud.sql.connector import Connector

    storage_client = storage.Client(project=PROJECT_ID)

    bucket = storage_client.get_bucket(BUCKET_NAME)
    blobs = bucket.list_blobs()

    if mode == "bq": 
        # Convert Timestamp cols in df from String to Datetime 
        # indices = field_types.index("TIMESTAMP")
        indices = [i for i, e in enumerate(field_types) if e == "TIMESTAMP"]
        
        col_names = list()
        for index in indices: 
            col = [e for i, e in enumerate(field_names) if i == index]
            col_names.append(col)

    loop = asyncio.get_running_loop()
    async with Connector(loop=loop) as connector:
        # Create connection to Cloud SQL database
        conn: asyncpg.Connection = await connector.connect_async(
            f"{PROJECT_ID}:{PG_REGION}:{PG_INSTANCE}",  # Cloud SQL instance connection name
            "asyncpg",
            user=f"{PG_USER}",
            password=f"{PG_PASSWORD}",
            db=f"{PG_DATABASE}",
        )

        for idx,blob in enumerate(blobs):
            if idx < 1: # LIMIT TO TEN 
                URI = "gs://{}".format(blob.id).split('.csv', 1)[0]+'.csv'
                df = pd.read_csv(URI)

                df = df.dropna()

                # df.info() 

                # convert the 'Date' column to datetime format
                if mode == "bq": 
                    for col in col_names: 
                        df[col]= pd.to_datetime(df[col].stack(),infer_datetime_format=True).dt.tz_localize(None).unstack()

                df.info()   

                # Copy the dataframe to the table.
                tuples = list(df.itertuples(index=False))

                r = tuples 
                c = list(df) 

                await conn.copy_records_to_table(
                    BQ_TABLE, records=tuples, columns=list(df), timeout=10000
                )
        await conn.close()



async def load_retail_data(PROJECT_ID,
                           PG_REGION,
                           PG_INSTANCE,
                           PG_USER,
                           PG_PASSWORD,
                           PG_DATABASE):
    import pandas as pd
    import os
    import asyncio
    import asyncpg
    from google.cloud.sql.connector import Connector

    DATASET_URL = "https://github.com/GoogleCloudPlatform/python-docs-samples/raw/main/cloud-sql/postgres/pgvector/data/retail_toy_dataset.csv"
    df = pd.read_csv(DATASET_URL)
    df = df.loc[:, ["product_id", "product_name", "description", "list_price"]]
    df = df.dropna()
    df.head(10)

    loop = asyncio.get_running_loop()
    async with Connector(loop=loop) as connector:
        # Create connection to Cloud SQL database
        conn: asyncpg.Connection = await connector.connect_async(
            f"{PROJECT_ID}:{PG_REGION}:{PG_INSTANCE}",  # Cloud SQL instance connection name
            "asyncpg",
            user=f"{PG_USER}",
            password=f"{PG_PASSWORD}",
            db=f"{PG_DATABASE}",
        )

        await conn.execute("DROP TABLE IF EXISTS products CASCADE")
        # Create the `products` table.
        await conn.execute(
            """CREATE TABLE products(
                                product_id VARCHAR(1024) PRIMARY KEY,
                                product_name TEXT,
                                description TEXT,
                                list_price NUMERIC)"""
        )

        # Copy the dataframe to the `products` table.
        tuples = list(df.itertuples(index=False))
        await conn.copy_records_to_table(
            "products", records=tuples, columns=list(df), timeout=10000
        )
        await conn.close()



if __name__ == '__main__': 
    from utilities import PROJECT_ID, PG_DATABASE, PG_INSTANCE, PG_PASSWORD, PG_REGION, PG_USER

    BQ_PROJECT = "bigquery-public-data"
    BQ_DATABASE = "google_dei"
    BQ_TABLE = "dar_intersectional_hiring"

    BUCKET_NAME = "dar_intersectional_hiring"
    BUCKET_FILENAME = "dei*.csv"

    import asyncio
    # # Create Cloud Storage Bucket 
    create_bucket(BUCKET_NAME, PROJECT_ID)

    # # Export BQ Table to Cloud Storage Bucket 
    export_bq_cs(BQ_PROJECT, BQ_DATABASE, BQ_TABLE, BUCKET_NAME, BUCKET_FILENAME, PROJECT_ID)

    # # Get BQ Column names and DTypes 
    # # field_names, field_types = get_bq_schema(BQ_PROJECT, BQ_DATABASE, BQ_TABLE, PROJECT_ID)
    field_names, field_types = get_df_schema(BUCKET_NAME, PROJECT_ID)

    # # Create SQL for PG Table Creation 
    sql = get_sql(BQ_TABLE, field_names, field_types)

    # # Create PG Table 
    asyncio.run(create_pg_table(PROJECT_ID, PG_REGION, PG_INSTANCE, PG_USER, PG_PASSWORD, PG_DATABASE, BQ_TABLE, sql, mode="pd"))

    # # Load Data into PG Table 
    asyncio.run(import_to_pg(PROJECT_ID, PG_REGION, PG_INSTANCE, PG_USER, PG_PASSWORD, PG_DATABASE, BQ_TABLE, BUCKET_NAME, field_types, mode="pd"))

    # Load demo retail data in PG Table
    asyncio.run(load_retail_data(PROJECT_ID, PG_REGION, PG_INSTANCE, PG_USER, PG_PASSWORD, PG_DATABASE))