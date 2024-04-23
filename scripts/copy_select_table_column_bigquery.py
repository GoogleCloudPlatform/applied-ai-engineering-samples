import pandas as pd
from google.cloud import bigquery

def copy_tables(project_id, source_dataset, destination_dataset, df):
   
   client = bigquery.Client()
   unique_table_names = df['TableName'].unique()

   for table_name in unique_table_names:
      print(f"Processing table: {table_name}")
      dest_table_id = f"{project_id}.{destination_dataset}.{table_name}"
      orig_table_id = f"{project_id}.{source_dataset}.{table_name}"

      # Copy the table (all columns initially)
      job = client.copy_table(orig_table_id, dest_table_id)  
      job.result() 

      # Get columns to preserve
      columns_to_preserve = df[df['TableName'] == table_name]['ColumnName'].tolist()

      # Drop unwanted columns 
      dest_table = client.get_table(dest_table_id)
      all_columns = [c.name for c in dest_table.schema]
      for column in all_columns:
         print(f'Cheking if column {column} should be preserved')
         if column not in columns_to_preserve:
               query = f"ALTER TABLE {dest_table_id} DROP COLUMN IF EXISTS {column}"
               client.query(query).result()  

      # Update descriptions
      for column_name in columns_to_preserve:
         print(f'Updating description for column {column_name}')
         description = df[(df['TableName'] == table_name) & (df['ColumnName'] == column_name)]['Description'].iloc[0]
         query = f"""
         ALTER TABLE {dest_table_id} 
         ALTER COLUMN {column_name} SET OPTIONS(description='{description}')
         """

         try:
            client.query(query).result()  
         except Exception as e:
             print(f"An error occurred while additon desciption to the column {column_name} in table {dest_table_id}: {e}")


def add_table_description(project_id, dataset, df):
   
   client = bigquery.Client()

   for _, row in df.iterrows():
      table_name = row['TableName']
      table_description = row['TableDescription']
      table_id = f"{project_id}.{dataset}.{table_name}"

      print(f'Updating description for Table - {table_name}')
      query = f"""
      ALTER TABLE {table_id} SET OPTIONS(description='{table_description}')
      """

      try:
         client.query(query).result()  
      except Exception as e:
            print(f"An error occurred while additon desciption to the column {column_name} in table {table_id}: {e}")


def add_column_description(project_id, dataset, df):
   
   client = bigquery.Client()

   for _, row in df.iterrows():
      table_name = row['TableName']
      column_name = row['ColumnName']
      column_description = row['ColumnDescription']
      table_id = f"{project_id}.{dataset}.{table_name}"

      print(f'Updating description for Column - {table_name}.{column_name}')
      query = f"""
      ALTER TABLE {table_id} 
      ALTER COLUMN {column_name} SET OPTIONS(description='{column_description}')
      """

      try:
         client.query(query).result()  
      except Exception as e:
            print(f"An error occurred while additon desciption to the column {column_name} in table {table_id}: {e}")



if __name__ == "__main__":

   import os
   current_dir = os.path.dirname(__file__)

   # --- Read 'TablesAndColumns' sheet from Excel ---
   file_path = f"{current_dir}/tables_columns_descriptions.csv"
   df = pd.read_csv(file_path)

   # --- Drop rows with null values ---
   df.dropna(subset=['TableName', 'ColumnName'], inplace=True)

   # --- BigQuery setup ---
   client = bigquery.Client()
   project_id = "premi0537540-gitgbide" 
   source_dataset = "ds_sales_poc"
   destination_dataset = "google_demo" 

   # # Copy Tables
   # copy_tables(project_id, source_dataset, 
   #             destination_dataset, 
   #             df=df)


   # Add table descriptions
   df_table_desc = df[['TableName', 'TableDescription']]  # Select required columns
   df_table_desc = df_table_desc.dropna()  # Handle missing ColumnDescriptions (optional)
   df_table_desc = df_table_desc.drop_duplicates(subset=['TableName', 'TableDescription'])  # Drop duplicate table-column pairs

   add_table_description(project_id, destination_dataset, df_table_desc)

   # Add column descriptions
   df_col_desc = df[['TableName', 'ColumnName', 'ColumnDescription']]  # Select required columns
   df_col_desc = df_col_desc.dropna()  # Handle missing ColumnDescriptions (optional)
   df_col_desc = df_col_desc.drop_duplicates(subset=['TableName', 'ColumnName'])  # Drop duplicate table-column pairs

   add_column_description(project_id, destination_dataset, df_col_desc)