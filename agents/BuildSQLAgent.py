from abc import ABC
from .core import Agent 



class BuildSQLAgent(Agent, ABC):
    """
    This Agent produces the SQL query 
    """

    agentType: str = "BuildSQLAgent"

    def build_sql(self,source_type, user_question,tables_schema,tables_detailed_schema, similar_sql): 

        not_related_msg='select \'Question is not related to the dataset\' as unrelated_answer from dual;'
        
        if source_type=='bigquery':
            context_prompt = f"""
      You are a BigQuery SQL guru. Write a SQL comformant query for Bigquery that answers the following question while using the provided context to correctly refer to the BigQuery tables and the needed column names.

      Guidelines:
      - Join as minimal tables as possible.
      - When joining tables ensure all join columns are the same data_type.
      - Analyze the database and the table schema provided as parameters and undestand the relations (column and table relations).
      - Use always SAFE_CAST. If performing a SAFE_CAST, use only Bigquery supported datatypes.
       - Always SAFE_CAST and then use aggregate functions
      - Don't include any comments in code.
      - Remove ```sql and ``` from the output and generate the SQL in single line.
      - Tables should be refered to using a fully qualified name with enclosed in ticks (`) e.g. `project_id.owner.table_name`.
      - Use all the non-aggregated columns from the "SELECT" statement while framing "GROUP BY" block.
      - Return syntactically and symantically correct SQL for BigQuery with proper relation mapping i.e project_id, owner, table and column relation.
      - Use ONLY the column names (column_name) mentioned in Table Schema. DO NOT USE any other column names outside of this.
      - Associate column_name mentioned in Table Schema only to the table_name specified under Table Schema.
      - Use SQL 'AS' statement to assign a new name temporarily to a table column or even a table wherever needed.
      - Table names are case sensitive. DO NOT uppercase or lowercase the table names.
      - Always enclose subqueries and union queries in brackets.
      - Refer to the examples provided i.e. {similar_sql}


            Here are some examples of user-question and SQL queries:
            {similar_sql}

            question:
            {user_question}

            Table Schema:
            {tables_schema}

            Column Description:
            {tables_detailed_schema}

            """
            # print(context_prompt)


        else: 

        
            from dbconnectors import pg_specific_data_types
            pg_specific_data_types = pg_specific_data_types() 

            
            context_prompt = f"""

            You are an PostgreSQL SQL guru. Write a SQL comformant query for PostgreSQL that answers the following question while using the provided context to correctly refer to postgres tables and the needed column names.

            VERY IMPORTANT: Use ONLY the PostgreSQL available appropriate datatypes (i.e {pg_specific_data_types}) while casting the column in the SQL.
            IMPORTANT: In "FROM" and "JOIN" blocks always refer the table_name as schema.table_name.
            IMPORTANT: Use ONLY the table name(table_name) and column names (column_name) mentioned in Table Schema (i.e {tables_schema}). DO NOT USE any other column names outside of this.
            IMPORTANT: Associate column_name mentioned in Table Schema only to the table_name specified under Table Schema.
            NOTE: Use SQL 'AS' statement to assign a new name temporarily to a table column or even a table wherever needed.

            Guidelines:.
            - Only answer questions relevant to the tables or columns listed in the table schema If a non-related question comes, answer exactly: {not_related_msg}
            - Join as minimal tables as possible.
            - When joining tables ensure all join columns are the same data_type.
            - Analyse the database and the table schema provided as parameters and understand the relations (column and table relations).
            - Don't include any comments in code.
            - Remove ```sql and ``` from the output and generate the SQL in single line.
            - Tables should be refered to using a fully qualified name including owner and table name.
            - Use table_alias.column_name when referring to columns. Example: dept_id=hr.dept_id
            - Capitalize the table names on SQL "where" condition.
            - Use the columns from the "SELECT" statement while framing "GROUP BY" block.
            - Always refer the column-name with rightly mapped table-name as seen in the table schema.
            - Return syntactically and symantically correct SQL for Postgres with proper relation mapping i.e owner, table and column relation.
            - Refer to the examples provided i.e. {similar_sql}


            Here are some examples of user-question and SQL queries:
            {similar_sql}

            question:
            {user_question}

            Table Schema:
            {tables_schema}

            Column Description:
            {tables_detailed_schema}

            """
            # print(context_prompt)

        if self.model_id =='gemini-pro':
            context_query = self.model.generate_content(context_prompt, stream=False)
            generated_sql = str(context_query.candidates[0].text)

        else:
            context_query = self.model.predict(context_prompt, max_output_tokens = 8000, temperature=0)
            generated_sql = str(context_query.candidates[0])


        return generated_sql
