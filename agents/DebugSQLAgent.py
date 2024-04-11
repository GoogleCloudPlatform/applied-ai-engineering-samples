
from abc import ABC
from vertexai.preview.language_models import CodeChatModel
from .core import Agent 
from agents import ValidateSQLAgent 
import pandas as pd
import json  
from dbconnectors import pgconnector, bqconnector



class DebugSQLAgent(Agent, ABC): 
    """ 
    This Chat Agent checks the SQL for vailidity
    """ 

    agentType: str = "DebugSQLAgent"

    # TODO: can we support other models for chat?? 
    def __init__(self): 
        self.model_id = 'codechat-bison-32k'
        self.model = CodeChatModel.from_pretrained("codechat-bison-32k")


    def init_chat(self,source_type, tables_schema,tables_detailed_schema,sql_example="-No examples provided..-"):
        if source_type in ('bigquery'):
            context_prompt = f"""
            You are an BigQuery SQL guru. This session is trying to troubleshoot an BigQuery SQL query.  As the user provides versions of the query and the errors returned by BigQuery,
            return a new alternative SQL query that fixes the errors. It is important that the query still answer the original question.


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
            - Refer to the examples provided i.e. {sql_example}

        Parameters:
        - table metadata: {tables_schema}
        - column metadata: {tables_detailed_schema}
        - SQL example: {sql_example}

        """

        else:
            context_prompt = f"""

            You are an Postgres SQL guru. This session is trying to troubleshoot an Postgres SQL query.  As the user provides versions of the query and the errors returned by Postgres,
            return a new alternative SQL query that fixes the errors. It is important that the query still answer the original question.

            Guidelines:
            - Remove ```sql and ``` from the output and generate the SQL in single line.
            - Rewritten SQL can't be igual to the original one.
            - Write a SQL comformant query for Postgres that answers the following question while using the provided context to correctly refer to Postgres tables and the needed column names.
            - All column_name in the query must exist in the table_name.
            - If a join includes d.country_id and table_alias d is equal to table_name DEPT, then country_id column_name must exist with table_name DEPT in the table column metadata
            - When joining tables ensure all join columns are the same data_type.
            - Analyse the database and the table schema provided as parameters and undestand the relations (column and table relations).
            - Don't include any comments in code.
            - Tables should be refered to using a fully qualified name including owner and table name.
            - Use table_alias.column_name when referring to columns. Example: dept_id=hr.dept_id
            - Capitalize the table names on SQL "where" condition.
            - Use the columns from the "SELECT" statement while framing "GROUP BY" block.
            - Always refer the column-name with rightly mapped table-name as seen in the table schema.
            - Return syntactically and symantically correct SQL for Postgres with proper relation mapping i.e owner, table and column relation.
            - Use only column names listed in the column metadata.
            - Always ensure to refer the table as schema.table_name.
            - Refer to the examples provided i.e. {sql_example}

        Parameters:
        - table metadata: {tables_schema}
        - column metadata: {tables_detailed_schema}
        - SQL example: {sql_example}

        """
        
        chat_session = self.model.start_chat(context=context_prompt)
        return chat_session


    def rewrite_sql_chat(self, chat_session, question, error_df):


        context_prompt = f"""
            What is an alternative SQL statement to address the error mentioned below?
            Present a different SQL from previous ones. It is important that the query still answer the original question.
            All columns selected must be present on tables mentioned on the join section.
            Avoid repeating suggestions.

            Original SQL:
            {question}

            Error:
            {error_df}

            """

        response = chat_session.send_message(context_prompt).candidates[0]

        return response


    def start_debugger  (self,
                        source_type,
                        query,
                        user_question, 
                        SQLChecker,
                        tables_schema, 
                        tables_detailed_schema,
                        AUDIT_TEXT, 
                        similar_sql="-No examples provided..-", 
                        DEBUGGING_ROUNDS = 2):
        i = 0  
        STOP = False 
        invalid_response = False 
        chat_session = self.init_chat(source_type,tables_schema,tables_detailed_schema,similar_sql)
        sql = query.replace("```sql","").replace("```","").replace("EXPLAIN ANALYZE ","")

        AUDIT_TEXT=AUDIT_TEXT+"Entering the debugging steps!"
        while (not STOP):
            # sql = query.replace("```sql","").replace("```","").replace("EXPLAIN ANALYZE ","")
            json_syntax_result = SQLChecker.check(user_question,tables_schema,tables_detailed_schema, sql) 



            if json_syntax_result['valid'] is True:
                # Testing SQL Execution
                AUDIT_TEXT=AUDIT_TEXT+"Generated SQL is syntactically"
                # print(AUDIT_TEXT)
                if source_type=='bigquery':
                    connector=bqconnector
                else:
                    connector=pgconnector
                    
                correct_sql, exec_result_df = connector.test_sql_plan_execution(sql)
                print("exec_result_df:" + exec_result_df)
                if not correct_sql:
                        AUDIT_TEXT=AUDIT_TEXT+"Generated SQL is not able to generate the query-plan!"
                        rewrite_result = self.rewrite_sql_chat(chat_session, sql, exec_result_df)
                        print('\n Rewritten and Cleaned SQL: ' + str(rewrite_result))
                        AUDIT_TEXT=AUDIT_TEXT+"\n Rewritten and Cleaned SQL: ' + str({rewrite_result})"
                        sql = str(rewrite_result).replace("```sql","").replace("```","").replace("EXPLAIN ANALYZE ","")

                else: STOP = True
            else:
                print('\n Will try to rewrite the query due to syntax error ...')
                AUDIT_TEXT=AUDIT_TEXT+'\n Will try to rewrite the query due to syntax error ...'
                print('\n Error Message: ' + str(json_syntax_result))
                AUDIT_TEXT=AUDIT_TEXT+'\n Error Message: ' + str(json_syntax_result)
                syntax_err_df = pd.read_json(json.dumps(json_syntax_result))
                rewrite_result=self.rewrite_sql_chat(chat_session, sql, syntax_err_df)
                print(rewrite_result)
                AUDIT_TEXT=AUDIT_TEXT+'\n Rewritten SQL: ' + str(rewrite_result)
                sql=str(rewrite_result).replace("```sql","").replace("```","").replace("EXPLAIN ANALYZE ","")
            i+=1
            if i > DEBUGGING_ROUNDS:
                AUDIT_TEXT=AUDIT_TEXT+ "Exceeded the number of iterations for correction!"
                AUDIT_TEXT=AUDIT_TEXT+ "The generated SQL can be invalid!"
                STOP = True
                invalid_response=True
            # After the while is completed
        if i > DEBUGGING_ROUNDS:
            invalid_response=True
        # print(AUDIT_TEXT)
        return sql, invalid_response, AUDIT_TEXT
