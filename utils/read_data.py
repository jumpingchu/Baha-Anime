import streamlit as st
from google.oauth2.service_account import Credentials
from pandas_gbq import read_gbq

@st.cache_data(ttl=3600)
def read_bq_table(project_id, dataset_id, table_name, _credentials_info):
    sql = f"""
        SELECT
            *
        FROM
            `{dataset_id}.{table_name}`
        QUALIFY 
            RANK() OVER (PARTITION BY name ORDER BY created_at DESC) = 1
        ORDER BY score DESC
    """
    credentials = Credentials.from_service_account_info(_credentials_info)
    df = read_gbq(
        sql, project_id=project_id, dialect="standard", credentials=credentials
    )
    return df
