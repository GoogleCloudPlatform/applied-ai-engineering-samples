import json 
from abc import ABC
from .core import Agent 
from vertexai.generative_models import HarmCategory, HarmBlockThreshold

class ResponseAgent(Agent, ABC): 
    """ 
    This Chat Agent checks the SQL for vailidity
    """ 

    agentType: str = "ResponseAgent"

    # TODO: Make the LLM Validator optional
    def run(self, user_question, sql_result):

        context_prompt = f"""

            You are a Data Assistant that helps to answer users' questions on their data within their databases.
            The user has provided the following question in natural language: "{str(user_question)}"

            The system has returned the following result after running the SQL query: "{str(sql_result)}".

            Provide a natural sounding response to the user to answer the question with the SQL result provided to you.
        """


        if self.model_id =='gemini-1.0-pro':
            context_query = self.model.generate_content(context_prompt,safety_settings=self.safety_settings, stream=False)
            generated_sql = str(context_query.candidates[0].text)

        else:
            context_query = self.model.predict(context_prompt, max_output_tokens = 8000, temperature=0)
            generated_sql = str(context_query.candidates[0])
        
        return generated_sql

    def generate_missing_descriptions(self,source,table_desc_df, column_name_df):
        llm_generated=0
        for index, row in table_desc_df.iterrows():
            if row['table_description'] is None or row['table_description']=='NA':
                q=f"table_name == '{row['table_name']}' and table_schema == '{row['table_schema']}'"
                if source=='bigquery':
                    context_prompt = f"""
                        Generate table description short and crisp for the table {row['project_id']}.{row['table_schema']}.{row['table_name']}
                        Remember that these desciprtion should help LLMs to help build better SQL for any quries related to this table.
                        Parameters:
                        - column metadata: {column_name_df.query(q).to_markdown(index = False)}
                        - table metadata: {table_desc_df.query(q).to_markdown(index = False)}
                        
                        DO NOT generate description more than two lines
                    """
                else:
                     context_prompt = f"""
                        Generate table description short and crisp for the table {row['table_schema']}.{row['table_name']}
                        Remember that these desciprtion should help LLMs to help build better SQL for any quries related to this table.
                        Parameters:
                        - column metadata: {column_name_df.query(q).to_markdown(index = False)}
                        - table metadata: {table_desc_df.query(q).to_markdown(index = False)}

                        DO NOT generate description more than two lines
                    """

                table_desc_df.at[index,'table_description']=self.generate_llm_response(context_prompt)
                # print(row['table_description'])
                llm_generated=llm_generated+1
        print("\nLLM generated "+ str(llm_generated) + " Table Descriptions")
        llm_generated = 0
        for index, row in column_name_df.iterrows():
            # print(row['column_description'])
            if row['column_description'] is None or row['column_description']=='':
                q=f"table_name == '{row['table_name']}' and table_schema == '{row['table_schema']}'"
                if source=='bigquery':
                    context_prompt = f"""
                    Generate short and crisp description for the column {row['project_id']}.{row['table_schema']}.{row['table_name']}.{row['column_name']}

                    Remember that this description should help LLMs to help generate better SQL for any queries related to these columns.

                    Consider the below information to generate a good comment

                    Name of the column : {row['column_name']}
                    Data type of the column is : {row['data_type']}
                    Details of the table of this column are below:
                    {table_desc_df.query(q).to_markdown(index=False)}
                    Column Contrainst of this column are : {row['column_constraints']}

                    DO NOT generate description more than two lines
                """
                else:
                    context_prompt = f"""
                    Generate short and crisp description for the column {row['table_schema']}.{row['table_name']}.{row['column_name']}

                    Remember that this description should help LLMs to help generate better SQL for any queries related to these columns.

                    Consider the below information to generate a good comment

                    Name of the column : {row['column_name']}
                    Data type of the column is : {row['data_type']}
                    Details of the table of this column are below:
                    {table_desc_df.query(q).to_markdown(index=False)}
                    Column Contrainst of this column are : {row['column_constraints']}

                    DO NOT generate description more than two lines
                """

                column_name_df.at[index,'column_description']=self.generate_llm_response(prompt=context_prompt)
                # print(row['column_description'])
                llm_generated=llm_generated+1
        print("\nLLM generated "+ str(llm_generated) + " Column Descriptions")
        return table_desc_df,column_name_df