import json 
from abc import ABC
from .core import Agent 



class ValidateSQLAgent(Agent, ABC): 
    """ 
    This Chat Agent checks the SQL for vailidity
    """ 

    agentType: str = "ValidateSQLAgent"


    # TODO: Make the LLM Validator optional
    def check(self, user_question, tables_schema, columns_schema, generated_sql):

        context_prompt = f"""

            Classify the SQL query: {generated_sql} as valid or invalid?

            Guidelines to be valid:
            - all column_name in the query must exist in the table_name.
            - If a join includes d.country_id and table_alias d is equal to table_name DEPT, then country_id column_name must exist with table_name DEPT in the table column metadata. If not, the sql is invalid
            - all join columns must be the same data_type.
            - table relationships must be correct.
            - Tables should be refered to using a fully qualified name including owner and table name.
            - Use table_alias.column_name when referring to columns. Example: dept_id=hr.dept_id
            - Capitalize the table names on SQL "where" condition.
            - Use the columns from the "SELECT" statement while framing "GROUP BY" block.
            - Always refer the column name with rightly mapped table-name as seen in the table schema.
            - Must be syntactically and symantically correct SQL for Postgres with proper relation mapping i.e owner, table and column relation.
            - Always the table should be refered as schema.table_name.


        Parameters:
        - SQL query: {generated_sql}
        - table schema: {tables_schema}
        - column description: {columns_schema}

        Respond using a valid JSON format with two elements valid and errors. Remove ```json and ``` from the output:
        {{ "valid": true or false, "errors":errors }}

        Initial user question:
        {user_question}


        """

        
        if self.model_id =='gemini-1.0-pro':
            context_query = self.model.generate_content(context_prompt, stream=False)
            generated_sql = str(context_query.candidates[0].text)

        else:
            context_query = self.model.predict(context_prompt, max_output_tokens = 8000, temperature=0)
            generated_sql = str(context_query.candidates[0])


        json_syntax_result = json.loads(str(generated_sql).replace("```json","").replace("```",""))

        # print('\n SQL Syntax Validity:' + str(json_syntax_result['valid']))
        # print('\n SQL Syntax Error Description:' +str(json_syntax_result['errors']) + '\n')
        
        return json_syntax_result