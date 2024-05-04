import streamlit as st
import pandas as pd

st.set_page_config(page_title="動畫評分整理", layout="wide")
st.title("近期動畫評分")

df = pd.read_csv("data/anime_info.csv", index_col=0)

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
        format="%f ⭐",
    ),
    "觀看人數": st.column_config.NumberColumn(
        format="%f 萬",
    )
}

st.dataframe(
    df,
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
