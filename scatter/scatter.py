import streamlit as st
import pandas as pd
import numpy as np
import textwrap
import json, requests, urllib, io
import plotly.express as px

st.set_page_config(
    page_title='Scatter Plot Demo',
    page_icon='🚀'#,
#    layout='wide'
)

def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        with st.container():
            lb, col, rb = st.columns([1,3,1])
            col.subheader('Login')
            col.caption('This dashboard is private. If you know the password to open it, type it below:')
            col.text_input(
                "Password", type="password", on_change=password_entered, key="password"
            )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        with st.container():
            lb, col, rb = st.columns([1,3,1])
            col.subheader('Login')
            col.caption('This dashboard is private. If you know the password to open it, type it below:')
            col.text_input(
                "Password", type="password", on_change=password_entered, key="password"
            )
            col.error("Password incorrect")
        return False
    else:
        # Password correct.
        return True

if check_password():
    st.title('Streamlit Scatter')
    #st.subheader('Interactive scatter plot:')
    
    @st.cache
    def load_data(user, pao, csv_url):
                
        github_session = requests.Session()
        github_session.auth = (user, pao)

        download = github_session.get(csv_url).content
        data = pd.read_csv(io.StringIO(download.decode('utf-8')), sep=',', quotechar='"',quoting=2)
        data['Statement Hover'] = data['Statement'].apply(lambda x: '<br>' + '<br>'.join(textwrap.wrap(x, 30)))
        data['Step Hover'] = data['Step'].apply(lambda x: '<br>'.join(textwrap.wrap(x, 30)))
        return data
    
    
    user = st.secrets["git_username"]
    pao = st.secrets["git_pao"]
    csv_url = st.secrets["git_csv_path"]
    

    data = load_data(user, pao, csv_url)
        
    fig = px.scatter(data, x="Importance_Score", y="Satisfaction_Score", color="Step",
            size='Opportunity_Score', hover_name='Step Hover', 
            hover_data={
                'Step': False,
                'Importance_Score': ':.2f',
                'Satisfaction_Score': ':.2f',
                'Opportunity_Score': ':.2f',
                'Statement Hover': True
            },
            labels={'Importance_Score': 'Importance Score', 
            'Satisfaction_Score': 'Satisfaction Score', 
            'Opportunity_Score': 'Opportunity Score',
            'Statement Hover': 'Statement'}, height=900)

    fig.update_xaxes(range=[0,10], showspikes=True)
    fig.update_yaxes(range=[0,10], showspikes=True)
    fig.update_layout(legend=dict(x=0.5, y=-0.1, xanchor='center',yanchor='top', orientation="v"), hoverlabel={'align': 'left'})
    fig.update_layout(font_size=16)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("The Legend is interactive. All items are activated by default. Clicking on an item will toggle its visibility on the chart. You can double click on an item in the legend to focus on it. After double clicking on one item, you can add more items to the analysis by clicking on the others.")
    
    with st.expander('Show Raw data'):
        df = data[['Step', 'Statement', 'Importance_Score', 'Satisfaction_Score', 'Opportunity_Score']]
        df.columns = df.columns.str.replace('_', ' ')
        #df = df.set_index(['Step', 'Statement'])
        df = df.style.format({'Importance Score': '{:20,.2f}', 'Satisfaction Score': '{:20,.2f}', 'Opportunity Score': '{:20,.2f}'})
        st.table(df)
