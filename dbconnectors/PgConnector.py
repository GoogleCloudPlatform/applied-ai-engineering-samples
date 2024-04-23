"""
PostgreSQL Connector Class 
"""
import asyncpg
from google.cloud.sql.connector import Connector
from sqlalchemy import create_engine
import pandas as pd 
from sqlalchemy.sql import text
from pgvector.asyncpg import register_vector
import asyncio
from pg8000.exceptions import DatabaseError 

from utilities import root_dir
from google.cloud.sql.connector import Connector

from dbconnectors import DBConnector
from abc import ABC



def pg_specific_data_types(): 
    return '''
    PostgreSQL offers a wide variety of datatypes to store different types of data effectively. Here's a breakdown of the available categories:

    Numeric datatypes -
    SMALLINT: Stores small-range integers between -32768 and 32767.
    INTEGER: Stores typical integers between -2147483648 and 2147483647.
    BIGINT: Stores large-range integers between -9223372036854775808 and 9223372036854775807.
    DECIMAL(p,s): Stores arbitrary precision numbers with a maximum of p digits and s digits to the right of the decimal point.
    NUMERIC: Similar to DECIMAL but with additional features like automatic scaling.
    REAL: Stores single-precision floating-point numbers with an approximate range of -3.4E+38 to 3.4E+38.
    DOUBLE PRECISION: Stores double-precision floating-point numbers with an approximate range of -1.7E+308 to 1.7E+308.


    Character datatypes -
    CHAR(n): Fixed-length character string with a specified length of n characters.
    VARCHAR(n): Variable-length character string with a maximum length of n characters.
    TEXT: Variable-length string with no maximum size limit.
    CHARACTER VARYING(n): Alias for VARCHAR(n).
    CHARACTER: Alias for CHAR.

    Monetary datatypes -
    MONEY: Stores monetary amounts with two decimal places.

    Date/Time datatypes -
    DATE: Stores dates without time information.
    TIME: Stores time of day without date information (optionally with time zone).
    TIMESTAMP: Stores both date and time information (optionally with time zone).
    INTERVAL: Stores time intervals between two points in time.

    Binary types -
    BYTEA: Stores variable-length binary data.
    BIT: Stores single bits.
    BIT VARYING: Stores variable-length bit strings.

    Other types -
    BOOLEAN: Stores true or false values.
    UUID: Stores universally unique identifiers.
    XML: Stores XML data.
    JSON: Stores JSON data.
    ENUM: Stores user-defined enumerated values.
    RANGE: Stores ranges of data values.

    This list covers the most common datatypes in PostgreSQL.
    '''




class PgConnector(DBConnector, ABC):
    """
    Instantiates a Postgres Connector. 
    """

    def __init__(self,
                project_id:str, 
                region:str, 
                instance_name:str,
                database_name:str, 
                database_user:str, 
                database_password:str): 

        self.project_id = project_id
        self.region = region 
        self.instance_name = instance_name 
        self.database_name = database_name
        self.database_user = database_user
        self.database_password = database_password

        self.pool = create_engine(
            "postgresql+pg8000://",
            creator=self.getconn,
        )


    def getconn(self): 
        """
        function to return the database connection object
        """
        # initialize Connector object
        connector = Connector()
        conn = connector.connect(
            f"{self.project_id}:{self.region}:{self.instance_name}",
            "pg8000",
            user=f"{self.database_user}",
            password=f"{self.database_password}",
            db=f"{self.database_name}"
        )

        return conn 


    def retrieve_df(self, query):
        """ 
        TODO: Description 
        """

        result_df=pd.DataFrame()
        try: 
            with self.pool.connect() as db_conn:
                # query and fetch ratings table
                df = pd.read_sql(text(query), con=db_conn)
                result_df = df
            # print('\n Return from code execution: ' + str(result_df) )
            return result_df
        
        except Exception as e: 
            print(f"Database Error: {e}")
            df = pd.DataFrame({'Error. Message': e}, index=[0])
            return df 
        
    
    async def cache_known_sql(self):
        
        df = pd.read_csv(f"{root_dir}/{scripts}/known_good_sql.csv")
        df = df.loc[:, ["prompt", "sql", "database_name"]]
        df = df.dropna()

        loop = asyncio.get_running_loop()
        async with Connector(loop=loop) as connector:
            # # Create connection to Cloud SQL database.
            conn: asyncpg.Connection = await connector.connect_async(
                f"{self.project_id}:{self.region}:{self.instance_name}", 
                "asyncpg",
                user=f"{self.database_user}",
                password=f"{self.database_password}",
                db=f"{self.database_name}",
            )


            await register_vector(conn)

            # Delete the table if it exists.
            await conn.execute("DROP TABLE IF EXISTS query_example_embeddings CASCADE")
                
            # Create the `query_example_embeddings` table.
            await conn.execute(
                """CREATE TABLE query_example_embeddings(
                                    prompt TEXT,
                                    sql TEXT,
                                    database_name TEXT)"""
            )

            # Copy the dataframe to the 'query_example_embeddings' table.
            tuples = list(df.itertuples(index=False))
            await conn.copy_records_to_table(
                "query_example_embeddings", records=tuples, columns=list(df), timeout=10000
            )
            
        await conn.close()


    async def retrieve_matches(self, mode, schema, qe, similarity_threshold, limit): 
        """
        This function retrieves the most similar table_schema and column_schema.
        Modes can be either 'table', 'column', or 'example' 
        """
        matches = [] 

        loop = asyncio.get_running_loop()
        async with Connector(loop=loop) as connector:
            # # Create connection to Cloud SQL database.
            conn: asyncpg.Connection = await connector.connect_async(
                f"{self.project_id}:{self.region}:{self.instance_name}", 
                "asyncpg",
                user=f"{self.database_user}",
                password=f"{self.database_password}",
                db=f"{self.database_name}",
            )


            await register_vector(conn)


            # Prepare the SQL depending on 'mode' 
            if mode == 'table': 
                sql = """           
                    WITH vector_matches AS (
                    SELECT table_name, table_schema, content,
                    (embedding <=> $1) AS similarity
                    FROM table_details_embeddings
                    WHERE 1 - (embedding <=> $1) > $2
                    AND table_schema = $4
                    ORDER BY similarity ASC LIMIT $3
                    )
                    SELECT content as tables_content
                    FROM vector_matches
                """
                

            elif mode == 'column': 
                sql = """
                    WITH vector_matches AS (
                    SELECT table_name, table_schema, content,
                    (embedding <=> $1) AS similarity
                    FROM tablecolumn_details_embeddings
                    WHERE 1 - (embedding <=> $1) > $2
                    AND table_schema = $4
                    ORDER BY similarity ASC LIMIT $3
                    )
                    SELECT content as columns_content
                    FROM vector_matches
                """

            elif mode == 'example': 
                sql = """
                    WITH vector_matches AS (
                    SELECT table_schema, example_user_question, example_generated_sql,
                    (embedding <=> $1) AS similarity
                    FROM example_prompt_sql_embeddings
                    WHERE 1 - (embedding <=> $1) > $2
                    AND table_schema = $4
                    ORDER BY similarity ASC LIMIT $3
                    )
                    SELECT example_user_question, example_generated_sql,similarity
                    FROM vector_matches
                """

            else: 
                ValueError("No valid mode. Must be either table, column, or example")
                name_txt = ''
                
            # print(sql,qe,similarity_threshold,limit,schema)
            # FETCH RESULTS FROM POSTGRES DB 
            results = await conn.fetch(
                sql,
                qe,
                similarity_threshold,
                limit,
                schema
            )

            # CHECK RESULTS 
            if len(results) == 0:
                print("Did not find any results. Adjust the query parameters.")

            if mode == 'table': 
                name_txt = ''
                for r in results:
                    name_txt=name_txt+r["tables_content"]+"\n\n"

            elif mode == 'column': 
                name_txt = '' 
                for r in results:
                    name_txt=name_txt+r["columns_content"]+"\n\n "

            elif mode == 'example': 
                name_txt = ''
                for r in results:
                    example_user_question=r["example_user_question"]
                    example_sql=r["example_generated_sql"]
                    # print(example_user_question+"\nThreshold::"+str(r["similarity"]))
                    name_txt = name_txt + "\n Example_question: "+example_user_question+ "; Example_SQL: "+example_sql

            else: 
                ValueError("No valid mode. Must be either table, column, or example")
                name_txt = ''

            matches.append(name_txt)

        # Close the connection to the database.
        await conn.close()

        return matches 



    async def getSimilarMatches(self, mode, schema, qe, num_matches, similarity_threshold):

        if mode == 'table': 
            match_result=await self.retrieve_matches(mode, schema, qe, similarity_threshold, num_matches)
            match_result = match_result[0]

        elif mode == 'column': 
            match_result=await self.retrieve_matches(mode, schema, qe, similarity_threshold, num_matches)
            match_result = match_result[0]
        
        elif mode == 'example': 
            match_result=await self.retrieve_matches(mode, schema, qe, similarity_threshold, num_matches)
            if len(match_result) == 0:
                match_result = None
            else:
                match_result = match_result[0]

        return match_result


    def test_sql_plan_execution(self, generated_sql):
        exec_result_df = pd.DataFrame()
        sql = f"""EXPLAIN ANALYZE {generated_sql}"""
        exec_result_df = self.retrieve_df(sql)

        if not exec_result_df.empty:
            if str(exec_result_df.iloc[0]).startswith('Error. Message'):
                correct_sql = False 
                
            else:
                print('\n No need to rewrite the query. This seems to work fine and returned rows...')
                correct_sql = True
        else:
            print('\n No need to rewrite the query. This seems to work fine but no rows returned...')
            correct_sql = True
        
        return correct_sql, exec_result_df



    def getExactMatches(self, query): 
        """ 
        Checks if the exact question is already present in the example SQL set 
        """
        check_history_sql=f"""SELECT example_user_question,example_generated_sql
        FROM example_prompt_sql_embeddings
        WHERE lower(example_user_question) = lower('{query}') LIMIT 1; """

        exact_sql_history = self.retrieve_df(check_history_sql)

        if exact_sql_history[exact_sql_history.columns[0]].count() != 0:
            sql_example_txt = ''
            exact_sql = ''
            for index, row in exact_sql_history.iterrows():
                example_user_question=row["example_user_question"]
                example_sql=row["example_generated_sql"]
                exact_sql=example_sql
                sql_example_txt = sql_example_txt + "\n Example_question: "+example_user_question+ "; Example_SQL: "+example_sql

            print("Found a matching question from the history!" + str(sql_example_txt))
            final_sql=exact_sql

        else: 
            print("No exact match found for the user prompt")
            final_sql = None

        return final_sql 
    




    def return_column_schema_sql(self, schema): 
        """
        This SQL returns a df containing the cols table_schema, table_name, column_name, data_type, column_description, table_description, primary_key, column_constraints
        for the schema specified above, e.g. 'retail'
        - table_schema: e.g. retail 
        - table_name: name of the table inside the schema, e.g. products 
        - column_name: name of each col in each table in the schema, e.g. id_product 
        - data_type: data type of each col 
        - column_description: col descriptor, can be empty 
        - table_description: text descriptor, can be empty 
        - primary_key: whether the col is PK; if yes, the field contains the col_name 
        - column_constraints: e.g. "Primary key for this table"
        """


        column_schema_sql = f'''
        WITH
        columns_schema
        AS
        (select c.table_schema,c.table_name,c.column_name,c.data_type,d.description as column_description, obj_description(c1.oid) as table_description
        from information_schema.columns c
        inner join pg_class c1
        on c.table_name=c1.relname
        inner join pg_catalog.pg_namespace n
        on c.table_schema=n.nspname
        and c1.relnamespace=n.oid
        left join pg_catalog.pg_description d
        on d.objsubid=c.ordinal_position
        and d.objoid=c1.oid
        where
        c.table_schema='{schema}'),
        pk_schema as
        (SELECT table_name, column_name AS primary_key
        FROM information_schema.key_column_usage
        WHERE TABLE_SCHEMA='{schema}'
        AND CONSTRAINT_NAME like '%_pkey%'
        ORDER BY table_name, primary_key),
        fk_schema as
        (SELECT table_name, column_name AS foreign_key
        FROM information_schema.key_column_usage
        WHERE TABLE_SCHEMA='{schema}'
        AND CONSTRAINT_NAME like '%_fkey%'
        ORDER BY table_name, foreign_key)

        select lr.*,
        case
        when primary_key is not null then 'Primary key for this table'
        when foreign_key is not null then CONCAT('Foreign key',column_description)
        else null
        END as column_constraints
        from
        (select l.*,r.primary_key
        from
        columns_schema l
        left outer join
        pk_schema r
        on
        l.table_name=r.table_name
        and
        l.column_name=r.primary_key) lr
        left outer join
        fk_schema rt
        on
        lr.table_name=rt.table_name
        and
        lr.column_name=rt.foreign_key
        ;
        '''

        return column_schema_sql



    
    def return_table_schema_sql(self, schema): 
        """
        This SQL returns a df containing the cols table_schema, table_name, table_description, table_columns (with cols in the table)
        for the schema specified above, e.g. 'retail'
        - table_schema: e.g. retail 
        - table_name: name of the table inside the schema, e.g. products 
        - table_description: text descriptor, can be empty 
        - table_columns: aggregate of the col names inside the table 
        """


        table_schema_sql = f'''
        SELECT table_schema, table_name,table_description, array_to_string(array_agg(column_name), ' , ') as table_columns
        FROM
        (select c.table_schema,c.table_name,c.column_name,c.ordinal_position,c.column_default,c.data_type,d.description, obj_description(c1.oid) as table_description
        from information_schema.columns c
        inner join pg_class c1
        on c.table_name=c1.relname
        inner join pg_catalog.pg_namespace n
        on c.table_schema=n.nspname
        and c1.relnamespace=n.oid
        left join pg_catalog.pg_description d
        on d.objsubid=c.ordinal_position
        and d.objoid=c1.oid
        where
        c.table_schema='{schema}') data
        GROUP BY table_schema, table_name, table_description
        ORDER BY table_name;
        '''

        return table_schema_sql  
    

