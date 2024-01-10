from generate_dei import generate_sql_answer, generate_dei_paragraph
from generate import make_docx
from vertex_search_retrieval import vertex_search_response
from chat_html import get_chat_html
from retrieve_bq_df import bq_to_df
from st_aggrid import AgGrid
import streamlit as st
import pandas as pd
import os

df = bq_to_df() 


###_____________MAIN PAGE_____________### 
# PAGE CONFIG  
st.set_page_config(
    page_title="Compliant ESG Reporting",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# TITLE AND ICON 
left, right = st.columns(2)
left.title('Compliant ESG Reporting')
st.text("")


# VISIBILITY CONFIG 
if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False

l, m, r = st.columns(3)
MODEL = l.selectbox(
    'Which model do you want to use?',
    ('gemini-pro','text-bison@001', 'text-bison@002'))

st.text("")


# TABS 
tab1, tab2, tab3 = st.tabs(["Explore", "Build", "Comply"])

st.text("")
st.text("")




###_____________EXPLORE_____________### 
with tab1: 

    st.subheader('Explore your knowledge base', divider='rainbow')
    st.text("")
    
    extab1, extab2, extab3 = st.tabs(["Search your Documents", "Chat with your Documents", "Chat with your Database"])

    with extab1: 
        st.text("")

        l,m,r = st.columns(3)

        l.info('Connected to Document Storage', icon="ℹ️")

        l2, r2 = st.columns(2)

        text_search = l2.text_input(        
        "Search",
        label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,
        placeholder="Explore your Documents...",
        )

        if text_search:
            try: 
                model_response = vertex_search_response(MODEL, search_query=text_search)
                st.write("ANSWER: ", model_response)

            
            except: 
                st.write("Something went wrong. Please try again.")


    with extab2: 
        st.text("")

        l,m,r = st.columns(3)
        l.info('Connected to Document Storage', icon="ℹ️")

        # Retrieve Chat Widget 
        from streamlit.components.v1 import html
        my_html = get_chat_html()
        html(my_html, height=600) 
        

    with extab3: 
        st.text("")

        l,m,r = st.columns(3)
        l.info('Connected to BigQuery DEI Table', icon="ℹ️")
        
        l2, r2 = st.columns(2)

        text_input = l2.text_input(
        "Query",
        label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,
        placeholder="Enter your NL query here",
        )

        if text_input:
            try: 
                 answer = generate_sql_answer(text_input, MODEL = MODEL)
                 st.write("ANSWER: ", answer)

            
            except: 
                 st.write("Couldn't process NL query. Did you ask for information that is present in the database?")

        ag1 = AgGrid(df, key="ag1")



###_____________BUILD_____________### 
with tab2: 
    st.subheader('Build your Report', divider='rainbow')
    st.text("")

    l,m,r = st.columns(3)

    l.info('Connected to BigQuery DEI Table', icon="ℹ️")


    gtab1, gtab2 = st.tabs(["Build your report", "Check your data"])

    with gtab1: 
        prompt = st.text_area(
        "Report Generation Prompt",
        """You are an ESG consulter that's writing the diversity section of the 2023 ESG report. With the data provided to you, write a short abstract with roughly 500 words about Googles Diversity mission, the stats in 2023 and the differences compared to the previous year. Include the representation of women in different roles as well as the representation of underrepresented groups.""")

        if st.button('Build Report'): 
            with st.spinner('Your report is being built...'):

                try: 

                    response = generate_dei_paragraph(prompt, MODEL=MODEL)
                    # st.success('Done!')

                    st.write(response)

                except: 
                    st.write("Sorry. Something went wrong. Please try a different prompt")

    with gtab2: 
        ag2 = AgGrid(df, key="ag2")



###_____________COMPLY_____________### 
with tab3: 
    st.subheader('Answer the CDP Questionnaire', divider='rainbow')
    st.text("")

    left_column, right_column = st.columns(2)

    doc_path = None
    
    ### FILE SELECTION 
    uploaded_template = left_column.selectbox(
    'Please select the template file',
    ("CDP.docx", ""))
    doc_path = "Files/CDP.docx"

    # ### FILE UPLOAD ### 
    # uploaded_template = left_column.file_uploader("Upload the CDP Template")
    
    # if uploaded_template is not None:
    #     name = uploaded_template.name
    #     doc_path = "Files/"+name
    #     st.write(doc_path)

    

    ### GENERATE BUTTON ### 
    # st.button('Generate')
    st.text("")

    if st.button('Generate CDP Report'): 
        if doc_path is not None: 
            with st.spinner('Report is being generated...'):

                resulting_file = make_docx(MODEL, doc_path)

                st.success('Done!')


                st.write(f"Report Generated under {resulting_file}. You can also download it below.")

                ### DOWNLOAD ###
                with open(resulting_file, 'rb') as f:
                    st.download_button('Download Docx', f, file_name="result.docx")
                # st.download_button('Download', str(generate_output))

        else: 
            st.write("You have to upload a file first.")
        





###_____________SIDEBAR_____________###

st.sidebar.image("Files/Images/Title.png", width= 250)

st.sidebar.header('Explore', divider='rainbow')
st.sidebar.markdown('Explore your knowledge bases and develop an understanding of your ESG data.')

st.sidebar.header('Build', divider='rainbow')
st.sidebar.markdown('Build your diversity report with your latest DEI data.')

st.sidebar.header('Comply', divider='rainbow')
st.sidebar.markdown('Provide your reports to automatically answer and fill in the CDP Questionnaire.')

st.sidebar.image("Files/Images/Gemini.png", width= 300)





