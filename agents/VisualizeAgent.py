#This agent generates google charts code for displaying charts on web application

#Generates two charts with elements "chart-div" and "chart-div-1"

#Code is in javascript

from abc import ABC
from vertexai.preview.language_models import CodeChatModel
from vertexai.preview.generative_models import GenerativeModel
from .core import Agent 
from agents import ValidateSQLAgent 
import pandas as pd
import json  


class VisualizeAgent(Agent, ABC):

    agentType: str ="VisualizeAgent"

    def __init__(self):
        self.model_id = 'gemini-pro'
        self.model = GenerativeModel("gemini-pro")

    def getChartType(self,user_question, generated_sql):
        map_prompt=f'''
        You are expert in generated visualizations.

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
        Chart Type: Bar Chart

        Question: Which city had maximum number of sales?
        SQL: select st.city_id from retail.sales as s join retail.stores as st on s.id_store = st.id_store group by st.city_id order by count(*) desc limit 1;
        Chart Type: Table Chart

        Question: Which product had maximum number of sales?
        SQL: select\n  p.id_product,\n  count(p.id_product) as product_sales_count\nfrom\n  retail.sales as s\n  join retail.products as p on s.id_product = p.id_product\ngroup by\n  p.id_product\norder by\n  product_sales_count desc\nlimit\n  1;
        Chart Type: Table Chart

        Question: Which products was sold most number of times?
        SQL: select\n  p.id_product,\n  count(p.id_product) as product_sales_count\nfrom\n  retail.sales as s\n  join retail.products as p on s.id_product = p.id_product\ngroup by\n  p.id_product\norder by\n  product_sales_count desc\nlimit\n  5;
        Chart Type: Bar Chart

        Question: Which unique products share same parent hierarchy?
        SQL: select distinct\n  T1.ID_PRODUCT\nfrom\n  RETAIL.PRODUCTS AS T1\n  INNER JOIN RETAIL.PRODUCTS AS T2 ON T1.HIERARCHY1_ID = T2.HIERARCHY1_ID\nwhere\n  T1.ID_PRODUCT <> T2.ID_PRODUCT;
        Chart Type: Table Chart

        Question: Which city has maximum number of stores?
        SQL: select\n  count(retail.stores.city_id),\n  retail.stores.city_id\nfrom\n  retail.stores\ngroup by\n  2\norder by\n  1 desc\nlimit\n  1
        Chart Type: Table Chart

        You are asked to generate a visualization for the following question:
        {user_question}
        The SQL generated for the question is:
        {generated_sql}

        Based on the Question and SQL Generated suggest best two of the chart types from below

        Table
        Bullet Chart
        Bar Chart
        Column Chart
        Line Chart
        Area Chart
        Pie Chart
        Scatter Chart
        Bubble Chart
        Histogram
        Map Chart
        Gantt Chart
        Heatmap

        Response should in below format
        Chart-1, Chart-2
      '''
        chart_type=self.model.generate_content(map_prompt, stream=False).candidates[0].text
        # chart_type = model.predict(map_prompt, max_output_tokens = 1024, temperature= 0.2).candidates[0].text
        return chart_type.replace("```json", "").replace("```", "").replace("json", "").replace("```html", "").replace("```", "").replace("js\n","").replace("json\n","").replace("python\n","").replace("javascript\n","")

    def getChartPrompt(self,user_question, generated_sql, chart_type, chart_div, sql_results):
        return f'''
        You are expert in generated visualizations.

    You are asked to generate a visualization for the following question:
    {user_question}

    The SQL generated for the question is:
    {generated_sql}

    The results of the sql which should be used to generate the visualization are in json format as follows:
    {sql_results}

    Needed chart type is  : {chart_type}

    Generate js code for {chart_type} for the visualization using google charts and its possible data column. You do not need to use all the columns if not possible.
    
    ONLY USE the template below and STRICTLY USE ELEMENT ID {chart_div} TO CREATE THE CHART

    google.charts.load('current', <add packages>);
    google.charts.setOnLoadCallback(drawChart);
    drawchart function \
        var data = <Datatable>\
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
        '''

    def generate_charts(self,user_question,generated_sql,sql_results):
        chart_type = self.getChartType(user_question,generated_sql)

        chart_type = chart_type.split(",")
        chart_list = [x.strip() for x in chart_type]

        context_prompt=self.getChartPrompt(user_question,generated_sql,chart_list[0],"chart_div",sql_results)
        context_prompt_1=self.getChartPrompt(user_question,generated_sql,chart_list[1],"chart_div_1",sql_results)

        context_query = self.model.generate_content(context_prompt, stream=False)
        context_query_1 = self.model.generate_content(context_prompt_1, stream=False)
        google_chart_js={"chart_div":context_query.candidates[0].text.replace("```json", "").replace("```", "").replace("json", "").replace("```html", "").replace("```", "").replace("js\n","").replace("json\n","").replace("python\n","").replace("javascript\n",""),
                        "chart_div_1":context_query_1.candidates[0].text.replace("```json", "").replace("```", "").replace("json", "").replace("```html", "").replace("```", "").replace("js\n","").replace("json\n","").replace("python\n","").replace("javascript\n","")}

        return google_chart_js

