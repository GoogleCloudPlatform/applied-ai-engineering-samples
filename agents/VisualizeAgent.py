#This agent generates google charts code for displaying charts on web application

#Generates two charts with elements "chart-div" and "chart-div-1"

#Code is in javascript

from abc import ABC
from vertexai.language_models import CodeChatModel
from vertexai.generative_models import GenerativeModel,HarmCategory,HarmBlockThreshold
from .core import Agent 
from agents import ValidateSQLAgent 
import pandas as pd
import json  


class VisualizeAgent(Agent, ABC):

    agentType: str ="VisualizeAgent"

    def __init__(self):
        self.model_id = 'gemini-1.0-pro'
        self.model = GenerativeModel("gemini-1.0-pro-001")

    def getChartType(self,user_question, generated_sql):
        map_prompt=f'''
        You are expert in generated visualizations.

        Some commonly used charts and when do use them:

        Text or Score card is best for showing single value answer

        Table is best for Showing data in a tabular format.

        Bullet Chart is best for Showing individual values across categories.

        Bar Chart is best for Comparing individual values across categories, especially with many categories or long labels.

        Column Chart is best for Comparing individual values across categories, best for smaller datasets.

        Line Chart is best for Showing trends over time or continuous data sets with many data points.

        Area Chart is best for Emphasizing cumulative totals over time, or the magnitude of change across multiple categories.

        Pie Chart is best for Show proportions of a whole, but only for a few categories (ideally less than 6).

        Scatter Plot	is best for Investigating relationships or correlations between two variables.

        Bubble Chart	is best for Comparing and showing relationships between three variables.

        Histogram	is best for Displaying the distribution and frequency of continuous data.

        Map Chart	is best for Visualizing data with a geographic dimension (countries, states, regions, etc.).

        Gantt Chart	is best for Managing projects, visualizing timelines, and task dependencies.

        Heatmap is best for	Showing the density of data points across two dimensions, highlighting areas of concentration.


        Examples:

        Question: What are top 5 product skus that are ordered?
        SQL: SELECT  productSKU as ProductSKUCode, sum(total_ordered) as TotalOrderedItems
        FROM `inbq1-joonix.demo.sales_sku` group by productSKU order by sum(total_ordered) desc limit 5
        Answer: Bar Chart, Table Chart 

        Question: Which city had maximum number of sales?
        SQL: select st.city_id from retail.sales as s join retail.stores as st on s.id_store = st.id_store group by st.city_id order by count(*) desc limit 1;
        Answer: Table Chart, Bar Chart

        Question: Which products was sold most number of times?
        SQL: select\n  p.id_product,\n  count(p.id_product) as product_sales_count\nfrom\n  retail.sales as s\n  join retail.products as p on s.id_product = p.id_product\ngroup by\n  p.id_product\norder by\n  product_sales_count desc\nlimit\n  5;
        Answer: Bar Chart, Table Chart

        Question: What is the proportions of ethnicities enrolled in the program
        SQL: select\n  race as enthnicity, sum(enrolled_numbers) as enrolled_count from registration_tables
        Answer: Pie Chart, Bar Chart

        Guidelines:
        -Do not add any explanation to the response. Only stick to format Chart-1, Chart-2
        -Do not enclose the response with js or javascript or ```

        Below is the Question and corresponding SQL Generated, suggest best two of the chart types

        Question : {user_question}
        Corresponding SQL : {generated_sql}

        Respond using a valid JSON format with two elements chart_1 and chart_2 as below
        
        {{"chart_1":suggestion-1,
         "chart_2":suggestion-2}}

        
      '''
        chart_type=self.model.generate_content(map_prompt, stream=False).candidates[0].text
        # print(chart_type)
        # chart_type = model.predict(map_prompt, max_output_tokens = 1024, temperature= 0.2).candidates[0].text
        return chart_type.replace("\n", "").replace("```", "").replace("json", "").replace("```html", "").replace("```", "").replace("js\n","").replace("json\n","").replace("python\n","").replace("javascript","")

    def getChartPrompt(self,user_question, generated_sql, chart_type, chart_div, sql_results):
        return f'''
        You are expert in generated visualizations.
        
    Guidelines:
    -Do not add any explanation to the response.
    -Do not enclose the response with js or javascript or ```

    You are asked to generate a visualization for the following question:
    {user_question}

    The SQL generated for the question is:
    {generated_sql}

    The results of the sql which should be used to generate the visualization are in json format as follows:
    {sql_results}

    Needed chart type is  : {chart_type}

Guidelines:

   - Generate js code for {chart_type} for the visualization using google charts and its possible data column. You do not need to use all the columns if not possible.
   - The generated js code should be able to be just evaluated as javascript so do not add any extra text to it.
   - ONLY USE the template below and STRICTLY USE ELEMENT ID {chart_div} TO CREATE THE CHART

    google.charts.load('current', <add packages>);
    google.charts.setOnLoadCallback(drawChart);
    drawchart function 
        var data = <Datatable>
        with options
    Title=<<Give appropiate title>>
    width=600,
    height=300,
    hAxis.textStyle.fontSize=5
    vAxis.textStyle.fontSize=5
    legend.textStyle.fontSize=10

    other necessary options for the chart type

        var chart = new google.charts.<chart name>(document.getElementById('{chart_div}'));

        chart.draw()

    Example Response: 

   google.charts.load('current', {{packages: ['corechart']}});
   google.charts.setOnLoadCallback(drawChart);
    function drawChart() 
   {{var data = google.visualization.arrayToDataTable([['Product SKU', 'Total Ordered Items'],
     ['GGOEGOAQ012899', 456],   ['GGOEGDHC074099', 334], 
      ['GGOEGOCB017499', 319],    ['GGOEGOCC077999', 290], 
         ['GGOEGFYQ016599', 253],  ]); 
         
         var options =
          {{ title: 'Top 5 Product SKUs Ordered',  
           width: 600,   height: 300,    hAxis: {{     
           textStyle: {{       fontSize: 12    }} }},  
            vAxis: {{     textStyle: {{      fontSize: 12     }}    }},
               legend: {{    textStyle: {{       fontSize: 12\n      }}   }},  
                bar: {{      groupWidth: '50%'    }}  }};
                 var chart = new google.visualization.BarChart(document.getElementById('{chart_div}')); 
                  chart.draw(data, options);}}
        '''

    def generate_charts(self,user_question,generated_sql,sql_results):
        chart_type = self.getChartType(user_question,generated_sql)
        # chart_type = chart_type.split(",")
        # chart_list = [x.strip() for x in chart_type]
        chart_json = json.loads(chart_type)
        chart_list =[chart_json['chart_1'],chart_json['chart_2']]
        print("Charts Suggested : " + str(chart_list))
        context_prompt=self.getChartPrompt(user_question,generated_sql,chart_list[0],"chart_div",sql_results)
        context_prompt_1=self.getChartPrompt(user_question,generated_sql,chart_list[1],"chart_div_1",sql_results)
        safety_settings: Optional[dict] = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        context_query = self.model.generate_content(context_prompt,safety_settings=safety_settings, stream=False)
        context_query_1 = self.model.generate_content(context_prompt_1,safety_settings=safety_settings, stream=False)
        google_chart_js={"chart_div":context_query.candidates[0].text.replace("```json", "").replace("```", "").replace("json", "").replace("```html", "").replace("```", "").replace("js","").replace("json","").replace("python","").replace("javascript",""),
                        "chart_div_1":context_query_1.candidates[0].text.replace("```json", "").replace("```", "").replace("json", "").replace("```html", "").replace("```", "").replace("js","").replace("json","").replace("python","").replace("javascript","")}

        return google_chart_js

