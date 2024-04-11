
import asyncio
from dbconnectors import pgconnector

async def cache_known_sql(VECTOR_STORE):
    

    if VECTOR_STORE == "cloudsql-pgvector": 
        pgconnector.cache_known_sql() #this function takes known_good_sql.csv as source file update it

    elif VECTOR_STORE == "bigquery": 
        """TODO"""
        print("")

    else: raise ValueError("Not a valid parameter for a vector store.")



if __name__ == '__main__':
    from utilities import PROJECT_ID, PG_DATABASE, PG_INSTANCE, PG_PASSWORD, PG_REGION, PG_USER

    asyncio.run(cache_known_sql(PROJECT_ID,
                           PG_REGION,
                           PG_INSTANCE,
                           PG_USER,
                           PG_PASSWORD,
                           PG_DATABASE, 
                           VECTOR_STORE="cloudsql-pgvector"))