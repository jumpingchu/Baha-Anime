import streamlit as st
from google.oauth2.service_account import Credentials
from pandas_gbq import read_gbq

st.set_page_config(page_title="動畫瘋 - 近期動畫評分", layout="wide")
st.title("動畫瘋 - 近期動畫評分")


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


gcp_secrets = st.secrets["gcp"]
df = read_bq_table(
    gcp_secrets["project_id"],
    gcp_secrets["dataset_id"],
    gcp_secrets["table_name"],
    gcp_secrets,
)

df = df.rename(
    columns={
        "name": "動畫名稱",
        "yyyymm": "上映日期",
        "episodes": "集數",
        "view_count": "觀看人數",
        "score": "評分",
        "score_count": "評分人數",
        "five_stars_ratio": "五星比例",
        "anime_url": "連結",
    }
)

column_config = {
    "連結": st.column_config.LinkColumn(
        disabled=True,
        display_text="前往",
    ),
    "五星比例": st.column_config.ProgressColumn(
        min_value=0, max_value=100, format="%f%%"
    ),
    "評分": st.column_config.NumberColumn(
        format="%.1f ⭐",
    ),
    "觀看人數": st.column_config.NumberColumn(
        format="%f 萬",
    ),
}

st.dataframe(
    df,
    hide_index=True,
    width=1000,
    height=1000,
    column_config=column_config,
    column_order=[
        "上映日期",
        "連結",
        "動畫名稱",
        "評分",
        "評分人數",
        "觀看人數",
        "五星比例",
        "集數",
    ],
)
