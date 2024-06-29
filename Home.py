import streamlit as st
from utils import read_bq_table

st.set_page_config(page_title="動畫瘋 - 近期動畫評分", layout="wide")
st.title("動畫瘋 - 近期動畫評分")

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
        "yyyymm": "上映時間",
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
    "評分人數": st.column_config.NumberColumn(
        format="%d",
    ),
    "集數": st.column_config.NumberColumn(
        format="%d",
    ),
    "上映時間": st.column_config.DateColumn(
        format="YYYY-MM",
    ),
}

yyyymm_options = sorted(list(df["上映時間"].unique()), reverse=True)
default_yyyymm = yyyymm_options[:2]
selected_yyyymm = st.multiselect("選擇上映時間", options=yyyymm_options, default=default_yyyymm)
if selected_yyyymm:
    df = df[df["上映時間"].isin(selected_yyyymm)]

st.dataframe(
    df,
    hide_index=True,
    width=1000,
    # height=1000,
    column_config=column_config,
    column_order=[
        "上映時間",
        "連結",
        "動畫名稱",
        "評分",
        "評分人數",
        "觀看人數",
        "五星比例",
        "集數",
    ],
)
