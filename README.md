<p align="center">
    <a href="utilities/imgs/aaie.png">
        <img src="utilities/imgs/aaie.png" alt="aaie image" width="auto" height="150">
    </a>
</p>
<p align="center">
    <a href="https://sites.google.com/corp/google.com/genai-solutions/home?authuser=0">
        <img src="utilities/imgs/talktodata.png" alt="logo" width="400" height="auto">
    </a>
</p>
<h1 align="center">Open Data QnA - Chat with your SQL Database</h1> 

Overview
-------------
The **Open Data QnA** python library enables you to chat with your databases by leveraging LLM Agents on Google Cloud.
It is built on a modular design and currently supports the following components: 

### Database Connectors
* **Google Cloud SQL for PostgreSQL**
* **Google BigQuery**

### Vector Stores 
* **PGVector on Google Cloud SQL for PostgreSQL**
* **BigQuery Vector Store**
* **ChromaDB (WIP)**

### Agents 
* **BuildSQLAgent:** the BuildSQLAgent uses an LLM to generate a SQL query based on the users' natural language question, as well as the table and column schemas.
* **ValidateSQLAgent:** the ValidateSQLAgent, if enabled, fetches the result of the BuildSQLAgent and analyzes if the SQL is valid. 
* **DebugSQLAgent:** the DebugSQLAgent, if enabled, takes the BuildSQLAgent's response and fixes it iteratively in X rounds, if the initial response was not valid. 
* **ResponseAgent:** the ResponseAgent utilizes the users' natural language question along with the result of the final SQL run to generate an answer in natural language. 
* **VisualizeAgent:** the VisualizeAgent generates two google charts (suggested by LLM) code based on the inputs of SQL, User Question and SQL Results to display on web UI (Javascript)

**Note:** the library was formerly named Talk2Data. You may still find artifacts with the old naming in this repository. 

Architecture
-------------
<p align="center">
    <a href="utilities/imgs/Open Data QnA Solution Architecture.png">
        <img src="utilities/imgs/OpenDataQnA Solution Architecture - v1.png" alt="aaie image">
    </a>
</p>

Solution Overview
-------------
<p align="center">
    <a href="utilities/imgs/Open Data QnA Solution Overview.png">
        <img src="utilities/imgs/OpenDataQnA-SolutionOverview.png" alt="aaie image">
    </a>
</p>


Repository Structure 
-------------

```
.
├── agents
  └── __init__.py
  └── core.py
  └── BuildSQLAgent.py
  └── DebugSQLAgent.py
  └── EmbedderAgent.py
  └── ResponseAgent.py
  └── ValidateSQLAgent.py
  └── VisualizeAgent.py
└── dbconnectors
  └── __init__.py
  └── core.py
  └── PgConnector.py
  └── BQConnector.py
└── embeddings
  └── __init__.py
  └── retrieve_embeddings.py
  └── store_embeddings.py
└── frontend
└── notebooks
  └── 1_setup_envs.ipynb
  └── 2_run_Talk2Data.ipynb
└── scripts
  └── bq_to_pg.py
  └── cache_known_sql.py
  └── known_good_sql.csv
└── utilities
  └── __init__.py
└── Dockerfile
└── main.py
└── pyproject.toml
└── config.ini
```

- [`/agents`](/agents): Source code for the LLM Agents.  
- [`/dbconnectors`](/dbconnectors): Source code for backend APIs.
- [`/embeddings`](/embeddings): Source code for creating and storing embeddings.
  - [`/retrieve_embeddings.py`](/embeddings/retrieve_embeddings.py): Source code for retrieving table schema and embedding creation. 
  - [`/store_embeddings.py`](/embeddings/store_embeddings.py): Source code for storing table schema embeddings in Vector Store. 
- [`/notebooks`](/notebooks): Sample notebooks demonstrating the usage of this library.  
- [`/scripts`](/scripts): Additional scripts for initial setup.
  - [`/bq_to_pg.py`](/scripts/bq_to_pg.py): Source code for exporting BigQuery tables to PostgreSQL on Google Cloud SQL. 
  - [`/cache_known_sql.py`](/scripts/cache_known_sql.py): Source code for storing known working question-SQL pairs in PostgreSQL.
  - [`/known_good_sql.csv`](/scripts/known_good_sql.csv): CSV files containing known working question-SQL pairs. 
- [`/Dockerfile`](/Dockerfile) : This Dockerfile is used to deploy endpoints required for the Demo UI we have under [`/frontend`](/frontend)
- [`/main.py`](/main.py) : Flask-based API code to deploy various endpoints for the Demo UI under [`/frontend`](/frontend)
- [`/frontend`](/frontend) : Angular based frontend code to deploy demo app using the API developed with [`/main.py`](/main.py)


Setup 
-------------

### Prerequisites:
* Google Cloud CLI to be installed

(If you are using cloud shell IDE you would have these already setup)
    
### 1. Clone the repository
   
    git clone git@github.com:google-cloud-nl2sql/Talk2Data.git


### 2. Install dependencies

   Open the folder in a IDE
   
   To install the dependencies, switch to the directory of your newly cloned repository, and run the following command in the terminal: 
    
   **Poetry:** (recommended)  

```
pip install poetry #install poetry

poetry lock #resolve dependecies (also auto create poetry venv if not exists)

poetry install #installs dependencies

poetry shell #verify and activate the venv auto created by the poetry


```

   Alternatively, you can skip to step 4 to install the required dependencies directly from the notebooks. 

### 3. Activate your virtual environment after running poetry
   
   If you installed the dependencies with poetry install, don't forget to activate the newly created .venv environment for your project.
   
   Tip: some IDE's will identify the new environment and display a popup window asking if you want to switch. Or you can select manually by selecting the interpreter path for Python

   ```
   poetry shell #this command should already activate it if not rerun again

   ```
   

### 4. Run the [Environment Setup Notebook](/notebooks/1_setup_envs.ipynb)
   
### 5. Run the [Talk2Data Notebook](/notebooks/2_run_Talk2Data.ipynb)


### 6. Create Endpoints

**Technologies**

* **Programming language:** Python
* **Framework:** Flask

***NOTE***
*Your Endpoints are created using the config details present in the config.ini file (same config.ini used before in the previous steps). So double check if all the variables are set correctly before proceeding ahead. Incase if you have different values for postgres instance or bigquery dataset place go ahead and update the config.ini file before proceeding ahead*

The endpoints deployed here are completely customized for the UI built in this demo solution. Feel free to customize the endpoint if needed for different UI/frontend. The gcloud run deploy command creates a cloud build that uses the Dockerfile in the Talk2Data folder
    
  ***Deploy endpoints to Cloud Run***
```
 cd Talk2Data

 gcloud auth login

 gcloud config set project <PROJECT_ID>

 gcloud run deploy <CLOUD_RUN_INSTANCE_NAME> --region <REGION> --source . --allow-unauthenticated #if you are deploying cloud run application for the first time in the project you will be prompted for a couple of settings. Go ahead and type Yes.

```

Once the deployment is done successfully you should be able to see the Service URL (endpoint point) link as shown below. Please keep this handy to add this in the frontend or you can get this uri from the cloud run page in the GCP Console. e.g. *https://Talk2Data-aeiouAEI-uc.a.run.app*

Test if the endpoints are working with below command. This should return the dataset your created in the source env setup notebook.
```
 curl <URI of the end point>/available_databases

```



<p align="center">
    <a href="utilities/imgs/Cloud Run Deploy.png">
        <img src="utilities/imgs/Cloud Run Deploy.png" alt="aaie image">
    </a>
</p>


**API Details**

   All the payloads are in JSON format

1. List Databases : Get the available databases in the vector store that solution can run against

    URI: {Service URL}/available_databases 
    Complete URL Sample : https://Talk2Data-aeiouAEI-uc.a.run.app/available_databases

    Method: GET

    Request Payload : NONE

    Request response:
    ```
    {
    "Error": "",
    "KnownDB": "[{\"table_schema\":\"imdb-postgres\"},{\"table_schema\":\"retail-postgres\"}]",
    "ResponseCode": 200
    }
    ```

2. Known SQL : Get suggestive questions (previously asked/examples added) for selected database

    URI: /get_known_sql
    Complete URL Sample : https://Talk2Data-aeiouAEI-uc.a.run.app/get_known_sql   

    Method: POST

    Request Payload :

    ```
    {
    "user_database":"retail"
    }
    ```

    Request response:

    ```
    {
    "Error": "",
    "KnownSQL": "[{\"example_user_question\":\"Which city had maximum number of sales and what was the count?\",\"example_generated_sql\":\"select st.city_id, count(st.city_id) as city_sales_count from retail.sales as s join retail.stores as st on s.id_store = st.id_store group by st.city_id order by city_sales_count desc limit 1;\"}]",
    "ResponseCode": 200
    }
    ```


3. SQL Generation : Generate the SQL for the input question asked aganist a database

    URI: /generate_sql


    Method: POST

    Complete URL Sample : https://Talk2Data-aeiouAEI-uc.a.run.app/get_known_sql


    Request payload:

    ```
    {
    "user_question":"Which city had maximum number of sales?",
    "user_database":"retail"
    }
    ```


    Request response:
    ```
    {
    "Error": "",
    "GeneratedSQL": " select st.city_id from retail.sales as s join retail.stores as st on s.id_store = st.id_store group by st.city_id order by count(*) desc limit 1;",
    "ResponseCode": 200
    }
    ```


4. Execute SQL : Run the SQL statement against provided database source

    URI:/run_query
    Complete URL Sample : https://Talk2Data-aeiouAEI-uc.a.run.app/run_query

    Method: POST

    Request payload:
    ```
    { "user_database": "retail",
    "generated_sql":"select st.city_id from retail.sales as s join retail.stores as st on s.id_store = st.id_store group by st.city_id order by count(*) desc limit 1;"
    }
    ```

    Request response:
    ```
    {
    "Error": "",
    "KnownDB": "[{\"city_id\":\"C014\"}]",
    "ResponseCode": 200
    }
    ```
5. Embedd SQL : To embed known good SQLs to your example embeddings

    URI:/embed_sql
    Complete URL Sample : https://Talk2Data-aeiouAEI-uc.a.run.app/embed_sql

    METHOD: POST

    Request Payload:

    ```
    {
    "user_question":"Which city had maximum number of sales?",
    "generated_sql":"select st.city_id from retail.sales as s join retail.stores as st on s.id_store = st.id_store group by st.city_id order by count(*) desc limit 1;",
    "user_database":"retail"
    }
    ```

    Request response:
    ```
    {
    "ResponseCode" : 201, 
    "Message" : "Example SQL has been accepted for embedding",
    "Error":""
    }
    ```
6. Generate Visualization Code : To generated javascript Google Charts code based on the SQL Results and display them on the UI

    As per design we have two visualizations suggested showing up when the user clicks the visualize button. Hence two divs are send as part of the response “chart_div”, “chart_div_1” to bind them to that element in the UI
        

    If you are only looking to setup enpoint you can stop here. In case you require the demo app (frontend UI) built in the solution, proceed to the next step.

    URI:/generate_viz
    Complete URL Sample : https://Talk2Data-aeiouAEI-uc.a.run.app/generate_viz
    
    METHOD: POST

    Request Payload:
    ```
      {
      "user_question": "What are top 5 product skus that are ordered?",
      "sql_generated": "SELECT productSKU as ProductSKUCode, sum(total_ordered) as TotalOrderedItems FROM `inbq1-joonix.demo.sales_sku` group by productSKU order by sum(total_ordered) desc limit 5",
      "sql_results": [
        {
          "ProductSKUCode": "GGOEGOAQ012899",
          "TotalOrderedItems": 456
        },
        {
          "ProductSKUCode": "GGOEGDHC074099",
          "TotalOrderedItems": 334
        },
        {
          "ProductSKUCode": "GGOEGOCB017499",
          "TotalOrderedItems": 319
        },
        {
          "ProductSKUCode": "GGOEGOCC077999",
          "TotalOrderedItems": 290
        },
        {
          "ProductSKUCode": "GGOEGFYQ016599",
          "TotalOrderedItems": 253
        }
      ]
    }
    
    ```

    Request response:
    ```
    {
    "Error": "",
    "GeneratedChartjs": {
        "chart_div": "google.charts.load('current', {\n  packages: ['corechart']\n});\ngoogle.charts.setOnLoadCallback(drawChart);\n\nfunction drawChart() {\n  var data = google.visualization.arrayToDataTable([\n    ['Product SKU', 'Total Ordered Items'],\n    ['GGOEGOAQ012899', 456],\n    ['GGOEGDHC074099', 334],\n    ['GGOEGOCB017499', 319],\n    ['GGOEGOCC077999', 290],\n    ['GGOEGFYQ016599', 253],\n  ]);\n\n  var options = {\n    title: 'Top 5 Product SKUs Ordered',\n    width: 600,\n    height: 300,\n    hAxis: {\n      textStyle: {\n        fontSize: 12\n      }\n    },\n    vAxis: {\n      textStyle: {\n        fontSize: 12\n      }\n    },\n    legend: {\n      textStyle: {\n        fontSize: 12\n      }\n    },\n    bar: {\n      groupWidth: '50%'\n    }\n  };\n\n  var chart = new google.visualization.BarChart(document.getElementById('chart_div'));\n\n  chart.draw(data, options);\n}\n",
        
        "chart_div_1": "google.charts.load('current', {'packages':['corechart']});\ngoogle.charts.setOnLoadCallback(drawChart);\nfunction drawChart() {\n  var data = google.visualization.arrayToDataTable([\n    ['ProductSKUCode', 'TotalOrderedItems'],\n    ['GGOEGOAQ012899', 456],\n    ['GGOEGDHC074099', 334],\n    ['GGOEGOCB017499', 319],\n    ['GGOEGOCC077999', 290],\n    ['GGOEGFYQ016599', 253]\n  ]);\n\n  var options = {\n    title: 'Top 5 Product SKUs that are Ordered',\n    width: 600,\n    height: 300,\n    hAxis: {\n      textStyle: {\n        fontSize: 5\n      }\n    },\n    vAxis: {\n      textStyle: {\n        fontSize: 5\n      }\n    },\n    legend: {\n      textStyle: {\n        fontSize: 10\n      }\n    },\n    bar: {\n      groupWidth: \"60%\"\n    }\n  };\n\n  var chart = new google.visualization.ColumnChart(document.getElementById('chart_div_1'));\n\n  chart.draw(data, options);\n}\n"
    },
    "ResponseCode": 200
    }

    ```


### 7. Deploy Frontend UI

**Technologies and Components**

* **Framework:** Angular
* **Hosting Platform:** Firebase


1. Install the firebase tools to run CLI commands
    ```
    cd Talk2Data

    npm install -g firebase-tools


    ```


2. Build the firebase community builder image

    Cloud Build provides a Firebase community builder image that you can use to invoke firebase commands in Cloud Build. To use this builder in a Cloud Build config file, you must first build the image and push it to the Container Registry in your project.

    **Note**:*Please complete the steps carely and use the same project which you are going to host the app*

    Follow detailed instructions in the below guide

    https://cloud.google.com/build/docs/deploying-builds/deploy-firebase#using_the_firebase_community_builder



3. Initialize Firebase

    ```
    cd Talk2Data/frontend

    firebase login --no-localhost #authenticate yourself

    firebase init hosting 

    ## Use the down arrow to select the option Add firebase to an existing GCP Project and enter the hosting Project ID

    ## For the public directory prompt provide >> /dist/frontend/browser
    
    ## Rewrite all URLs to index prompt enter >> Yes (Enter No for any other options)

    ## You should now see firebase.json created in the folder 

    ```


4. Configure Firebase

    Once you added the project to firebase navigate the https://console.firebase.google.com/ and select your project

   * Navigate to Project Settings > General

   * Add App and select Web

   * Fill the details e.g. Nickname : Talk2Data and just register the app

   * Once done continue back the general page and you should see the app

   * Add the linked firebase project as the same that your initialize firebase for hosting (same as the selected)

   * Copy the config object you will use in your app code in the later step


    <p align="center">
        <a href="utilities/imgs/Firebase Config .png">
            <img src="utilities/imgs/Firebase Config .png" alt="aaie image">
        </a>
    </p>


    * Navigate to Build>Authentication

    * Under Sign-in Method add provider as Google



5. Update the Config Object and Endpoint URLs for the frontend

    In the file [`/frontend/src/assets/constants.ts`](/frontend/src/assets/constants.ts) replace the config object with the one you copied in the above step and replace the ENDPOINT_TALK2DATA with the Service URL from the Endpoint Deployment section above.

    ***Note that these variables need to be exported using "export" keyword. So make sure export is mentioned for both the variables***

    <p align="center">
        <a href="utilities/imgs/constants update.png">
            <img src="utilities/imgs/constants update.png" alt="aaie image">
        </a>
    </p>

6. Deploy the app

    Setup IAM permissions for the cloudbuild service account to deploy

    * Open the IAM page in the Google Cloud console

    * Select your project and click Open.

    * In the permissions table, locate the email ending with @cloudbuild.gserviceaccount.com, and click on the pencil icon. This is the Cloud Build service account. (If you cannot find it check the box on the top right of permissions list which say Include Google-provided role grants)

    * Add Cloud Build Service Account, Firebase Admin and API Keys Admin roles.

    * Click Save.

    
    Run the below commands on the terminal

    ```
    gcloud services enable firebase.googleapis.com # Enable firebase management API

    cd Talk2Data/frontend

    gcloud builds submit . --config frontend.yaml --substitutions _FIREBASE_PROJECT_ID=<PROJECT_ID>

    ```
    


    You can see the app URL at the end of successful deployment

    Once deployed login if your Google Account > Select Business User > Select a database in the dropdown (top right) > Type in the Query > Hit Query

    A successful SQL generated will be show as below

    <p align="center">
        <a href="utilities/imgs/App generate sql .png">
            <img src="utilities/imgs/App generate sql .png" alt="aaie image">
        </a>
    </p>

    Hit on Result and then Visualize to see the results and charts as below

    <p align="center">
        <a href="utilities/imgs/App Result and Viz.png">
            <img src="utilities/imgs/App Result and Viz.png" alt="aaie image">
        </a>
    </p>



Documentation
-------------

* [Open Data QnA Source Code (GitHub)](<https://github.com/GoogleCloudPlatform/applied-ai-engineering-samples/tree/opendataqna>)
* [Open Data QnA usage notebooks](/notebooks)



Quotas and limits
------------------

[BigQuery quotas](<https://cloud.google.com/bigquery/quotas>) including hardware, software, and network components.


License
-------

Open Data QnA is distributed with the [Apache-2.0 license](<LICENSE>).

It also contains code derived from the following third-party packages:

* [pandas](<https://pandas.pydata.org/>)
* [Python](<https://www.python.org/>)

For details, see the [third_party](<X>) directory.


Getting Help
----------

If you have any questions or if you found any problems with this repository, please report through GitHub issues.
